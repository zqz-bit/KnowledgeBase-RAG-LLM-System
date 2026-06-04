"""
基于Streamlit完成WEB网页上传服务

Streamlit ： 当WEB页面元素变化，则代码重新执行一遍，无法维护状态
"""
import streamlit as st
import time


from knowledge_base import KnowledgeBaseService
from document_parser import parse_uploaded_file
from document_cleaner import clean_parsed_document
import config_data as config


# 添加网页标题
st.title("知识库更新服务")

# file_uploader
# ---------这是第2次更新，更新内容为：上传入口从只支持 TXT 改为支持 TXT/PDF/DOC/DOCX/HTML/XLSX---------
# uploader_file=st.file_uploader(
#     "请上传TXT文件",
#     type=['txt'],
#     accept_multiple_files=False,   # False表示仅接受一个文件的上传
# )
uploader_file=st.file_uploader(
    "请上传知识库文件",
    type=config.supported_upload_file_types,
    accept_multiple_files=False,   # False表示仅接受一个文件的上传
)
# ---------第2次更新结束---------

if "service" not in st.session_state:          # 会话状态字典，session_state本身也是字典
    st.session_state["service"]=KnowledgeBaseService()
# count=0
if uploader_file is not None:
    # 提取文件信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size /1024
    st.subheader(f"文件名:{file_name}")
    st.write(f"格式:{file_type}  | 大小:{file_size:.2f}KB")

    # get_value -> bytes -> decode("utf-8")
    # ---------这是第2次更新，更新内容为：注释原 TXT 直接解码逻辑，改为统一文档解析器---------
    # text=uploader_file.getvalue().decode("utf-8")
    # ---------第2次更新结束---------

    with st.spinner("载入知识库中。。。"):     # 在 spinner内的代码执行过程中，会有一个转圈动画，优化用户体验
        time.sleep(1)
        # ---------这是第2次更新，更新内容为：解析多格式文件后再调用 Parent-Child 入库流程---------
        try:
            parsed_document=parse_uploaded_file(uploader_file)
            # ---------这是第3次更新，更新内容为：解析后、入库前增加保守数据清洗---------
            cleaned_document=clean_parsed_document(parsed_document)
            # ---------第3次更新结束---------
        except Exception as e:
            st.error(f"文件解析或清洗失败：{e}")
        else:
            # 这是第1次更新，更新内容为：将文件扩展名传给入库层，方便后续扩展 PDF/DOCX/XLSX 解析
            # file_extension=file_name.rsplit(".",1)[-1].lower() if "." in file_name else "txt"
            # result= st.session_state["service"].upload_by_str(text,file_name,file_type=file_extension)
            # 第1次更新结束
            result= st.session_state["service"].upload_by_str(
                # ---------这是第3次更新，更新内容为：使用清洗后的文本和清洗 metadata 进入知识库---------
                # parsed_document.text,
                cleaned_document.text,
                # ---------第3次更新结束---------
                file_name,
                file_type=cleaned_document.file_type,
                extra_metadata=cleaned_document.metadata,
            )
            st.write(result)
        # ---------第2次更新结束---------
