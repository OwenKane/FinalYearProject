from django.conf.urls import url, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'friends'

urlpatterns = [
    url(r'^view_friends/', views.view_friends, name="view_friends"),
    url(r'^delete_friend/', views.delete_friend, name="delete_friend"),
    url(r'^confirm_friend/', views.confirm_friend, name="confirm_friend"),
    url(r'^deny_friend/', views.deny_friend, name="deny_friend"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)