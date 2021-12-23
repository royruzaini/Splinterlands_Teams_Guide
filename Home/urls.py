from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('getcard/',views.Api.get_cards, name='get-my-card'),
    path('life/',views.Api.getteamwhite, name='get-team-white'),
    path('death/',views.Api.getteamblack, name='get-team-black'),
    path('water/',views.Api.getteamblue, name='get-team-blue'),
    path('fire/',views.Api.getteamred, name='get-team-red'),
    path('earth/',views.Api.getteamgreen, name='get-team-green'),
    path('dragon/',views.Api.getteamgold, name='get-team-gold')
]