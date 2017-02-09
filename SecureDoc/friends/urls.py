from django.conf.urls import url, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'friends'

urlpatterns = [
    url(r'^view_friends/', views.view_friends, name="view_friends"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
