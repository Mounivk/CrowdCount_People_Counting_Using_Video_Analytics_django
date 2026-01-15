from django.urls import path
from . import views

urlpatterns = [

    # ================= HOME =================
    path("", views.home, name="home"),

    # ================= AUTH =================
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Viewer auth
    path("viewer/register/", views.viewer_register, name="viewer_register"),
    path("viewer/login/", views.viewer_login, name="viewer_login"),
    path("viewer/logout/", views.viewer_logout, name="viewer_logout"),

    path("redirect/", views.redirect_view, name="redirect"),

    # ================= DASHBOARDS =================
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("viewer-dashboard/", views.viewer_dashboard, name="viewer_dashboard"),

    # ================= VIDEO UPLOAD & VIEW =================
path("upload-video/", views.upload_video, name="upload_video"),
path("video-view/<int:pk>/", views.video_view, name="video_view"),

    # ================= VIDEO STREAM =================
    path("video-feed/<int:pk>/", views.video_feed, name="video_feed"),

    # ================= WEBCAM =================
path("webcam-feed/", views.webcam_feed, name="webcam_feed"),
path("live-webcam/", views.live_webcam_page, name="live_webcam"),

   # ================= LIVE COUNT APIs =================
path("api/live-count/", views.live_count_api, name="live_count_api"),
path("api/live-count/webcam/", views.live_count_webcam, name="live_count_webcam"),
path("api/live-count/video/", views.live_count_video, name="live_count_video"),

]    
