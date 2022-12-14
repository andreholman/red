import json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import Http404, HttpResponse
from django.db import IntegrityError

from .models import *

################################
#           INTERFACE          #
################################

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    all_posts = Post.objects.order_by("-created").filter(deleted__isnull=True)
    context = {"latest_posts_list": all_posts}
    return render(request, "red/index.html", context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user(request, username):
    user = get_object_or_404(User, username__iexact=username)

    user_posts = Post.objects.filter(author__id=user.id).order_by("-created")
    user_comments = Comment.objects.filter(author__id=user.id).order_by("-created")

    context = {'account': user, "account_posts": user_posts, "account_comments": user_comments}
    return render(request, 'red/user.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sub(request, sub):
    sub_object = get_object_or_404(Sub, name__iexact=sub)
    
    # code under here not executed if 404 raised.
    sub_posts = Post.objects.filter(sub__id=sub_object.id, deleted__isnull=True).order_by("-created")

    context = {"sub": sub_object, "sub_posts": sub_posts}
    return render(request, "red/sub.html", context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sub_posts(request, sub): # For redirecting s/sub/posts 
    return redirect("sub", sub=sub)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def post_editor(request, sub):
    sub_object = get_object_or_404(Sub, name__iexact=sub)
    sub_flairs = PostFlair.objects.filter(sub__id=sub_object.id)

    context = {
        "sub": sub_object,
        "post_flairs": sub_flairs
    }
    return render(request, "red/post_editor.html", context=context)

################################
#             AUTH             #
################################

def login(request):
    match request.method:
        case "POST":
            try:
                request_data = json.loads(request.body)
                user = authenticate(
                    request,
                    username=request_data["username"],
                    password=request_data["password"]
                )

                if user is not None:
                    auth_login(request, user)
                    # Redirect to a success page.
                    return HttpResponse(status=204)
                else: # invalid login
                    return HttpResponse(status=403)
            except (json.decoder.JSONDecodeError, IndexError):
                return HttpResponse(status=400)
        case "GET":
            return render(request, "red/login.html")
        case _:
            return HttpResponse(status=405)

def create_account(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)
            new_user = User.objects.create_user(
                request_data["username"],
                request_data["email"],
                request_data["password"]
            )
            login(request)
        except (json.decoder.JSONDecodeError):
            return HttpResponse(status=400)
        except IntegrityError:
            return HttpResponse(status=403)
        print(request_data)
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=405)

def logout(request):
    if request.method == "POST":
        auth_logout(request)
        return HttpResponse(status=204)

################################
#             API              #
################################

####### HELPER FUNCTIONS #######

def validate_api_request(request, method, post_id, post_author_required=False): 
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    elif request.method == method.upper(): # correct method
        post_object = get_object_or_404(Post, id=post_id)
        if post_object.deleted:
            return HttpResponse(status=404) # already deleted
        elif post_author_required and post_object.author != request.user:
            return HttpResponse(status=403)
        else:
            return post_object
    else:
        return HttpResponse(status=405) # bad request format

def execute_vote(direction, liked_already, disliked_already, add_like, remove_like, add_dislike, remove_dislike):
    if direction == 1:
        if disliked_already:
            remove_dislike()
            add_like()
        elif liked_already:
            remove_like()
        else: # not liked yet
            add_like()
    elif direction == 0:
        if liked_already:
            remove_like()
            add_dislike()
        elif disliked_already:
            remove_dislike()
        else: # not disliked yet
            add_dislike()
    else: # no vote direction specified
        return HttpResponse(status=400)
    return HttpResponse(status=204)

########### ENDPOINTS ##########

@login_required
def create_post(request, sub):
    if request.method == "POST": # checks if there's post request
        sub_object = get_object_or_404(Sub, name__iexact=sub)
        try:
            post_flair_id = int(request.POST["flair"])
            post_flair = get_object_or_404(PostFlair, id=post_flair_id)
        except KeyError:
            post_flair = None
        
        if not request.POST["title"] or not request.POST["content"]:
            return HttpResponse(status=400)

        new_post = Post(
            sub=sub_object,
            author=request.user,
            title=request.POST["title"],
            content=request.POST["content"],
            flair=post_flair,
            nsfw=bool(request.POST.get("nsfw")),
            spoiler=bool(request.POST.get("spoiler")),
            likes=1, # auto like own posts
            points=1,
        )
        new_post.save()

        request.user.liked_posts.add(new_post)

        return redirect(f"/s/{sub}/posts/{new_post.id}") # redirect to new post
    else:
        return HttpResponse(status=405) # bad request format

def post_vote(request, sub, post_id):
    request_validated = validate_api_request(request, "PATCH", post_id)
    if type(request_validated) != HttpResponse:
        try:
            request_data = json.loads(request.body)

            if str(request_validated.sub) != sub:
                return HttpResponse(status=404)
            
            def add_like():
                request_validated.likes += 1
                request_validated.save()

                request.user.liked_posts.add(request_validated)
            
            def remove_like():
                request_validated.likes -= 1
                request_validated.save()

                request.user.liked_posts.remove(request_validated)
            
            def add_dislike():
                request_validated.dislikes += 1
                request_validated.save()

                request.user.disliked_posts.add(request_validated)
            
            def remove_dislike():
                request_validated.dislikes -= 1
                request_validated.save()

                request.user.disliked_posts.remove(request_validated)

            liked_already = request.user.liked_posts.filter(id=request_validated.id).exists()
            disliked_already = request.user.disliked_posts.filter(id=request_validated.id).exists()

            return execute_vote(request_data["v"], liked_already, disliked_already, add_like, remove_like, add_dislike, remove_dislike)
        except (KeyError, json.decoder.JSONDecodeError):
            return HttpResponse(status=400)
    else:
        return request_validated

def update_post(request, sub, post_id):
    request_validated = validate_api_request(request, "PUT", post_id, True)
    if type(request_validated) != HttpResponse:
        try:
            request_data = json.loads(request.body)
        
            if str(request_validated.sub) != sub:
                return HttpResponse(status=404)

            request_validated.content = request_data["content"]
            request_validated.edit()
            request_validated.save()
            return HttpResponse(status=204)
        except (KeyError, json.decoder.JSONDecodeError):
            return HttpResponse(status=400)
    else:
        return request_validated

def delete_post(request, sub, post_id):
    request_validated = validate_api_request(request, "DELETE", post_id, True)
    if type(request_validated) != HttpResponse:
        request_validated.soft_delete()
        request_validated.save()
        return HttpResponse(status=204) # no response
    else:
        return request_validated # bad request format

def create_comment(request, sub, post_id):
    request_validated = validate_api_request(request, "POST", post_id)
    if type(request_validated) != HttpResponse:
        try:
            request_data = json.loads(request.body)

            if request_data.get("parent"):
                comment_parent_id = int(request_data["parent"])
                
                if comment_parent_id == 0:
                    comment_parent = None
                else:
                    comment_parent = get_object_or_404(Comment, id=comment_parent_id)
                    
                    if comment_parent.deleted:
                        return HttpResponse(status=404)
                    elif comment_parent.post != request_validated:
                        return HttpResponse(status=400) # wrong post or deleted parent
            else:
                comment_parent = None
            
            comment_content = request_data["content"]
            comment_content[0]
        except (KeyError, IndexError, ValueError, json.decoder.JSONDecodeError): # index error means no content
            return HttpResponse(status=400) # bad request
        
        new_comment = Comment(
            post=request_validated,
            author=request.user,
            content=comment_content,
            parent=comment_parent,
            likes=1
        )
        new_comment.save()
        return HttpResponse(status=204) # no response
    else:
        return request_validated

def comment_vote(request, sub, post_id):
    request_validated = validate_api_request(request, "PATCH", post_id)
    if type(request_validated) != HttpResponse:
        try:
            request_data = json.loads(request.body)
            comment_object = get_object_or_404(Comment, id=request_data["c"])

            if comment_object.post.id != request_validated.id:
                return HttpResponse(status=404)

            def add_like():
                comment_object.likes += 1
                comment_object.save()

                request.user.liked_comments.add(comment_object)
            
            def remove_like():
                comment_object.likes -= 1
                comment_object.save()

                request.user.liked_comments.remove(comment_object)
            
            def add_dislike():
                comment_object.dislikes += 1
                comment_object.save()

                request.user.disliked_comments.add(comment_object)
            
            def remove_dislike():
                comment_object.dislikes -= 1
                comment_object.save()

                request.user.disliked_comments.remove(comment_object)
            
            liked_already = request.user.liked_comments.filter(id=comment_object.id).exists()
            disliked_already = request.user.disliked_comments.filter(id=comment_object.id).exists()

            return execute_vote(request_data["v"], liked_already, disliked_already, add_like, remove_like, add_dislike, remove_dislike)
        except (KeyError, IndexError, json.decoder.JSONDecodeError):
            return HttpResponse(status=400) # improper format 
    else:
        return request_validated

def update_comment(request, sub, post_id):
    request_validated = validate_api_request(request, "PUT", post_id)
    if type(request_validated) != HttpResponse:
        try:
            request_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return HttpResponse(status=400)
        
        if len(request_data.get("content")) >= 1 and request_data.get("c"):
            try:
                comment_object = get_object_or_404(Comment, id=request_data["c"])
            except ValueError: # invalid comment
                return HttpResponse(status=400)

            if request_validated != comment_object.post:
                return HttpResponse(status=404) # wrong post
            if comment_object.author != request.user:
                return HttpResponse(status=403) # not the comment owner
            
            comment_object.content = request_data["content"]
            comment_object.edit()
            comment_object.save()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)
    else:
        return request_validated

def delete_comment(request, sub, post_id):
    request_validated = validate_api_request(request, "DELETE", post_id)
    if type(request_validated) != HttpResponse:
        try:
            request_data = json.loads(request.body)
            comment_object = get_object_or_404(Comment, id=request_data.get("c"))
        except (ValueError, json.decoder.JSONDecodeError): # invalid comment
            return HttpResponse(400)
        
        if request_validated != comment_object.post:
            return HttpResponse(404) # wrong post
        if comment_object.author != request.user:
            return HttpResponse(status=403) # not the comment owner

        comment_object.soft_delete()
        comment_object.save()
        return HttpResponse(status=204) # no response
    else:
        return request_validated