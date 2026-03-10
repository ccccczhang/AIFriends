import json

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph

# 告诉 Django REST framework：这是一个用来输出 SSE 的 Renderer，
# 不要帮我改数据，原样把我给的内容写进 HTTP 响应流。
class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

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

        def event_stream(): # 流式输出
            final_usage = {} # 记录最终 token 用量
            for msg, metadata in app.stream(inputs, stream_mode="messages"):
        # msg：当前模型生成的一小段消息，metadata：元信息（路由、节点名、step 等）
                if isinstance(msg, BaseMessageChunk): # 判断是不是「消息分片」,BaseMessageChunk 就是这种“半截消息”
                    if msg.content:
                        yield f"data: {json.dumps({'content': msg.content}, ensure_ascii=False)}\n\n" #SSE 核心格式
                        #data: → SSE 规定字段，json.dumps(...) → 前端好解析，\n\n → 一条事件结束标志
                    if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                        final_usage = msg.usage_metadata
            yield "data: [DONE]\n\n" # 这是一种约定俗成的结束标记
            print(final_usage)
        # 修改输出方式
        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        return response
