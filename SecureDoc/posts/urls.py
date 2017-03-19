from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'posts'

urlpatterns = [
    url(r'^create/', views.create, name="create"),
    url(r'^post/(?P<post_id>[0-9]+)/$', views.post_detail, name="post_detail"),
    url(r'^update/', views.update, name="update"),
    url(r'^revoke/', views.revoke, name="revoke"),
    url(r'^update_nominated/', views.update_nominated, name="update_nominated"),
    url(r'^view/(?P<post_id>[0-9]+)/$', views.view, name="view"),
    url(r'^share_editing/', views.share_editing, name="share_editing"),
    url(r'^share_viewing/', views.share_viewing, name="share_viewing"),
    url(r'^generate_pdf/', views.generate_pdf, name="generate_pdf"),
    url(r'^generate_doc/', views.generate_doc, name="generate_doc"),
    url(r'^download_pdf/', views.download_pdf, name="download_pdf"),
    url(r'^download_doc/', views.download_pdf, name="download_doc"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)