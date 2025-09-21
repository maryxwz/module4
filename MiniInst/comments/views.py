from django.apps import apps
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.db.models import Prefetch

from .models.comment import Comment
from .profanity import contains_profanity  # ← ДОБАВЛЕНО

Post = apps.get_model('posts', 'Post')


def _is_owner(request, user_id: int) -> bool:
    return request.user.is_authenticated and request.user.id == user_id


def _serialize_comment(c, request, include_replies=False, replies_qs=None):
    avatar = None
    try:
        if getattr(c.author, "avatar", None):
            avatar = c.author.avatar.url
    except Exception:
        avatar = None

    data = {
        "id": c.id,
        "author": c.author.username,
        "author_url": f"/users/profile/{escape(c.author.username)}",
        "avatar": avatar,
        "text": c.text,
        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
        "is_owner": _is_owner(request, c.author_id),
        "replies_count": getattr(c, "replies_count", None) or c.replies.filter(is_deleted=False).count(),
    }

    if include_replies:
        replies = replies_qs if replies_qs is not None else c.replies.select_related("author").filter(is_deleted=False).order_by("created_at")
        data["replies"] = [
            _serialize_comment(r, request, include_replies=False) for r in replies
        ]

    return data


@require_http_methods(["GET", "POST"])
def api_comments(request):
    if request.method == "GET":
        post_id = request.GET.get("post_id")
        if not post_id:
            return HttpResponseBadRequest("post_id required")
        post = get_object_or_404(Post, pk=post_id)

        roots = (Comment.objects
                 .select_related("author")
                 .filter(post=post, parent__isnull=True, is_deleted=False)
                 .order_by("-created_at"))

        roots = roots.prefetch_related(
            Prefetch("replies", queryset=Comment.objects.select_related("author").filter(is_deleted=False))
        )

        data = [_serialize_comment(c, request, include_replies=False) for c in roots]
        return JsonResponse({
            "ok": True,
            "is_auth": request.user.is_authenticated,
            "comments": data,
            "count": len(data)
        })

    action = request.POST.get("action")

    if action == "create":
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "error": "auth"}, status=401)
        post_id = request.POST.get("post_id")
        text = (request.POST.get("text") or "").strip()
        if not post_id or not text:
            return JsonResponse({"ok": False, "error": "bad_params"}, status=400)
        if contains_profanity(text):
            return JsonResponse({"ok": False, "error": "profanity"}, status=422)
        post = get_object_or_404(Post, pk=post_id)
        c = Comment.objects.create(author=request.user, post=post, text=text)
        return JsonResponse({"ok": True, "comment": _serialize_comment(c, request)})

    if action == "reply":
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "error": "auth"}, status=401)
        parent_id = request.POST.get("parent_id")
        text = (request.POST.get("text") or "").strip()
        if not parent_id or not text:
            return JsonResponse({"ok": False, "error": "bad_params"}, status=400)
        if contains_profanity(text):
            return JsonResponse({"ok": False, "error": "profanity"}, status=422)
        parent = get_object_or_404(Comment, pk=parent_id, is_deleted=False)
        c = Comment.objects.create(author=request.user, post=parent.post, parent=parent, text=text)
        replies_qs = parent.replies.select_related("author").filter(is_deleted=False).order_by("created_at")
        return JsonResponse({
            "ok": True,
            "parent_id": parent.id,
            "replies": [_serialize_comment(r, request) for r in replies_qs]
        })

    if action == "load_replies":
        parent_id = request.POST.get("parent_id")
        if not parent_id:
            return JsonResponse({"ok": False, "error": "bad_params"}, status=400)
        parent = get_object_or_404(Comment, pk=parent_id, is_deleted=False)
        replies_qs = parent.replies.select_related("author").filter(is_deleted=False).order_by("created_at")
        return JsonResponse({
            "ok": True,
            "parent_id": parent.id,
            "replies": [_serialize_comment(r, request) for r in replies_qs],
            "is_auth": request.user.is_authenticated,
        })

    if action == "edit":
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "error": "auth"}, status=401)
        cid = request.POST.get("id")
        text = (request.POST.get("text") or "").strip()
        c = get_object_or_404(Comment, pk=cid, is_deleted=False)
        if not _is_owner(request, c.author_id):
            return JsonResponse({"ok": False, "error": "forbidden"}, status=403)
        if not text:
            return JsonResponse({"ok": False, "error": "empty"}, status=400)
        if contains_profanity(text):
            return JsonResponse({"ok": False, "error": "profanity"}, status=422)
        c.text = text
        c.save(update_fields=["text"])
        return JsonResponse({"ok": True, "comment": _serialize_comment(c, request)})

    if action == "delete":
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "error": "auth"}, status=401)
        cid = request.POST.get("id")
        c = get_object_or_404(Comment, pk=cid, is_deleted=False)
        if not _is_owner(request, c.author_id):
            return JsonResponse({"ok": False, "error": "forbidden"}, status=403)
        c.is_deleted = True
        c.save(update_fields=["is_deleted"])
        return JsonResponse({"ok": True, "id": c.id})

    return JsonResponse({"ok": False, "error": "unknown_action"}, status=400)


