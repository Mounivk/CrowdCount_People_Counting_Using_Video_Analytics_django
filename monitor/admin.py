# monitor/admin.py
from django.contrib import admin
from .models import UploadedVideo, CrowdCount


@admin.register(UploadedVideo)
class UploadedVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_at")
    search_fields = ("id",)


@admin.register(CrowdCount)
class CrowdCountAdmin(admin.ModelAdmin):
    list_display = (
        "video_count",
        "webcam_count",
        "video_accuracy",
        "webcam_accuracy",
        "alert_active",
        "updated_at",
    )
    list_filter = ("alert_active",)
