from django.db import models
import uuid
from django.db.models.signals import pre_save,pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

class UserOwnModel(AbstractUser):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created=models.DateTimeField(auto_now_add=True)
    attemps_groups=models.ManyToManyField(to='Group')
    favorites_users=models.ManyToManyField(to='UserOwnModel')
    attemps=models.ManyToManyField(to='AttempUserModel')
    class Meta:
        ordering=['-created']    

class AttempUserModel(models.Model):
    attemper=models.TextField()
    attemped=models.TextField()

class Group(models.Model):
    name=models.TextField(unique=True)
    integrants=models.ManyToManyField(UserOwnModel)
    creator=models.TextField(default='admin')

class AttempGroupModel(models.Model):
    group=models.TextField()
    gattemper=models.TextField()
    gattemped=models.TextField()

class Conversation(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created=models.DateTimeField(auto_now_add=True)
    user_1=models.ForeignKey(UserOwnModel,on_delete=models.SET_NULL,related_name='user_1_conversations',blank=True,null=True)
    user_2=models.ForeignKey(UserOwnModel,on_delete=models.SET_NULL,related_name='user_2_conversations',blank=True,null=True)
    name=models.TextField(unique=True,default='')
    class Meta:
        ordering=['-created']

@receiver(pre_delete,sender=UserOwnModel)
def set_favorites_at_deleting(sender,instance:UserOwnModel,**kwargs):
    # users
    users=UserOwnModel.objects.filter(favorites_users__in=[instance])
    for user in users:
        user.favorites_users.remove(instance)
        user.save()
    # conversations
    conversations=Conversation.objects.filter(models.Q(user_1=instance)|models.Q(user_2=instance))
    for conversation in conversations:
        if conversation.user_1==instance:
            try:
                user_2=UserOwnModel.objects.get(id=conversation.user_2.id)
            except Exception:
                conversation.delete()
        else:
            try:
                user_1=UserOwnModel.objects.get(id=conversation.user_1.id)
            except Exception:
                conversation.delete()
    # groups
    groups=Group.objects.filter(integrants__in=[instance])
    for i in groups:
        inte=0
        for user in i.integrants.values_list('username',flat=True):
            inte+=1
        if inte==0:
            i.delete()
                
@receiver(pre_save,sender=Conversation)
def set_users_for_a_conversation(sender, instance:Conversation, **kwargs):
    instance.user_1=UserOwnModel.objects.get(username=instance.name.split('_')[0])
    instance.user_2=UserOwnModel.objects.get(username=instance.name.split('_')[1])

class Message(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created=models.DateTimeField(auto_now_add=True)
    conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE,blank=True,null=True)
    group=models.ForeignKey(Group,on_delete=models.CASCADE,blank=True,null=True)
    writer_name=models.TextField()
    url=models.URLField(blank=True,null=True)
    kind=models.TextField(default='text')
    text=models.TextField()
    class Meta:
        ordering=['-created']