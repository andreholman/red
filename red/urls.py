from django.urls import path
from red import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.index, name="index"),
    path("u/<str:username>/", views.user, name="user"),
    path("s/<str:sub>/", views.sub, name="sub"),
    path("s/<str:sub>/p/<int:post_id>/", views.post, name="post"),
    path("s/<str:sub>/p/<int:post_id>/vote", views.post_vote, name="vote"),
    path("s/<str:sub>/p/<int:post_id>/update", views.update_post, name="update_post"),
    path("s/<str:sub>/p/<int:post_id>/delete", views.delete_post, name="delete_post"),
    path("s/<str:sub>/post", views.post_editor, name="post_editor"),
    path("s/<str:sub>/create_post", views.create_post, name="create_post"),
    path("login", views.login, name="login"),
] + staticfiles_urlpatterns()