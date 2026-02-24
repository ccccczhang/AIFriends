from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response

from web.models.character import Character


class HomepageIndexView(APIView):
    def get(self, request):
        try:
            items_count = int(request.query_params.get('items_count', 0)) #  加上 0，意味如果items_count没传参，则默认值为0
            search_query = request.query_params.get('search_query', '').strip()  #  后端处理查询操作
            if search_query:
                queryset = Character.objects.filter(
                    Q(name__icontains=search_query) | Q(profile__icontains=search_query) # Q:django中利用 Q进行复杂查询 i:不区分大小写，contains：包含
                )
            else:
                queryset = Character.objects.all()
            characters_raw = queryset.order_by('-id')[items_count: items_count + 20] #从 Character 表中按 id 倒序跳过前 items_count 条再取接下来的 20 条数据
            characters = []
            for character in characters_raw:
                author = character.author
                characters.append({
                    'id': character.id,
                    'name': character.name,
                    'profile': character.profile,
                    'photo': character.photo.url,
                    'background_image': character.background_image.url,
                    'author': {
                        'user_id': author.user_id,
                        'username': author.user.username,
                        'photo': author.photo.url,
                    }
                })
            return Response({
                'result': 'success',
                'characters': characters
            })
        except :
            return Response({
                'result': '系统异常，请稍后重试'
            })
