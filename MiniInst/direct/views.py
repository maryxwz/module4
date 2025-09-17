from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Direct, DirectMessage, GroupChat, GroupMessage, PinnedConversation, PinnedConversation, ConversationOrder
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST
from users.models.block import Block
from users.models.custom_user import CustomUser
from users.models.follow import Follow
import json
from django.utils import timezone

@require_POST
@login_required
def create_direct(request):
    target_id = request.POST.get("target_id")
    if not target_id:
        return JsonResponse({"error": "target_id не вказаний"}, status=400)

    target_user = get_object_or_404(CustomUser, id=target_id)

    if Block.objects.filter(blocker=target_user, blocked=request.user).exists() or \
       Block.objects.filter(blocker=request.user, blocked=target_user).exists():
        return JsonResponse({"error": "Не можна створити чат, один з користувачів заблокований"}, status=403)

    if not Follow.objects.filter(follower=request.user, following=target_user).exists() or \
       not Follow.objects.filter(follower=target_user, following=request.user).exists():
        return JsonResponse({"error": "Обидва користувачі повинні бути підписані один на одного"}, status=403)

    direct, created = Direct.objects.get_or_create(
        user1=min(request.user, target_user, key=lambda u: u.id),
        user2=max(request.user, target_user, key=lambda u: u.id)
    )

    return JsonResponse({
        "ok": True,
        "created": created,
        "direct_id": str(direct.id)
    })


@login_required
def inbox(request):
    q = (request.GET.get('q') or '').strip()
    
    directs_qs = Direct.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    groups_qs = GroupChat.objects.filter(members=request.user)

    if q:
        directs_qs = directs_qs.filter(
            Q(user1__username__icontains=q) | Q(user2__username__icontains=q)
        )
        groups_qs = groups_qs.filter(name__icontains=q)

    directs_qs = directs_qs.order_by('-created_at').select_related('user1', 'user2')
    groups_qs = groups_qs.order_by('-created_at')

    direct_ct = ContentType.objects.get_for_model(Direct)
    group_ct = ContentType.objects.get_for_model(GroupChat)

    pinned_direct_ids = set(
        PinnedConversation.objects.filter(user=request.user, content_type=direct_ct)
        .values_list('object_id', flat=True)
    )
    pinned_group_ids = set(
        PinnedConversation.objects.filter(user=request.user, content_type=group_ct)
        .values_list('object_id', flat=True)
    )
    pinned_map = {}
    for p in PinnedConversation.objects.filter(user=request.user):
        pinned_map[(p.content_type_id, str(p.object_id))] = p.pinned_at

    positions_map = {}
    for o in ConversationOrder.objects.filter(user=request.user):
        positions_map[(o.content_type_id, str(o.object_id))] = o.position

    following_ids = list(
        Follow.objects.filter(follower=request.user)
        .values_list('following_id', flat=True)
        .distinct()
    )

    followers_ids = list(
        Follow.objects.filter(following=request.user)
        .values_list('follower_id', flat=True)
        .distinct()
    )

    direct_partner_ids = list(Direct.objects.filter(user1=request.user).values_list('user2_id', flat=True)) + \
                         list(Direct.objects.filter(user2=request.user).values_list('user1_id', flat=True))
    
    direct_partner_ids = list({int(x) for x in direct_partner_ids if x is not None})

    blocked_by_me_ids = list(Block.objects.filter(blocker=request.user).values_list('blocked_id', flat=True).distinct())
    blocked_me_ids = list(Block.objects.filter(blocked=request.user).values_list('blocker_id', flat=True).distinct())
    
    if not following_ids or not followers_ids:
        suggested_users_qs = CustomUser.objects.none()
    else:
        suggested_users_qs = CustomUser.objects.filter(
            id__in=following_ids
        ).filter(
            id__in=followers_ids
        )

        if direct_partner_ids:
            suggested_users_qs = suggested_users_qs.exclude(id__in=direct_partner_ids)

        if blocked_by_me_ids:
            suggested_users_qs = suggested_users_qs.exclude(id__in=blocked_by_me_ids)
        if blocked_me_ids:
            suggested_users_qs = suggested_users_qs.exclude(id__in=blocked_me_ids)

        suggested_users_qs = suggested_users_qs.exclude(id=request.user.id).filter(is_banned=False)

        suggested_users_qs = suggested_users_qs.order_by('username').distinct()

    if q:
        suggested_users_qs = suggested_users_qs.filter(username__icontains=q)
    
    suggested_users = suggested_users_qs

    conversations = []

    for chat in directs_qs:
        other = chat.get_receiver(request.user)

        if other and Block.objects.filter(
                Q(blocker=request.user, blocked=other) | Q(blocker=other, blocked=request.user)
        ).exists():
            continue

        conv_id = str(chat.id)
        ct_id = direct_ct.id
        pinned = (chat.id in pinned_direct_ids)

        last_msg = DirectMessage.objects.filter(direct=chat).order_by("-created_at").first()

        conversations.append({
            'kind': 'direct',
            'id': conv_id,
            'title': other.username if other else '',
            'other': other,
            'created_at': chat.created_at,
            'last_message': last_msg,
            'pinned': pinned,
            'pinned_at': pinned_map.get((ct_id, conv_id)),
            'position': positions_map.get((ct_id, conv_id)),  # None або int
        })

    for g in groups_qs:
        conv_id = str(g.id)
        ct_id = group_ct.id
        pinned = (g.id in pinned_group_ids)

        last_msg = GroupMessage.objects.filter(group_chat=g).order_by("-created_at").first()

        conversations.append({
            'kind': 'group',
            'id': conv_id,
            'title': g.name or 'Груповий чат',
            'group': g,
            'last_message': last_msg,
            'created_at': g.created_at,
            'pinned': pinned,
            'pinned_at': pinned_map.get((ct_id, conv_id)),
            'position': positions_map.get((ct_id, conv_id)),
        })

    pinned = sorted(
        [c for c in conversations if c['pinned']],
        key=lambda x: (x.get('position') if x.get('position') is not None else float('inf'))
    )

    not_pinned = sorted(
        [c for c in conversations if not c['pinned']],
        key=lambda x: (x.get('created_at') or timezone.now()),
        reverse=True
    )

    conversations_sorted = pinned + not_pinned

    return render(request, 'direct/inbox.html', {
        'conversations': conversations_sorted,
        'search_query': q,
        'suggested_users': suggested_users,
    })

@login_required
def get_friends(request):
    q = (request.GET.get('q') or '').strip()

    following_ids = list(
        Follow.objects.filter(follower=request.user)
        .values_list('following_id', flat=True)
        .distinct()
    )
    followers_ids = list(
        Follow.objects.filter(following=request.user)
        .values_list('follower_id', flat=True)
        .distinct()
    )

    blocked_by_me_ids = list(
        Block.objects.filter(blocker=request.user)
        .values_list('blocked_id', flat=True)
        .distinct()
    )
    blocked_me_ids = list(
        Block.objects.filter(blocked=request.user)
        .values_list('blocker_id', flat=True)
        .distinct()
    )

    if not following_ids or not followers_ids:
        friends_qs = CustomUser.objects.none()
    else:
        friends_qs = CustomUser.objects.filter(
            id__in=following_ids
        ).filter(
            id__in=followers_ids
        )

        if blocked_by_me_ids:
            friends_qs = friends_qs.exclude(id__in=blocked_by_me_ids)
        if blocked_me_ids:
            friends_qs = friends_qs.exclude(id__in=blocked_me_ids)

        friends_qs = friends_qs.exclude(id=request.user.id).filter(is_banned=False)

        if q:
            friends_qs = friends_qs.filter(username__icontains=q)

        friends_qs = friends_qs.order_by('username').distinct()

    friends = [
        {
            "id": str(user.id),
            "username": user.username,
            "avatar": user.avatar.url if user.avatar else None,
        }
        for user in friends_qs
    ]

    return JsonResponse({"friends": friends})

@login_required
@require_POST
def create_group(request):
    name = request.POST.get('name')
    if not name:
        return JsonResponse({"error": "Назва групи не може бути порожньою"}, status=400)
    
    participants_ids = request.POST.getlist('participants[]')
    if not participants_ids:
        return JsonResponse({"error": "Потрібно додати хоча б одного учасника"}, status=400)

    participants_ids = list({int(pid) for pid in participants_ids if pid.isdigit()})

    valid_participants = []
    errors = []

    for pid in participants_ids:
        if pid == request.user.id:
            errors.append(f"Користувач {request.user.username} вже є у групі")
            continue

        user = get_object_or_404(CustomUser, id=pid)

        if user.is_banned:
            errors.append(f"Користувач {user.username} заблокований системою")
            continue

        if not (Follow.objects.filter(follower=request.user, following=user).exists() and
                Follow.objects.filter(follower=user, following=request.user).exists()):
            errors.append(f"Немає взаємної підписки з {user.username}")
            continue

        if Block.objects.filter(Q(blocker=request.user, blocked=user) | Q(blocker=user, blocked=request.user)).exists():
            errors.append(f"Користувач {user.username} заблокований")
            continue

        valid_participants.append(user)

    if errors:
        return JsonResponse({"error": "Не вдалося створити групу", "details": errors}, status=403)

    group = GroupChat.objects.create(name=name, creator=request.user)
    group.members.add(request.user, *valid_participants)

    return JsonResponse({
        "ok": True,
        "group_id": str(group.id),
        "name": group.name,
        "participants": [u.username for u in group.members.all()]
    })


@require_POST
@login_required
def toggle_pin(request):
    kind = request.POST.get('kind')
    obj_id = request.POST.get('id')
    if kind not in ('direct', 'group') or not obj_id:
        return HttpResponseBadRequest("Invalid parameters")

    model = Direct if kind == 'direct' else GroupChat

    try:
        obj = get_object_or_404(model, id=obj_id)
    except Exception:
        return HttpResponseBadRequest("Object not found")

    ct = ContentType.objects.get_for_model(model)

    pin_qs = PinnedConversation.objects.filter(user=request.user, content_type=ct, object_id=obj_id)
    if pin_qs.exists():
        pin_qs.delete()
        ConversationOrder.objects.filter(user=request.user, content_type=ct, object_id=str(obj_id)).delete()
        return JsonResponse({'pinned': False})
    else:
        PinnedConversation.objects.create(user=request.user, content_type=ct, object_id=obj_id)

        existing = ConversationOrder.objects.filter(user=request.user, content_type=ct).order_by('position')
        if existing.exists():
            min_pos = existing.first().position
            new_pos = min_pos - 1
        else:
            new_pos = 0

        ConversationOrder.objects.create(
            user=request.user,
            content_type=ct,
            object_id=str(obj_id),
            position=new_pos
        )
        return JsonResponse({'pinned': True})
    
@require_POST
@login_required
def reorder_pins(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        order = payload.get('order') or []
    except Exception:
        return HttpResponseBadRequest("Bad payload")

    pos = 0
    for item in order:
        kind = item.get('kind')
        obj_id = item.get('id')
        if kind not in ('direct', 'group') or not obj_id:
            continue

        model = Direct if kind == 'direct' else GroupChat
        ct = ContentType.objects.get_for_model(model)

        pinned_exists = PinnedConversation.objects.filter(user=request.user, content_type=ct, object_id=obj_id).exists()
        if not pinned_exists:
            continue

        co, created = ConversationOrder.objects.get_or_create(
            user=request.user,
            content_type=ct,
            object_id=str(obj_id),
            defaults={'position': pos}
        )
        if not created:
            if co.position != pos:
                co.position = pos
                co.save(update_fields=['position'])
        pos += 1

    return JsonResponse({'ok': True})
    

@login_required
def thread_view(request, kind, chat_id):
    if kind not in ('direct', 'group'):
        return redirect('direct:inbox')

    if kind == 'direct':
        direct = get_object_or_404(Direct, id=chat_id)
        if request.user not in (direct.user1, direct.user2):
            return redirect('direct:inbox')
        other = direct.get_receiver(request.user)

        if Block.objects.filter(
                Q(blocker=request.user, blocked=other) | Q(blocker=other, blocked=request.user)
        ).exists():
            return redirect('direct:inbox')

        context_obj = direct
    else:
        group = get_object_or_404(GroupChat, id=chat_id)
        if not group.members.filter(pk=request.user.pk).exists():
            return redirect('direct:inbox')
        other = group.name or 'Group chat'
        context_obj = group

    return render(request, 'direct/thread.html', {
        'kind': kind,
        'chat': context_obj,
        'other': other,
    })


@login_required
def thread_messages_api(request, kind, chat_id):
    if kind == 'direct':
        direct = get_object_or_404(Direct, id=chat_id)
        if request.user not in (direct.user1, direct.user2):
            return JsonResponse({'error': 'Not allowed'}, status=403)

        other = direct.get_receiver(request.user)
        if Block.objects.filter(
                Q(blocker=request.user, blocked=other) | Q(blocker=other, blocked=request.user)
        ).exists():
            return JsonResponse({'error': 'Blocked'}, status=403)

        qs_desc = DirectMessage.objects.filter(direct=direct).select_related('sender').order_by('-created_at')
    elif kind == 'group':
        group = get_object_or_404(GroupChat, id=chat_id)
        if not group.members.filter(pk=request.user.pk).exists():
            return JsonResponse({'error': 'Not allowed'}, status=403)
        qs_desc = GroupMessage.objects.filter(group_chat=group).select_related('sender').order_by('-created_at')
    else:
        return JsonResponse({'error': 'Bad kind'}, status=400)

    per_page = 10
    paginator = Paginator(qs_desc, per_page)
    num_pages = paginator.num_pages or 1

    try:
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    if page < 1:
        page = 1
    if page > num_pages:
        return JsonResponse({'messages': [], 'page': page, 'num_pages': num_pages})

    page_obj = paginator.get_page(page)
    msgs = list(page_obj.object_list)[::-1]

    data = [{
        'id': str(m.id),
        'message': m.message,
        'sender_id': m.sender.id,
        'sender_username': m.sender.username,
        'created_at': m.created_at.isoformat(),
        'created_time': m.created_at.strftime('%H:%M'),
        'edited': getattr(m, 'edited', False),
    } for m in msgs]

    return JsonResponse({'messages': data, 'page': page, 'num_pages': num_pages})