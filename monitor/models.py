from django.db import models


# ================= ADMIN VIDEO MODEL =================
class Video(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="videos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ================= VIEWER UPLOADED VIDEO =================
class UploadedVideo(models.Model):
    video = models.FileField(upload_to="uploaded_videos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UploadedVideo {self.id}"


# ================= CROWD COUNT MODEL =================
class CrowdCount(models.Model):
    # Webcam data
    webcam_count = models.IntegerField(default=0)
    webcam_accuracy = models.FloatField(default=0.0)

    # Video data
    video_count = models.IntegerField(default=0)
    video_accuracy = models.FloatField(default=0.0)

    # Alert system
    alert_active = models.BooleanField(default=False)
    alert_message = models.CharField(max_length=255, blank=True)
    alert_sent = models.BooleanField(default=False)  

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Crowd Count Status"
