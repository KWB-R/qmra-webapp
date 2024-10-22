from django.urls import path, include
from qmra.risk_assessment import views


urlpatterns = [
    path(
        "assessments",
        views.list_risk_assessment_view,
        name="assessments",
    ),
    path(
        "assessment",
        views.risk_assessment_view,
        name="assessment",
    ),
    path(
        "assessment/<uuid:risk_assessment_id>",
        views.risk_assessment_view,
        name="assessment",
    ),
    path(
        "assessment/<uuid:risk_assessment_id>/results",
        views.risk_assessment_result,
        name="assessment-result",
    ),
    path(
        "assessment/results",
        views.risk_assessment_result,
        name="assessment-result",
    ),
    path('', include('django_prometheus.urls')),
]