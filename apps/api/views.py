from rest_framework_simplejwt.tokens import AccessToken
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist

from ..models_app.serializers import (
                                        ConversationSerializer,
                                        AttempGroupSerializer,
                                        MessageSerializer,
                                        AttempSerializer,
                                        AttempGroupModel,
                                        GroupSerializer,
                                        AttempUserModel,
                                        UserSerializer,
                                        UserOwnModel,
                                        Conversation,
                                        Message,
                                        Group,
                                    )

def get_user(request):
    user=UserOwnModel.objects.get(id=AccessToken(request.META['HTTP_AUTHORIZATION'].split(' ')[1]).payload['user']['id'])
    return user

# users

class FavoritesUsersAPIView(APIView):
    # get yours favorites users or friend that you accepted in attemps
    def get(self,request):
        user=get_user(request)
        favorites=UserSerializer(user.favorites_users.all(),many=True).data
        return Response(favorites,status=200)
    # add a user that attemped you to favorite users
    def post(self,request):
        user=get_user(request)
        user_2=UserOwnModel.objects.get(username=request.data['username_add'])
        user.favorites_users.add(user_2)
        user_2.favorites_users.add(user)
        user_2.attemps.remove(user)
        attemp=AttempUserModel.objects.filter(attemper=user_2,attemped=user)
        attemp.delete()
        return Response({'all':'fine'},status=200)
    # remove a user from your favorite user list
    def delete(self,request):
        user=get_user(request)
        user_2=UserOwnModel.objects.get(username=request.data['username_delete'])
        user.favorites_users.remove(user_2)
        user_2.favorites_users.remove(user)
        try:
            conversation=Conversation.objects.get(name=f'{user.username}_{user_2.username}')
        except Exception:
            try:
                conversation=Conversation.objects.get(name=f'{user_2.username}_{user.username}')
                # dont forget add the delete of the files of firebase since the model of message bro 
                conversation.delete()
            except Exception:
                False
        return Response({f'{user_2.username}':'removed from favorite uses'},status=200)

class AttempsAPIView(APIView):
    # get all the attemps that users have sended to you
    def get(self,request):
        user=get_user(request)
        serializer=AttempSerializer(user.attemps.all(),many=True).data
        return Response(serializer,status=200)
    # add an attemp from you to another user
    def post(self,request):
        user=get_user(request)
        user_2=UserOwnModel.objects.get(username=request.data['username_add'])
        attemp=AttempUserModel(attemper=user,attemped=user_2)
        attemp.save()
        user_2.attemps.add(attemp)
        return Response({"all":"fine"},status=200)
    # get all the attemps that you sended to others users
    def put(self,request):
        user=get_user(request)
        attemps_from_me=AttempUserModel.objects.filter(attemper=user)
        serializer=AttempSerializer(attemps_from_me,many=True).data
        return Response(serializer,status=200)
    def delete(self,request):
        attemped=request.data['attemped']
        attemper=request.data['attemper']
        attemp=AttempUserModel.objects.filter(attemped=attemped,attemper=attemper)
        attemp.delete()
        return Response({'all':'fine'},status=200)

# conversations

class ConversationsAPIView(APIView):
    # create a new conversation with other user
    def post(self,request):
        user=get_user(request)
        username_2=request.data['username_2']
        conversation=Conversation(name=f'{user.username}_{username_2}')
        conversation.save()
        serializer=ConversationSerializer(conversation,many=False)
        return Response(serializer.data,status=200)

class ConversationOneAPIView(APIView):
    # get a conversation by its name an thrw and 400 if it does not exist
    def get(self,request,conversation_name):
        try:
            conversation=Conversation.objects.get(name=conversation_name)
            serializer=ConversationSerializer(conversation,many=False)
            return Response(serializer.data,status=200)
        except ObjectDoesNotExist:
            return Response({'that conversation':'does not exist'},status=400)
               
# messages        
        
class MessagesAPIView(APIView):
    # get all the messages from a conversation
    def get(self,request,conversation_name):
        conversation=Conversation.objects.get(name=conversation_name)
        messages=Message.objects.filter(conversation=conversation)
        serializer=MessageSerializer(messages,many=True)
        return Response(serializer.data,status=200)
    
# groups
    
class GroupAPIView(APIView):
    # get all the groups where you are in
    def get(self,request):
        user=get_user(request)
        groups=Group.objects.filter(integrants__in=[user])
        serializer=GroupSerializer(groups,many=True).data
        return Response(serializer)
    # create a new group and if there is another with the same name throw a 400
    def post(self,request):
        user=get_user(request)
        group_name=request.data['name']
        try:
            group=Group(name=group_name,creator=user.username)
            group.save()
            group.integrants.add(user)
            return Response(GroupSerializer(group,many=False).data,status=200)
        except IntegrityError:
            return Response({'error':'unique'},status=400)
    # get you out from a group and delete it if there is no more users in there
    def delete(self,request):
        user=get_user(request)
        group=Group.objects.get(name=request.data['name'])
        group.integrants.remove(user)
        if len(group.integrants)<=0:
            group.delete()
        return Response({'group':'escaped'})
    # add your user to a group
    def put(self,request):
        user=get_user(request)
        group=Group.objects.get(name=request.data['name'])
        group.integrants.add(user)
        attemps=AttempGroupModel.objects.filter(gattemped=user.username,group=group)
        attemps.delete()
        return Response({'user':'added'})
class GroupsAllAPIView(APIView):
    # get the attempeds that groups have made to you
    def get(self,request):
        user=get_user(request)
        attemps=AttempGroupModel.objects.filter(attemped=user.username)
        serializer=AttempGroupSerializer(attemps,many=True).data
        return Response(serializer,status=200)
    # make a attemp to an user for joining to the group
    def post(self,request):
        user=get_user(request)
        attemp_group=AttempGroupModel(group=request.data['group'],gattemped=request.data['user'],gattemper=user.username)
        attemp_group.save()
        serializer=AttempGroupSerializer(attemp_group,many=False).data
        return Response(serializer,status=200)
    # delete an attemp from a group-user
    def delete(self,request):
        attemped=request.data['gattemped']
        attemper=request.data['gattemper']
        group=request.data['group']
        attemp_group=AttempGroupModel.objects.filter(gattemped=attemped,gattemper=attemper,group=group)
        attemp_group.delete()
        return Response({'all':'fine'},status=200)
    # get the attemps groups that you´ve made to others
    def put(self,request):
        user=get_user(request)
        attemps=AttempGroupModel.objects.filter(attemper=user.username)
        serializer=AttempGroupSerializer(attemps,many=True).data
        return Response(serializer,status=200)

@api_view(['GET'])
def getGroup(request,groupname):
    group=Group.objects.get(name=groupname)
    serializer=GroupSerializer(group,many=False).data
    serializer['numbers']=len(group.integrants.all())
    return Response(serializer,status=200)

class MessagesGroupGetAPIView(APIView):
    # get the messages from a group
    def get(self,request,groupname):
        group_messages=Group.objects.get(name=groupname)
        messages=Message.objects.filter(group=group_messages)
        return Response(MessageSerializer(messages,many=True).data)