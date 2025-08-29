from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from backoffice.forms import UserSettingsForm
from backoffice.models import UserReport


@staff_member_required
def user_reports_list(request: HttpRequest) -> HttpResponse:
    reports = UserReport.objects.all().order_by('-created_at')
    context = dict(
        reports=reports,
    )
    return render(
        request=request,
        template_name='backoffice/user_reports.html',
        context=context,
    )


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