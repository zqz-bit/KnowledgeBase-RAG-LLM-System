"""
强标识符文档下的 Hybrid Retrieval 自动评测。

语料：
- Redis 命令 JSON 文档：命令名、复杂度、flags、arguments、reply schema。
- Kubernetes API SwaggerDoc 字段说明：类型名、字段名、字段说明。

对比：
- Vector Only：只用向量检索 Top3。
- Hybrid RRF：向量 Top6 + BM25 Top6，经 RRF 融合取 Top3。
"""
import argparse
import ast
import json
import os
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

import config_data as config
from benchmarks.parent_child_benchmark import (
    BM25Index,
    add_documents_in_batches,
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


DEFAULT_REDIS_COMMANDS = "/tmp/codex_redis_src/src/commands"
DEFAULT_K8S_API = "/tmp/codex_k8s_api"
DEFAULT_RESULT_DIR = "benchmark_results"


@dataclass
class IdentifierSection:
    section_id: str
    source: str
    title: str
    identifier: str
    text: str
    kind: str


@dataclass
class IdentifierCase:
    case_id: str
    question: str
    section_id: str
    source: str
    title: str
    identifier: str
    gold_text: str
    category: str
    exact_terms: list[str]


CASE_SPECS = [
    ("redis_command", "Redis HEXPIRE", "Redis 命令 HEXPIRE 是做什么的？复杂度和返回值语义是什么？", ["HEXPIRE"]),
    ("redis_command", "Redis HPEXPIRETIME", "Redis 命令 HPEXPIRETIME 返回什么？和 hash field expiration 有什么关系？", ["HPEXPIRETIME"]),
    ("redis_command", "Redis HPERSIST", "Redis 命令 HPERSIST 的作用是什么？它对 hash field 的过期时间做什么？", ["HPERSIST"]),
    ("redis_command", "Redis HGETDEL", "Redis 命令 HGETDEL 的语义是什么？会删除什么内容？", ["HGETDEL"]),
    ("redis_command", "Redis XAUTOCLAIM", "Redis 命令 XAUTOCLAIM 是什么？它会如何处理 pending entries？", ["XAUTOCLAIM"]),
    ("redis_command", "Redis BZMPOP", "Redis 命令 BZMPOP 的阻塞行为和返回值是什么？", ["BZMPOP"]),
    ("redis_command", "Redis ZINTERCARD", "Redis 命令 ZINTERCARD 计算什么？LIMIT 参数有什么作用？", ["ZINTERCARD", "LIMIT"]),
    ("redis_command", "Redis GEOSEARCHSTORE", "Redis 命令 GEOSEARCHSTORE 的作用是什么？它和地理空间索引有什么关系？", ["GEOSEARCHSTORE"]),
    ("redis_command", "Redis FUNCTION LIST", "Redis 命令 FUNCTION LIST 返回哪些 library/function 信息？", ["FUNCTION", "LIST"]),
    ("redis_command", "Redis ACL WHOAMI", "Redis 命令 ACL WHOAMI 返回什么？", ["ACL", "WHOAMI"]),
    ("k8s_field", "Kubernetes PodSpec.terminationGracePeriodSeconds", "Kubernetes 字段 PodSpec.terminationGracePeriodSeconds 表示什么？", ["PodSpec", "terminationGracePeriodSeconds"]),
    ("k8s_field", "Kubernetes PodSpec.hostUsers", "Kubernetes 字段 PodSpec.hostUsers 的用途是什么？", ["PodSpec", "hostUsers"]),
    ("k8s_field", "Kubernetes PodSpec.runtimeClassName", "Kubernetes 字段 PodSpec.runtimeClassName 用来选择什么？", ["PodSpec", "runtimeClassName"]),
    ("k8s_field", "Kubernetes PodSecurityContext.fsGroupChangePolicy", "Kubernetes 字段 PodSecurityContext.fsGroupChangePolicy 如何影响 volume ownership？", ["PodSecurityContext", "fsGroupChangePolicy"]),
    ("k8s_field", "Kubernetes PodAffinityTerm.matchLabelKeys", "Kubernetes 字段 PodAffinityTerm.matchLabelKeys 是什么？", ["PodAffinityTerm", "matchLabelKeys"]),
    ("k8s_field", "Kubernetes ServiceSpec.internalTrafficPolicy", "Kubernetes 字段 ServiceSpec.internalTrafficPolicy 控制什么？", ["ServiceSpec", "internalTrafficPolicy"]),
    ("k8s_field", "Kubernetes ServiceSpec.ipFamilyPolicy", "Kubernetes 字段 ServiceSpec.ipFamilyPolicy 有什么作用？", ["ServiceSpec", "ipFamilyPolicy"]),
    ("k8s_field", "Kubernetes ServiceSpec.loadBalancerClass", "Kubernetes 字段 ServiceSpec.loadBalancerClass 表示什么？", ["ServiceSpec", "loadBalancerClass"]),
    ("k8s_field", "Kubernetes JobSpec.podReplacementPolicy", "Kubernetes 字段 JobSpec.podReplacementPolicy 什么时候创建 replacement Pod？", ["JobSpec", "podReplacementPolicy"]),
    ("k8s_field", "Kubernetes RollingUpdateDeployment.maxUnavailable", "Kubernetes 字段 RollingUpdateDeployment.maxUnavailable 如何约束 rolling update？", ["RollingUpdateDeployment", "maxUnavailable"]),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis-commands", default=DEFAULT_REDIS_COMMANDS)
    parser.add_argument("--k8s-api", default=DEFAULT_K8S_API)
    parser.add_argument("--result-dir", default=DEFAULT_RESULT_DIR)
    parser.add_argument("--case-count", type=int, default=20)
    parser.add_argument("--skip-llm-judge", action="store_true")
    args = parser.parse_args()

    if not os.getenv("DASHSCOPE_API_KEY"):
        raise RuntimeError("缺少 DASHSCOPE_API_KEY，请先配置 DASHSCOPE_API_KEY。")

    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("%Y%m%d_%H%M%S")
    work_dir = Path("/tmp") / f"codex_identifier_hybrid_benchmark_{run_id}"
    work_dir.mkdir(parents=True, exist_ok=True)

    print("[1/6] 构建强标识符语料", flush=True)
    sections = load_identifier_sections(Path(args.redis_commands), Path(args.k8s_api))
    cases = build_cases(sections, args.case_count)
    print(f"sections={len(sections)}, test_cases={len(cases)}", flush=True)

    print("[2/6] 构建同一套向量索引与 BM25 索引", flush=True)
    embedding = DashScopeEmbeddings(model=config.embedding_model_name)
    system = IdentifierRetrievalSystem(sections, embedding, str(work_dir / "identifier_chroma"))

    chat_model = ChatTongyi(model=config.chat_model_name)
    judge_model = ChatTongyi(model=config.chat_model_name)

    print("[3/6] 执行 Vector Only 与 Hybrid RRF 对照测试", flush=True)
    case_results = []
    for index, case in enumerate(cases, start=1):
        print(f"case {index}/{len(cases)} [{case.category}]: {case.identifier}", flush=True)
        vector_result = run_case(system, "vector_only", chat_model, case)
        hybrid_result = run_case(system, "hybrid_rrf", chat_model, case)
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
        "source_repos": {
            "redis": "https://github.com/redis/redis/tree/unstable/src/commands",
            "kubernetes_api": "https://github.com/kubernetes/api",
        },
        "config": {
            "case_count": len(cases),
            "sections": len(sections),
            "vector_k": 6,
            "bm25_k": 6,
            "rerank_top_k": 3,
            "rrf_k": 60,
            "embedding_model": config.embedding_model_name,
            "chat_model": config.chat_model_name,
        },
        "summary": summary,
        "cases": case_results,
    }

    print("[5/6] 写入测试报告", flush=True)
    json_path = result_dir / f"identifier_hybrid_benchmark_{run_id}.json"
    md_path = result_dir / f"identifier_hybrid_benchmark_{run_id}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(payload), encoding="utf-8")

    print("[6/6] 清理临时索引", flush=True)
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"json_result={json_path}", flush=True)
    print(f"markdown_result={md_path}", flush=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


class IdentifierRetrievalSystem:
    def __init__(self, sections, embedding, persist_dir):
        self.docs = [
            Document(
                page_content=section.text,
                metadata={
                    "section_id": section.section_id,
                    "source": section.source,
                    "title": section.title,
                    "identifier": section.identifier,
                    "kind": section.kind,
                },
            )
            for section in sections
        ]
        self.vector_store = Chroma(
            collection_name="identifier_hybrid_benchmark",
            embedding_function=embedding,
            persist_directory=persist_dir,
        )
        ids = [doc.metadata["section_id"] for doc in self.docs]
        add_documents_in_batches(self.vector_store, self.docs, ids)
        self.bm25 = BM25Index(self.docs, doc_id_key="section_id")

    def retrieve(self, query, mode):
        start = time.perf_counter()
        vector_docs = self.vector_store.similarity_search(query, k=6)
        if mode == "vector_only":
            docs = vector_docs[:3]
        elif mode == "hybrid_rrf":
            bm25_docs = self.bm25.search(query, k=6)
            docs = rrf_rerank(vector_docs, bm25_docs, doc_id_key="section_id", top_k=3)
        else:
            raise ValueError(f"未知检索模式：{mode}")
        elapsed = time.perf_counter() - start
        context = "\n\n".join(
            f"资料：{doc.page_content}\n来源：{doc.metadata.get('source')}"
            for doc in docs
        )
        return docs, context, elapsed


def load_identifier_sections(redis_commands_dir, k8s_api_dir):
    sections = []
    sections.extend(load_redis_command_sections(redis_commands_dir))
    sections.extend(load_k8s_field_sections(k8s_api_dir))
    return sections


def load_redis_command_sections(commands_dir):
    sections = []
    for json_path in sorted(commands_dir.glob("*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        for command_name, record in data.items():
            if not isinstance(record, dict):
                continue
            container = record.get("container")
            full_name = f"{container} {command_name}" if container else command_name
            identifier = f"Redis {full_name}"
            arguments = record.get("arguments", [])
            reply_schema = record.get("reply_schema", {})
            text = "\n".join([
                f"Identifier: {identifier}",
                f"Command: {full_name}",
                f"Summary: {record.get('summary', '')}",
                f"Complexity: {record.get('complexity', '')}",
                f"Group: {record.get('group', '')}",
                f"Since: {record.get('since', '')}",
                f"Arity: {record.get('arity', '')}",
                f"Function: {record.get('function', '')}",
                f"Command flags: {', '.join(record.get('command_flags', []))}",
                f"ACL categories: {', '.join(record.get('acl_categories', []))}",
                f"Arguments: {trim_json(arguments, 1200)}",
                f"Reply schema: {trim_json(reply_schema, 1200)}",
            ])
            sections.append(IdentifierSection(
                section_id=stable_id("redis", full_name),
                source=str(json_path),
                title=identifier,
                identifier=identifier,
                text=text,
                kind="redis_command",
            ))
    return sections


def load_k8s_field_sections(k8s_api_dir):
    sections = []
    files = [
        "core/v1/types_swagger_doc_generated.go",
        "apps/v1/types_swagger_doc_generated.go",
        "batch/v1/types_swagger_doc_generated.go",
        "networking/v1/types_swagger_doc_generated.go",
    ]
    for relative_path in files:
        file_path = k8s_api_dir / relative_path
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for type_name, docs in parse_swagger_doc_maps(text):
            type_description = docs.get("", "")
            for field_name, field_description in docs.items():
                if not field_name:
                    continue
                identifier = f"Kubernetes {type_name}.{field_name}"
                section_text = "\n".join([
                    f"Identifier: {identifier}",
                    f"API type: {type_name}",
                    f"Field: {field_name}",
                    f"Type description: {type_description}",
                    f"Field description: {field_description}",
                    f"Source file: {relative_path}",
                ])
                sections.append(IdentifierSection(
                    section_id=stable_id("k8s", relative_path, type_name, field_name),
                    source=str(file_path),
                    title=identifier,
                    identifier=identifier,
                    text=section_text,
                    kind="k8s_field",
                ))
    return sections


def parse_swagger_doc_maps(text):
    for match in re.finditer(r"var map_(\w+) = map\[string\]string\{(.*?)\n\}", text, re.S):
        type_name = match.group(1)
        block = match.group(2)
        docs = {}
        for field_match in re.finditer(r'"((?:\\.|[^"\\])*)"\s*:\s*"((?:\\.|[^"\\])*)"', block, re.S):
            key = ast.literal_eval('"' + field_match.group(1) + '"')
            value = ast.literal_eval('"' + field_match.group(2) + '"')
            docs[key] = value
        if docs:
            yield type_name, docs


def build_cases(sections, case_count):
    by_identifier = {section.identifier: section for section in sections}
    cases = []
    for index, (category, identifier, question, terms) in enumerate(CASE_SPECS[:case_count], start=1):
        section = by_identifier.get(identifier)
        if not section:
            raise ValueError(f"测试用例找不到对应文档：{identifier}")
        cases.append(IdentifierCase(
            case_id=f"case_{index:02d}",
            question=question,
            section_id=section.section_id,
            source=section.source,
            title=section.title,
            identifier=section.identifier,
            gold_text=section.text,
            category=category,
            exact_terms=terms,
        ))
    return cases


def run_case(system, mode, chat_model, case):
    docs, context, retrieval_seconds = system.retrieve(case.question, mode)
    prompt_messages = [
        SystemMessage(content=(
            "你是技术文档问答助手。只能依据用户提供的参考资料回答。"
            "回答时必须保留命令名、字段名、复杂度、flags、参数名等精确标识符。"
            "如果资料不足，请说明资料不足。"
        )),
        HumanMessage(content=(
            f"参考资料：\n{context}\n\n"
            f"用户问题：{case.question}\n\n"
            "请简洁回答，并保留关键标识符："
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

    retrieved_ids = [doc.metadata.get("section_id") for doc in docs]
    hit_rank = first_hit_rank(retrieved_ids, case.section_id)
    return {
        "mode": mode,
        "retrieved_section_ids": retrieved_ids,
        "retrieved_identifiers": [doc.metadata.get("identifier") for doc in docs],
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
        return {
            "context_coverage": safe_div(len(gold_tokens & context_tokens), len(gold_tokens)),
            "context_noise": 1 - safe_div(len(context_tokens & gold_tokens), len(context_tokens)),
            "answer_gold_overlap": safe_div(len(gold_tokens & answer_tokens), len(gold_tokens)),
            "exact_term_recall": exact_terms_recall(case.exact_terms, result["context"]),
            "identifier_at_1": 1.0 if result["retrieved_section_ids"] and result["retrieved_section_ids"][0] == case.section_id else 0.0,
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
- keypoint_coverage：是否覆盖标准资料中的关键点
- identifier_preservation：是否保留命令名、字段名、flags、参数名、复杂度等精确标识符

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
    "identifier_preservation": 0
  }},
  "hybrid_rrf": {{
    "correctness": 0,
    "groundedness": 0,
    "keypoint_coverage": 0,
    "identifier_preservation": 0
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
    vector = collect_metrics(case_results, "vector_only")
    hybrid = collect_metrics(case_results, "hybrid_rrf")
    dims = ["correctness", "groundedness", "keypoint_coverage", "identifier_preservation"]
    vector_quality = collect_quality(case_results, "vector_only", dims)
    hybrid_quality = collect_quality(case_results, "hybrid_rrf", dims)
    vector["llm_quality_avg_0_5"] = vector_quality
    hybrid["llm_quality_avg_0_5"] = hybrid_quality

    category_summary = {}
    for category in sorted({item["case"]["category"] for item in case_results}):
        items = [item for item in case_results if item["case"]["category"] == category]
        category_summary[category] = {
            "case_count": len(items),
            "vector_hit_rate": mean([1 if item["vector_only"]["hit_gold"] else 0 for item in items]),
            "hybrid_hit_rate": mean([1 if item["hybrid_rrf"]["hit_gold"] else 0 for item in items]),
            "vector_mrr": mean([item["vector_only"]["mrr"] for item in items]),
            "hybrid_mrr": mean([item["hybrid_rrf"]["mrr"] for item in items]),
            "vector_at_1": mean([item["lexical_scores"]["vector_only"]["identifier_at_1"] for item in items]),
            "hybrid_at_1": mean([item["lexical_scores"]["hybrid_rrf"]["identifier_at_1"] for item in items]),
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
        "identifier_at_1_relative_change": relative_change(hybrid["identifier_at_1"], vector["identifier_at_1"]),
        "exact_term_recall_relative_change": relative_change(hybrid["avg_exact_term_recall"], vector["avg_exact_term_recall"]),
        "context_noise_relative_change": relative_change(hybrid["avg_context_noise"], vector["avg_context_noise"]),
        "quality_relative_change": relative_change(hybrid_quality, vector_quality),
        "retrieval_latency_relative_change": relative_change(hybrid["avg_retrieval_seconds"], vector["avg_retrieval_seconds"]),
        "total_latency_relative_change": relative_change(hybrid["avg_total_seconds"], vector["avg_total_seconds"]),
        "context_chars_relative_change": relative_change(hybrid["avg_context_chars"], vector["avg_context_chars"]),
        "winners": winners,
        "category_summary": category_summary,
    }


def collect_metrics(case_results, key):
    results = [item[key] for item in case_results]
    lexical = [item["lexical_scores"][key] for item in case_results]
    return {
        "hit_rate": mean([1 if item["hit_gold"] else 0 for item in results]),
        "mrr": mean([item["mrr"] for item in results]),
        "identifier_at_1": mean([item["identifier_at_1"] for item in lexical]),
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


def collect_quality(case_results, key, dims):
    values = []
    for item in case_results:
        judge = item.get("judge_scores") or {}
        if key not in judge:
            continue
        values.append(statistics.mean([to_float(judge[key].get(dim)) for dim in dims]))
    return mean(values)


def render_markdown_report(payload):
    summary = payload["summary"]
    lines = [
        "# Identifier Hybrid Retrieval Benchmark",
        "",
        f"- Redis source: {payload['source_repos']['redis']}",
        f"- Kubernetes API source: {payload['source_repos']['kubernetes_api']}",
        f"- Cases: {summary['case_count']}",
        f"- Sections: {payload['config']['sections']}",
        f"- Chat model: {payload['config']['chat_model']}",
        f"- Embedding model: {payload['config']['embedding_model']}",
        "",
        "## Summary",
        "",
        "| Metric | Vector Only | Hybrid RRF | Change |",
        "| --- | ---: | ---: | ---: |",
    ]
    rows = [
        ("Hit Rate", "hit_rate", "percent"),
        ("MRR", "mrr", "number"),
        ("Identifier@1", "identifier_at_1", "percent"),
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
        "| Category | Cases | Vector Hit | Hybrid Hit | Vector MRR | Hybrid MRR | Vector @1 | Hybrid @1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for category, row in summary["category_summary"].items():
        lines.append(
            f"| {category} | {row['case_count']} | {row['vector_hit_rate'] * 100:.2f}% | {row['hybrid_hit_rate'] * 100:.2f}% | "
            f"{row['vector_mrr']:.3f} | {row['hybrid_mrr']:.3f} | {row['vector_at_1'] * 100:.2f}% | {row['hybrid_at_1'] * 100:.2f}% |"
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
            f"### {case['case_id']} {case['identifier']}",
            "",
            f"- Category: {case['category']}",
            f"- Question: {case['question']}",
            f"- Vector hit/rank: {item['vector_only']['hit_gold']} / {item['vector_only']['hit_rank']}",
            f"- Hybrid hit/rank: {item['hybrid_rrf']['hit_gold']} / {item['hybrid_rrf']['hit_rank']}",
            f"- Vector retrieved: {item['vector_only']['retrieved_identifiers']}",
            f"- Hybrid retrieved: {item['hybrid_rrf']['retrieved_identifiers']}",
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
    return sum(1 for term in terms if term.lower() in text_lower) / len(terms)


def trim_json(value, max_chars):
    text = json.dumps(value, ensure_ascii=False)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "...[truncated]"


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
