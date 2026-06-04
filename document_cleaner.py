"""
文档清洗器。
"""
import re
from collections import Counter

import config_data as config
from document_parser import ParsedDocument


# ---------这是第3次更新，更新内容为：新增保守数据清洗层，解析后入库前清理明显噪声---------
PAGE_NUMBER_PATTERNS = [
    re.compile(r"^第\s*\d+\s*页$", re.IGNORECASE),
    re.compile(r"^第\s*\d+\s*/\s*\d+\s*页$", re.IGNORECASE),
    re.compile(r"^page\s+\d+(\s+of\s+\d+)?$", re.IGNORECASE),
    re.compile(r"^\d+\s*/\s*\d+$"),
    re.compile(r"^-+\s*\d+\s*-+$"),
]

SENTENCE_ENDINGS = ("。", "！", "？", ".", "!", "?", "；", ";", "：", ":")
STRUCTURAL_PREFIXES = ("文件：", "文件类型：", "[", "#", "表头：", "Word 表格", "工作表 ")


def clean_parsed_document(parsed_document: ParsedDocument) -> ParsedDocument:
    """对解析后的文本做保守清洗，不改写正文语义。"""
    if not config.enable_document_cleaning:
        return parsed_document

    original_text = parsed_document.text or ""
    text = _remove_control_chars(original_text)
    text = _normalize_special_spaces(text)

    raw_lines = text.splitlines()
    normalized_lines = [_normalize_line(line) for line in raw_lines]
    compact_lines = _compact_blank_lines(normalized_lines)

    page_clean_lines, removed_page_lines = _remove_page_number_lines(compact_lines)
    repeat_clean_lines, removed_repeated_lines = _remove_repeated_short_lines(page_clean_lines)
    merged_lines, merged_broken_lines = _merge_broken_lines(repeat_clean_lines, parsed_document.file_type)
    final_lines = _compact_blank_lines(merged_lines)
    cleaned_text = "\n".join(final_lines).strip()

    if not cleaned_text:
        raise ValueError("数据清洗后未剩余有效文本，请检查原文件内容或清洗规则")

    metadata = dict(parsed_document.metadata or {})
    metadata.update({
        "cleaner": "conservative-v1",
        "clean_original_line_count": len(raw_lines),
        "clean_final_line_count": len(cleaned_text.splitlines()),
        "clean_removed_page_lines": removed_page_lines,
        "clean_removed_repeated_lines": removed_repeated_lines,
        "clean_merged_broken_lines": merged_broken_lines,
    })

    return ParsedDocument(
        text=cleaned_text,
        file_type=parsed_document.file_type,
        metadata=metadata,
    )


def _remove_control_chars(text):
    return "".join(
        char for char in text
        if char in ("\n", "\t") or ord(char) >= 32
    )


def _normalize_special_spaces(text):
    return (
        text
        .replace("\ufeff", "")
        .replace("\u00a0", " ")
        .replace("\u3000", " ")
    )


def _normalize_line(line):
    return re.sub(r"[ \t]+", " ", line or "").strip()


def _compact_blank_lines(lines):
    compacted = []
    last_blank = False
    for line in lines:
        if not line:
            if not last_blank:
                compacted.append("")
            last_blank = True
            continue
        compacted.append(line)
        last_blank = False

    while compacted and compacted[0] == "":
        compacted.pop(0)
    while compacted and compacted[-1] == "":
        compacted.pop()

    return compacted


def _remove_page_number_lines(lines):
    cleaned_lines = []
    removed = 0
    for line in lines:
        if line and any(pattern.match(line) for pattern in PAGE_NUMBER_PATTERNS):
            removed += 1
            continue
        cleaned_lines.append(line)
    return cleaned_lines, removed


def _remove_repeated_short_lines(lines):
    non_blank_lines = [line for line in lines if line]
    counts = Counter(non_blank_lines)
    cleaned_lines = []
    removed = 0

    for line in lines:
        if _is_removable_repeated_line(line, counts):
            removed += 1
            continue
        cleaned_lines.append(line)

    return cleaned_lines, removed


def _is_removable_repeated_line(line, counts):
    if not line:
        return False
    if len(line) > config.cleaning_repeated_line_max_length:
        return False
    if counts[line] < config.cleaning_repeated_line_min_count:
        return False
    if line.startswith(STRUCTURAL_PREFIXES):
        return False
    if re.match(r"^第\s*\d+\s*(条|章|节|部分)", line):
        return False
    return True


def _merge_broken_lines(lines, file_type):
    if file_type not in config.cleaning_merge_broken_lines_file_types:
        return lines, 0

    merged_lines = []
    merged_count = 0
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line:
            merged_lines.append(line)
            index += 1
            continue

        if index + 1 < len(lines):
            next_line = lines[index + 1]
            if _should_merge_with_next(line, next_line):
                merged_lines.append(_join_broken_line(line, next_line))
                merged_count += 1
                index += 2
                continue

        merged_lines.append(line)
        index += 1

    return merged_lines, merged_count


def _should_merge_with_next(line, next_line):
    if not next_line:
        return False
    if line.startswith(STRUCTURAL_PREFIXES) or next_line.startswith(STRUCTURAL_PREFIXES):
        return False
    if line.endswith(SENTENCE_ENDINGS):
        return False
    if _looks_like_list_item(line) or _looks_like_list_item(next_line):
        return False
    if len(line) < 8 or len(next_line) < 4:
        return False
    if len(line) > 80 or len(next_line) > 80:
        return False
    return True


def _looks_like_list_item(line):
    return bool(re.match(r"^(\d+[\.\、]|[（(]?\d+[）)]|[一二三四五六七八九十]+[、.])", line))


def _join_broken_line(line, next_line):
    if re.search(r"[A-Za-z0-9]$", line) and re.match(r"^[A-Za-z0-9]", next_line):
        return f"{line} {next_line}"
    return f"{line}{next_line}"
# ---------第3次更新结束---------
