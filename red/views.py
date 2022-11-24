import json
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse
from pprint import pprint

from .models import *

# view = category of web page that holds a specific template
# and serves a specific purpose

def index(request): # negative sign ahead makes it newest first
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

def post(request, sub, post_id):
    post = get_object_or_404(Post, id=post_id)
    if sub != post.sub.name:
        raise Http404("Post does not exist in this sub.")
    
    comment_depth_list = [] # used by django view to display
    comments = Comment.objects.order_by("-created")
    top_level_comments = comments.filter(post__id=int(post.id), parent__id=None)

    def add_comment(comment, level):
        comment_depth_list.append({"comment": comment, "level": level})

    def check_children(comment, level):
        responses = comments.filter(parent__id=comment.id)
        for response in responses:
            add_comment(response, level)
            if len(responses): # comment has children
                check_children(response, level + 1)
        
    for comment in top_level_comments:
        add_comment(comment, 0)
        replies = comments.filter(parent__id=comment.id)
        if len(replies): # comment has children
            check_children(comment, 1)

    context = {"post": post, "comments": comment_depth_list}
    return render(request, "red/post.html", context)

def post_editor(request, sub):
    sub_object = get_object_or_404(Sub, name__iexact=sub)
    post_flairs = PostFlair.objects.filter(sub__id=sub_object.id)

    context = {"sub": sub_object, "post_flairs": post_flairs}
    return render(request, "red/post_editor.html", context=context)

def post_vote(request, sub, post_id):
    post_data = json.loads(request.body)
    print(post_data)
    if post_data: # checks if there's post request
        post_object = get_object_or_404(Post, id=post_id)
        try:
            if post_data["v"] == 1:
                post_object.likes += 1
                post_object.save()
            elif post_data["v"] == 0:
                post_object.dislikes += 1
                post_object.save()
            else: 
                return HttpResponse(status=400) # bad request
        except:
            return HttpResponse(status=400)
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=405) # bad request format

def create_post(request, sub):
    if request.method == "POST": # checks if there's post request
        sub_object = get_object_or_404(Sub, name__iexact=sub)
        post_flair_id = int(request.POST.get("flair"))
        post_flair = get_object_or_404(PostFlair, id=post_flair_id)
        
        new_post = Post(
            sub=sub_object,
            author=get_object_or_404(User, id=3),
            title=request.POST["title"],
            content=request.POST["content"],
            flair=post_flair,
            views=0,
            likes=0,
            dislikes=0,
            points=0
        )

        new_post.save()

        return HttpResponse(status=204) # no response
    else:
        return HttpResponse(status=405) # bad request format

def update_post(request, sub, post):
    # post_id = request.POST.get("id")
    return HttpResponse(status=204)

def delete_post(request, sub, post):
    return

def login(request):
    return HttpResponse("login")