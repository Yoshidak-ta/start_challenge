from pywebpush import webpush, WebPushException
from django.conf import settings

def send_web_push(user_subscription, message):
    try:
        webpush(
            subscription_info={
                "endpoint": user_subscription.endpoint,
                "keys": {
                    "auth": user_subscription.auth_key,
                    "p256dh": user_subscription.p256dh_key,
                }
            },
            data=message,
            vapid_private_key=settings.WEBPUSH_SETTINGS["VAPID_PRIVATE_KEY"],
            vapid_claims={"sub": "mailto:{}".format(settings.WEBPUSH_SETTINGS["VAPID_ADMIN_EMAIL"])}
        )
        return True
    except WebPushException as ex:
        print("Web Push Error:", ex)
        return False
