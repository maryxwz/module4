from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages

from backoffice.forms import UserSettingsForm, UserReportForm
from backoffice.models import UserReport
from users.models import CustomUser


@staff_member_required
def user_reports_list(request: HttpRequest) -> HttpResponse:
    reports = (
        UserReport.objects.select_related("author", "reported_user")
        .all()
        .order_by("-created_at")
    )

    for report in reports:
        if report.reported_user:
            report.reported_user_count = UserReport.objects.filter(
                reported_user=report.reported_user
            ).count()
        else:
            report.reported_user_count = 0

    context = dict(
        reports=reports,
    )
    return render(
        request=request,
        template_name="backoffice/user_reports.html",
        context=context,
    )


@staff_member_required
def block_user(request: HttpRequest, user_id: int) -> HttpResponse:
    if request.method == "POST":
        user = get_object_or_404(CustomUser, id=user_id)

        reports_count = UserReport.objects.filter(reported_user=user).count()

        if reports_count > 5:
            user.is_banned = True
            user.save()
            messages.success(request, f"Користувач {user.username} заблокован.")
        else:
            messages.error(
                request,
                f"Недостатньо репортів для блокування користувача {user.username}.",
            )

    return redirect("user_reports_list")

@login_required
def settings(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
            form = UserSettingsForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('settings')
    else:
        form = UserSettingsForm(instance=request.user)

    return render(
        request=request,
        template_name='backoffice/settings.html',
        context={'form': form},
    )


@login_required
@require_POST
def report_user(request, username):
    reported_user = get_object_or_404(CustomUser, username=username)
    current_user = request.user

    if current_user == reported_user:
        messages.error(request, 'Ви не можете поскаржитися на себе')
        return redirect('users:profile', username=username)

    form = UserReportForm(request.POST, request.FILES)

    if form.is_valid():
        content_file = form.cleaned_data.get('content')
        if content_file and content_file.size > 10 * 1024 * 1024:
            messages.error(request, 'Розмір файлу не повинен перевищувати 10MB')
            return redirect('users:profile', username=username)

        try:
            report = form.save(commit=False)
            report.author = current_user
            report.reported_user = reported_user
            report.save()

            messages.success(request, 'Вашу скаргу успішно надіслано. Дякуємо за повідомлення!')

        except Exception as e:
            messages.error(request, 'Виникла помилка при надсиланні скарги. Спробуйте пізніше.')

    else:
        for field, errors in form.errors.items():
            for error in errors:
                if field == 'description':
                    messages.error(request, f'Опис скарги: {error}')
                elif field == 'content':
                    messages.error(request, f'Файл: {error}')
                else:
                    messages.error(request, f'Помилка: {error}')

    return redirect('users:profile', username=username)
