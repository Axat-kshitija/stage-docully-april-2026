from notifications.models import AllNotifications

def set_all_notification(instance):
	AllNotifications.objects.create(dataroom_member=instance, dataroom_id=instance.dataroom_id)