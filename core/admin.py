from django.contrib import admin
from .models import User, Categories, Products, ProductsImage


# Register your models here.

class ProductsImageInline(admin.TabularInline):
    model = ProductsImage
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
        'get_thumbnail'
        'slug',
        'price',
        'stock',
        'is_active',
        'is_sale',
        'new_price',
        'get_price_in_toman'
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
    list_editable = ('is_active', 'is_sale', 'is_suggestion', 'category', 'new_price', 'price')

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


