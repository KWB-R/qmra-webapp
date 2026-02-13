from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
import django
from qmra.risk_assessment.models import RiskAssessment

from django.db import models


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(f"{reverse('assessments')}?isLogin={request.GET.get('isLogin', 0)}")
    else:
        return render(request, "index.html")


def dsgvo(request):
    return render(request, "DSGVO.html", dict(locale=request.GET.get("locale", "de")))


def faqs(request):
    return render(request, "faqs.html")


def imprint(request):
    return render(request, "imprint.html")


def health(request):
    django.db.connection.ensure_connection()
    return HttpResponse("Ok")


def ready(request):
    django.db.connection.ensure_connection()
    return HttpResponse("Ok")