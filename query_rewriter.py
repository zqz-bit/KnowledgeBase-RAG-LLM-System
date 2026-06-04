"""
用户问题改写器。
"""
import re

import config_data as config

# ---------这是第6次更新，更新内容为：问题改写时保留长期历史摘要---------
from context_compressor import (
    get_message_content,
    get_message_role,
    is_context_summary_message,
    strip_context_summary_content,
)
# ---------第6次更新结束---------


# ---------这是第5次更新，更新内容为：新增结合历史的用户问题改写服务，用于检索和最终回答---------
class QueryRewriteService(object):
    """结合最近对话历史，将口语化问题改写成更适合知识库检索和回答的问题。"""

    def __init__(self):
        self.rewrite_chain = None
        self._init_rewrite_chain()

    def _init_rewrite_chain(self):
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_community.chat_models.tongyi import ChatTongyi
        except ImportError:
            return

        prompt_template = ChatPromptTemplate.from_messages([
            ("system",
             "你是知识库检索问题改写器。你的任务不是回答问题，而是把用户当前问题改写成一句更清晰、"
             "更适合知识库检索和问答的问题。可以结合最近对话历史补全“这个、那个、上面、它、那”等指代。"
             "必须保留用户输入或历史中的数字、日期、条款号、课程代码、专业名、文件名。"
             "不要编造历史和问题中没有的信息；如果无法确定指代对象，直接返回用户原问题。"
             "如果用户问题已经清楚，直接原样返回。只输出一条改写后的问题，不要解释。"),
            ("user", "最近对话历史：\n{history}\n\n用户当前问题：{input}\n\n请输出改写后的问题：")
        ])
        chat_model = ChatTongyi(model=config.query_rewrite_model_name)
        self.rewrite_chain = prompt_template | chat_model | StrOutputParser()

    def rewrite(self, user_input, history=None):
        """返回一条改写后的问题；失败时回退到原始问题。"""
        user_input = (user_input or "").strip()
        if not config.enable_query_rewrite or not user_input:
            return user_input
        if self.rewrite_chain is None:
            return user_input

        try:
            rewritten_query = self.rewrite_chain.invoke({
                "input": user_input,
                "history": format_history_for_rewrite(history or []),
            })
        except Exception:
            return user_input

        rewritten_query = clean_rewritten_query(rewritten_query)
        if not rewritten_query:
            return user_input
        return rewritten_query[:config.query_rewrite_max_chars]


def format_history_for_rewrite(history):
    """将最近几轮消息格式化为短文本，供改写器补全上下文指代。"""
    # max_messages = max(0, config.query_rewrite_history_turns * 2)
    # if max_messages:
    #     history = list(history)[-max_messages:]
    # ---------这是第6次更新，更新内容为：改写问题时始终保留摘要，再拼接最近若干轮原文---------
    history = list(history or [])
    summary_lines = []
    regular_messages = []
    for message in history:
        if is_context_summary_message(message):
            summary = strip_context_summary_content(get_message_content(message))
            if summary:
                summary_lines.append(summary)
        else:
            regular_messages.append(message)

    max_messages = max(0, config.query_rewrite_history_turns * 2)
    if max_messages:
        regular_messages = regular_messages[-max_messages:]

    lines = []
    if summary_lines:
        lines.append("长期历史摘要：\n" + "\n".join(summary_lines))

    for message in regular_messages:
        role = get_message_role(message)
        content = get_message_content(message)
        if not content:
            continue
        lines.append(f"{role}：{content}")
    # ---------第6次更新结束---------

    if not lines:
        return "无"
    return "\n".join(lines)


def clean_rewritten_query(text):
    """清理模型输出，只保留一条问题。"""
    text = (text or "").strip()
    if not text:
        return ""

    text = re.sub(r"^```[a-zA-Z]*", "", text).strip()
    text = text.replace("```", "").strip()

    for prefix in ("改写后的问题：", "改写问题：", "优化后的问题：", "优化问题：", "问题："):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    text = lines[0].strip("\"'“”‘’")
    return text


def _get_message_role(message):
    message_type = getattr(message, "type", "")
    if message_type == "human":
        return "用户"
    if message_type == "ai":
        return "助手"
    if message_type == "system":
        return "系统"
    return "消息"


def _get_message_content(message):
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()
# ---------第5次更新结束---------
