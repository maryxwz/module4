from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

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