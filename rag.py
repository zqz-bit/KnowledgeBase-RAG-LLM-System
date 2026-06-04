from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# ---------这是第6次更新，更新内容为：兼容不同 LangChain 版本的 RunnableWithMessageHistory 导入路径---------
try:
    from langchain_core.runnables import RunnableWithMessageHistory
except ImportError:
    from langchain_core.runnables.history import RunnableWithMessageHistory
# ---------第6次更新结束---------
from file_history_store import get_history
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from parent_store import ParentStoreService
from hybrid_retriever import HybridRetrieverService
from query_rewriter import QueryRewriteService


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)

    return prompt


class RagService(object):
    def __init__(self):

        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )

        # 这是第1次更新，更新内容为：RAG 检索 child 后，通过 parent_id 回查 parent 上下文
        self.parent_store = ParentStoreService()
        # 第1次更新结束

        # ---------这是第4次更新，更新内容为：使用 BM25+向量混合检索替代单路向量检索---------
        self.hybrid_retriever = HybridRetrieverService(
            vector_retriever=self.vector_service.get_retriever()
        )
        # ---------第4次更新结束---------

        # ---------这是第5次更新，更新内容为：新增结合历史的 Query Rewrite，后续检索和回答都使用改写问题---------
        self.query_rewriter = QueryRewriteService()
        # ---------第5次更新结束---------

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                # ---------这是第6次更新，更新内容为：提示模型正确使用压缩后的历史摘要---------
                # ("system", "以我提供的已知参考资料为主，"
                #  "简洁和专业的回答用户问题。参考资料:{context}。"),
                # ("system", "并且我提供用户的对话历史记录，如下："),
                ("system", "以我提供的已知参考资料为主，简洁和专业地回答用户问题。"
                 "参考资料：{context}。"
                 "并且我会提供用户的对话历史记录，历史中可能包含长期摘要。"
                 "历史只用于理解用户意图和指代，事实依据仍以参考资料为主。"),
                # ---------第6次更新结束---------
                MessagesPlaceholder("history"),
                ("user", "请回答用户提问：{input}")
            ]
        )

        self.chat_model = ChatTongyi(model=config.chat_model_name)

        self.chain = self.__get_chain()

    def __get_chain(self):
        """获取最终的执行链"""

        # ---------这是第4次更新，更新内容为：注释旧 retriever，后续 context 由 hybrid_retriever 统一召回和 RRF 重排---------
        # retriever = self.vector_service.get_retriever()
        # ---------第4次更新结束---------

        # ---------这是第5次更新，更新内容为：在 RAG 链路最前面将用户输入改写为更清晰的问题---------
        def rewrite_chain_input(value: dict)->dict:
            if isinstance(value, dict):
                new_value = dict(value)
                user_input = new_value.get("input", "")
                history = new_value.get("history", [])
            else:
                new_value = {"input": value, "history": []}
                user_input = value
                history = []

            rewritten_input = self.query_rewriter.rewrite(user_input, history)
            new_value["input"] = rewritten_input
            new_value["rewritten_input"] = rewritten_input
            return new_value
        # ---------第5次更新结束---------

        def format_document(docs: list[Document]):
            if not docs:
                return "无相关参考资料"

            formatted_str = ""
            # 这是第1次更新，更新内容为：注释旧的直接使用 child 文档片段逻辑，改为优先使用 parent 完整上下文
            # for doc in docs:
            #     formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            used_parent_ids=set()
            for doc in docs:
                parent_id=doc.metadata.get("parent_id")
                if parent_id:
                    if parent_id in used_parent_ids:
                        continue
                    parent_record=self.parent_store.get_parent(parent_id)
                    if parent_record:
                        used_parent_ids.add(parent_id)
                        formatted_str += (
                            f"父级文档片段：{parent_record.get('text', '')}\n"
                            f"父级文档元数据：{parent_record.get('metadata', {})}\n"
                            f"命中的子片段：{doc.page_content}\n"
                            f"子片段元数据：{doc.metadata}\n\n"
                        )
                        continue

                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            # 第1次更新结束

            return formatted_str

        def format_for_retriever(value: dict)->str:

            return value["input"]

        def format_for_prompt_template(value):
            # {input, context, history}
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value


        # ---------这是第5次更新，更新内容为：注释旧的直接进入检索链路，改为先 Query Rewrite 再检索和回答---------
        # chain = (
        #     {
        #         "input": RunnablePassthrough(),
        #         # ---------这是第4次更新，更新内容为：RAG 上下文改为 BM25+向量混合检索结果---------
        #         # "context": RunnableLambda(format_for_retriever) | retriever | format_document
        #         "context": RunnableLambda(format_for_retriever) | RunnableLambda(self.hybrid_retriever.invoke) | format_document
        #         # ---------第4次更新结束---------
        #     }| RunnableLambda(format_for_prompt_template) |self.prompt_template | print_prompt |self.chat_model | StrOutputParser()
        # )
        chain = RunnableLambda(rewrite_chain_input) | (
            {
                "input": RunnablePassthrough(),
                # ---------这是第4次更新，更新内容为：RAG 上下文改为 BM25+向量混合检索结果---------
                # "context": RunnableLambda(format_for_retriever) | retriever | format_document
                "context": RunnableLambda(format_for_retriever) | RunnableLambda(self.hybrid_retriever.invoke) | format_document
                # ---------第4次更新结束---------
            }| RunnableLambda(format_for_prompt_template) |self.prompt_template | print_prompt |self.chat_model | StrOutputParser()
        )
        # ---------第5次更新结束---------

        conversation_chain = RunnableWithMessageHistory(       # 增强的链
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        return conversation_chain


if __name__ == '__main__':
    # session id 配置
    session_config ={
        "configurable":{
            "session_id":"user_001",
        }
    }
    res = RagService().chain.invoke({"input":"我之前问了什么"},session_config)
    print(res)
