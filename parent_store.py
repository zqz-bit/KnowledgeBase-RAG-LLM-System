"""
Parent chunk 本地存储。
"""
import json
import os

import config_data as config


# 这是第1次更新，更新内容为：新增 parent chunk 的 JSON 存取服务
class ParentStoreService(object):
    """使用 JSON 文件保存 parent chunk，供 RAG 检索到 child 后回查完整上下文。"""

    def __init__(self, storage_path=None):
        self.storage_path = storage_path or config.parent_store_path
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)

    def _load_all(self):
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                parent_data = json.load(f)
                if isinstance(parent_data, dict):
                    return parent_data
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_all(self, parent_data):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(parent_data, f, ensure_ascii=False, indent=2)

    def save_many(self, parent_records):
        """批量保存 parent chunk，key 为 parent_id。"""
        parent_data = self._load_all()
        parent_data.update(parent_records)
        self._save_all(parent_data)

    def get_parent(self, parent_id):
        """根据 parent_id 读取 parent chunk。"""
        return self._load_all().get(parent_id)
# 第1次更新结束
