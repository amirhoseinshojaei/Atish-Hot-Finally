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


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        if not username:
            raise ValueError('Users must have an username')

        if not password:
            raise ValueError('Users must have a password')

        user = self.model(
            username=username,
            email=self.normalize_email(email)

        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
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
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return self.full_name

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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_sale = models.BooleanField(default=False)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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

    def get_price_in_toman(self):
        '''
        convert usd price to toman iran
        '''

        try:

            price_to_convert = self.new_price if self.new_price else self.price

            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            if response.status_code == 200:
                data = response.json()
                # Convert to IRR
                usd_to_irr = data['rates']['IRR']
                return price_to_convert * usd_to_irr

        except Exception as e:
            print('{e}:خطا در دریافت نرخ ارز')
        return None

    def discount_percentage(self):
        if self.is_sale and self.new_price < self.price:
            discount = (self.price - self.new_price) / self.price * 100
            return round(discount, 2)

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

    image = models.ImageField(upload_to=get_upload_path,null=True, blank=True)

    def __str__(self):
        return self.product.name


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    regex_phone = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره شما باید با فرمت 09 وارد شود'
    )

    phone = models.CharField(validators=[regex_phone], max_length=11)
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

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')

    phone_number = models.CharField(validators=[regex_phone], max_length=11)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=1500)
    postal_code = models.CharField(max_length=20)
    identification_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    products = models.ManyToManyField(Products, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_shipped = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        db_table = 'orders'
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def save(self, *args, **kwargs):
        if self.status == 'Delivered' and self.date_shipped is None:
            self.date_shipped = timezone.now()

        super(Orders, self).save(*args, **kwargs)

    def get_usd_to_toman_rate(self):
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
            if response.status_code == 200:
                data = response.json()
                return data['rates']['IRR']
        except Exception as e:
            print(f"{e}: خطا در دریافت نرخ ارز")
        return None

    def calculate_total_price(self):
        """
        محاسبه قیمت کل سفارش بر اساس محصولات (به تومان)
        """
        usd_to_irr = self.get_usd_to_toman_rate()  # دریافت نرخ تبدیل
        if not usd_to_irr:
            return 0  # اگر نرخ تبدیل موجود نبود، مقدار صفر برگردانده شود

        total = sum(item.get_total_price_in_toman(usd_to_irr) for item in self.order_items.all())
        self.total_price = total
        return total

    def save(self, *args, **kwargs):
        """
        قبل از ذخیره سفارش، قیمت کل را به‌روزرسانی می‌کنیم
        """
        self.calculate_total_price()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_items')  # سفارش مرتبط
    product = models.ForeignKey('Products', on_delete=models.CASCADE, related_name='order_items')  # محصول مرتبط
    quantity = models.PositiveIntegerField(default=1)  # تعداد محصول

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price_in_toman(self, usd_to_irr):
        """
        محاسبه قیمت کل این محصول در سفارش (به تومان)
        """
        price_in_usd = self.product.new_price if self.product.new_price else self.product.price
        return self.quantity * price_in_usd * usd_to_irr
