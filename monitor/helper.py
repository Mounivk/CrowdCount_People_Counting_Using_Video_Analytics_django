def get_alert_recipients(request):
    user = request.user

    if user.is_staff:  # Admin
        return [user.email]
    else:              # Viewer
        return [user.email]
