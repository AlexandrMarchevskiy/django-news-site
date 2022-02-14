from django.urls import path
from django.views.decorators.cache import cache_page
from .views import *


urlpatterns = [
    path('', cache_page(60) (NewsHome.as_view()), name='home'),
    path('about/', about, name='about'),
    path('addpage/', AddPage.as_view(), name='add_page'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('post/<slug:post_slug>/', showpost, name='post'),
    path('category/<slug:cat_slug>/', NewsCategory.as_view(), name='category'),
]

