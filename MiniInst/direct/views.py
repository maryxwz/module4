from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Direct, DirectMessage, GroupChat, GroupMessage, PinnedConversation
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST
from users.models.block import Block


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

    conversations = []
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
        })

    pinned = sorted([c for c in conversations if c['pinned']],
                    key=lambda x: x['pinned_at'] or 0, reverse=True)
    not_pinned = sorted([c for c in conversations if not c['pinned']],
                        key=lambda x: x['created_at'] or 0, reverse=True)
    conversations_sorted = pinned + not_pinned

    return render(request, 'direct/inbox.html', {
        'conversations': conversations_sorted,
        'search_query': q,
    })


@require_POST
@login_required
def toggle_pin(request):
    kind = request.POST.get('kind')
    obj_id = request.POST.get('id')
    if kind not in ('direct', 'group') or not obj_id:
        return HttpResponseBadRequest("Invalid parameters")

    if kind == 'direct':
        model = Direct
    else:
        model = GroupChat

    try:
        obj = get_object_or_404(model, id=obj_id)
    except Exception:
        return HttpResponseBadRequest("Object not found")

    ct = ContentType.objects.get_for_model(model)
    pin_qs = PinnedConversation.objects.filter(user=request.user, content_type=ct, object_id=obj_id)
    if pin_qs.exists():
        pin_qs.delete()
        return JsonResponse({'pinned': False})
    else:
        PinnedConversation.objects.create(user=request.user, content_type=ct, object_id=obj_id)
        return JsonResponse({'pinned': True})


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
