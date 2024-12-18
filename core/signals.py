from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Orders, Customer


@receiver(post_save, sender=Orders)
def create_customer_from_order(sender, instance, created, **kwargs):
    if created:
        # فقط زمانی که یک سفارش جدید ایجاد می‌شود
        customer = Customer.objects.create(
            full_name=instance.full_name,
            phone_number=instance.phone_number,
            city=instance.city,
            address=instance.address,
            postal_code=instance.postal_code,
        )
        instance.customer = customer  # به سفارش مشتری جدید را نسبت می‌دهیم
        instance.save()  # ذخیره مجدد سفارش برای ذخیره ارتباط با مشتری
