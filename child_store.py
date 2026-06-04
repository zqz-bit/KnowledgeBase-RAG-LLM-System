"""
Child chunk 本地存储。
"""
import json
import os

import config_data as config


# ---------这是第4次更新，更新内容为：新增 child chunk 的 JSON 存取服务，供 BM25 检索建索引---------
class ChildStoreService(object):
    """使用 JSON 文件保存 child chunk，供 BM25 与混合检索读取。"""

    def __init__(self, storage_path=None):
        self.storage_path = storage_path or config.child_store_path
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)

    def _load_all(self):
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                child_data = json.load(f)
                if isinstance(child_data, dict):
                    return child_data
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_all(self, child_data):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(child_data, f, ensure_ascii=False, indent=2)

    def save_many(self, child_records):
        """批量保存 child chunk，key 为 child_id。"""
        child_data = self._load_all()
        child_data.update(child_records)
        self._save_all(child_data)

    def get_all(self):
        """读取全部 child chunk，供 BM25 建索引。"""
        return self._load_all()

    def get_child(self, child_id):
        """根据 child_id 读取 child chunk。"""
        return self._load_all().get(child_id)
# ---------第4次更新结束---------
