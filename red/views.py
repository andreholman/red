import json
from time import time as epoch
from datetime import timedelta
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import Http404, HttpResponse
from django.core.mail import send_mail
from django.db import IntegrityError
from django.conf import settings as config

from .models import *

################################
#           INTERFACE          #
################################

def tos(request):
    return render(request, "red/tos.html")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    all_posts = Post.objects.order_by("-created").filter(deleted__isnull=True)
    context = {"latest_posts_list": all_posts}
    return render(request, "red/index.html", context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user(request, username):
    user = get_object_or_404(User, username__iexact=username)

    user_posts = Post.objects.filter(author__id=user.id, deleted__isnull=True).order_by("-created")
    user_comments = Comment.objects.filter(author__id=user.id, deleted__isnull=True).order_by("-created")

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
    
    comment_depth_list = [] # used by view to display in order
    comments = list(Comment.objects.filter(post=post))

    sort = request.GET.get("sort", "hot").lower() # default = hot
    match sort:
        case "new":
            comments = sorted(
                comments,
                key=lambda i: i.created,
                reverse=True
            )
        case "top":
            comments = sorted(
                comments,
                key=lambda i: i.likes-i.dislikes,
                reverse=True
            )
        case _: # hot
            comments = sorted(
                comments,
                key=lambda i: i.score(),
                reverse=True
            )
    unchecked_comments = comments # items will be popped! do not return

    def add_comment(comment, level):
        comment_depth_list.append({"comment": comment, "level": level})
    
    def check_children(comment, level):
        for c in unchecked_comments:
            if c.parent == comment:
                add_comment(c, level)
                check_children(c, level + 1)
                unchecked_comments.remove(c)
    
    top_level_comments = [c for c in comments if not c.parent]

    for c in top_level_comments:
        add_comment(c, 0)
        replies = [reply for reply in comments if reply.parent == c]
        if len(replies): # comment has children
            check_children(c, 1)
    
    context = {"post": post, "comments": comment_depth_list, "sorting": sort}
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

def password_changer(request, slug=None):
    match request.method:
        case "POST":
            try:
                if slug:
                    link_request = get_object_or_404(LinkOpenedRequest, url=slug, purpose="P")
                    if timezone.now() - link_request.created >= timedelta(hours=1):
                        link_request.delete()
                        return HttpResponse(status=410) # expired
                    password = str(json.loads(request.body)["password"])
                    
                    if len(password) != 64: # invalid password. should be a hash
                        return HttpResponse(status=400)
                    
                    link_request.user.set_password(password)
                    link_request.user.save()

                    link_request.delete()
                    return HttpResponse(status=204)
                else:
                    return HttpResponse(status=401)
            except (IndexError, json.decoder.JSONDecodeError):
                return HttpResponse(status=400)
        case "GET":
            if slug:
                link_request = get_object_or_404(LinkOpenedRequest, url=slug)

                context = {"verified": True, "username": link_request.user.username}
                if timezone.now() - link_request.created >= timedelta(hours=1):
                    link_request.delete()
                    context["expired"] = True
            else:
                context = {"verified": False}
            return render(request, "red/password_changer.html", context)
        case _:
            return HttpResponse(status=405)

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
    if not request.user.is_authenticated: # not logged in
        return HttpResponse(status=401)
    elif request.method == method.upper(): # correct method
        post_object = get_object_or_404(Post, id=post_id)
        if post_object.deleted:
            return HttpResponse(status=404) # already deleted
        elif post_author_required and post_object.author != request.user:
            return HttpResponse(status=403) # no perms
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
        else: # not liked yet or not voted
            add_like()
    elif direction == 0:
        if liked_already:
            remove_like()
            add_dislike()
        elif disliked_already:
            remove_dislike()
        else: # not disliked yet or not voted
            add_dislike()
    else: # no vote direction specified
        return HttpResponse(status=400)
    return HttpResponse(status=204)

def increase_user_points(content):
    try:
        print("Adding for " + str(content.vote_difference - 100) )
        content.author.points += config.ADDITIVE_KARMA[content.vote_difference + 100]
        content.author.save()
    except IndexError: pass

def decrease_user_points(content):
    try:
        content.author.points -= config.ADDITIVE_KARMA[content.vote_difference + 101]
        content.author.save()
    except IndexError: pass

########### ENDPOINTS ##########

def link_verified_request(request):
    if request.method == "POST":
        try:
            request_data = json.loads(request.body)

            if request_data["purpose"] == "P":
                title = "Red: Reset your password"
                body = "Click this link to verify your identity and reset your password: {}\nNot you? You can safely ignore this email."
            elif request_data["purpose"] == "E":
                title = "Red: Verify your email"
                body = "Click this link to confirm this email address: {}"
            else: # no valid purpose included
                return HttpResponse(status=400)

            user_object = get_object_or_404(User, email__iexact=request_data["email"])

            try:
                active_request = LinkOpenedRequest.objects.get(
                    user=user_object,
                    created__gte=(timezone.now() - timedelta(hours=1))
                )
                # ratelimit
                if active_request:
                    return HttpResponse(status=429)
            except LinkOpenedRequest.MultipleObjectsReturned:
                return HttpResponse(status=429) 
            except LinkOpenedRequest.DoesNotExist:
                ver = LinkOpenedRequest(
                    user=user_object,
                    purpose=request_data["purpose"]
                )
                ver.save() # generates ID from db
                slug = urlsafe_b64encode(sha512(str(ver.id + epoch()).encode()).digest()).decode()[:-2]

                ver.url = slug
                ver.save()

                email_response = send_mail(
                    title, 
                    body.format("https://red.andreholman.com" + reverse("password_changer", kwargs={"slug":slug})),
                    config.DEFAULT_FROM_EMAIL,
                    [request_data["email"]]
                )
                
                if email_response == 1:
                    return HttpResponse(status=204)
                else: # didn't work
                    return HttpResponse(status=503)
        except (KeyError, json.decoder.JSONDecodeError):
            return HttpResponse(status=400) 
    else:
        return HttpResponse(status=405)

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
        )
        new_post.save()

        request.user.liked_posts.add(new_post)

        return redirect(f"/s/{sub}/posts/{new_post.id}/") # redirect to new post
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
                
                increase_user_points(request_validated)
            
            def remove_like():
                request_validated.likes -= 1
                request_validated.save()

                request.user.liked_posts.remove(request_validated)

                decrease_user_points(request_validated)

            def add_dislike():
                request_validated.dislikes += 1
                request_validated.save()

                request.user.disliked_posts.add(request_validated)

                decrease_user_points(request_validated)

            def remove_dislike():
                request_validated.dislikes -= 1
                request_validated.save()

                request.user.disliked_posts.remove(request_validated)

                increase_user_points(request_validated)

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

        request.user.liked_comments.add(new_comment)
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
            
                increase_user_points(comment_object)

            def remove_like():
                comment_object.likes -= 1
                comment_object.save()

                request.user.liked_comments.remove(comment_object)
                
                decrease_user_points(comment_object)

            def add_dislike():
                comment_object.dislikes += 1
                comment_object.save()

                request.user.disliked_comments.add(comment_object)
                
                decrease_user_points(comment_object)

            def remove_dislike():
                comment_object.dislikes -= 1
                comment_object.save()

                request.user.disliked_comments.remove(comment_object)
            
                increase_user_points(comment_object)

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
            return HttpResponse(status=400)
        
        if request_validated != comment_object.post:
            return HttpResponse(status=404) # wrong post
        if comment_object.author != request.user:
            return HttpResponse(status=403) # not the comment owner

        comment_object.soft_delete()
        comment_object.save()
        return HttpResponse(status=204) # no response
    else:
        return request_validated
def award_content(request, sub, post_id):
    request_validated = validate_api_request(request, "POST", post_id)
    if type(request_validated) != HttpResponse:
        if request.user == request_validated.author:
            return HttpResponse(status=403) # can't gift yourself
        try:
            request_data = json.loads(request.body)
            award_type = request_data["type"]

            new_award = {
                "name": request.user.username,
                "time": round(epoch()),
                "anonymous": request_data["anonymous"] # bool
            }
            message = request_data["message"]
            if message:
                if len(message) > 64:
                    return HttpResponse(status=400)
                new_award["message"] = message
            
            cost = config.AWARDS_LIST[award_type]
            if request.user.coins <= cost:
                return HttpResponse(status=402) # can't afford the award
            else:
                request.user.coins -= cost
                request.user.save()

            comment_id = request_data.get("c")
            if comment_id:
                content = get_object_or_404(Comment, id=comment_id)
            else:
                content = request_validated
            
            current_count = content.awards.get(award_type)
            if current_count:
                content.awards[award_type].append()
            else:
                content.awards[award_type] = [new_award]
            content.save()

            return HttpResponse(status=204)
        except (KeyError, ValueError, json.decoder.JSONDecodeError): # invalid comment
            return HttpResponse(status=400)
    else:
        return request_validated