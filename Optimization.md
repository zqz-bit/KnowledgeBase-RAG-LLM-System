# KnowledgeBase-RAG-LLM-System

 ## 对项目的优化更新
---

## ✨ 更新内容

### 第1次更新：Parent-Child Chunking 入库与检索

#### 更新好处
本次 Parent-Child Chunking 更新的核心好处是把“检索”和“回答”拆成两个不同粒度来处理：

- child chunk 更小，负责向量检索，能提升问题命中的精准度。
- parent chunk 更大，负责提供回答上下文，能减少回答时上下文不足、信息断裂的问题。
- parent 存本地 JSON，child 存 Chroma，避免把不参与检索的大块文本也全部向量化，结构更清晰。
- child metadata 中保存 `parent_id`，检索结果可以稳定回查完整 parent，为后续支持 PDF、DOCX、XLSX 的页码、章节、Sheet、行号等元数据扩展打基础。
- 整体 RAG 链路仍保持轻量，不引入复杂数据库或重型语义切分，适合当前学习项目逐步升级。

#### 具体更新内容
- 新增 `parent_store.py`，使用 `parent_store.json` 保存 parent chunk。
- `knowledge_base.py` 入库流程改为：原文先切 parent，parent 再切 child；child 写入 Chroma 向量库，parent 写入本地 JSON。
- `rag.py` 检索时先命中 child，再通过 `parent_id` 回查 parent，把更完整的 parent 上下文交给大模型回答。
- `app_upload.py` 开始向入库层传入文件扩展名，为后续 PDF、DOCX、XLSX 解析扩展预留接口。
- 本次更新暂不新增 PDF、DOCX、XLSX 解析能力。

### 第2次更新：多格式文档解析入库

#### 更新好处
本次更新把“上传文件”和“解析文件内容”拆开，项目不再只依赖 TXT，可以更通用地接入学校资料、业务手册、网页文档和表格数据：

- 支持 TXT、PDF、DOC、DOCX、HTML、XLSX 上传，知识库来源更丰富。
- 新增 `document_parser.py` 作为独立解析层，后续继续增强 OCR、表格语义化、更多文件类型时，不需要大改入库主流程。
- DOCX 和 XLSX 会尽量保留段落、标题、表格、Sheet、行等结构信息，转成更适合向量检索的文本。
- PDF 会按页加入页码标记，后续可以继续扩展到答案溯源。
- 解析后的文本继续复用第1次更新的 Parent-Child 入库链路，避免重复造一套入库逻辑。

#### 具体更新内容
- 新增 `document_parser.py`，提供 TXT、PDF、DOC、DOCX、HTML、XLSX 的统一解析入口 `parse_uploaded_file`。
- `app_upload.py` 上传类型从 `txt` 扩展为 `txt/pdf/doc/docx/html/htm/xlsx`，并改为先解析文件再调用 `upload_by_str`。
- `config_data.py` 新增 `supported_upload_file_types`，集中管理上传入口支持的文件扩展名。
- DOC 解析采用轻量兼容方案：优先使用 macOS 自带 `textutil`，其次使用本机 `antiword`；如果环境没有这些工具，建议先将 `.doc` 转成 `.docx` 后上传。
- 扫描版 PDF 暂不支持 OCR，本次主要支持可提取文本的普通 PDF。

### 第3次更新：保守数据清洗层

#### 更新好处
本次更新在“文档解析后、知识库入库前”增加数据清洗层，目标是先清掉明显噪声，同时尽量不误删学校资料、政策条款、数字、日期等关键信息：

- 减少页码、重复页眉页脚、控制字符、多余空白等噪声进入向量库。
- 提升 Parent-Child 切块质量，让 parent 和 child 更接近真实正文内容。
- 降低无意义文本的 embedding 数量，减少检索干扰和后续成本。
- 清洗动作会写入 metadata，方便后续排查某篇文档清洗前后的变化。
- 保持清洗规则保守，不使用大模型改写正文，优先保证入库内容真实、稳定、可解释。

#### 具体更新内容
- 新增 `document_cleaner.py`，提供统一入口 `clean_parsed_document`。
- `app_upload.py` 改为：上传文件 -> 解析文件 -> 清洗文本 -> 调用 `upload_by_str` 入库。
- `config_data.py` 新增清洗配置，包括是否启用清洗、重复短行阈值、断行合并适用文件类型。
- 清洗内容包括：去控制字符、规范空白、压缩空行、删除明显页码行、删除重复短行、轻量合并断行。
- 清洗 metadata 会随文档一起进入入库 metadata，例如清洗前后行数、删除页码行数量、删除重复行数量、合并断行数量。

### 第4次更新：BM25 + 向量混合检索与 RRF 重排

#### 更新好处
本次更新把单路向量检索升级为“关键词检索 + 语义检索”的混合召回，更适合学校资料、制度条款、课程表这类既有语义问题又有精确编号/术语的问题：

- 向量检索继续负责语义相似召回，适合自然语言提问。
- BM25 负责关键词、编号、课程代码、日期、条款号等精确匹配召回。
- RRF 轻量重排不需要额外大模型，能把两路检索都命中的 child 排到更靠前。
- `child_store.json` 保存 child 原文和 metadata，BM25 不依赖 Chroma 内部结构，后续调试和扩展更清楚。
- 混合检索后仍通过 `parent_id` 回查 parent，保留第1次更新的“child 精准检索、parent 完整回答”优势。

#### 具体更新内容
- 新增 `child_store.py`，保存 child chunk 的原文和 metadata。
- `knowledge_base.py` 入库时为每个 child 生成稳定 `child_id`，并同步写入 Chroma 与 `child_store.json`。
- 新增 `hybrid_retriever.py`，实现向量检索、BM25 检索、RRF 融合重排。
- `rag.py` 从单路向量检索改为调用 `HybridRetrieverService`，再沿用 parent 回查逻辑组织上下文。
- `config_data.py` 新增混合检索配置：`vector_search_k`、`bm25_search_k`、`rerank_top_k`、`rrf_k`。
- `requirements.txt` 新增 `rank-bm25` 和 `jieba`，用于 BM25 与中文分词。

### 第5次更新：结合历史的用户问题改写

#### 更新好处
本次更新在 RAG 检索前增加 Query Rewrite，用大模型结合最近对话历史把口语化、指代不清的问题改写成更清晰的问题，提升后续混合检索和回答效果：

- 可以补全“这个、那个、上面、它、那”等口语化指代，减少检索 query 信息不足的问题。
- 改写后的问题会同时用于检索和最终回答，整个 RAG 流程围绕更清晰的问题执行。
- 只输出一条改写问题，不引入多 query 检索，避免改动现有 BM25 + 向量混合检索逻辑。
- 改写失败、模型异常或输出为空时自动回退到用户原问题，保证系统可用性。
- 改写 prompt 明确要求保留数字、日期、条款号、课程代码、专业名、文件名，降低关键信息被误改的风险。

#### 具体更新内容
- 新增 `query_rewriter.py`，提供 `QueryRewriteService`。
- `config_data.py` 新增 Query Rewrite 配置，包括是否启用、模型名称、历史轮数和最大输出长度。
- `rag.py` 在 RAG 链路最前面加入 `rewrite_chain_input`，先改写用户问题，再进入 hybrid retrieval 和最终 prompt。
- 本次不改 `hybrid_retriever.py`，仍保持单 query 检索、BM25 + 向量召回、RRF 重排流程。

### 第6次更新：Codex 风格上下文滚动压缩

#### 更新好处
本次更新在会话历史存储层增加“长期摘要 + 最近原文消息”的滚动压缩能力，解决连续对话越聊越长、但只取最近几轮又容易遗落早期关键信息的问题：

- 未超过阈值时仍读取完整历史，保持普通短对话的上下文完整性。
- 超过阈值后，将较早历史合并为 1 条长期摘要，只保留最近原始消息，控制历史文件体积和最终 prompt 长度。
- 长期摘要会保留用户身份、年级、专业、数字、日期、条款号、课程代码、文件名、已确认结论和未解决问题，尽量减少早期重要信息丢失。
- Query Rewrite 阶段会同时读取长期摘要和最近几轮原文，避免摘要被最近消息截断逻辑裁掉。
- 如果压缩模型不可用，会使用保底截断摘要，避免因为压缩失败导致聊天写入或项目运行中断。
- 最终回答 prompt 明确历史只用于理解用户意图和指代，事实依据仍以知识库检索资料为主，降低历史摘要影响事实回答的风险。

#### 具体更新内容
- 新增 `context_compressor.py`，提供上下文摘要识别、历史拆分、滚动压缩和保底压缩能力。
- `config_data.py` 新增上下文压缩配置，包括是否启用、压缩模型、触发消息数、保留最近消息数、摘要最大长度和单条消息最大输入长度。
- `file_history_store.py` 在 `add_messages` 写入新消息后触发压缩检查，超过 20 条原始消息时保存为“1 条带 `[历史摘要]` 标记的普通历史消息 + 最近 10 条原始消息”，避免通义模型的多 system message 限制。
- `query_rewriter.py` 改为格式化历史时始终保留长期摘要，再拼接最近若干轮原文消息。
- `rag.py` 调整历史提示词，合并为单条 system message，说明历史中可能包含长期摘要，并强调回答事实仍以检索参考资料为主。
