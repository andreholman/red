from django.urls import path
from red import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("u/<str:username>/", views.user, name="user"),
    path("s/<str:sub>/", views.sub, name="sub"),
    path("s/<str:sub>/p/<int:post_id>/", views.post, name="post"),
    path("s/<str:sub>/post", views.post_editor, name="add_post"),
    path("s/<str:sub>/create_post", views.create_post, name="create_post"),
    path("update_post", views.update_post, name="update_post"),
    path("delete_post", views.delete_post, name="delete_post"),
    path("login", views.login, name="login"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)