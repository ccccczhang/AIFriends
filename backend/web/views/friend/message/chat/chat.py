from langchain_core.messages import HumanMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph


class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # 这里不要加try-except了，这里需要对接大模型，会经常报异常，如果加try-except，报错就看不到了，不方便调试
        friend_id = request.data['friend_id']
        message = request.data['message'].strip()
        if not message:
            return Response({
                'result': '消息不能为空'
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user) #pk:Primary Key（主键）
        if not friends:
            return Response({
                'result': '好友不存在'
            })
        friend = friends.first()
        # 用langGraph搭建大模型
        app = ChatGraph.create_app()

        inputs = {
            'messages': [HumanMessage(message)], # 因为graph.py为messages
        }
        res = app.invoke(inputs)
        print(res['messages'][-1].content) # 这里-1是因为messages有俩部分，1是user_message 2是AIoutput
        return Response({
            'result': 'success',
        })