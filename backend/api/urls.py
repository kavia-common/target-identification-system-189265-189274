from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health,
    TargetViewSet,
    SourceViewSet,
    IndicatorViewSet,
    AssociationViewSet,
)

router = DefaultRouter()
router.register(r"targets", TargetViewSet, basename="target")
router.register(r"sources", SourceViewSet, basename="source")
router.register(r"indicators", IndicatorViewSet, basename="indicator")
router.register(r"associations", AssociationViewSet, basename="association")

urlpatterns = [
    path("health/", health, name="Health"),
    path("", include(router.urls)),
]
