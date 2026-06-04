"""
Query Rewrite 多轮指代问题自动评测脚本。

对比：
1. Original Query：直接用当前用户问题检索。
2. Rewritten Query：Qwen 结合最近历史将当前问题改写后再检索。

本测试不涉及上下文压缩，只测试最近对话历史对查询改写和检索的帮助。
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

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import config_data as config
from benchmarks.parent_child_benchmark import (
    ParentChildRagSystem,
    load_sections,
    mean,
    parse_json_object,
    relative_change,
    safe_div,
    tokenize,
    to_float,
    trim_text,
)
from query_rewriter import QueryRewriteService


DEFAULT_REPO_PATH = "/tmp/codex_xiaolin_csbase"
DEFAULT_RESULT_DIR = "benchmark_results"


@dataclass
class RewriteCase:
    case_id: str
    category: str
    source: str
    title: str
    section_id: str
    gold_text: str
    history: list[tuple[str, str]]
    current_question: str
    expected_terms: list[str]


CASE_SPECS = [
    ("pronoun", "network/3_tcp/tcp_interview.md", "为什么是三次握手？不是两次、四次？", "为什么它不是两次就够了？", ["TCP", "三次握手", "两次"]),
    ("pronoun", "network/3_tcp/tcp_interview.md", "为什么 TIME_WAIT 等待的时间是 2MSL？", "为什么它要等这么久？", ["TIME_WAIT", "2MSL"]),
    ("ellipsis", "network/3_tcp/tcp_interview.md", "什么是 SYN 攻击？如何避免 SYN 攻击？", "那怎么避免这个问题？", ["SYN", "攻击"]),
    ("ellipsis", "network/3_tcp/tcp_interview.md", "TCP 四次挥手过程是怎样的？", "FIN 和 ACK 是怎么交互的？", ["TCP", "四次挥手", "FIN", "ACK"]),
    ("pronoun", "network/2_http/http_interview.md", "HTTP/2 做了什么优化？", "它的头部压缩和 Stream 是怎么优化的？", ["HTTP/2", "头部压缩", "Stream"]),
    ("pronoun", "network/2_http/http_interview.md", "HTTP/3 做了哪些优化？", "它和 QUIC 解决了哪些问题？", ["HTTP/3", "QUIC"]),
    ("ellipsis", "network/4_ip/ip_base.md", "ARP", "它是怎么根据 IP 地址找到 MAC 地址的？", ["ARP", "IP", "MAC"]),
    ("ellipsis", "network/4_ip/ip_base.md", "无分类地址 CIDR", "这个斜杠后面的数字是什么意思？", ["CIDR", "斜杠"]),
    ("pronoun", "mysql/transaction/mvcc.md", "Read View 在 MVCC 里如何工作的？", "它怎么判断版本是否可见？", ["Read View", "MVCC", "可见"]),
    ("ellipsis", "mysql/transaction/mvcc.md", "可重复读是如何工作的？", "这个隔离级别是怎么做到重复读的？", ["可重复读", "隔离级别"]),
    ("pronoun", "redis/base/redis_interview.md", "Redis 使用的过期删除策略是什么？", "它具体用了哪几种删除策略？", ["Redis", "过期删除"]),
    ("ellipsis", "redis/base/redis_interview.md", "RDB 快照是如何实现的呢？", "fork 之后数据被修改怎么办？", ["RDB", "fork"]),
    ("pronoun", "redis/storage/aof.md", "AOF 后台重写", "那新写入的命令怎么处理？", ["AOF", "后台重写", "新写入"]),
    ("comparison", "redis/base/redis_interview.md", "LRU 算法和 LFU 算法有什么区别？", "它俩主要差别是什么？", ["LRU", "LFU"]),
    ("ellipsis", "redis/base/redis_interview.md", "如何避免缓存雪崩、缓存击穿、缓存穿透？", "这三种问题分别怎么避免？", ["缓存雪崩", "缓存击穿", "缓存穿透"]),
    ("pronoun", "os/4_process/process_base.md", "线程与进程的比较", "它们最大的区别是什么？", ["线程", "进程"]),
    ("ellipsis", "os/4_process/process_base.md", "进程的上下文切换", "为什么这个操作会有成本？", ["进程", "上下文切换"]),
    ("pronoun", "os/3_memory/vmem.md", "虚拟内存", "它解决了什么问题？", ["虚拟内存"]),
    ("comparison", "os/8_network_system/selete_poll_epoll.md", "select/poll", "它们的问题在哪里？", ["select", "poll"]),
    ("comparison", "os/8_network_system/selete_poll_epoll.md", "epoll", "它比前两个改进了什么？", ["epoll", "select", "poll"]),
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
    work_dir = Path("/tmp") / f"codex_query_rewrite_benchmark_{run_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/6] 读取资料：{repo_path}", flush=True)
    sections = load_sections(repo_path)
    cases = build_cases(sections, args.case_count)
    print(f"sections={len(sections)}, test_cases={len(cases)}", flush=True)

    print("[2/6] 构建 Parent-Child + Hybrid 检索索引", flush=True)
    embedding = DashScopeEmbeddings(model=config.embedding_model_name)
    retrieval_system = ParentChildRagSystem(
        sections=sections,
        embedding=embedding,
        persist_dir=str(work_dir / "query_rewrite_chroma"),
    )
    rewriter = QueryRewriteService()
    chat_model = ChatTongyi(model=config.chat_model_name)
    judge_model = ChatTongyi(model=config.chat_model_name)

    print("[3/6] 执行原始查询与改写查询全链路对照测试", flush=True)
    case_results = []
    for index, case in enumerate(cases, start=1):
        print(f"case {index}/{len(cases)} [{case.category}]: {case.title}", flush=True)
        history_messages = build_history_messages(case)
        rewrite_start = time.perf_counter()
        rewritten_query = rewriter.rewrite(case.current_question, history_messages)
        rewrite_seconds = time.perf_counter() - rewrite_start

        original_result = retrieve_case(retrieval_system, case.current_question, case)
        rewritten_result = retrieve_case(retrieval_system, rewritten_query, case)
        answer_case(chat_model, case.current_question, history_messages, original_result)
        answer_case(chat_model, rewritten_query, history_messages, rewritten_result)
        lexical_scores = evaluate_lexical(case, case.current_question, rewritten_query, original_result, rewritten_result)
        judge_scores = {}
        if not args.skip_llm_judge:
            judge_scores = judge_answers(judge_model, case, original_result, rewritten_result)

        case_results.append({
            "case": case_to_dict(case),
            "history_text": format_history(case.history),
            "original_query": case.current_question,
            "rewritten_query": rewritten_query,
            "rewrite_seconds": rewrite_seconds,
            "rewrite_changed": normalize_text(rewritten_query) != normalize_text(case.current_question),
            "original": original_result,
            "rewritten": rewritten_result,
            "lexical_scores": lexical_scores,
            "judge_scores": judge_scores,
        })

    print("[4/6] 汇总指标", flush=True)
    summary = summarize_results(case_results)
    payload = {
        "run_id": run_id,
        "source_repo": "https://github.com/xiaolincoder/CS-Base",
        "config": {
            "case_count": len(cases),
            "sections": len(sections),
            "chat_model": config.chat_model_name,
            "embedding_model": config.embedding_model_name,
            "rewrite_model": config.query_rewrite_model_name,
            "query_rewrite_history_turns": config.query_rewrite_history_turns,
            "query_rewrite_max_chars": config.query_rewrite_max_chars,
            "skip_llm_judge": args.skip_llm_judge,
            "retrieval": "parent-child + hybrid RRF",
        },
        "summary": summary,
        "cases": case_results,
    }

    print("[5/6] 写入测试报告", flush=True)
    json_path = result_dir / f"query_rewrite_benchmark_{run_id}.json"
    md_path = result_dir / f"query_rewrite_benchmark_{run_id}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(payload), encoding="utf-8")

    print("[6/6] 清理临时索引", flush=True)
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"json_result={json_path}", flush=True)
    print(f"markdown_result={md_path}", flush=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


def build_cases(sections, case_count):
    by_key = {(section.source, section.title): section for section in sections}
    cases = []
    for index, (category, source, title, current_question, terms) in enumerate(CASE_SPECS[:case_count], start=1):
        section = by_key.get((source, title))
        if not section:
            raise ValueError(f"找不到测试章节：{source} / {title}")
        history = [
            ("user", f"我正在复习「{title}」这个知识点，请先记住这个主题。"),
            ("assistant", f"好的，我们当前讨论的主题是「{title}」。后续问题我会围绕这个主题理解。"),
        ]
        cases.append(RewriteCase(
            case_id=f"case_{index:02d}",
            category=category,
            source=source,
            title=title,
            section_id=section.section_id,
            gold_text=section.text,
            history=history,
            current_question=current_question,
            expected_terms=terms,
        ))
    return cases


def build_history_messages(case):
    messages = []
    for role, content in case.history:
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    return messages


def retrieve_case(system, query, case):
    docs, context, retrieval_seconds = system.retrieve(query)
    section_ids = [doc.metadata.get("section_id") for doc in docs]
    hit_rank = first_hit_rank(section_ids, case.section_id)
    return {
        "query": query,
        "retrieved_section_ids": section_ids,
        "retrieved_titles": [doc.metadata.get("title") for doc in docs],
        "hit_gold": hit_rank is not None,
        "hit_rank": hit_rank,
        "mrr": 0.0 if hit_rank is None else 1 / hit_rank,
        "context": context,
        "context_chars": len(context),
        "retrieval_seconds": retrieval_seconds,
    }


def answer_case(chat_model, user_question, history_messages, result):
    prompt_messages = [
        SystemMessage(content=(
            "你是知识复用助手。以用户提供的已知参考资料为主，简洁和专业地回答用户问题。"
            "回答时尽量沿用资料原有的知识结构、术语、分类和因果链。"
            "历史只用于理解用户意图和指代，事实依据仍以参考资料为主。"
            f"\n\n参考资料：\n{result['context']}"
        )),
        *history_messages,
        HumanMessage(content=f"请回答用户提问：{user_question}"),
    ]
    answer_start = time.perf_counter()
    try:
        answer = chat_model.invoke(prompt_messages).content
        error = ""
    except Exception as exc:
        answer = ""
        error = str(exc)
    answer_seconds = time.perf_counter() - answer_start

    result["answer"] = answer
    result["answer_chars"] = len(answer)
    result["answer_seconds"] = answer_seconds
    result["total_seconds"] = result["retrieval_seconds"] + answer_seconds
    result["error"] = error
    return result


def evaluate_lexical(case, original_query, rewritten_query, original_result, rewritten_result):
    gold_tokens = set(tokenize(case.gold_text))

    def context_score(result):
        context_tokens = set(tokenize(result["context"]))
        answer_tokens = set(tokenize(result.get("answer", "")))
        return {
            "context_coverage": safe_div(len(gold_tokens & context_tokens), len(gold_tokens)),
            "context_noise": 1 - safe_div(len(context_tokens & gold_tokens), len(context_tokens)),
            "answer_gold_overlap": safe_div(len(gold_tokens & answer_tokens), len(gold_tokens)),
        }

    return {
        "original_query_term_recall": exact_terms_recall(case.expected_terms, original_query),
        "rewritten_query_term_recall": exact_terms_recall(case.expected_terms, rewritten_query),
        "original": context_score(original_result),
        "rewritten": context_score(rewritten_result),
    }


def judge_answers(judge_model, case, original_result, rewritten_result):
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

历史主题：
{case.title}

用户当前问题：
{case.current_question}

标准资料：
{trim_text(case.gold_text, 5000)}

回答 A（Original Query，未改写）：
{trim_text(original_result.get("answer", ""), 2600)}

回答 B（Rewritten Query，Qwen 改写后）：
{trim_text(rewritten_result.get("answer", ""), 2600)}

JSON 格式：
{{
  "original": {{
    "correctness": 0,
    "groundedness": 0,
    "keypoint_coverage": 0,
    "term_preservation": 0,
    "structure_preservation": 0
  }},
  "rewritten": {{
    "correctness": 0,
    "groundedness": 0,
    "keypoint_coverage": 0,
    "term_preservation": 0,
    "structure_preservation": 0
  }},
  "winner": "original 或 rewritten 或 tie"
}}
""".strip()

    try:
        text = judge_model.invoke([HumanMessage(content=prompt)]).content
        return parse_json_object(text)
    except Exception as exc:
        return {"error": str(exc)}


def summarize_results(case_results):
    original = collect_result_metrics(case_results, "original")
    rewritten = collect_result_metrics(case_results, "rewritten")
    judge_dims = ["correctness", "groundedness", "keypoint_coverage", "term_preservation", "structure_preservation"]
    original_quality = collect_quality(case_results, "original", judge_dims)
    rewritten_quality = collect_quality(case_results, "rewritten", judge_dims)
    original["llm_quality_avg_0_5"] = original_quality
    rewritten["llm_quality_avg_0_5"] = rewritten_quality
    original_term_recall = mean([item["lexical_scores"]["original_query_term_recall"] for item in case_results])
    rewritten_term_recall = mean([item["lexical_scores"]["rewritten_query_term_recall"] for item in case_results])

    fixed_misses = sum(
        1 for item in case_results
        if not item["original"]["hit_gold"] and item["rewritten"]["hit_gold"]
    )
    regressions = sum(
        1 for item in case_results
        if item["original"]["hit_gold"] and not item["rewritten"]["hit_gold"]
    )
    winners = {"original": 0, "rewritten": 0, "tie": 0, "unknown": 0}
    for item in case_results:
        winner = (item.get("judge_scores") or {}).get("winner", "unknown")
        winners[winner if winner in winners else "unknown"] += 1

    return {
        "case_count": len(case_results),
        "original": original,
        "rewritten": rewritten,
        "original_query_term_recall": original_term_recall,
        "rewritten_query_term_recall": rewritten_term_recall,
        "query_term_recall_relative_change": relative_change(rewritten_term_recall, original_term_recall),
        "hit_rate_relative_change": relative_change(rewritten["hit_rate"], original["hit_rate"]),
        "mrr_relative_change": relative_change(rewritten["mrr"], original["mrr"]),
        "context_coverage_relative_change": relative_change(rewritten["avg_context_coverage"], original["avg_context_coverage"]),
        "context_noise_relative_change": relative_change(rewritten["avg_context_noise"], original["avg_context_noise"]),
        "answer_gold_overlap_relative_change": relative_change(rewritten["avg_answer_gold_overlap"], original["avg_answer_gold_overlap"]),
        "quality_relative_change": relative_change(rewritten_quality, original_quality),
        "retrieval_latency_relative_change": relative_change(rewritten["avg_retrieval_seconds"], original["avg_retrieval_seconds"]),
        "total_latency_relative_change": relative_change(rewritten["avg_total_seconds"], original["avg_total_seconds"]),
        "end_to_end_latency_relative_change": relative_change(rewritten["avg_end_to_end_seconds"], original["avg_end_to_end_seconds"]),
        "context_chars_relative_change": relative_change(rewritten["avg_context_chars"], original["avg_context_chars"]),
        "rewrite_changed_rate": mean([1 if item["rewrite_changed"] else 0 for item in case_results]),
        "avg_rewrite_seconds": mean([item["rewrite_seconds"] for item in case_results]),
        "fixed_misses": fixed_misses,
        "regressions": regressions,
        "winners": winners,
        "category_summary": summarize_by_category(case_results),
    }


def collect_result_metrics(case_results, key):
    def end_to_end_seconds(item):
        base_seconds = item[key].get("total_seconds", item[key]["retrieval_seconds"])
        if key == "rewritten":
            return base_seconds + item["rewrite_seconds"]
        return base_seconds

    return {
        "hit_rate": mean([1 if item[key]["hit_gold"] else 0 for item in case_results]),
        "mrr": mean([item[key]["mrr"] for item in case_results]),
        "avg_context_coverage": mean([item["lexical_scores"][key]["context_coverage"] for item in case_results]),
        "avg_context_noise": mean([item["lexical_scores"][key]["context_noise"] for item in case_results]),
        "avg_answer_gold_overlap": mean([item["lexical_scores"][key]["answer_gold_overlap"] for item in case_results]),
        "avg_context_chars": mean([item[key]["context_chars"] for item in case_results]),
        "avg_answer_chars": mean([item[key].get("answer_chars", 0) for item in case_results]),
        "avg_retrieval_seconds": mean([item[key]["retrieval_seconds"] for item in case_results]),
        "avg_answer_seconds": mean([item[key].get("answer_seconds", 0) for item in case_results]),
        "avg_total_seconds": mean([item[key].get("total_seconds", item[key]["retrieval_seconds"]) for item in case_results]),
        "avg_end_to_end_seconds": mean([end_to_end_seconds(item) for item in case_results]),
        "error_count": sum(1 for item in case_results if item[key].get("error")),
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


def summarize_by_category(case_results):
    summary = {}
    for category in sorted({item["case"]["category"] for item in case_results}):
        items = [item for item in case_results if item["case"]["category"] == category]
        summary[category] = {
            "case_count": len(items),
            "original_hit_rate": mean([1 if item["original"]["hit_gold"] else 0 for item in items]),
            "rewritten_hit_rate": mean([1 if item["rewritten"]["hit_gold"] else 0 for item in items]),
            "original_term_recall": mean([item["lexical_scores"]["original_query_term_recall"] for item in items]),
            "rewritten_term_recall": mean([item["lexical_scores"]["rewritten_query_term_recall"] for item in items]),
            "original_llm_quality": collect_quality(items, "original", ["correctness", "groundedness", "keypoint_coverage", "term_preservation", "structure_preservation"]),
            "rewritten_llm_quality": collect_quality(items, "rewritten", ["correctness", "groundedness", "keypoint_coverage", "term_preservation", "structure_preservation"]),
        }
    return summary


def render_markdown_report(payload):
    summary = payload["summary"]
    lines = [
        "# Query Rewrite Benchmark",
        "",
        f"- Source: {payload['source_repo']}",
        f"- Cases: {summary['case_count']}",
        f"- Chat model: {payload['config']['chat_model']}",
        f"- Rewrite model: {payload['config']['rewrite_model']}",
        f"- Embedding model: {payload['config']['embedding_model']}",
        f"- Retrieval: {payload['config']['retrieval']}",
        "",
        "## Summary",
        "",
        "| Metric | Original Query | Rewritten Query | Change |",
        "| --- | ---: | ---: | ---: |",
        f"| Query Term Recall | {summary['original_query_term_recall'] * 100:.2f}% | {summary['rewritten_query_term_recall'] * 100:.2f}% | {format_percent(summary['query_term_recall_relative_change'])} |",
        f"| Hit Rate | {summary['original']['hit_rate'] * 100:.2f}% | {summary['rewritten']['hit_rate'] * 100:.2f}% | {format_percent(summary['hit_rate_relative_change'])} |",
        f"| MRR | {summary['original']['mrr']:.3f} | {summary['rewritten']['mrr']:.3f} | {format_percent(summary['mrr_relative_change'])} |",
        f"| Context Coverage | {summary['original']['avg_context_coverage'] * 100:.2f}% | {summary['rewritten']['avg_context_coverage'] * 100:.2f}% | {format_percent(summary['context_coverage_relative_change'])} |",
        f"| Context Noise | {summary['original']['avg_context_noise'] * 100:.2f}% | {summary['rewritten']['avg_context_noise'] * 100:.2f}% | {format_percent(summary['context_noise_relative_change'])} |",
        f"| Answer Gold Overlap | {summary['original']['avg_answer_gold_overlap'] * 100:.2f}% | {summary['rewritten']['avg_answer_gold_overlap'] * 100:.2f}% | {format_percent(summary['answer_gold_overlap_relative_change'])} |",
        f"| LLM Quality 0-5 | {summary['original']['llm_quality_avg_0_5']:.3f} | {summary['rewritten']['llm_quality_avg_0_5']:.3f} | {format_percent(summary['quality_relative_change'])} |",
        f"| Avg Context Chars | {summary['original']['avg_context_chars']:.3f} | {summary['rewritten']['avg_context_chars']:.3f} | {format_percent(summary['context_chars_relative_change'])} |",
        f"| Avg Retrieval Seconds | {summary['original']['avg_retrieval_seconds']:.3f} | {summary['rewritten']['avg_retrieval_seconds']:.3f} | {format_percent(summary['retrieval_latency_relative_change'])} |",
        f"| Avg Retrieval+Answer Seconds | {summary['original']['avg_total_seconds']:.3f} | {summary['rewritten']['avg_total_seconds']:.3f} | {format_percent(summary['total_latency_relative_change'])} |",
        f"| Avg End-to-End Seconds | {summary['original']['avg_end_to_end_seconds']:.3f} | {summary['rewritten']['avg_end_to_end_seconds']:.3f} | {format_percent(summary['end_to_end_latency_relative_change'])} |",
        "",
        "## Rewrite Stats",
        "",
        f"- Rewrite changed rate: {summary['rewrite_changed_rate'] * 100:.2f}%",
        f"- Avg rewrite seconds: {summary['avg_rewrite_seconds']:.3f}",
        f"- Fixed misses: {summary['fixed_misses']}",
        f"- Regressions: {summary['regressions']}",
        "",
        "## Winners",
        "",
        f"- Original Query: {summary['winners']['original']}",
        f"- Rewritten Query: {summary['winners']['rewritten']}",
        f"- Tie: {summary['winners']['tie']}",
        f"- Unknown: {summary['winners']['unknown']}",
        "",
        "## Category Summary",
        "",
        "| Category | Cases | Original Hit | Rewritten Hit | Original Term Recall | Rewritten Term Recall | Original Quality | Rewritten Quality |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for category, row in summary["category_summary"].items():
        lines.append(
            f"| {category} | {row['case_count']} | {row['original_hit_rate'] * 100:.2f}% | {row['rewritten_hit_rate'] * 100:.2f}% | "
            f"{row['original_term_recall'] * 100:.2f}% | {row['rewritten_term_recall'] * 100:.2f}% | "
            f"{row['original_llm_quality']:.3f} | {row['rewritten_llm_quality']:.3f} |"
        )

    lines.extend(["", "## Cases", ""])
    for item in payload["cases"]:
        case = item["case"]
        lines.extend([
            f"### {case['case_id']} {case['title']}",
            "",
            f"- Category: {case['category']}",
            f"- History: {item['history_text']}",
            f"- Original query: {item['original_query']}",
            f"- Rewritten query: {item['rewritten_query']}",
            f"- Original hit/rank: {item['original']['hit_gold']} / {item['original']['hit_rank']}",
            f"- Rewritten hit/rank: {item['rewritten']['hit_gold']} / {item['rewritten']['hit_rank']}",
            f"- Original retrieved: {item['original']['retrieved_titles']}",
            f"- Rewritten retrieved: {item['rewritten']['retrieved_titles']}",
            f"- Judge: `{json.dumps(item.get('judge_scores', {}), ensure_ascii=False)}`",
            "",
        ])
    return "\n".join(lines)


def case_to_dict(case):
    return {
        "case_id": case.case_id,
        "category": case.category,
        "source": case.source,
        "title": case.title,
        "section_id": case.section_id,
        "current_question": case.current_question,
        "expected_terms": case.expected_terms,
    }


def format_history(history):
    return " / ".join(f"{role}: {content}" for role, content in history)


def first_hit_rank(section_ids, gold_section_id):
    for index, section_id in enumerate(section_ids, start=1):
        if section_id == gold_section_id:
            return index
    return None


def exact_terms_recall(terms, text):
    if not terms:
        return 0.0
    lower_text = (text or "").lower()
    return sum(1 for term in terms if term.lower() in lower_text) / len(terms)


def normalize_text(text):
    return "".join((text or "").split()).lower()


def format_percent(value):
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


if __name__ == "__main__":
    main()
