"""
BM25 + 向量检索 + RRF 重排全链路自动评测脚本。

对比：
1. Vector Only：只使用 child 向量检索，再回查 parent。
2. Hybrid RRF：child 向量检索 + child BM25 检索，再用 RRF 融合重排，最后回查 parent。
"""
import argparse
import json
import os
import shutil
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_chroma import Chroma
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config_data as config
from benchmarks.parent_child_benchmark import (
    SELECTED_FILES,
    BM25Index,
    add_documents_in_batches,
    load_sections,
    mean,
    parse_json_object,
    relative_change,
    rrf_rerank,
    safe_div,
    stable_id,
    to_float,
    tokenize,
    trim_text,
)


DEFAULT_REPO_PATH = "/tmp/codex_xiaolin_csbase"
DEFAULT_RESULT_DIR = "benchmark_results"


@dataclass
class RetrievalTestCase:
    case_id: str
    question: str
    section_id: str
    source: str
    title: str
    gold_text: str
    category: str
    exact_terms: list[str]


CASE_SPECS = [
    ("exact_term", "Read View 在 MVCC 里如何工作的？", "Read View 在 MVCC 里如何工作的？请保留 Read View、活跃事务、版本链等术语。", ["Read View", "MVCC"]),
    ("exact_term", "为什么 TIME_WAIT 等待的时间是 2MSL？", "TIME_WAIT 为什么要等待 2MSL？", ["TIME_WAIT", "2MSL"]),
    ("exact_term", "Redis 使用的过期删除策略是什么？", "Redis 使用的过期删除策略是什么？", ["Redis", "过期删除"]),
    ("exact_term", "AOF 后台重写", "AOF 后台重写期间，新写入的命令是怎么处理的？", ["AOF", "后台重写"]),
    ("exact_term", "RDB 快照是如何实现的呢？", "RDB 快照是如何实现的？fork 和写时复制在其中起什么作用？", ["RDB", "fork", "写时复制"]),
    ("mixed_keyword", "select/poll", "select 和 poll 的区别是什么？它们有什么性能问题？", ["select", "poll"]),
    ("mixed_keyword", "epoll", "epoll 相比 select/poll 做了哪些改进？", ["epoll", "select", "poll"]),
    ("mixed_keyword", "HTTP/2 做了什么优化？", "HTTP/2 做了什么优化？请说明 HPACK、Stream 和二进制帧。", ["HTTP/2", "HPACK", "Stream"]),
    ("mixed_keyword", "HTTP/3 做了哪些优化？", "HTTP/3 和 QUIC 解决了 HTTP/2 的哪些问题？", ["HTTP/3", "QUIC"]),
    ("mixed_keyword", "LRU 算法和 LFU 算法有什么区别？", "Redis 里的 LRU 和 LFU 有什么区别？", ["LRU", "LFU"]),
    ("protocol_field", "如何唯一确定一个 TCP 连接呢？", "TCP 连接为什么可以用四元组唯一确定？四元组分别是什么？", ["TCP", "四元组"]),
    ("protocol_field", "什么是 SYN 攻击？如何避免 SYN 攻击？", "什么是 SYN 攻击？有哪些避免办法？", ["SYN", "攻击"]),
    ("protocol_field", "TCP 四次挥手过程是怎样的？", "TCP 四次挥手里 FIN 和 ACK 是如何交互的？", ["TCP", "FIN", "ACK"]),
    ("protocol_field", "ARP", "ARP 是如何根据 IP 地址获取 MAC 地址的？", ["ARP", "IP", "MAC"]),
    ("protocol_field", "无分类地址 CIDR", "CIDR 是什么？子网掩码和网络号如何理解？", ["CIDR", "子网掩码"]),
    ("semantic", "为什么是三次握手？不是两次、四次？", "为什么建立连接不能只握手两次，也不需要四次？", ["三次握手"]),
    ("semantic", "线程与进程的比较", "操作系统为什么要区分进程和线程？它们各自有什么特点？", ["进程", "线程"]),
    ("semantic", "进程的上下文切换", "为什么进程切换会有上下文切换成本？", ["上下文切换"]),
    ("semantic", "虚拟内存", "为什么操作系统需要虚拟内存？它解决了什么问题？", ["虚拟内存"]),
    ("semantic", "如何避免缓存雪崩、缓存击穿、缓存穿透？", "缓存雪崩、缓存击穿、缓存穿透分别如何避免？", ["缓存雪崩", "缓存击穿", "缓存穿透"]),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", default=DEFAULT_REPO_PATH)
    parser.add_argument("--result-dir", default=DEFAULT_RESULT_DIR)
    parser.add_argument("--case-count", type=int, default=20)
    parser.add_argument("--skip-llm-judge", action="store_true")
    args = parser.parse_args()

    if not os.getenv("DASHSCOPE_API_KEY"):
        raise RuntimeError("缺少 DASHSCOPE_API_KEY，请先配置 DASHSCOPE_API_KEY。")

    repo_path = Path(args.repo_path)
    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)

    run_id = time.strftime("%Y%m%d_%H%M%S")
    work_dir = Path("/tmp") / f"codex_hybrid_retrieval_benchmark_{run_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/6] 读取资料：{repo_path}", flush=True)
    sections = load_sections(repo_path)
    cases = build_test_cases(sections, args.case_count)
    print(f"sections={len(sections)}, test_cases={len(cases)}", flush=True)

    print("[2/6] 构建同一套 Parent-Child 索引", flush=True)
    embedding = DashScopeEmbeddings(model=config.embedding_model_name)
    retriever = ParentChildRetrievalSystem(
        sections=sections,
        embedding=embedding,
        persist_dir=str(work_dir / "hybrid_chroma"),
    )
    print(
        f"parents={len(retriever.parent_records)}, child_vector_chunks={len(retriever.child_docs)}",
        flush=True,
    )

    chat_model = ChatTongyi(model=config.chat_model_name)
    judge_model = ChatTongyi(model=config.chat_model_name)

    print("[3/6] 执行 Vector Only 与 Hybrid RRF 对照测试", flush=True)
    case_results = []
    for index, case in enumerate(cases, start=1):
        print(f"case {index}/{len(cases)} [{case.category}]: {case.title[:42]}", flush=True)
        vector_result = run_case(retriever, "vector_only", chat_model, case)
        hybrid_result = run_case(retriever, "hybrid_rrf", chat_model, case)
        lexical_scores = evaluate_lexical(case, vector_result, hybrid_result)
        judge_scores = {}
        if not args.skip_llm_judge:
            judge_scores = judge_answers(judge_model, case, vector_result, hybrid_result)

        case_results.append({
            "case": case.__dict__,
            "vector_only": vector_result,
            "hybrid_rrf": hybrid_result,
            "lexical_scores": lexical_scores,
            "judge_scores": judge_scores,
        })

    print("[4/6] 汇总指标", flush=True)
    summary = summarize_results(case_results)
    payload = {
        "run_id": run_id,
        "source_repo": "https://github.com/xiaolincoder/CS-Base",
        "selected_files": SELECTED_FILES,
        "config": {
            "parent_chunk_size": 2000,
            "parent_chunk_overlap": 200,
            "child_chunk_size": 400,
            "child_chunk_overlap": 80,
            "vector_k": 6,
            "bm25_k": 6,
            "rerank_top_k": 3,
            "rrf_k": 60,
            "case_count": len(cases),
            "embedding_model": config.embedding_model_name,
            "chat_model": config.chat_model_name,
        },
        "index_stats": {
            "sections": len(sections),
            "parent_records": len(retriever.parent_records),
            "child_vector_chunks": len(retriever.child_docs),
        },
        "summary": summary,
        "cases": case_results,
    }

    print("[5/6] 写入测试报告", flush=True)
    json_path = result_dir / f"hybrid_retrieval_benchmark_{run_id}.json"
    md_path = result_dir / f"hybrid_retrieval_benchmark_{run_id}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(payload), encoding="utf-8")

    print("[6/6] 清理临时索引", flush=True)
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"json_result={json_path}", flush=True)
    print(f"markdown_result={md_path}", flush=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


class ParentChildRetrievalSystem:
    def __init__(self, sections, embedding, persist_dir):
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=config.parent_child_separators,
            length_function=len,
        )
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=80,
            separators=config.parent_child_separators,
            length_function=len,
        )

        self.parent_records = {}
        self.child_docs = []
        child_ids = []
        for section in sections:
            parents = parent_splitter.split_text(section.text)
            for parent_index, parent_text in enumerate(parents):
                parent_id = stable_id("parent", section.section_id, parent_index)
                self.parent_records[parent_id] = {
                    "text": parent_text,
                    "metadata": {
                        "parent_id": parent_id,
                        "section_id": section.section_id,
                        "source": section.source,
                        "title": section.title,
                        "parent_index": parent_index,
                    },
                }
                children = child_splitter.split_text(parent_text)
                for child_index, child_text in enumerate(children):
                    child_id = stable_id("child", parent_id, child_index)
                    self.child_docs.append(Document(
                        page_content=child_text,
                        metadata={
                            "child_id": child_id,
                            "parent_id": parent_id,
                            "section_id": section.section_id,
                            "source": section.source,
                            "title": section.title,
                            "parent_index": parent_index,
                            "child_index": child_index,
                        },
                    ))
                    child_ids.append(child_id)

        self.vector_store = Chroma(
            collection_name="hybrid_retrieval_benchmark",
            embedding_function=embedding,
            persist_directory=persist_dir,
        )
        add_documents_in_batches(self.vector_store, self.child_docs, child_ids)
        self.bm25 = BM25Index(self.child_docs, doc_id_key="child_id")

    def retrieve(self, query, mode):
        start = time.perf_counter()
        vector_docs = self.vector_store.similarity_search(query, k=6)
        if mode == "vector_only":
            child_docs = vector_docs[:3]
        elif mode == "hybrid_rrf":
            bm25_docs = self.bm25.search(query, k=6)
            child_docs = rrf_rerank(vector_docs, bm25_docs, doc_id_key="child_id", top_k=3)
        else:
            raise ValueError(f"未知检索模式：{mode}")

        parent_docs = self._children_to_parents(child_docs)
        elapsed = time.perf_counter() - start
        context = "\n\n".join(
            f"父级资料片段：{doc.page_content}\n来源：{doc.metadata.get('source')} / {doc.metadata.get('title')}\n命中的子片段：{doc.metadata.get('matched_child')}"
            for doc in parent_docs
        )
        return child_docs, parent_docs, context, elapsed

    def _children_to_parents(self, child_docs):
        parent_docs = []
        used_parent_ids = set()
        for child_doc in child_docs:
            parent_id = child_doc.metadata.get("parent_id")
            if not parent_id or parent_id in used_parent_ids:
                continue
            parent_record = self.parent_records.get(parent_id)
            if not parent_record:
                continue
            used_parent_ids.add(parent_id)
            metadata = dict(parent_record["metadata"])
            metadata["matched_child"] = child_doc.page_content
            metadata["matched_child_id"] = child_doc.metadata.get("child_id")
            parent_docs.append(Document(page_content=parent_record["text"], metadata=metadata))
        return parent_docs


def build_test_cases(sections, case_count):
    section_by_title = {section.title: section for section in sections}
    cases = []
    for index, (category, title, question, terms) in enumerate(CASE_SPECS[:case_count], start=1):
        section = section_by_title.get(title)
        if not section:
            continue
        cases.append(RetrievalTestCase(
            case_id=f"case_{index:02d}",
            question=question,
            section_id=section.section_id,
            source=section.source,
            title=section.title,
            gold_text=section.text,
            category=category,
            exact_terms=terms,
        ))
    return cases


def run_case(retriever, mode, chat_model, case):
    child_docs, parent_docs, context, retrieval_seconds = retriever.retrieve(case.question, mode)
    prompt_messages = [
        SystemMessage(content=(
            "你是知识复用助手。只能依据用户提供的参考资料回答。"
            "回答时尽量沿用资料原有的知识结构、术语、分类和因果链。"
            "如果资料不足，请说明资料不足。"
        )),
        HumanMessage(content=(
            f"参考资料：\n{context}\n\n"
            f"用户问题：{case.question}\n\n"
            "请输出适合复习的结构化回答："
        )),
    ]
    answer_start = time.perf_counter()
    try:
        answer = chat_model.invoke(prompt_messages).content
        error = ""
    except Exception as exc:
        answer = ""
        error = str(exc)
    answer_seconds = time.perf_counter() - answer_start

    retrieved_section_ids = [doc.metadata.get("section_id") for doc in parent_docs]
    hit_rank = first_hit_rank(retrieved_section_ids, case.section_id)
    return {
        "mode": mode,
        "retrieved_section_ids": retrieved_section_ids,
        "retrieved_titles": [doc.metadata.get("title") for doc in parent_docs],
        "child_titles": [doc.metadata.get("title") for doc in child_docs],
        "hit_gold": hit_rank is not None,
        "hit_rank": hit_rank,
        "mrr": 0.0 if hit_rank is None else 1 / hit_rank,
        "context": context,
        "context_chars": len(context),
        "answer": answer,
        "answer_chars": len(answer),
        "retrieval_seconds": retrieval_seconds,
        "answer_seconds": answer_seconds,
        "total_seconds": retrieval_seconds + answer_seconds,
        "error": error,
    }


def evaluate_lexical(case, vector_result, hybrid_result):
    gold_tokens = set(tokenize(case.gold_text))

    def score(result):
        context_tokens = set(tokenize(result["context"]))
        answer_tokens = set(tokenize(result["answer"]))
        context_coverage = safe_div(len(gold_tokens & context_tokens), len(gold_tokens))
        answer_overlap = safe_div(len(gold_tokens & answer_tokens), len(gold_tokens))
        context_noise = 1 - safe_div(len(context_tokens & gold_tokens), len(context_tokens))
        exact_term_recall = exact_terms_recall(case.exact_terms, result["context"])
        return {
            "context_coverage": context_coverage,
            "context_noise": context_noise,
            "answer_gold_overlap": answer_overlap,
            "exact_term_recall": exact_term_recall,
        }

    return {
        "vector_only": score(vector_result),
        "hybrid_rrf": score(hybrid_result),
    }


def judge_answers(judge_model, case, vector_result, hybrid_result):
    prompt = f"""
你是严格的 RAG 自动评测员。请根据“标准资料”分别评价两个回答。
评分必须只依据标准资料，不要按你自己的知识补分。

评分维度，每项 0-5 分：
- correctness：事实正确性
- groundedness：是否能被标准资料支持
- keypoint_coverage：是否覆盖资料中的关键点
- term_preservation：是否保留问题和资料中的关键术语、缩写、协议字段
- structure_preservation：是否沿用标准资料的知识结构、术语、分类和因果链

请只输出 JSON，不要解释，不要 Markdown。

问题：
{case.question}

标准资料：
{trim_text(case.gold_text, 5000)}

回答 A（Vector Only）：
{trim_text(vector_result["answer"], 2600)}

回答 B（Hybrid RRF）：
{trim_text(hybrid_result["answer"], 2600)}

JSON 格式：
{{
  "vector_only": {{
    "correctness": 0,
    "groundedness": 0,
    "keypoint_coverage": 0,
    "term_preservation": 0,
    "structure_preservation": 0
  }},
  "hybrid_rrf": {{
    "correctness": 0,
    "groundedness": 0,
    "keypoint_coverage": 0,
    "term_preservation": 0,
    "structure_preservation": 0
  }},
  "winner": "vector_only 或 hybrid_rrf 或 tie"
}}
""".strip()

    try:
        text = judge_model.invoke([HumanMessage(content=prompt)]).content
        return parse_json_object(text)
    except Exception as exc:
        return {"error": str(exc)}


def summarize_results(case_results):
    vector = collect_system_metrics(case_results, "vector_only")
    hybrid = collect_system_metrics(case_results, "hybrid_rrf")

    judge_dims = ["correctness", "groundedness", "keypoint_coverage", "term_preservation", "structure_preservation"]
    vector_quality = collect_quality(case_results, "vector_only", judge_dims)
    hybrid_quality = collect_quality(case_results, "hybrid_rrf", judge_dims)
    vector["llm_quality_avg_0_5"] = vector_quality
    hybrid["llm_quality_avg_0_5"] = hybrid_quality

    category_summary = {}
    categories = sorted({item["case"]["category"] for item in case_results})
    for category in categories:
        category_items = [item for item in case_results if item["case"]["category"] == category]
        category_summary[category] = {
            "case_count": len(category_items),
            "vector_only_hit_rate": mean([1 if item["vector_only"]["hit_gold"] else 0 for item in category_items]),
            "hybrid_rrf_hit_rate": mean([1 if item["hybrid_rrf"]["hit_gold"] else 0 for item in category_items]),
            "vector_only_mrr": mean([item["vector_only"]["mrr"] for item in category_items]),
            "hybrid_rrf_mrr": mean([item["hybrid_rrf"]["mrr"] for item in category_items]),
            "vector_only_exact_term_recall": mean([item["lexical_scores"]["vector_only"]["exact_term_recall"] for item in category_items]),
            "hybrid_rrf_exact_term_recall": mean([item["lexical_scores"]["hybrid_rrf"]["exact_term_recall"] for item in category_items]),
        }

    winners = {"vector_only": 0, "hybrid_rrf": 0, "tie": 0, "unknown": 0}
    for item in case_results:
        winner = (item.get("judge_scores") or {}).get("winner", "unknown")
        winners[winner if winner in winners else "unknown"] += 1

    return {
        "case_count": len(case_results),
        "vector_only": vector,
        "hybrid_rrf": hybrid,
        "hit_rate_relative_change": relative_change(hybrid["hit_rate"], vector["hit_rate"]),
        "mrr_relative_change": relative_change(hybrid["mrr"], vector["mrr"]),
        "exact_term_recall_relative_change": relative_change(hybrid["avg_exact_term_recall"], vector["avg_exact_term_recall"]),
        "context_noise_relative_change": relative_change(hybrid["avg_context_noise"], vector["avg_context_noise"]),
        "quality_relative_change": relative_change(hybrid_quality, vector_quality),
        "retrieval_latency_relative_change": relative_change(hybrid["avg_retrieval_seconds"], vector["avg_retrieval_seconds"]),
        "total_latency_relative_change": relative_change(hybrid["avg_total_seconds"], vector["avg_total_seconds"]),
        "context_chars_relative_change": relative_change(hybrid["avg_context_chars"], vector["avg_context_chars"]),
        "winners": winners,
        "category_summary": category_summary,
    }


def collect_system_metrics(case_results, key):
    results = [item[key] for item in case_results]
    lexical = [item["lexical_scores"][key] for item in case_results]
    return {
        "hit_rate": mean([1 if item["hit_gold"] else 0 for item in results]),
        "mrr": mean([item["mrr"] for item in results]),
        "avg_context_coverage": mean([item["context_coverage"] for item in lexical]),
        "avg_context_noise": mean([item["context_noise"] for item in lexical]),
        "avg_answer_gold_overlap": mean([item["answer_gold_overlap"] for item in lexical]),
        "avg_exact_term_recall": mean([item["exact_term_recall"] for item in lexical]),
        "avg_context_chars": mean([item["context_chars"] for item in results]),
        "avg_answer_chars": mean([item["answer_chars"] for item in results]),
        "avg_retrieval_seconds": mean([item["retrieval_seconds"] for item in results]),
        "avg_answer_seconds": mean([item["answer_seconds"] for item in results]),
        "avg_total_seconds": mean([item["total_seconds"] for item in results]),
        "error_count": sum(1 for item in results if item.get("error")),
    }


def collect_quality(case_results, system_key, dims):
    values = []
    for item in case_results:
        judge = item.get("judge_scores") or {}
        if system_key not in judge:
            continue
        scores = [to_float(judge[system_key].get(dim)) for dim in dims]
        values.append(statistics.mean(scores))
    return mean(values)


def render_markdown_report(payload):
    summary = payload["summary"]
    lines = [
        "# Hybrid Retrieval Benchmark",
        "",
        f"- Source: {payload['source_repo']}",
        f"- Cases: {summary['case_count']}",
        f"- Chat model: {payload['config']['chat_model']}",
        f"- Embedding model: {payload['config']['embedding_model']}",
        f"- Parent records: {payload['index_stats']['parent_records']}",
        f"- Child vector chunks: {payload['index_stats']['child_vector_chunks']}",
        "",
        "## Summary",
        "",
        "| Metric | Vector Only | Hybrid RRF | Change |",
        "| --- | ---: | ---: | ---: |",
    ]

    rows = [
        ("Hit Rate", "hit_rate", "percent"),
        ("MRR", "mrr", "number"),
        ("Exact Term Recall", "avg_exact_term_recall", "percent"),
        ("Context Coverage", "avg_context_coverage", "percent"),
        ("Context Noise", "avg_context_noise", "percent"),
        ("Answer Gold Overlap", "avg_answer_gold_overlap", "percent"),
        ("LLM Quality 0-5", "llm_quality_avg_0_5", "number"),
        ("Avg Context Chars", "avg_context_chars", "number"),
        ("Avg Retrieval Seconds", "avg_retrieval_seconds", "number"),
        ("Avg Total Seconds", "avg_total_seconds", "number"),
    ]
    for label, key, fmt in rows:
        vector_value = summary["vector_only"].get(key)
        hybrid_value = summary["hybrid_rrf"].get(key)
        lines.append(
            f"| {label} | {format_value(vector_value, fmt)} | {format_value(hybrid_value, fmt)} | {format_percent(relative_change(hybrid_value, vector_value))} |"
        )

    lines.extend([
        "",
        "## Category Summary",
        "",
        "| Category | Cases | Vector Hit | Hybrid Hit | Vector MRR | Hybrid MRR | Vector Term Recall | Hybrid Term Recall |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for category, row in summary["category_summary"].items():
        lines.append(
            f"| {category} | {row['case_count']} | {row['vector_only_hit_rate'] * 100:.2f}% | {row['hybrid_rrf_hit_rate'] * 100:.2f}% | "
            f"{row['vector_only_mrr']:.3f} | {row['hybrid_rrf_mrr']:.3f} | "
            f"{row['vector_only_exact_term_recall'] * 100:.2f}% | {row['hybrid_rrf_exact_term_recall'] * 100:.2f}% |"
        )

    lines.extend([
        "",
        "## Winners",
        "",
        f"- Vector Only: {summary['winners']['vector_only']}",
        f"- Hybrid RRF: {summary['winners']['hybrid_rrf']}",
        f"- Tie: {summary['winners']['tie']}",
        "",
        "## Cases",
        "",
    ])
    for item in payload["cases"]:
        case = item["case"]
        lines.extend([
            f"### {case['case_id']} {case['title']}",
            "",
            f"- Category: {case['category']}",
            f"- Question: {case['question']}",
            f"- Gold source: {case['source']}",
            f"- Vector hit/rank: {item['vector_only']['hit_gold']} / {item['vector_only']['hit_rank']}",
            f"- Hybrid hit/rank: {item['hybrid_rrf']['hit_gold']} / {item['hybrid_rrf']['hit_rank']}",
            f"- Judge: `{json.dumps(item.get('judge_scores', {}), ensure_ascii=False)}`",
            "",
        ])
    return "\n".join(lines)


def first_hit_rank(section_ids, gold_section_id):
    for index, section_id in enumerate(section_ids, start=1):
        if section_id == gold_section_id:
            return index
    return None


def exact_terms_recall(terms, text):
    if not terms:
        return 0.0
    text_lower = (text or "").lower()
    hits = 0
    for term in terms:
        if term.lower() in text_lower:
            hits += 1
    return hits / len(terms)


def format_percent(value):
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def format_value(value, fmt):
    if value is None:
        return "N/A"
    if fmt == "percent":
        return f"{value * 100:.2f}%"
    return f"{value:.3f}"


if __name__ == "__main__":
    main()
