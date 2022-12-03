from django.urls import path
from red import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.index, name="index"), # GET
    path("u/<str:username>/", views.user, name="user"), # GET
    path("s/<str:sub>/", views.sub, name="sub"), # GET
    path("s/<str:sub>/posts/", views.sub_posts, name="sub_posts"), # GET 303
    path("s/<str:sub>/posts/<int:post_id>/", views.post, name="post"), # GET
    path("s/<str:sub>/posts/<int:post_id>/vote/", views.post_vote, name="vote"), # POST
    path("s/<str:sub>/posts/<int:post_id>/update/", views.update_post, name="update_post"), # GET
    path("s/<str:sub>/posts/<int:post_id>/delete/", views.delete_post, name="delete_post"), # POST
    path("s/<str:sub>/post/", views.post_editor, name="post_editor"), # GET
    path("s/<str:sub>/create_post/", views.create_post, name="create_post"), # POST
    # path("login", views.login, name="login"), # this will be used later
] + staticfiles_urlpatterns() # serve statics