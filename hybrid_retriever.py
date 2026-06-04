"""
BM25 + 向量混合检索与 RRF 重排。
"""
import re

from langchain_core.documents import Document

import config_data as config
from child_store import ChildStoreService


# ---------这是第4次更新，更新内容为：新增 BM25+向量混合检索，并使用 RRF 做轻量 rerank---------
class HybridRetrieverService(object):
    """向量检索负责语义召回，BM25 负责关键词召回，RRF 融合排序。"""

    def __init__(self, vector_retriever, child_store=None):
        self.vector_retriever = vector_retriever
        self.child_store = child_store or ChildStoreService()

    def invoke(self, query):
        vector_docs = self.vector_retriever.invoke(query)
        if not config.enable_hybrid_search:
            return vector_docs[:config.rerank_top_k]

        bm25_docs = self._bm25_search(query)
        return self._rrf_rerank(vector_docs, bm25_docs)

    def _bm25_search(self, query):
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            return []

        child_records = self.child_store.get_all()
        if not child_records:
            return []

        child_items = [
            (child_id, child_record)
            for child_id, child_record in child_records.items()
            if child_record.get("text", "").strip()
        ]
        if not child_items:
            return []

        tokenized_corpus = [
            _tokenize(child_record["text"])
            for _, child_record in child_items
        ]
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(query_tokens)
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        docs = []
        for index in ranked_indices[:config.bm25_search_k]:
            score = float(scores[index])
            if score <= 0:
                continue

            child_id, child_record = child_items[index]
            metadata = dict(child_record.get("metadata", {}))
            metadata.update({
                "child_id": child_id,
                "retrieval_source": "bm25",
                "bm25_score": score,
            })
            docs.append(Document(
                page_content=child_record.get("text", ""),
                metadata=metadata,
            ))
        return docs

    def _rrf_rerank(self, vector_docs, bm25_docs):
        merged_docs = {}
        vector_ranks = _build_rank_map(vector_docs)
        bm25_ranks = _build_rank_map(bm25_docs)
        all_keys = set(vector_ranks.keys()) | set(bm25_ranks.keys())

        for doc in vector_docs + bm25_docs:
            key = _doc_key(doc)
            if key not in merged_docs:
                merged_docs[key] = doc

        scored_docs = []
        for key in all_keys:
            score = 0.0
            sources = []

            if key in vector_ranks:
                score += 1 / (config.rrf_k + vector_ranks[key])
                sources.append("vector")
            if key in bm25_ranks:
                score += 1 / (config.rrf_k + bm25_ranks[key])
                sources.append("bm25")

            doc = merged_docs[key]
            metadata = dict(doc.metadata)
            metadata.update({
                "rrf_score": score,
                "vector_rank": vector_ranks.get(key),
                "bm25_rank": bm25_ranks.get(key),
                "retrieval_sources": ",".join(sources),
            })
            scored_docs.append(Document(
                page_content=doc.page_content,
                metadata=metadata,
            ))

        scored_docs.sort(key=lambda doc: doc.metadata["rrf_score"], reverse=True)
        return scored_docs[:config.rerank_top_k]


def _build_rank_map(docs):
    rank_map = {}
    for index, doc in enumerate(docs, start=1):
        key = _doc_key(doc)
        if key not in rank_map:
            rank_map[key] = index
    return rank_map


def _doc_key(doc):
    child_id = doc.metadata.get("child_id")
    if child_id:
        return child_id

    parent_id = doc.metadata.get("parent_id", "")
    parent_index = doc.metadata.get("parent_index", "")
    child_index = doc.metadata.get("child_index", "")
    return f"{parent_id}:{parent_index}:{child_index}:{hash(doc.page_content)}"


def _tokenize(text):
    try:
        import jieba
        return [
            token.strip().lower()
            for token in jieba.lcut(text or "")
            if token.strip()
        ]
    except ImportError:
        return re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", (text or "").lower())
# ---------第4次更新结束---------
