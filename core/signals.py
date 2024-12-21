from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Orders, Customer, Products, VendorProfile, Vendors, User, Profile, OrderItem


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


@receiver(post_save, sender=Orders)
def restore_stock_on_cancellation(sender, instance, **kwargs):
    # بررسی اینکه وضعیت به "Cancelled" تغییر کرده است
    if instance.status == 'Canceled':
        # پیمایش همه محصولات مرتبط با سفارش
        order_items = OrderItem.objects.filter(order=instance)
        for order_item in order_items:
            product = order_item.product
            product.stock += order_item.quantity  # بازگرداندن موجودی
            product.save()  # ذخیره تغییرات


@receiver(post_save, sender=Vendors)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created:  # بررسی اینکه آیا رکورد جدید ایجاد شده است
        VendorProfile.objects.create(
            vendor=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            vendor_code=instance.code,
            city=instance.city,
            address=instance.address,
            phone_number=instance.phone_number,
            profit=instance.get_total_profit(),  # متد باید فراخوانی شود
        )
    else:
        vendor_profile = VendorProfile.objects.get(vendor=instance)  # دریافت پروفایل موجود
        vendor_profile.first_name = instance.first_name  # به‌روزرسانی فیلدها
        vendor_profile.last_name = instance.last_name
        vendor_profile.city = instance.city
        vendor_profile.address = instance.address
        vendor_profile.phone_number = instance.phone_number
        vendor_profile.profit = instance.get_total_profit()  # متد را فراخوانی کنید
        vendor_profile.save()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            full_name=instance.full_name,  # کپی کردن نام کامل از یوزر
            email=instance.email,  # کپی کردن ایمیل از یوزر
            phone_number=instance.phone_number,
        )
    else:
        profile = instance.profile
        profile.full_name = instance.full_name  # به‌روزرسانی نام کامل
        profile.email = instance.email  # به‌روزرسانی ایمیل
        profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
