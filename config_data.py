
md5_path = "./md5.text"

# Chroma
collection_name="rag"
persist_directory="./chroma_db"

# ---------这是第2次更新，更新内容为：集中配置上传入口支持的文件类型---------
supported_upload_file_types = ["txt", "pdf", "doc", "docx", "html", "htm", "xlsx"]
# ---------第2次更新结束---------

# ---------这是第3次更新，更新内容为：新增保守数据清洗配置---------
enable_document_cleaning = True
cleaning_repeated_line_min_count = 3
cleaning_repeated_line_max_length = 40
cleaning_merge_broken_lines_file_types = ["pdf", "doc"]
# ---------第3次更新结束---------

# ---------这是第4次更新，更新内容为：新增 child_store 与 BM25+向量混合检索 RRF 重排配置---------
child_store_path = "./child_store.json"

enable_hybrid_search = True
vector_search_k = 6
bm25_search_k = 6
rerank_top_k = 3
rrf_k = 60
# ---------第4次更新结束---------

# spliter
chunk_size= 1000
chunk_overlap= 100
separators =["\n\n","\n",".","!","?","。","！","？"," ",""]

max_spliter_char_number= 1000  # 文本分割阈值

# 这是第1次更新，更新内容为：新增 Parent-Child Chunking 配置，child 入向量库，parent 入本地 JSON
parent_store_path = "./parent_store.json"

parent_chunk_size = 2000
parent_chunk_overlap = 200

child_chunk_size = 400
child_chunk_overlap = 80

parent_child_separators = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", "；", ";", "，", ",", " ", ""]
# 第1次更新结束

# 相似度K值
# 这是第1次更新，更新内容为：child chunk 更小，检索 TopK 从 1 调整为 3
similarity_threshold =3     # 检索返回匹配的文档数量
# 第1次更新结束

embedding_model_name="text-embedding-v4"
chat_model_name="qwen3-max"

# ---------这是第5次更新，更新内容为：新增结合历史的用户问题改写配置---------
enable_query_rewrite = True
query_rewrite_model_name = chat_model_name
query_rewrite_history_turns = 4
query_rewrite_max_chars = 200
# ---------第5次更新结束---------

# ---------这是第6次更新，更新内容为：新增 Codex 风格上下文滚动压缩配置---------
enable_context_compression = True
context_compress_model_name = chat_model_name
context_compress_trigger_messages = 20
context_keep_recent_messages = 10
context_summary_max_chars = 1200
context_compress_single_message_max_chars = 800
# ---------第6次更新结束---------

#
session_config = {
    "configurable": {
        "session_id": "user_001",
    }
}
