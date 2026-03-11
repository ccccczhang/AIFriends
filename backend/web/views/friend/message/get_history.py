from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend, Message


class GetHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            last_message_id = int(request.query_params.get('last_message_id')) #if判断要用，所以改为数字
            friend_id = request.query_params.get('friend_id')
            queryset = Message.objects.filter(friend_id=friend_id, friend__me__user = request.user)
            if last_message_id > 0: # 不是第一次加载
                queryset = queryset.filter(pk__lt=last_message_id)
            message_raw = queryset.order_by('-id')[:1] # 倒序，从新到久
            messages = []
            for m in message_raw:
                messages.append({
                    'id': m.id,
                    'user_message': m.user_message,
                    'output': m.output,
                })
            return Response({
                'result': 'success',
                'messages': messages,
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })