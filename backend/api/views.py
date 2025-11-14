from django.db.models import QuerySet, Sum, F
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter, DateTimeFromToRangeFilter
from rest_framework import viewsets, permissions, decorators, response, status, filters
from rest_framework.pagination import PageNumberPagination

from .models import Target, Source, Indicator, Association
from .serializers import (
    TargetSerializer,
    SourceSerializer,
    IndicatorSerializer,
    AssociationSerializer,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    """Default pagination for the API."""
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200


class TargetFilter(FilterSet):
    """Filter params for Target."""
    status = CharFilter(field_name="status", lookup_expr="iexact")
    priority_min = NumberFilter(field_name="priority", lookup_expr="gte")
    priority_max = NumberFilter(field_name="priority", lookup_expr="lte")
    confidence_min = NumberFilter(field_name="confidence", lookup_expr="gte")
    confidence_max = NumberFilter(field_name="confidence", lookup_expr="lte")
    created_at = DateTimeFromToRangeFilter()

    class Meta:
        model = Target
        fields = ["status", "created_at"]


class IndicatorFilter(FilterSet):
    """Filter params for Indicator."""
    type = CharFilter(field_name="type", lookup_expr="iexact")
    score_min = NumberFilter(field_name="score", lookup_expr="gte")
    score_max = NumberFilter(field_name="score", lookup_expr="lte")
    source = NumberFilter(field_name="source_id", lookup_expr="exact")

    class Meta:
        model = Indicator
        fields = ["type", "source"]


class AssociationFilter(FilterSet):
    """Filter params for Association."""
    target = NumberFilter(field_name="target_id", lookup_expr="exact")
    indicator = NumberFilter(field_name="indicator_id", lookup_expr="exact")
    weight_min = NumberFilter(field_name="weight", lookup_expr="gte")
    weight_max = NumberFilter(field_name="weight", lookup_expr="lte")

    class Meta:
        model = Association
        fields = ["target", "indicator"]


# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint returning simple status."""
    return Response({"message": "Server is up!"})


class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common configuration."""
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]


# PUBLIC_INTERFACE
class TargetViewSet(BaseViewSet):
    """CRUD endpoints for Target model with search, filter, ordering and custom actions."""
    queryset: QuerySet[Target] = Target.objects.all()
    serializer_class = TargetSerializer
    search_fields = ["name", "description", "tags"]
    filterset_class = TargetFilter
    ordering_fields = ["priority", "confidence", "updated_at", "created_at"]

    # PUBLIC_INTERFACE
    @decorators.action(
        methods=["get"],
        detail=True,
        url_path="score",
        url_name="score",
        permission_classes=[permissions.AllowAny],
        summary="Get target score",
    )
    def score(self, request, pk=None):
        """
        Get weighted score for a target.

        The score is computed as the sum over associations of (indicator.score * association.weight).
        Returns JSON: {"target": <id>, "score": <float>}
        """
        target = self.get_object()
        agg = Association.objects.filter(target=target).aggregate(
            total=Sum(F("indicator__score") * F("weight"))
        )
        total_score = agg["total"] or 0.0
        return response.Response({"target": target.id, "score": float(total_score)})

    # PUBLIC_INTERFACE
    @decorators.action(
        methods=["post"],
        detail=True,
        url_path="promote",
        url_name="promote",
        permission_classes=[permissions.AllowAny],
        summary="Promote target status",
    )
    def promote(self, request, pk=None):
        """
        Promote target status.

        Body: {"status": "under_review|confirmed|rejected|new"}
        Validates choice and updates the target status; returns updated Target.
        """
        target = self.get_object()
        new_status = request.data.get("status")
        valid = [choice for choice, _ in Target.Status.choices]
        if new_status not in valid:
            return response.Response(
                {"detail": f"Invalid status. Valid: {valid}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        target.status = new_status
        target.save(update_fields=["status", "updated_at"])
        return response.Response(self.get_serializer(target).data)


# PUBLIC_INTERFACE
class SourceViewSet(BaseViewSet):
    """CRUD endpoints for Source model."""
    queryset: QuerySet[Source] = Source.objects.all()
    serializer_class = SourceSerializer
    search_fields = ["name", "url"]
    filterset_fields = ["type"]
    ordering_fields = ["name", "created_at", "updated_at"]


# PUBLIC_INTERFACE
class IndicatorViewSet(BaseViewSet):
    """CRUD endpoints for Indicator model."""
    queryset: QuerySet[Indicator] = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    search_fields = ["value"]
    filterset_class = IndicatorFilter
    ordering_fields = ["score", "created_at", "updated_at"]


# PUBLIC_INTERFACE
class AssociationViewSet(BaseViewSet):
    """CRUD endpoints for Association model."""
    queryset: QuerySet[Association] = Association.objects.select_related("target", "indicator", "indicator__source").all()
    serializer_class = AssociationSerializer
    search_fields = ["rationale", "analyst_notes"]
    filterset_class = AssociationFilter
    ordering_fields = ["weight", "created_at", "updated_at"]
