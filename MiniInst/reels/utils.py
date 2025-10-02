from django.contrib.contenttypes.models import ContentType

from comments.models.comment import Comment


def serialize_comment(comment_obj):
    return {
        "id": comment_obj.id,
        "author": comment_obj.author.username,
        "text": comment_obj.text,
        "created_at": comment_obj.created_at.strftime("%d.%m.%Y %H:%M"),
    }


def get_reel_comments(reel):
    content_type = ContentType.objects.get_for_model(reel)
    return Comment.objects.filter(
        content_type=content_type,
        object_id=reel.id,
        is_deleted=False
    ).select_related("author").order_by("-created_at")
