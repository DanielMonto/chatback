from django.urls import path
from ..users.views import UsersNoFavorites
from .views import (
                    MessagesGroupGetAPIView,
                    ConversationOneAPIView,
                    FavoritesUsersAPIView,
                    ConversationsAPIView,
                    GroupsAllAPIView,
                    MessagesAPIView,
                    AttempsAPIView,
                    GroupAPIView,
                    getGroup,
                    )

urlpatterns=[
    path('conversation/<str:conversation_name>/',ConversationOneAPIView.as_view()),
    path('messagesgroup/<str:groupname>/',MessagesGroupGetAPIView.as_view()),
    path('messages/<str:conversation_name>/',MessagesAPIView.as_view()),
    path('conversations/',ConversationsAPIView.as_view()),
    path('favorites/',FavoritesUsersAPIView.as_view()),
    path('nofavorites/',UsersNoFavorites.as_view()),
    path('allgroups/',GroupsAllAPIView.as_view()),
    path('attemps/',AttempsAPIView.as_view()),
    path('group/<str:groupname>/',getGroup),
    path('groups/',GroupAPIView.as_view()),
]