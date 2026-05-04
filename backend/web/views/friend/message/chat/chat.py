import asyncio
import base64
import json
import os
import threading
from queue import Queue

import uuid

import websockets
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
# 添加系统提示词
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

        friends = Friend.objects.filter(pk=friend_id, me__user=request.user)  #pk: Primary Key（主键）
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

        # 修改输出方式
        response = StreamingHttpResponse(
            self.event_stream(app, inputs, friend, message),
            content_type="text/event-stream",
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no' # 避免缓存
        return response

    async def tts_sender(self, app, inputs, mq, ws, task_id):
        async for msg, metadata in app.astream(inputs, stream_mode="messages"):
            # msg：当前模型生成的一小段消息，metadata：元信息（路由、节点名、step 等）
            if isinstance(msg, BaseMessageChunk):  # 判断是不是「消息分片」,BaseMessageChunk 就是这种“半截消息”
                if msg.content:
                    await ws.send(json.dumps({
                        "header": {
                            "action": "continue-task",
                            "task_id": task_id,  # 随机uuid
                            "streaming": "duplex"
                        },
                        "payload": {
                            "input": {
                                "text": msg.content,
                            }
                        }
                    }))
                    mq.put_nowait({'content': msg.content}) #加到消息队列里
                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                    mq.put_nowait({'usage': msg.usage_metadata})
        await ws.send(json.dumps({
            "header": {
                "action": "finish-task",
                "task_id": task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {}  # input不能省去，否则会报错
            }
        }))

    async def tts_receiver(self, mq, ws):
        async for msg in ws:
            if isinstance(msg, bytes):
                audio = base64.b64encode(msg).decode('utf8')
                mq.put_nowait({'audio': audio})
            else:
                data = json.loads(msg)
                event = data['header']['event']
                if event in ['task-finished', 'task-failed']:
                    break


    async def run_tts_tasks(self, app, inputs, mq):
        task_id = uuid.uuid4().hex
        api_key = os.getenv('API_KEY')
        wss_url = os.getenv('WSS_URL')
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        async with websockets.connect(wss_url, additional_headers=headers) as ws:
            await ws.send(json.dumps({
                    "header": {
                    "action": "run-task",
                    "task_id": task_id, # 随机uuid
                    "streaming": "duplex"
                },
                "payload": {
                    "task_group": "audio",
                    "task": "tts",
                    "function": "SpeechSynthesizer",
                    "model": "cosyvoice-v3-flash",
                    "parameters": {
                        "text_type": "PlainText",
                        "voice": "longanyang",            # 音色
                        "format": "mp3",		        # 音频格式
                        "sample_rate": 22050,	        # 采样率
                        "volume": 50,			# 音量
                        "rate": 1.25,				# 语速
                        "pitch": 1				# 音调
                    },
                    "input": {# input不能省去，不然会报错
                    }
                }
            }))
            async for msg in ws:
                if json.loads(msg)['header']['event'] == 'task-started':
                    break
            await asyncio.gather(
                self.tts_sender(app, inputs, mq, ws, task_id),
                self.tts_receiver(mq, ws),
            )


    def work(self, app, inputs, mq):
        try:
            asyncio.run(self.run_tts_tasks(app, inputs, mq))
        finally:
            mq.put_nowait(None) # 无论如何都返回None，防止while true死循环


    def event_stream(self, app, inputs, friend, message):  # 流式输出
        mq = Queue() # 定义一个消息队列
        thread = threading.Thread(target=self.work, args=(app, inputs, mq)) # 定义一个线程
        thread.start() # 启动线程

        full_output = ''  # 把大模型输出存入Message数据库？中
        full_usage = {}  # 记录最终 token 用量
        while True: # 死循环每次从消息队列中取数据
            msg = mq.get()
            full_output = full_output + json.dumps(msg, ensure_ascii=False)
            if not msg: # work 最后返回一个null
                break
            # msg 有三种可能
            if msg.get('content', None): #如果存在，返回它的值，如果不存在，返回默认值 None
                full_output += msg['content']
                yield f"data: {json.dumps({'content': msg['content']}, ensure_ascii=False)}\n\n"  # SSE 核心格式
            if msg.get('audio', None):
                yield f"data: {json.dumps({'audio': msg['audio']}, ensure_ascii=False)}\n\n"  # SSE 核心格式
            if msg.get('usage', None):
                full_usage = msg['usage']

        yield "data: [DONE]\n\n"  # 这是一种约定俗成的结束标记

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

