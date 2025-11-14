from rest_framework import serializers
from .models import Target, Source, Indicator, Association


# PUBLIC_INTERFACE
class TargetSerializer(serializers.ModelSerializer):
    """Serializer for Target model with validation."""

    # PUBLIC_INTERFACE
    def validate_confidence(self, value: float) -> float:
        """Ensure confidence is in [0,1]."""
        if value < 0 or value > 1:
            raise serializers.ValidationError("confidence must be between 0 and 1")
        return value

    class Meta:
        model = Target
        fields = [
            "id",
            "name",
            "description",
            "status",
            "priority",
            "tags",
            "confidence",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# PUBLIC_INTERFACE
class SourceSerializer(serializers.ModelSerializer):
    """Serializer for Source model."""

    class Meta:
        model = Source
        fields = ["id", "name", "type", "url", "metadata", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


# PUBLIC_INTERFACE
class IndicatorSerializer(serializers.ModelSerializer):
    """Serializer for Indicator model with validation."""

    # PUBLIC_INTERFACE
    def validate_score(self, value: float) -> float:
        """Ensure score is in [0,1]."""
        if value < 0 or value > 1:
            raise serializers.ValidationError("score must be between 0 and 1")
        return value

    class Meta:
        model = Indicator
        fields = ["id", "type", "value", "score", "source", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


# PUBLIC_INTERFACE
class AssociationSerializer(serializers.ModelSerializer):
    """Serializer for Association model with nested read-only fields."""
    target_name = serializers.CharField(source="target.name", read_only=True)
    indicator_type = serializers.CharField(source="indicator.type", read_only=True)
    indicator_value = serializers.CharField(source="indicator.value", read_only=True)
    source_name = serializers.CharField(source="indicator.source.name", read_only=True)

    # PUBLIC_INTERFACE
    def validate_weight(self, value: float) -> float:
        """Ensure weight is in [0,1]."""
        if value < 0 or value > 1:
            raise serializers.ValidationError("weight must be between 0 and 1")
        return value

    class Meta:
        model = Association
        fields = [
            "id",
            "target",
            "indicator",
            "rationale",
            "analyst_notes",
            "weight",
            "created_at",
            "updated_at",
            # nested read items
            "target_name",
            "indicator_type",
            "indicator_value",
            "source_name",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "target_name", "indicator_type", "indicator_value", "source_name"]
