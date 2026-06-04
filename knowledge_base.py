"""
知识库
"""
import os
import  config_data as config
import  hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
from parent_store import ParentStoreService
from child_store import ChildStoreService

def check_md5(md5_str:str):
    """检查传入的MD5字符串是否已经被处理过了
            return False未处理，True已处理
    """
    if not os.path.exists(config.md5_path):
        # if 进入表示文件不存在，表示没有处理过这个MD5
        open(config.md5_path,'w',encoding='utf-8').close()
        return False
    else:
        for line in open(config.md5_path,'r',encoding='utf-8').readlines():
            line=line.strip()   # 处理字符串前后的空格和回车
            if line == md5_str:
                return True     # 已处理过
        return False

def save_md5(md5_str:str):
    """将传入的md5字符串，记录到文件内保存"""
    with open(config.md5_path,'a',encoding="utf-8")as f:
        f.write(md5_str + '\n')

def get_string_md5(input_str:str ,encoding='utf-8'):
    """将出传入的字符串转换为md5字符串"""

    # 将字符串转换为bytes字节数组
    str_bytes = input_str.encode(encoding=encoding)

    # 创建md5 对象
    md5_obj =hashlib.md5()      # 得到md5对象
    md5_obj.update(str_bytes)   # 更新内容（传入即将要转换的字节数组）
    md5_hex=md5_obj.hexdigest() # 得到md5的十六进制字符串

    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self):
        # 如果文件夹不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory,exist_ok=True)

        self.chroma=Chroma(          # 向量存储的示例 Chroma向量库对象
            collection_name=config.collection_name,      #数据库表名
            # 这是第1次更新，更新内容为：embedding 模型统一读取配置，方便后续替换模型
            embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
            # 第1次更新结束
            persist_directory=config.persist_directory,   #数据库本地存储文件夹
        )      # 向量存储的实例，Chroma向量库对象
        # 这是第1次更新，更新内容为：将原单层切块替换为 Parent-Child Chunking
        # self.spliter=RecursiveCharacterTextSplitter(  # 文本分割器的对象
        #     chunk_size=config.chunk_size,             # 分割后的文本段最大长度
        #     chunk_overlap=config.chunk_overlap,       # 连续文本段之间的字符重叠数量
        #     separators=config.separators,             # 自然段落划分的符号
        #     length_function=len,                      # 使用python自带的len函数做长度统计的依赖
        # )      # 文本分割器的对象
        self.parent_spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.parent_chunk_size,
            chunk_overlap=config.parent_chunk_overlap,
            separators=config.parent_child_separators,
            length_function=len,
        )
        self.child_spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.child_chunk_size,
            chunk_overlap=config.child_chunk_overlap,
            separators=config.parent_child_separators,
            length_function=len,
        )
        self.parent_store=ParentStoreService()
        # ---------这是第4次更新，更新内容为：新增 child_store，用于保存 BM25 检索所需的 child 文本---------
        self.child_store=ChildStoreService()
        # ---------第4次更新结束---------
        # 第1次更新结束

    # 这是第1次更新，更新内容为：upload_by_str 增加 file_type 和 extra_metadata，方便后续接入 PDF/DOCX/XLSX 解析
    def upload_by_str(self,data:str,filename,file_type="txt",extra_metadata=None):
    # 第1次更新结束
        """将传入的字符串，进行向量化，存入向量数据库中"""
        if not data or not data.strip():
            return "[Error] 上传内容为空，未写入知识库"

        # 先得到出传入的字符串的md5值
        md5_hex=get_string_md5(data)
        if check_md5(md5_hex):
            return "[Repeat] 内容已存在知识库"

        # 这是第1次更新，更新内容为：注释旧的单层 chunk 入库逻辑，改为 parent 入 JSON、child 入 Chroma
        # if len(data) > config.max_spliter_char_number:
        #     knowledge_chunks:list[str]=self.spliter.split_text(data) # 类型统一，均用列表套字符串
        # else:
        #     knowledge_chunks=[data]
        #
        # metadata={
        #     "source":filename,
        #     #2026-3-8 15:43:30
        #     "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #     "operator":"客户",
        # }
        #
        # self.chroma.add_texts(        # 内容加载到向量库中
        #     # iterable-> list \tuple
        #     knowledge_chunks,
        #     metadata=[metadata for _ in knowledge_chunks],
        #
        # )

        create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_metadata={
            "source":filename,
            "file_type":file_type,
            "create_time":create_time,
            "operator":"客户",
        }
        if extra_metadata:
            base_metadata.update(extra_metadata)

        parent_chunks:list[str]=self.parent_spliter.split_text(data)
        parent_records={}
        # ---------这是第4次更新，更新内容为：新增 child_records 与 child_ids，child 同时写 Chroma 和 child_store---------
        child_records={}
        child_ids=[]
        # ---------第4次更新结束---------
        child_chunks=[]
        child_metadatas=[]

        for parent_index,parent_text in enumerate(parent_chunks):
            parent_id=f"{md5_hex}_parent_{parent_index}"
            parent_metadata={
                **base_metadata,
                "parent_id":parent_id,
                "parent_index":parent_index,
                "chunk_role":"parent",
            }
            parent_records[parent_id]={
                "text":parent_text,
                "metadata":parent_metadata,
            }

            child_texts:list[str]=self.child_spliter.split_text(parent_text)
            for child_index,child_text in enumerate(child_texts):
                # ---------这是第4次更新，更新内容为：为每个 child 生成稳定 child_id，供 BM25、Chroma 和 RRF 去重对齐---------
                child_id=f"{parent_id}_child_{child_index}"
                # ---------第4次更新结束---------
                child_chunks.append(child_text)
                child_metadata={
                    **base_metadata,
                    "parent_id":parent_id,
                    "parent_index":parent_index,
                    "child_id":child_id,
                    "child_index":child_index,
                    "chunk_role":"child",
                }
                child_metadatas.append(child_metadata)
                # ---------这是第4次更新，更新内容为：将 child 原文和 metadata 保存到 child_store，供 BM25 建索引---------
                child_records[child_id]={
                    "text":child_text,
                    "metadata":child_metadata,
                }
                child_ids.append(child_id)
                # ---------第4次更新结束---------

        if not child_chunks:
            return "[Error] 未生成可入库的知识片段"

        self.parent_store.save_many(parent_records)
        # ---------这是第4次更新，更新内容为：同步保存 child_store，再写入 Chroma 向量库---------
        self.child_store.save_many(child_records)
        # ---------第4次更新结束---------
        self.chroma.add_texts(
            child_chunks,
            metadatas=child_metadatas,
            # ---------这是第4次更新，更新内容为：Chroma 中使用同一 child_id，便于混合检索结果对齐---------
            ids=child_ids,
            # ---------第4次更新结束---------
        )
        # 第1次更新结束
        save_md5(md5_hex)
        return f"[Success]内容已经成功载入知识库：parent {len(parent_records)} 个，child {len(child_chunks)} 个"

if __name__ =='__main__':
    # r1 = get_string_md5("周杰伦")
    # r2 = get_string_md5("周杰伦")
    # r3 = get_string_md5("周杰伦4")
    # # 为什么用md5  哈希算法（散列函数）能把任意长度数据，算出一串32位16进制的字符串
    # #优点： 快 简单 能做简单文件校验   ，缺点：  不能做安全加密   易于被破解，过时
    # #SHA-256  SHA-512
    #
    # print(r1)
    # print(r2)
    # print(r3)

    #save_md5("7a8941058aaf4df5147042ce104568da")
    #print(check_md5("7a8941058aaf4df5147042ce104568da"))
    service= KnowledgeBaseService()
    r=service.upload_by_str("流星","testfile")
    print(r)
