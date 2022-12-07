import json
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import Http404, HttpResponse
from pprint import pprint

from .models import *

# view = category of web page that holds a specific template
# and serves a specific purpose

def index(request): # negative sign ahead makes it newest first
    all_posts = Post.objects.order_by("-created").filter(deleted__isnull=True)
    context = {"latest_posts_list": all_posts}
    return render(request, "red/index.html", context)

def user(request, username):
    user = get_object_or_404(User, username__iexact=username)

    user_posts = Post.objects.filter(author__id=user.id).order_by("-created")
    user_comments = Comment.objects.filter(author__id=user.id).order_by("-created")

    context = {'user': user, "user_posts": user_posts, "user_comments": user_comments}
    return render(request, 'red/user.html', context)

def sub(request, sub):
    sub_object = get_object_or_404(Sub, name__iexact=sub)
    
    # code under here not executed if 404 raised.
    sub_posts = Post.objects.filter(sub__id=sub_object.id, deleted__isnull=True).order_by("-created")

    context = {"sub": sub_object, "sub_posts": sub_posts}
    return render(request, "red/sub.html", context)

def sub_posts(request, sub): # For redirecting s/sub/posts 
    return redirect("sub", sub=sub)

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
    sub_flairs = PostFlair.objects.filter(sub__id=sub_object.id)

    context = {
        "sub": sub_object,
        "post_flairs": sub_flairs
    }
    return render(request, "red/post_editor.html", context=context)

def validate_endpoint_request(request, method, post_id):
    if request.method == method.upper():
        post_object = get_object_or_404(Post, id=post_id)
        if post_object.deleted:
            return 410 # already deleted
        else:
            return post_object
    else:
        return HttpResponse(status=405) # bad request format

def post_vote(request, sub, post_id):
    request_data = json.loads(request.body)
    if request_data and request.method == "POST": # checks if there's post request
        post_object = get_object_or_404(Post, id=post_id)
        try:
            if request_data["v"] == 1:
                post_object.likes += 1
                post_object.save()
            elif request_data["v"] == 0:
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
        try:
            post_flair_id = int(request.POST["flair"])
            post_flair = get_object_or_404(PostFlair, id=post_flair_id)
        except KeyError:
            post_flair = None

        new_post = Post(
            sub=sub_object,
            author=get_object_or_404(User, id=3),
            title=request.POST["title"],
            content=request.POST["content"],
            flair=post_flair,
            nsfw=bool(request.POST.get("nsfw")),
            spoiler=bool(request.POST.get("spoiler")),
            likes=1,
            points=1,
        )

        new_post.save()

        return redirect(f"/s/{sub}/posts/{new_post.id}") # redirect to new post
    else:
        return HttpResponse(status=405) # bad request format

def update_post(request, sub, post_id):
    if request.method == "PUT":
        request_data = json.loads(request.body)
        
        if request_data.get("content"):
            post_object = get_object_or_404(Post, id=post_id)
            if post_object.deleted:
                return HttpResponse(status=410)
            post_object.content = request_data["content"]
            post_object.edit()
            post_object.save()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=405) # bad request format
    # post_id = request.POST.get("id")

def delete_post(request, sub, post_id):
    if request.method == "POST":
        post_object = get_object_or_404(Post, id=post_id)
        if post_object.deleted:
            return HttpResponse(status=410) # already deleted
        else:
            post_object.soft_delete()
            post_object.save()
            return HttpResponse(status=204) # no response
    else:
        return HttpResponse(status=405) # bad request format

def create_comment(request, sub, post_id):
    request_validated = validate_endpoint_request(request, "POST", post_id)
    if type(request_validated) != HttpResponse: # post is returned back
        try:
            request_data = json.loads(request.body)

            if request_data.get("parent"):
                try:
                    comment_parent_id = int(request_data["parent"])
                except ValueError: # Not an int
                    return HttpResponse(status=400)
                
                if comment_parent_id == 0:
                    comment_parent = None
                else:
                    comment_parent = get_object_or_404(Comment, id=comment_parent_id)
                    
                    if comment_parent.post != request_validated:
                        return HttpResponse(status=400) # wrong post
            else:
                comment_parent = None
            
            comment_content = request_data["content"]
            comment_content[1]
        except (KeyError, IndexError): # index error means no content
            return HttpResponse(status=400) # bad request
        
        new_comment = Comment(
            post=request_validated,
            author=get_object_or_404(User, id=3),
            content=comment_content,
            parent=comment_parent,
            likes=1
        )
        new_comment.save()
        return HttpResponse(status=204) # no response
    else:
        return request_validated

def comment_vote(request, sub, post_id):
    request_status = validate_endpoint_request(request, "POST")
    if not request_status:
        pass
    else:
        return HttpResponse(status=request_status)

def update_comment(request, sub, post_id):
    request_status = validate_endpoint_request(request, "PUT")
    if not request_status:
        pass
    else:
        return HttpResponse(status=request_status)

def delete_comment(request, sub, post_id):
    request_status = validate_endpoint_request(request, "POST")
    if not request_status:
        pass
    else:
        return HttpResponse(status=request_status)


def login(request):
    return HttpResponse("login")