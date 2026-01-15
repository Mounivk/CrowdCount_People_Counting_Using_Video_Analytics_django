import cv2
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse, JsonResponse
from .models import Video, UploadedVideo, CrowdCount
from .yolo_tracker import process_video  # your YOLO + DeepSORT processing function

# ================= HOME =================
def home(request):
    latest_video = UploadedVideo.objects.last()
    return render(request, "home.html", {"video": latest_video})


# ================= AUTH =================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid admin credentials!")

    return render(request, "auth/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")


# ================= VIEWER AUTH =================
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def viewer_register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]  # matches your form
        password2 = request.POST["password2"]  # matches your form

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("viewer_register")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("viewer_register")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Registration successful. Please login.")
        return redirect("viewer_login")

    return render(request, "viewer_register.html")

def viewer_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("viewer_dashboard")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("viewer_login")

    return render(request, "viewer_login.html")


def viewer_logout(request):
    logout(request)
    return redirect("viewer_login")


# ================= REDIRECT =================
@login_required
def redirect_view(request):
    if request.user.is_superuser:
        return redirect("admin_dashboard")
    return redirect("viewer_dashboard")


# ================= DASHBOARDS =================
@login_required
def admin_dashboard(request):
    if request.method == "POST":
        Video.objects.all().delete()
        Video.objects.create(
            title=request.POST.get("title"),
            file=request.FILES.get("video")
        )
    return render(request, "admin/dashboard.html")


@login_required(login_url='viewer_login')
def viewer_dashboard(request):
    latest_video = UploadedVideo.objects.last()
    video_count = UploadedVideo.objects.count()

    # Get live counts
    crowd_obj = CrowdCount.objects.first()  # get the first (and only) CrowdCount object
    live_count = crowd_obj.webcam_count if crowd_obj else 0
    live_accuracy = crowd_obj.webcam_accuracy if crowd_obj else 0

    return render(request, "viewer/dashboard.html", {
        "video": latest_video,
        "video_count": video_count,
        "live_count": live_count,
        "live_accuracy": live_accuracy
    })


# ================= VIDEO UPLOAD & VIEW =================
def upload_video(request):
    if request.method == "POST":
        video_file = request.FILES.get("video")
        if video_file:
            uploaded_video = UploadedVideo.objects.create(video=video_file)
            # Redirect to the video view page for this specific video
            return redirect("video_view", pk=uploaded_video.id)
    return render(request, "admin/upload_video.html")


def video_view(request, pk):
    video = UploadedVideo.objects.get(id=pk)
    return render(request, "viewer/video_view.html", {"video": video})


# ================= VIDEO STREAM =================
from .utils import send_alert_email
from .helper import get_alert_recipients
ALERT_THRESHOLD = 35

def video_stream(request, pk):
    video = UploadedVideo.objects.get(id=pk)

    for frame, count, accuracy in process_video(video.video.path):

        alert = count >= ALERT_THRESHOLD

        crowd, _ = CrowdCount.objects.get_or_create(id=1)

        crowd.video_count = count
        crowd.video_accuracy = accuracy
        crowd.alert_active = alert
        crowd.alert_message = " High Crowd Detected!" if alert else ""

        if alert and not crowd.alert_sent:
            recipients = get_alert_recipients(request)

            if recipients:
                send_alert_email(
                    subject=" High Crowd Alert!",
                    message = ( f" ALERT! High Crowd Detected!\n\n" f"Webcam Monitoring System has detected a crowd of *{count} people*.\n" f"Estimated accuracy: {accuracy:.2f}%\n\n" f"Please take immediate action to ensure safety! ⚠️" ),
                    recipient_list=recipients
                )

            crowd.alert_sent = True

        if not alert:
            crowd.alert_sent = False

        crowd.save()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


@login_required
def video_feed(request, pk):
    return StreamingHttpResponse(
        video_stream(request, pk),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )



# ================= WEBCAM STREAM =================

def webcam_stream(request):
    for frame, count, accuracy in process_video(0):

        alert = count >= ALERT_THRESHOLD

        crowd, _ = CrowdCount.objects.get_or_create(id=1)

        crowd.webcam_count = count
        crowd.webcam_accuracy = accuracy
        crowd.alert_active = alert
        crowd.alert_message = " High Crowd Detected!" if alert else ""

        if alert and not crowd.alert_sent:
            recipients = get_alert_recipients(request)

            if recipients:
                send_alert_email(
                    subject=" High Crowd Alert (Webcam)",
                    message = ( f" ALERT! High Crowd Detected!\n\n" f"Webcam Monitoring System has detected a crowd of *{count} people*.\n" f"Estimated accuracy: {accuracy:.2f}%\n\n" f"Please take immediate action to ensure safety! ⚠️" ),
                    recipient_list=recipients
                )

            crowd.alert_sent = True

        if not alert:
            crowd.alert_sent = False

        crowd.save()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )

@login_required
def webcam_feed(request):
    return StreamingHttpResponse(
        webcam_stream(request),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )



def live_webcam_page(request):
    return render(request, "viewer/live_webcam.html")


# ================= LIVE COUNT API =================
def live_count_api(request):
    obj = CrowdCount.objects.first()

    return JsonResponse({
        "webcam_count": obj.webcam_count if obj else 0,
        "video_count": obj.video_count if obj else 0,
        "webcam_active": bool(obj and obj.webcam_count > 0),
        "video_active": bool(obj and obj.video_count > 0),
    })


def live_count_webcam(request):
    obj = CrowdCount.objects.first()
    return JsonResponse({
        "count": obj.webcam_count if obj else 0,
        "accuracy": obj.webcam_accuracy if obj else 0
    })




def live_count_video(request):
    obj = CrowdCount.objects.first()
    return JsonResponse({
        "count": obj.video_count if obj else 0,
        "accuracy": obj.video_accuracy if obj else 0
    })




