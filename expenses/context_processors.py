def notification_count(request):
    """Add notification count to context for all templates"""
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        return {'notification_unread_count': unread_count}
    return {'notification_unread_count': 0} 