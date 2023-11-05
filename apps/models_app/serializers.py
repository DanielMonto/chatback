from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserOwnModel,Conversation,Message,Group,AttempUserModel,AttempGroupModel

class GroupSerializer(ModelSerializer):
    class Meta:
        model=Group
        fields='__all__'
        
class AttempSerializer(ModelSerializer):
    class Meta:
        model=AttempUserModel
        fields='__all__'
        
class AttempGroupSerializer(ModelSerializer):
    class Meta:
        model=AttempGroupModel
        fields='__all__'
        
class UserSerializer(ModelSerializer):
    class Meta:
        model=UserOwnModel
        fields='__all__'
        
class ConversationSerializer(ModelSerializer):
    class Meta:
        model=Conversation
        fields='__all__'
        
class MessageSerializer(ModelSerializer):
    class Meta:
        model=Message
        fields='__all__'
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user:UserOwnModel):
        token=super().get_token(user)
        token['user']={
            'id':str(user.id),
            'username':user.username,
            'is_staff':user.is_staff}
        return token