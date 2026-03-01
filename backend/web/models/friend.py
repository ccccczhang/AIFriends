# 每个用户与每个虚拟角色的好友关系
from django.db import models
from django.utils.timezone import now, localtime

from web.models.character import Character
from web.models.user import UserProfile


class Friend(models.Model):
    # models.ForeignKey() 是 Django 模型中定义多对一关系的字段。它会在数据库中创建一个外键列，指向另一个模型的主键，从而实现两个表之间的关联
    me = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    # 给大模型的短期记忆，给大模型总结一下与虚拟人物的关键信息
    memory = models.TextField(default='', max_length=5000, blank=True, null=True)
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.character.name} - {self.me.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}" #strftime