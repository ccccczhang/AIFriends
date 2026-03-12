import json

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, SystemMessage, AIMessage
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend, Message, SystemPrompt
from web.views.friend.message.chat.graph import ChatGraph
from web.views.friend.message.memory.update import update_memory


# 告诉 Django REST framework：这是一个用来输出 SSE 的 Renderer，
# 不要帮我改数据，原样把我给的内容写进 HTTP 响应流。
class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

def add_system_prompt(state, friend):
    msgs = state['messages']
    system_prompts = SystemPrompt.objects.filter(title='回复').order_by('order_number')
    prompt = ''
    for sp in system_prompts:
        prompt += sp.prompt
    prompt += f"\n【角色性格】\n{friend.character.profile}\n"
    prompt += f"【长期记忆】\n{friend.memory}\n"
    return {'messages': [SystemMessage(prompt)] + msgs}

def add_recent_messages(state, friend):
    msgs = state['messages']
    message_raw = list(Message.objects.filter(friend=friend).order_by('-id')[:10]) # 顺序是：最新 → 最旧
    message_raw.reverse() # 顺序是：最旧 → 最新，因为大模型上下文必须是：旧对话 -> 新对话
    messages = [] # 准备 LangGraph message 列表
    for m in message_raw:
        messages.append(HumanMessage(m.user_message))
        messages.append(AIMessage(m.output))
    return {'messages': msgs[:1] + messages + msgs[-1:]} # msgs[-1:]取最后一条消息

class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer] # 渲染器
    def post(self, request):
        # 这里不要加try-except了，这里需要对接大模型，会经常报异常，如果加try-except，报错就看不到了，不方便调试
        friend_id = request.data['friend_id']
        message = request.data['message'].strip()

        if not message:
            return Response({
                'result': '消息不能为空'
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user) #pk:Primary Key（主键）
        if not friends.exists():
            return Response({
                'result': '好友不存在'
            })
        friend = friends.first()
        # 用langGraph搭建大模型
        app = ChatGraph.create_app()

        inputs = {
            'messages': [HumanMessage(message)], # 因为graph.py为messages
        }
        inputs = add_system_prompt(inputs, friend)
        inputs = add_recent_messages(inputs, friend)

        def event_stream(): # 流式输出
            full_output = '' # 把大模型输出存入Message数据库？中
            full_usage = {} # 记录最终 token 用量
            for msg, metadata in app.stream(inputs, stream_mode="messages"):
        # msg：当前模型生成的一小段消息，metadata：元信息（路由、节点名、step 等）
                if isinstance(msg, BaseMessageChunk): # 判断是不是「消息分片」,BaseMessageChunk 就是这种“半截消息”
                    if msg.content:
                        full_output += msg.content
                        yield f"data: {json.dumps({'content': msg.content}, ensure_ascii=False)}\n\n" #SSE 核心格式
                        #data: → SSE 规定字段，json.dumps(...) → 前端好解析，\n\n → 一条事件结束标志
                    if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                        full_usage = msg.usage_metadata
            yield "data: [DONE]\n\n" # 这是一种约定俗成的结束标记

            # 存储到数据库的“管理界面”
            input_tokens = full_usage.get('input_tokens', 0)
            output_tokens = full_usage.get('output_tokens', 0)
            total_tokens = full_usage.get('total_tokens', 0)
            Message.objects.create(
                friend=friend,
                user_message=message[:500],
                input=json.dumps(
                    [m.model_dump() for m in inputs['messages']],  # 把一组消息对象转成 JSON 字符串，方便在 Django 里存数据库或记录日志
                    ensure_ascii=False
                )[:10000],
                output=full_output[:500],
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )
            if Message.objects.filter(friend=friend).count() % 1 == 0:
                update_memory(friend)


        # 修改输出方式
        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        return response
