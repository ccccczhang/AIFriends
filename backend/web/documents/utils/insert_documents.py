import lancedb
from lancedb.pydantic import vector
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import LanceDB
from langchain_core.runnables.schema import CustomStreamEvent
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import embeddings

from web.documents.utils.custom_embeddings import CustomEmbeddings

# 把文本变成documents对象
def insert_documents():
    loader = TextLoader('./web/documents/data.txt', encoding='utf-8') # 把本地 txt 文件加载成 LangChain 的 Document 对象。TextLoader 是 LangChain 提供的文档加载器。
    documents = loader.load() # Document 对象
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50) # 文档切分，RecursiveCharacterTextSplitter是 LangChain 的文本切分器。
    texts = text_splitter.split_documents(documents) # 执行切分，把 documents 切成多个小 Document
    print(f"已切分 {len(texts)} 个片段。") # 打印切分结果

    embeddings = CustomEmbeddings() # 创建 embedding 模型，用 embedding 模型把文本变成向量。
    db = lancedb.connect('./web/documents/lancedb_storage') # 连接 LanceDB 向量数据库，如果目录不存在：./web/documents/lancedb_storage，LanceDB 会自动创建。
    vector_db = LanceDB.from_documents( # 插入向量数据库
        documents=texts, # 要存入的文档。
        embedding=embeddings, # 指定向量模型
        connection=db, # 数据库连接对象。
        table_name='my_knowledge_base', # 数据库表名。
        mode='overwrite', # overwrite：覆盖写入，append：追加
    )
    print(f"已插入 {vector_db._table.count_raws()} 行数据。") # 查看数据库中有多少条记录