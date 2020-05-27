from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('hashtag/', views.HashtagView.as_view(), name='hashtag'),
    path('detailcheck/', views.DetailCheckView.as_view(), name='detailcheck'),
    # path('get_username/', views.get_username, name='get_username'),
    path('get_past_posts/', views.get_past_posts, name='get_past_posts'),
    path('info/', views.info, name='info'),
    path('shpion/', views.ShpionView.as_view(), name='shpion'),
    path('secondary/', views.SecondaryUserView.as_view(), name='secondary'),
path('blacklist/', views.BlackListView.as_view(), name='blacklist'),
path('parse/', views.parse, name='parse'),
path('parse_users/', views.parse_users, name='parse_users'),

]

