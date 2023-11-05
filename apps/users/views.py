from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpRequest
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from ..models_app.models import UserOwnModel,AttempUserModel
from django.contrib.auth.hashers import make_password
from ..models_app.serializers import UserSerializer,MyTokenObtainPairSerializer,Group,AttempGroupModel
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.exceptions import ObjectDoesNotExist

def get_user(request):
    user=UserOwnModel.objects.get(id=AccessToken(request.META['HTTP_AUTHORIZATION'].split(' ')[1]).payload['user']['id'])
    return user

def filter_users(request,is_for_group=False,group_name=''):
    user=get_user(request)
    if is_for_group:
        group=Group.objects.get(name=group_name)
        gipk=group.integrants.values_list('id',flat=True)
        ufbygi=UserOwnModel.objects.exclude(id__in=gipk)
        ag=AttempGroupModel.objects.filter(group=group.name)
        atdag=ag.values_list('attemped',flat=True)
        uf=ufbygi.exclude(username__in=atdag)
        return uf
    else:
        usernames_favorites=user.favorites_users.values_list('id',flat=True)
        no_favorites=UserOwnModel.objects.exclude(id__in=usernames_favorites)
        attemps_from_me=AttempUserModel.objects.filter(attemper=user)
        attdusnm=attemps_from_me.values_list('attemped',flat=True)
        ft=no_favorites.exclude(username__in=attdusnm)
        attemps_to_me=AttempUserModel.objects.filter(attemped=user)
        attrusnm=attemps_to_me.values_list('attemper',flat=True)
        filtereds=ft.exclude(username__in=attrusnm)
        return filtereds

# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes=[AllowAny]
    serializer_class=MyTokenObtainPairSerializer
    def post(self,request:HttpRequest):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = UserOwnModel.objects.get(username=username)
            if user.check_password(password):
                return super().post(request)
            else:
                return Response('contraseña incorrecta',status=400)
        except ObjectDoesNotExist:
            return Response('no existe el usuario',status=404)
    def delete(self,request):
        user=get_user(request)
        user.delete()
        return Response({'self':'deleted'})

class Users(APIView):
    permission_classes=[AllowAny]
    def post(self,request:HttpRequest):
        try:
            user=UserOwnModel.objects.get(username=request.data['username'])
            return Response('nombre de usuario en uso',status=405)
        except ObjectDoesNotExist:
            user=UserOwnModel(username=request.data['username'],password=make_password(request.data['password']))
            user.save()
            serializer=UserSerializer(user,many=False)
            return Response(serializer.data)
    def get(self,request):
        return Response({'hello':'world'})
class UsersNoFavorites(APIView):
    def get(self,request):
        filtereds=filter_users(request)
        serializer=UserSerializer(filtereds,many=True).data
        return Response(serializer,status=200)
    def post(self,request):
        group_name=request.data['groupname']
        username_searched=request.data['find']
        if username_searched=='* *':
            filtereds=filter_users(request,isForGroup=True,group_name=group_name)
        else:
            filtereds=filter_users(request,isForGroup=True,group_name=group_name).filter(username__icontains=username_searched)
        serializer=UserSerializer(filtereds,many=True).data
        return Response(serializer,status=200)
    def put(self,request):
        username_searched=request.data['find']
        if username_searched=='* *':
            filtereds=filter_users(request)
        else:
            filtereds=filter_users(request).filter(username__icontains=username_searched)
        serializer=UserSerializer(filtereds,many=True).data
        return Response(serializer,status=200)
    