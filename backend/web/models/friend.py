# 每个用户与每个虚拟角色的好友关系
from django.db import models
from django.utils.timezone import now, localtime

from web.models.character import Character
from web.models.user import UserProfile

# 创建一个数据库表：friend
class Friend(models.Model):
    # models.ForeignKey() 是 Django 模型中定义多对一关系的字段。它会在数据库中创建一个外键列，指向另一个模型的主键，从而实现两个表之间的关联
    me = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    # 给大模型的短期记忆，给大模型总结一下与虚拟人物的关键信息
    memory = models.TextField(default='', max_length=5000, blank=True, null=True)
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)
    # def __str__(self)作用是：后台显示这条数据的文字
    def __str__(self):
        return f"{self.character.name} - {self.me.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}" #strftime

class Message(models.Model):
    friend = models.ForeignKey(Friend, on_delete=models.CASCADE)
    user_message = models.TextField(max_length=500)
    input = models.TextField(max_length=10000) # 对大模型的输入
    output = models.TextField(max_length=500) # 对大模型的输出
    input_tokens = models.IntegerField(default=0) # 输入的 tokens Integer: 整数int
    output_tokens = models.IntegerField(default=0) # 输出的 tokens
    total_tokens = models.IntegerField(default=0) #总共的 tokens
    create_time = models.DateTimeField(default=now)
    # 方便在数据中看
    def __str__(self):                                                                             #输出前50个
        return f"{self.friend.character.name} - {self.friend.me.user.username} - {self.user_message[:50]} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"
# AI的系统提示词
class SystemPrompt(models.Model):
    title = models.CharField(max_length=100)
    order_number = models.IntegerField(default=0)
    prompt = models.TextField(max_length=10000)
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title} - {self.order_number} - {self.prompt[:50]} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"