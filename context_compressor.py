"""
对话上下文压缩器。
"""
from langchain_core.messages import HumanMessage

import config_data as config


# ---------这是第6次更新，更新内容为：新增 Codex 风格上下文滚动压缩服务---------
SUMMARY_PREFIX = "[历史摘要]"


def compress_chat_history_messages(messages):
    """超过阈值后，将较早原始消息滚动压缩为一条摘要，并保留最近原文消息。"""
    messages = list(messages or [])
    if not getattr(config, "enable_context_compression", True):
        return messages

    existing_summary, regular_messages = split_context_summary_messages(messages)
    trigger_messages = _get_int_config("context_compress_trigger_messages", 20)

    if len(regular_messages) <= trigger_messages:
        if existing_summary:
            return [build_context_summary_message(existing_summary)] + regular_messages
        return regular_messages

    compressor = ContextCompressService()
    return compressor.compress_messages(existing_summary, regular_messages)


class ContextCompressService(object):
    """把旧摘要和较早对话合并成一条新的长期摘要。"""

    def __init__(self):
        self.compress_chain = None
        self._init_compress_chain()

    def _init_compress_chain(self):
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_community.chat_models.tongyi import ChatTongyi
        except ImportError:
            return

        prompt_template = ChatPromptTemplate.from_messages([
            ("system",
             "你是知识库问答系统的对话历史压缩器。你的任务不是回答问题，而是把较早的多轮对话"
             "压缩成一条可以持续滚动更新的长期摘要。摘要要帮助后续问题改写和回答理解上下文。"
             "必须保留用户明确提到的身份、年级、专业、业务对象、文件名、数字、日期、条款号、"
             "课程代码、已确认结论、偏好和未解决问题。删除寒暄、重复内容和无效过程。"
             "不要编造历史中没有的信息。用中文输出，控制在 {max_chars} 字以内，只输出摘要正文。"),
            ("user",
             "已有长期摘要：\n{existing_summary}\n\n"
             "需要并入摘要的较早对话：\n{history}\n\n"
             "请输出更新后的长期摘要：")
        ])
        try:
            chat_model = ChatTongyi(model=config.context_compress_model_name)
            self.compress_chain = prompt_template | chat_model | StrOutputParser()
        except Exception:
            self.compress_chain = None

    def compress_messages(self, existing_summary, regular_messages):
        keep_recent_messages = _get_int_config("context_keep_recent_messages", 10)
        if keep_recent_messages > 0:
            messages_to_compress = regular_messages[:-keep_recent_messages]
            recent_messages = regular_messages[-keep_recent_messages:]
        else:
            messages_to_compress = regular_messages
            recent_messages = []

        new_summary = self.compress_summary(existing_summary, messages_to_compress)
        if not new_summary:
            return recent_messages
        return [build_context_summary_message(new_summary)] + recent_messages

    def compress_summary(self, existing_summary, messages_to_compress):
        if not messages_to_compress:
            return existing_summary

        fallback_summary = fallback_compress_summary(existing_summary, messages_to_compress)
        if self.compress_chain is None:
            return fallback_summary

        try:
            summary = self.compress_chain.invoke({
                "existing_summary": existing_summary or "无",
                "history": format_messages_for_summary(messages_to_compress),
                "max_chars": _get_int_config("context_summary_max_chars", 1200),
            })
        except Exception:
            return fallback_summary

        summary = clean_summary_text(summary)
        if not summary:
            return fallback_summary
        return _limit_text(summary, _get_int_config("context_summary_max_chars", 1200))


def split_context_summary_messages(messages):
    """返回已有摘要文本和普通历史消息。"""
    summary_parts = []
    regular_messages = []
    for message in messages:
        if is_context_summary_message(message):
            summary = strip_context_summary_content(get_message_content(message))
            if summary:
                summary_parts.append(summary)
        else:
            regular_messages.append(message)
    return "\n".join(summary_parts).strip(), regular_messages


def build_context_summary_message(summary):
    return HumanMessage(content=f"{SUMMARY_PREFIX}\n{summary.strip()}")


def is_context_summary_message(message):
    return get_message_content(message).startswith(SUMMARY_PREFIX)


def strip_context_summary_content(content):
    content = (content or "").strip()
    if content.startswith(SUMMARY_PREFIX):
        content = content[len(SUMMARY_PREFIX):].strip()
    return content


def fallback_compress_summary(existing_summary, messages_to_compress):
    """模型不可用时的保底压缩，避免历史写入失败。"""
    parts = []
    if existing_summary:
        parts.append(existing_summary.strip())

    history_text = format_messages_for_summary(messages_to_compress)
    if history_text and history_text != "无":
        parts.append("较早对话摘录：\n" + history_text)

    summary = "\n".join(parts).strip()
    return _limit_text(summary, _get_int_config("context_summary_max_chars", 1200))


def format_messages_for_summary(messages):
    lines = []
    single_message_max_chars = _get_int_config("context_compress_single_message_max_chars", 800)
    for message in messages:
        role = get_message_role(message)
        content = get_message_content(message)
        if not content:
            continue
        content = _limit_text(content, single_message_max_chars)
        lines.append(f"{role}：{content}")

    if not lines:
        return "无"
    return "\n".join(lines)


def clean_summary_text(text):
    text = (text or "").strip()
    if not text:
        return ""

    text = text.replace("```", "").strip()
    for prefix in ("更新后的长期摘要：", "长期摘要：", "摘要："):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    return strip_context_summary_content(text)


def get_message_role(message):
    message_type = getattr(message, "type", "")
    if message_type == "human":
        return "用户"
    if message_type == "ai":
        return "助手"
    if message_type == "system":
        return "系统"
    return "消息"


def get_message_content(message):
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


def _get_int_config(name, default):
    try:
        return max(0, int(getattr(config, name, default)))
    except (TypeError, ValueError):
        return default


def _limit_text(text, max_chars):
    text = (text or "").strip()
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."
# ---------第6次更新结束---------
