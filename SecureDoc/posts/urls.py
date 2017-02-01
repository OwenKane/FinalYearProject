from django.conf.urls import url
from . import views

app_name = 'posts'

urlpatterns = [
    url(r'^create/', views.create, name="create"),
    url(r'^post/(?P<post_id>[0-9]+)/$', views.post_detail, name="post_detail"),
]

