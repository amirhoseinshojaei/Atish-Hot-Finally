import uuid

from django.core.validators import RegexValidator
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField
import requests
import os
from django.utils.safestring import mark_safe
from decimal import Decimal
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError


# Create your models here.


def validate_image(file):
    """
    ولیدیشن برای بررسی تصویر آپلود شده.
    """
    # بررسی فرمت فایل
    valid_extensions = ['jpg', 'jpeg', 'png']
    if not file.name.split('.')[-1].lower() in valid_extensions:
        raise ValidationError('فرمت تصویر معتبر نیست. لطفاً از فرمت‌های jpg, jpeg, png  استفاده کنید.')

    # بررسی اندازه فایل (مثلاً حداکثر 2 مگابایت)
    max_size = 2 * 1024 * 1024  # 2 مگابایت
    if file.size > max_size:
        raise ValidationError('اندازه تصویر نباید بیشتر از ۲ مگابایت باشد.')


class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None):
        if not email:
            raise ValueError('ایمیل خودرا وارد کنید')

        if not phone_number:
            raise ValueError('شماره تماس خودرا وارد کنید')

        if not password:
            raise ValueError('پسورد خود را وارد کنید')

        user = self.model(
            phone_number=phone_number,
            email=self.normalize_email(email)

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            phone_number=phone_number,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره خودرا با فرمت صحیح 09 وارد کنید'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', ]

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        db_table = 'user'
        ordering = ['-date_joined']
        get_latest_by = 'date_joined'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.username


class Categories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'categories'
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.name, allow_unicode=True)
        super(Categories, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Products(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, null=True, blank=True)
    description = RichTextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ir_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_sale = models.BooleanField(default=False)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ir_new_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_suggestion = models.BooleanField(default=False)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'products'
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.name, allow_unicode=True)
        super(Products, self).save(*args, **kwargs)

    def get_upload_path(instance, filename):
        name = instance.name
        return os.path.join(
            'Products',
            name,
            filename
        )

    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True)

    def get_usd_to_irr_rate(self):
        url = 'https://www.tgju.org/profile/price_dollar_rl'

        try:
            # ارسال درخواست به سایت
            response = requests.get(url)

            if response.status_code == 200:
                # استفاده از BeautifulSoup برای تجزیه HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # پیدا کردن تگ <td> که قیمت دلار را در خود دارد
                rate_tag = soup.find('td', class_='text-left')

                # بررسی اینکه آیا نرخ پیدا شده است
                if rate_tag:
                    usd_to_irr = rate_tag.text.strip().replace(',', '')  # حذف کاما از عدد
                    return int(usd_to_irr) * 10  # تبدیل به عدد صحیح (ریال)
                else:
                    return "Rate not found"
            else:
                return f"Failed to fetch the page. Status code: {response.status_code}"
        except Exception as e:
            return f"An error occurred: {e}"

    def get_thumbnail(self):
        """
        نمایش Thumbnail در پنل ادمین.
        """
        if self.image:
            # تولید کد HTML برای نمایش تصویر
            return mark_safe(f'<img src="{self.image.url}" width="100" height="100" style="object-fit: cover;" />')
        return "No Image"

    get_thumbnail.short_description = 'Thumbnail'

    def __str__(self):
        return self.name


class ProductsImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='images')

    def get_upload_path(instance, filename):
        name = instance.product.name
        return os.path.join(
            'Products',
            name,
            filename
        )

    image = models.ImageField(upload_to=get_upload_path, null=True, blank=True)

    def __str__(self):
        return self.product.name


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    regex_phone = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره شما باید با فرمت 09 وارد شود'
    )

    phone_number = models.CharField(validators=[regex_phone], max_length=11)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=2500)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        db_table = 'customer'
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return self.full_name


class Vendors(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True, allow_unicode=True)
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=2500)
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره شما باید با فرمت 09 وارد شود'
    )

    phone_number = models.CharField(validators=[phone_regex], max_length=11, unique=True)

    code = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profit = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        db_table = 'vendor'
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.first_name} {self.last_name}', allow_unicode=True)
        super(Vendors, self).save(*args, **kwargs)

    def get_total_profit(self):
        # محاسبه مجموع سود از همه سفارشات مرتبط
        orders = self.orders.all()  # دسترسی به سفارشات مرتبط با فروشنده
        total_profit = round(sum(
            order.calculate_total_price() * Decimal(0.1) for order in orders if order.status == 'Delivered'))
        return total_profit

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Orders(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    regex_phone = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره شما باید با فرمت 09 وارد شود'
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)

    phone_number = models.CharField(validators=[regex_phone], max_length=11)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=1500)
    postal_code = models.CharField(max_length=20)
    identification_code = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    products = models.ManyToManyField(Products, through='OrderItem')
    date_shipped = models.DateTimeField(null=True, blank=True)
    vendor = models.ForeignKey(Vendors, on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        db_table = 'orders'
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    # def save(self, *args, **kwargs):
    #     if self.status == 'Delivered':
    #         self.date_shipped = timezone.now()
    #
    #     super(Orders, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            if self.vendor:
                # افزودن سود به فروشنده
                self.vendor.profit += self.calculate_total_price() * Decimal(0.1)  # 10% سود
                self.vendor.save()
            if self.identification_code and not self.vendor:
                try:
                    self.vendor = Vendors.objects.get(code=self.identification_code)
                except Vendors.DoesNotExist:
                    raise ValueError("فروشنده‌ای با این کد وجود ندارد.")
        super().save(*args, **kwargs)

    # def get_usd_to_irr_rate(self):
    #     url = 'https://www.tgju.org/profile/price_dollar_rl'
    #
    #     try:
    #         # ارسال درخواست به سایت
    #         response = requests.get(url)
    #
    #         if response.status_code == 200:
    #             # استفاده از BeautifulSoup برای تجزیه HTML
    #             soup = BeautifulSoup(response.text, 'html.parser')
    #
    #             # پیدا کردن تگ <td> که قیمت دلار را در خود دارد
    #             rate_tag = soup.find('td', class_='text-left')
    #
    #             # بررسی اینکه آیا نرخ پیدا شده است
    #             if rate_tag:
    #                 usd_to_irr = rate_tag.text.strip().replace(',', '') # حذف کاما از عدد
    #                 return int(usd_to_irr) * 10  # تبدیل به عدد صحیح (ریال)
    #             else:
    #                 return "Rate not found"
    #         else:
    #             return f"Failed to fetch the page. Status code: {response.status_code}"
    #     except Exception as e:
    #         return f"An error occurred: {e}"
    #
    # def calculate_total_price(self):
    #     """
    #     محاسبه قیمت کل سفارش بر اساس محصولات (به تومان)
    #     """
    #     usd_to_irr = self.get_usd_to_irr_rate()  # دریافت نرخ تبدیل
    #     if not usd_to_irr:
    #         return 0  # اگر نرخ تبدیل موجود نبود، مقدار صفر برگردانده شود
    #
    #     total = sum(item.get_usd_to_irr_rate(usd_to_irr) for item in self.order_items.all())
    #     self.total_price = total
    #     return total

    # به دلل متغیر بودن قیمت ها از روش بالا صرف نظر شد
    def calculate_total_price(self):
        total_price = sum(item.get_total_price() for item in self.order_items.all())
        return total_price

    # def save(self, *args, **kwargs):
    #     # ابتدا شیء را ذخیره کنید
    #     if not self.pk:  # بررسی کنید که آیا شیء ذخیره شده است یا نه
    #         super().save(*args, **kwargs)
    #     # سپس قیمت کل را محاسبه کنید
    #     self.calculate_total_price()
    #     # ذخیره نهایی شیء
    #     super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_items')  # سفارش مرتبط
    product = models.ForeignKey('Products', on_delete=models.CASCADE, related_name='order_items')  # محصول مرتبط
    quantity = models.PositiveIntegerField(default=1)  # تعداد محصول
    price = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if not self.pk:  # فقط برای آیتم‌های جدید
            if self.product.stock < self.quantity:
                raise ValueError(f"Not enough stock for {self.product.name}")
            self.product.stock -= self.quantity
            if self.product.stock == 0:  # غیرفعال کردن محصول در صورت صفر شدن موجودی
                self.product.is_active = False
            self.product.save()
        super(OrderItem, self).save(*args, **kwargs)


class VendorProfile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    vendor_code = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=1500, null=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره شما باید با فرمت 09 وارد شود'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=11, unique=True)
    profit = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vendor = models.ForeignKey(Vendors, on_delete=models.SET_NULL, related_name='profiles', null=True, blank=True)

    class Meta:
        verbose_name = 'Vendor Profile'
        verbose_name_plural = 'Vendor Profiles'
        db_table = 'vendor_profile'
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def get_total_profit(self):
        """
        محاسبه مجموع سود از سفارش‌هایی که توسط فروشنده انجام شده است.
        """
        orders = self.vendors.orders.all()  # فرض اینکه مدل Vendor متصل به Orders است
        total_profit = sum(order.calculate_total_price() for order in orders if order.status == 'Delivered')
        return total_profit

    def get_upload_path(instance, filename):
        full_name = f'{instance.first_name} {instance.last_name}'
        return os.path.join('Profiles', full_name, filename)

    profile_image = models.ImageField(upload_to=get_upload_path, null=True, blank=True, default='profile.jpg',
                                      validators=[validate_image])

    def get_profile_info(self):
        """
        بازگرداندن اطلاعات کلی فروشنده برای نمایش.
        """
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image': self.profile_image,
            'vendor_code': self.vendor_code,
            'city': self.city,
            'address': self.address,
            'phone_number': self.phone_number,
            'total_profit': self.get_total_profit(),
        }
