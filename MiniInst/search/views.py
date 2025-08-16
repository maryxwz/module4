from django.shortcuts import render


def index(request):
    # сюди має пізніше піти стягування всіх юзерів і постів і їх передача в штмл
    return render(request, 'index.html')
