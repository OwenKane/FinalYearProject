from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'posts'

urlpatterns = [
    url(r'^create/', views.create, name="create"),
    url(r'^post/(?P<post_id>[0-9]+)/$', views.post_detail, name="post_detail"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

