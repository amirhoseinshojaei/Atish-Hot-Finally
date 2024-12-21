from django.contrib import admin
from .models import (User, Categories, Products, ProductsImage,
                     Customer, Orders, OrderItem, Vendors, VendorProfile,
                     Profile)


# Register your models here.

class ProductsImageInline(admin.TabularInline):
    model = ProductsImage
    extra = 1


class VendorProfileInline(admin.TabularInline):
    model = VendorProfile
    extra = 1


class ProfileInline(admin.TabularInline):
    model = Profile
    extra = 1


class OrdersItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'username',
        'email',
        'is_active',
        'is_admin',
        'is_staff',
        'is_superuser',
        'date_joined',
        'last_login',

    )
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    inlines = [ProfileInline]

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'created_at',
        'updated_at',
    )

    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'slug')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    prepopulated_fields = {'slug': ('name',)}

    list_editable = ('name', 'slug')

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'get_thumbnail',
        'slug',
        'price',
        'ir_price',
        'stock',
        'is_active',
        'is_sale',
        'new_price',
        'ir_new_price',
        'get_usd_to_irr_rate',
        'is_suggestion',
        'category',
        'created_at',
        'updated_at',
    )

    inlines = [ProductsImageInline]

    list_filter = ('is_active', 'is_sale', 'is_suggestion', 'category')
    search_fields = ('name', 'slug')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'is_sale', 'category', 'new_price', 'price')
    prepopulated_fields = {'slug': ('name',)}

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'phone_number',
        'city',
        'address',
        'postal_code',
        'created_at',
        'updated_at',

    )

    list_filter = ('city',)
    search_fields = ('full_name', 'city')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'customer',
        'phone_number',
        'city',
        'address',
        'postal_code',
        'identification_code',
        'status',
        'calculate_total_price',
        'date_shipped',
        'created_at',
        'updated_at',
    )

    list_filter = ('customer', 'status', 'date_shipped', 'city', 'created_at')
    search_fields = ('full_name', 'city',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrdersItemInline]

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


@admin.register(Vendors)
class VendorsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'slug',
        'phone_number',
        'email',
        'city',
        'address',
        'code',
        'get_total_profit',
        'created_at',
        'updated_at',

    )

    list_filter = (
        'city',

    )

    search_fields = ('first_name', 'last_name', 'code')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'code')
    inlines = [VendorProfileInline]

    prepopulated_fields = {'slug': ('first_name', 'last_name', 'phone_number')}

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff
