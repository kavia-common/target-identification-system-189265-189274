from django.contrib import admin
from .models import Target, Source, Indicator, Association


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "priority", "confidence", "updated_at")
    list_filter = ("status", "priority", "confidence", "updated_at", "created_at")
    search_fields = ("name", "description", "tags")
    ordering = ("-updated_at", "-priority")


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "url")
    list_filter = ("type",)
    search_fields = ("name", "url")


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "value_short", "score", "source", "created_at")
    list_filter = ("type", "score", "source")
    search_fields = ("value",)

    def value_short(self, obj):
        return (obj.value or "")[:50]


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ("id", "target", "indicator", "weight", "created_at")
    list_filter = ("weight", "created_at", "updated_at", "target")
    search_fields = ("rationale", "analyst_notes")
