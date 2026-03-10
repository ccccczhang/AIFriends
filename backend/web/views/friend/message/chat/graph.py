import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


class ChatGraph:
    @staticmethod # 把后续后续函数封装到静态文件中，这样写，就可以这样调用ChatGraph.create_app()
    def create_app():
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
        )
        # 记录状态state 信息的存储方式
        class AgentState(TypedDict): # 不覆盖，追加到旧消息末尾
            messages: Annotated[Sequence[BaseMessage], add_messages] #Annotated:给类型Sequence[BaseMessage](是 LangChain 里的消息基类)附加“额外语义信息”，add_messages:当多个节点返回 messages 时，不要覆盖，而是“追加合并”

        # 定义 agent：对大模型的调用
        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages']) # invoke 表示对大模型的调用
            return {'messages': [res]}
        # 定义状态图，笔记里有：最简单的langgraph的计算流程
        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call) #节点

        graph.add_edge(START, 'agent')
        graph.add_edge('agent', END)

        return graph.compile() #

