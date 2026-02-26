# 后台管理系统，这里是在：定制后台页面怎么用
from django.contrib import admin
from web.models.user import UserProfile
from web.models.character import Character
from web.models.friend import Friend

@admin.register(UserProfile) #注册模型到后台
class UserProfileAdmin(admin.ModelAdmin): #告诉 Django：admin 后台要管理 UserProfile 这张表
    raw_id_fields = ('user',)
#逗号不可删，表示传的是列表，raw_id_fields是后台显示方式设置，如果不写会显示下拉框，显示所有用户，用户多了就会卡爆，写了的话，就会变成一个 ID 输入框 + 搜索按钮

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    raw_id_fields = ('me', 'character',)