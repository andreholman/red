from django.urls import path
from red import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("u/<str:username>/", views.user, name="user"),
    path("s/<str:sub>/", views.sub, name="sub"),
    path("p/<int:post_id>/", views.post, name="post"),
    path("login", views.login, name="login"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)