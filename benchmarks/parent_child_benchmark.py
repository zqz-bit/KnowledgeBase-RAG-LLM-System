"""
Parent-Child Chunking 全链路自动评测脚本。

对比：
1. 普通分块：flat chunk 1000/100，混合检索后直接把 chunk 给模型。
2. 父子分块：parent 2000/200 + child 400/80，混合检索命中 child 后回查 parent 给模型。

评测内容：
- 检索命中率
- 上下文覆盖度和噪声
- 回答质量、忠实度、知识结构复用
- 延迟和上下文长度
"""
import argparse
import hashlib
import json
import os
import random
import re
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


DEFAULT_REPO_PATH = "/tmp/codex_xiaolin_csbase"
DEFAULT_RESULT_DIR = "benchmark_results"


SELECTED_FILES = [
    "network/3_tcp/tcp_interview.md",
    "network/2_http/http_interview.md",
    "network/1_base/tcp_ip_model.md",
    "network/4_ip/ip_base.md",
    "os/4_process/process_base.md",
    "os/4_process/process_commu.md",
    "os/3_memory/vmem.md",
    "os/8_network_system/selete_poll_epoll.md",
    "mysql/index/index_interview.md",
    "mysql/transaction/mvcc.md",
    "redis/base/redis_interview.md",
    "redis/storage/aof.md",
]


@dataclass
class Section:
    section_id: str
    source: str
    title: str
    text: str


@dataclass
class TestCase:
    case_id: str
    question: str
    section_id: str
    source: str
    title: str
    gold_text: str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", default=DEFAULT_REPO_PATH)
    parser.add_argument("--result-dir", default=DEFAULT_RESULT_DIR)
    parser.add_argument("--case-count", type=int, default=18)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--skip-llm-judge", action="store_true")
    args = parser.parse_args()

    if not os.getenv("DASHSCOPE_API_KEY"):
        raise RuntimeError("缺少 DASHSCOPE_API_KEY，请先在环境变量中配置阿里云百炼 API Key。")

    random.seed(args.seed)
    repo_path = Path(args.repo_path)
    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)

    run_id = time.strftime("%Y%m%d_%H%M%S")
    work_dir = Path("/tmp") / f"codex_parent_child_benchmark_{run_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/6] 读取资料：{repo_path}")
    sections = load_sections(repo_path)
    test_cases = build_test_cases(sections, args.case_count)
    print(f"sections={len(sections)}, test_cases={len(test_cases)}")

    print("[2/6] 构建普通分块索引")
    embedding = DashScopeEmbeddings(model=config.embedding_model_name)
    flat_system = FlatRagSystem(
        sections=sections,
        embedding=embedding,
        persist_dir=str(work_dir / "flat_chroma"),
    )

    print("[3/6] 构建父子分块索引")
    parent_child_system = ParentChildRagSystem(
        sections=sections,
        embedding=embedding,
        persist_dir=str(work_dir / "parent_child_chroma"),
    )

    chat_model = ChatTongyi(model=config.chat_model_name)
    judge_model = ChatTongyi(model=config.chat_model_name)

    print("[4/6] 执行检索 + 回答 + 自动评分")
    case_results = []
    for index, case in enumerate(test_cases, start=1):
        print(f"case {index}/{len(test_cases)}: {case.title[:40]}")
        flat_result = run_case(flat_system, chat_model, case)
        parent_child_result = run_case(parent_child_system, chat_model, case)

        lexical_scores = evaluate_lexical(case, flat_result, parent_child_result)
        judge_scores = {}
        if not args.skip_llm_judge:
            judge_scores = judge_answers(judge_model, case, flat_result, parent_child_result)

        case_results.append({
            "case": case.__dict__,
            "flat": flat_result,
            "parent_child": parent_child_result,
            "lexical_scores": lexical_scores,
            "judge_scores": judge_scores,
        })

    print("[5/6] 汇总指标")
    summary = summarize_results(case_results)
    result_payload = {
        "run_id": run_id,
        "source_repo": "https://github.com/xiaolincoder/CS-Base",
        "selected_files": SELECTED_FILES,
        "config": {
            "flat_chunk_size": 1000,
            "flat_chunk_overlap": 100,
            "parent_chunk_size": 2000,
            "parent_chunk_overlap": 200,
            "child_chunk_size": 400,
            "child_chunk_overlap": 80,
            "vector_k": 6,
            "bm25_k": 6,
            "rerank_top_k": 3,
            "case_count": len(test_cases),
            "embedding_model": config.embedding_model_name,
            "chat_model": config.chat_model_name,
        },
        "summary": summary,
        "cases": case_results,
    }

    json_path = result_dir / f"parent_child_benchmark_{run_id}.json"
    md_path = result_dir / f"parent_child_benchmark_{run_id}.md"
    json_path.write_text(json.dumps(result_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(result_payload), encoding="utf-8")

    print("[6/6] 清理临时索引")
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"json_result={json_path}")
    print(f"markdown_result={md_path}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


class FlatRagSystem:
    name = "flat"

    def __init__(self, sections, embedding, persist_dir):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=config.parent_child_separators,
            length_function=len,
        )
        docs = []
        ids = []
        for section in sections:
            chunks = splitter.split_text(section.text)
            for chunk_index, chunk in enumerate(chunks):
                chunk_id = stable_id("flat", section.section_id, chunk_index)
                docs.append(Document(
                    page_content=chunk,
                    metadata={
                        "chunk_id": chunk_id,
                        "section_id": section.section_id,
                        "source": section.source,
                        "title": section.title,
                        "chunk_index": chunk_index,
                    },
                ))
                ids.append(chunk_id)

        self.docs_by_id = {doc.metadata["chunk_id"]: doc for doc in docs}
        self.vector_store = build_chroma("flat_benchmark", embedding, persist_dir)
        add_documents_in_batches(self.vector_store, docs, ids)
        self.bm25 = BM25Index(docs, doc_id_key="chunk_id")

    def retrieve(self, query):
        start = time.perf_counter()
        vector_docs = self.vector_store.similarity_search(query, k=6)
        bm25_docs = self.bm25.search(query, k=6)
        docs = rrf_rerank(vector_docs, bm25_docs, doc_id_key="chunk_id", top_k=3)
        elapsed = time.perf_counter() - start
        context = "\n\n".join(
            f"资料片段：{doc.page_content}\n来源：{doc.metadata.get('source')} / {doc.metadata.get('title')}"
            for doc in docs
        )
        return docs, context, elapsed


class ParentChildRagSystem:
    name = "parent_child"

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

        parent_records = {}
        child_docs = []
        child_ids = []
        for section in sections:
            parents = parent_splitter.split_text(section.text)
            for parent_index, parent_text in enumerate(parents):
                parent_id = stable_id("parent", section.section_id, parent_index)
                parent_records[parent_id] = {
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
                    child_docs.append(Document(
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

        self.parent_records = parent_records
        self.vector_store = build_chroma("parent_child_benchmark", embedding, persist_dir)
        add_documents_in_batches(self.vector_store, child_docs, child_ids)
        self.bm25 = BM25Index(child_docs, doc_id_key="child_id")

    def retrieve(self, query):
        start = time.perf_counter()
        vector_docs = self.vector_store.similarity_search(query, k=6)
        bm25_docs = self.bm25.search(query, k=6)
        child_docs = rrf_rerank(vector_docs, bm25_docs, doc_id_key="child_id", top_k=3)

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
            parent_docs.append(Document(page_content=parent_record["text"], metadata=metadata))

        elapsed = time.perf_counter() - start
        context = "\n\n".join(
            f"父级资料片段：{doc.page_content}\n来源：{doc.metadata.get('source')} / {doc.metadata.get('title')}\n命中的子片段：{doc.metadata.get('matched_child')}"
            for doc in parent_docs
        )
        return parent_docs, context, elapsed


class BM25Index:
    def __init__(self, docs, doc_id_key):
        from rank_bm25 import BM25Okapi

        self.docs = docs
        self.doc_id_key = doc_id_key
        self.tokenized_corpus = [tokenize(doc.page_content) for doc in docs]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query, k):
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        docs = []
        for index in ranked[:k]:
            score = float(scores[index])
            if score <= 0:
                continue
            doc = self.docs[index]
            metadata = dict(doc.metadata)
            metadata["bm25_score"] = score
            docs.append(Document(page_content=doc.page_content, metadata=metadata))
        return docs


def build_chroma(collection_name, embedding, persist_dir):
    return Chroma(
        collection_name=collection_name,
        embedding_function=embedding,
        persist_directory=persist_dir,
    )


def add_documents_in_batches(vector_store, docs, ids, batch_size=10):
    for start in range(0, len(docs), batch_size):
        end = start + batch_size
        vector_store.add_documents(docs[start:end], ids=ids[start:end])


def run_case(system, chat_model, case):
    docs, context, retrieval_seconds = system.retrieve(case.question)
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

    retrieved_section_ids = [doc.metadata.get("section_id") for doc in docs]
    context_chars = len(context)
    answer_chars = len(answer)
    return {
        "system": system.name,
        "retrieved_section_ids": retrieved_section_ids,
        "retrieved_titles": [doc.metadata.get("title") for doc in docs],
        "hit_gold": case.section_id in retrieved_section_ids,
        "context": context,
        "context_chars": context_chars,
        "answer": answer,
        "answer_chars": answer_chars,
        "retrieval_seconds": retrieval_seconds,
        "answer_seconds": answer_seconds,
        "total_seconds": retrieval_seconds + answer_seconds,
        "error": error,
    }


def judge_answers(judge_model, case, flat_result, parent_child_result):
    source_text = trim_text(case.gold_text, 5000)
    flat_answer = trim_text(flat_result["answer"], 2600)
    parent_child_answer = trim_text(parent_child_result["answer"], 2600)
    prompt = f"""
你是严格的 RAG 自动评测员。请根据“标准资料”分别评价两个回答。
评分必须只依据标准资料，不要按你自己的知识补分。

评分维度，每项 0-5 分：
- correctness：事实正确性
- groundedness：是否能被标准资料支持
- keypoint_coverage：是否覆盖资料中的关键点
- structure_preservation：是否沿用标准资料的知识结构、术语、分类和因果链

请只输出 JSON，不要解释，不要 Markdown。

问题：
{case.question}

标准资料：
{source_text}

回答 A（普通分块）：
{flat_answer}

回答 B（父子分块）：
{parent_child_answer}

JSON 格式：
{{
  "flat": {{
    "correctness": 0,
    "groundedness": 0,
    "keypoint_coverage": 0,
    "structure_preservation": 0
  }},
  "parent_child": {{
    "correctness": 0,
    "groundedness": 0,
    "keypoint_coverage": 0,
    "structure_preservation": 0
  }},
  "winner": "flat 或 parent_child 或 tie"
}}
""".strip()

    try:
        text = judge_model.invoke([HumanMessage(content=prompt)]).content
        return parse_json_object(text)
    except Exception as exc:
        return {"error": str(exc)}


def evaluate_lexical(case, flat_result, parent_child_result):
    gold_tokens = set(tokenize(case.gold_text))
    if not gold_tokens:
        gold_tokens = set()

    def score(result):
        context_tokens = set(tokenize(result["context"]))
        answer_tokens = set(tokenize(result["answer"]))
        context_coverage = safe_div(len(gold_tokens & context_tokens), len(gold_tokens))
        answer_overlap = safe_div(len(gold_tokens & answer_tokens), len(gold_tokens))
        context_noise = 1 - safe_div(len(context_tokens & gold_tokens), len(context_tokens))
        return {
            "context_coverage": context_coverage,
            "answer_gold_overlap": answer_overlap,
            "context_noise": context_noise,
        }

    return {
        "flat": score(flat_result),
        "parent_child": score(parent_child_result),
    }


def summarize_results(case_results):
    flat_quality = []
    parent_quality = []
    dimensions = ["correctness", "groundedness", "keypoint_coverage", "structure_preservation"]

    for item in case_results:
        judge = item.get("judge_scores") or {}
        if "flat" not in judge or "parent_child" not in judge:
            continue
        flat_scores = [to_float(judge["flat"].get(dim)) for dim in dimensions]
        parent_scores = [to_float(judge["parent_child"].get(dim)) for dim in dimensions]
        flat_quality.append(statistics.mean(flat_scores))
        parent_quality.append(statistics.mean(parent_scores))

    flat = collect_system_metrics(case_results, "flat")
    parent_child = collect_system_metrics(case_results, "parent_child")

    if flat_quality and parent_quality:
        flat["llm_quality_avg_0_5"] = statistics.mean(flat_quality)
        parent_child["llm_quality_avg_0_5"] = statistics.mean(parent_quality)
        quality_improvement = relative_change(
            parent_child["llm_quality_avg_0_5"],
            flat["llm_quality_avg_0_5"],
        )
    else:
        quality_improvement = None

    flat_structure = collect_judge_dimension(case_results, "flat", "structure_preservation")
    parent_structure = collect_judge_dimension(case_results, "parent_child", "structure_preservation")
    structure_improvement = relative_change(parent_structure, flat_structure)

    flat_reuse_efficiency = safe_div(flat.get("llm_quality_avg_0_5", 0), flat["avg_context_chars"])
    parent_reuse_efficiency = safe_div(parent_child.get("llm_quality_avg_0_5", 0), parent_child["avg_context_chars"])

    return {
        "case_count": len(case_results),
        "flat": flat,
        "parent_child": parent_child,
        "quality_relative_improvement": quality_improvement,
        "structure_preservation_flat_avg": flat_structure,
        "structure_preservation_parent_child_avg": parent_structure,
        "structure_preservation_relative_improvement": structure_improvement,
        "knowledge_reuse_efficiency_quality_per_1k_context_chars": {
            "flat": flat_reuse_efficiency * 1000,
            "parent_child": parent_reuse_efficiency * 1000,
            "relative_change": relative_change(parent_reuse_efficiency, flat_reuse_efficiency),
        },
        "latency_relative_change": relative_change(parent_child["avg_total_seconds"], flat["avg_total_seconds"]),
        "context_chars_relative_change": relative_change(parent_child["avg_context_chars"], flat["avg_context_chars"]),
    }


def collect_system_metrics(case_results, key):
    results = [item[key] for item in case_results]
    lexical = [item["lexical_scores"][key] for item in case_results]
    return {
        "hit_rate": mean([1 if item["hit_gold"] else 0 for item in results]),
        "avg_context_coverage": mean([item["context_coverage"] for item in lexical]),
        "avg_context_noise": mean([item["context_noise"] for item in lexical]),
        "avg_answer_gold_overlap": mean([item["answer_gold_overlap"] for item in lexical]),
        "avg_context_chars": mean([item["context_chars"] for item in results]),
        "avg_answer_chars": mean([item["answer_chars"] for item in results]),
        "avg_retrieval_seconds": mean([item["retrieval_seconds"] for item in results]),
        "avg_answer_seconds": mean([item["answer_seconds"] for item in results]),
        "avg_total_seconds": mean([item["total_seconds"] for item in results]),
        "error_count": sum(1 for item in results if item.get("error")),
    }


def collect_judge_dimension(case_results, system_key, dimension):
    values = []
    for item in case_results:
        judge = item.get("judge_scores") or {}
        if system_key in judge:
            values.append(to_float(judge[system_key].get(dimension)))
    return mean(values)


def render_markdown_report(payload):
    summary = payload["summary"]
    lines = [
        "# Parent-Child Chunking Benchmark",
        "",
        f"- Source: {payload['source_repo']}",
        f"- Cases: {summary['case_count']}",
        f"- Chat model: {payload['config']['chat_model']}",
        f"- Embedding model: {payload['config']['embedding_model']}",
        "",
        "## Summary",
        "",
        "| Metric | Flat | Parent-Child | Change |",
        "| --- | ---: | ---: | ---: |",
    ]
    rows = [
        ("Hit Rate", "hit_rate", "percent"),
        ("Context Coverage", "avg_context_coverage", "percent"),
        ("Context Noise", "avg_context_noise", "percent"),
        ("Answer Gold Overlap", "avg_answer_gold_overlap", "percent"),
        ("LLM Quality 0-5", "llm_quality_avg_0_5", "number"),
        ("Avg Context Chars", "avg_context_chars", "number"),
        ("Avg Total Seconds", "avg_total_seconds", "number"),
    ]
    for label, key, fmt in rows:
        flat_value = summary["flat"].get(key)
        parent_value = summary["parent_child"].get(key)
        change = relative_change(parent_value, flat_value)
        lines.append(f"| {label} | {format_value(flat_value, fmt)} | {format_value(parent_value, fmt)} | {format_percent(change)} |")

    lines.extend([
        "",
        "## Knowledge Reuse",
        "",
        f"- Quality relative improvement: {format_percent(summary['quality_relative_improvement'])}",
        f"- Structure preservation relative improvement: {format_percent(summary['structure_preservation_relative_improvement'])}",
        f"- Context chars relative change: {format_percent(summary['context_chars_relative_change'])}",
        f"- Latency relative change: {format_percent(summary['latency_relative_change'])}",
        f"- Quality per 1k context chars change: {format_percent(summary['knowledge_reuse_efficiency_quality_per_1k_context_chars']['relative_change'])}",
        "",
        "## Cases",
        "",
    ])

    for item in payload["cases"]:
        case = item["case"]
        lines.extend([
            f"### {case['case_id']} {case['title']}",
            "",
            f"- Question: {case['question']}",
            f"- Gold source: {case['source']}",
            f"- Flat hit: {item['flat']['hit_gold']}; Parent-Child hit: {item['parent_child']['hit_gold']}",
            f"- Judge: `{json.dumps(item.get('judge_scores', {}), ensure_ascii=False)}`",
            "",
        ])
    return "\n".join(lines)


def load_sections(repo_path):
    sections = []
    for relative_path in SELECTED_FILES:
        file_path = repo_path / relative_path
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        text = clean_markdown(text)
        sections.extend(split_markdown_sections(relative_path, text))
    return [section for section in sections if 500 <= len(section.text) <= 4500]


def split_markdown_sections(source, text):
    lines = text.splitlines()
    sections = []
    current_title = ""
    current_lines = []
    for line in lines:
        heading_match = re.match(r"^(#{2,4})\s+(.+)$", line.strip())
        if heading_match:
            flush_section(sections, source, current_title, current_lines)
            current_title = normalize_title(heading_match.group(2))
            current_lines = [current_title]
        else:
            current_lines.append(line)
    flush_section(sections, source, current_title, current_lines)
    return sections


def flush_section(sections, source, title, lines):
    title = title or Path(source).stem
    if should_skip_title(title):
        return
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) < 500:
        return
    section_id = stable_id(source, title, text[:100])
    sections.append(Section(
        section_id=section_id,
        source=source,
        title=title,
        text=text,
    ))


def build_test_cases(sections, case_count):
    candidates = [
        section for section in sections
        if not should_skip_title(section.title)
        and any(keyword in section.source for keyword in ["network", "os", "mysql", "redis"])
    ]
    random.shuffle(candidates)
    selected = sorted(candidates[:case_count], key=lambda section: section.source)
    cases = []
    templates = [
        "我想按资料原文的知识结构复习「{title}」，请说明核心机制、分类和关键原因。",
        "资料中是如何解释「{title}」的？请尽量保留原文的术语、层次和因果链。",
        "面试复习时如果被问到「{title}」，应该按照资料里的讲法怎么回答？",
    ]
    for index, section in enumerate(selected, start=1):
        question = templates[index % len(templates)].format(title=section.title)
        cases.append(TestCase(
            case_id=f"case_{index:02d}",
            question=question,
            section_id=section.section_id,
            source=section.source,
            title=section.title,
            gold_text=section.text,
        ))
    return cases


def clean_markdown(text):
    text = re.sub(r"!\[[^\]]*]\([^)]*\)", "", text)
    text = re.sub(r"\[[^\]]*]\((?:http|https)://[^)]*\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = text.replace("\r\n", "\n")
    return text


def should_skip_title(title):
    skip_words = ["readme", "目录", "前言", "总结", "最后", "参考", "公众号", "勘误", "题外话"]
    normalized = title.lower().strip()
    return any(word in normalized for word in skip_words)


def normalize_title(title):
    title = re.sub(r"\{#.*?}$", "", title).strip()
    title = title.strip("#").strip()
    return title


def rrf_rerank(vector_docs, bm25_docs, doc_id_key, top_k):
    ranks = {}
    docs_by_key = {}
    for source_docs in [vector_docs, bm25_docs]:
        for index, doc in enumerate(source_docs, start=1):
            key = doc.metadata.get(doc_id_key) or stable_id(doc.page_content)
            docs_by_key.setdefault(key, doc)
            ranks.setdefault(key, 0.0)
            ranks[key] += 1 / (60 + index)
    ranked_keys = sorted(ranks, key=lambda key: ranks[key], reverse=True)
    return [docs_by_key[key] for key in ranked_keys[:top_k]]


def tokenize(text):
    try:
        import jieba
        tokens = [
            token.strip().lower()
            for token in jieba.lcut(text or "")
            if token.strip()
        ]
    except ImportError:
        tokens = re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", (text or "").lower())
    stop = {"的", "了", "和", "是", "在", "有", "与", "及", "或", "中", "会", "就", "也", "都", "一个", "这个"}
    return [token for token in tokens if token not in stop and len(token) > 1]


def parse_json_object(text):
    text = (text or "").strip()
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", text, flags=re.S)
    if match:
        text = match.group(0)
    return json.loads(text)


def stable_id(*parts):
    raw = "||".join(str(part) for part in parts)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def trim_text(text, max_chars):
    text = text or ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[已截断]"


def safe_div(a, b):
    if not b:
        return 0.0
    return a / b


def mean(values):
    values = [value for value in values if value is not None]
    if not values:
        return 0.0
    return statistics.mean(values)


def relative_change(new_value, old_value):
    if new_value is None or old_value in (None, 0):
        return None
    return (new_value - old_value) / old_value


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


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
