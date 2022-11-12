from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from pprint import pprint

from .models import *

# view = category of web page that holds a specific template
# and serves a specific purpose

def home(request): # negative sign ahead makes it newest first
    all_posts = Post.objects.order_by("-created")
    context = {"latest_posts_list": all_posts}
    return render(request, "red/index.html", context)

def user(request, username):
    user = get_object_or_404(User, username__iexact=username)

    user_posts = Post.objects.filter(author__id=user.id).order_by("-created")
    user_comments = Comment.objects.filter(author__id=user.id).order_by("-created")

    context = {'user': user, "user_posts": user_posts, "user_comments": user_comments}
    return render(request, 'red/user.html', context)

def sub(request, sub):
    sub = get_object_or_404(Sub, name__iexact=sub)
    
    # code under here not executed if 404 raised.
    sub_posts = Post.objects.filter(sub__id=sub.id).order_by("-created")

    context = {"sub": sub, "sub_posts": sub_posts}
    return render(request, "red/sub.html", context)

def post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    comment_depth_list = [] # used by django view to display
    comments = Comment.objects.order_by("-created")
    top_level_comments = comments.filter(post__id=int(post.id), parent__id=None)

    def add_comment(comment, level):
        comment_depth_list.append({"comment": comment, "level": level})

    def check_children(comment, level):
        responses = comments.filter(parent__id=comment.id)
        print("= checking children for " + str(comment))
        for response in responses:
            print(f"+ appended level {level} comment: {str(response)}")
            add_comment(response, level)
            if len(responses): # comment has children
                check_children(response, level + 1)
        
    for comment in top_level_comments:
        print(f"+ appended level {0} comment: {str(comment)}")
        add_comment(comment, 0)
        replies = comments.filter(parent__id=comment.id)
        if len(replies): # comment has children
            check_children(comment, 1)
            
    pprint(comment_depth_list, indent=0)

    context = {"post": post, "comments": comment_depth_list}
    return render(request, "red/post.html", context)

def login(request):
    return HttpResponse("login")