import os
from pprint import pprint
from typing import TypedDict, Annotated, Sequence

import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from django.utils.timezone import localtime, now
from langgraph.prebuilt import ToolNode
from openai import embeddings

from web.documents.utils.custom_embeddings import CustomEmbeddings


class ChatGraph:
    @staticmethod # 把后续函数封装到静态文件中，这样写，就可以这样调用ChatGraph.create_app()
    def create_app():
        @tool # 工具
        def get_time() -> str:
            """当需要查询精确时间时，调用此函数。返回格式为:[年-月-日 时:分:秒]"""  # 三个引号在python里表示函数的文档，必须紧跟在函数下面，作用是告诉大模型它是干嘛的
            return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')

        @tool
        def search_knowledge_base(quary: str) -> str:
            """ 当用户查询阿里云百炼平台的相关信息时，调用此函数。输入为要查询的问题，输出为查询结果。 """
            db = lancedb.connect('./web/documents/lancedb_storage')
            embeddings = CustomEmbeddings()
            vector_db = LanceDB(
                connection=db,
                embedding=embeddings,
                table_name='my_knowledge_base',
            )
            docs = vector_db.similarity_search(quary, k=3) # 查询三个文档
            context = '\n\n'.join([f'内容片段：{i + 1}\n{doc.page_content}' for i, doc in enumerate(docs)]) # 把文档结果拼接起来, i + 1：从下标1开始
            return f'从知识库中找到以下信息：\n\n{context}\n'


        tools = [get_time, search_knowledge_base] # 这里是所有工具

        llm = ChatOpenAI(
            model = 'deepseek-v3.2',
            openai_api_key = os.getenv('API_KEY'),
            openai_api_base = os.getenv('API_BASE'),
            streaming = True,  # 流式输出
            model_kwargs={
                "stream_options": {
                    "include_usage": True,  # 输出token消耗数量
                }
            }
        ).bind_tools(tools)


        # 记录状态state 信息的存储方式
        class AgentState(TypedDict): # 不覆盖，追加到旧消息末尾
            messages: Annotated[Sequence[BaseMessage], add_messages] #Annotated:给类型Sequence[BaseMessage](是 LangChain 里的消息基类)附加“额外语义信息”，add_messages:当多个节点返回 messages 时，不要覆盖，而是“追加合并”

        # 定义 agent：对大模型的调用
        def model_call(state: AgentState) -> AgentState:
            pprint(state['messages'])
            res = llm.invoke(state['messages']) # invoke 表示对大模型的调用
            return {'messages': [res]}

        def should_continue(state: AgentState) -> str:
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return "tools"
            return "end"
        # 定义工具节点
        tool_node = ToolNode(tools)

        # 定义状态图，笔记里有：最简单的langgraph的计算流程
        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call) #节点
        graph.add_node('tools', tool_node)

        graph.add_edge(START, 'agent')
        graph.add_conditional_edges(
            'agent',
            should_continue,
            {
                'tools': 'tools',
                'end': END
            }
        )
        graph.add_edge('tools', 'agent')

        return graph.compile() #

