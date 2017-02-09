from django.conf.urls import url, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'accounts'

urlpatterns = [
    url(r'^signup/', views.signup, name="signup"),
    url(r'^profile/', views.profile, name="profile"),
    url(r'^login/', views.loginview, name="login"),
    url(r'^logout/', views.logoutview, name="logout"),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
