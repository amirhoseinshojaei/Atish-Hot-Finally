from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Orders, Customer, Products, VendorProfile, Vendors


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


@receiver(post_save, sender=Products)
def activate_product(sender, instance, **kwargs):
    if instance.stock > 0 and not instance.is_active:
        instance.is_active = True
        instance.save()


@receiver(post_save, sender=Vendors)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created:  # بررسی اینکه آیا رکورد جدید ایجاد شده است
        VendorProfile.objects.create(vendor=instance)
