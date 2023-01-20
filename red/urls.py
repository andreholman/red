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
    path("s/<str:sub>/posts/<int:post_id>/vote/", views.post_vote, name="post_vote"), # PATCH
    path("s/<str:sub>/posts/<int:post_id>/update/", views.update_post, name="update_post"), # PUT
    path("s/<str:sub>/posts/<int:post_id>/delete/", views.delete_post, name="delete_post"), # DELETE
    path("s/<str:sub>/posts/<int:post_id>/comment/", views.create_comment, name="create_comment"), # POST
    path("s/<str:sub>/posts/<int:post_id>/commentvote/", views.comment_vote, name="comment_vote"), # PATCH
    path("s/<str:sub>/posts/<int:post_id>/commentupdate/", views.update_comment, name="update_comment"), # PUT
    path("s/<str:sub>/posts/<int:post_id>/commentdelete/", views.delete_comment, name="delete_comment"), # DELETE
    path("s/<str:sub>/posts/<int:post_id>/award/", views.award_content, name="award_content"), # POST
    path("s/<str:sub>/post/", views.post_editor, name="post_editor"), # GET
    path("s/<str:sub>/create_post/", views.create_post, name="create_post"), # POST
    path("createaccount/", views.create_account, name="signup"), # POST
    path("login/", views.login, name="login"), # GET, POST
    path("logout/", views.logout, name="logout"), # POST
] + staticfiles_urlpatterns() # serve statics