from django.contrib import admin

from .models import Script, IssuedLicense, Tag, Category


class ReadOnlyModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TagInline(admin.TabularInline):
    model = Script.tags.through
    extra = 1


class ScriptAdmin(ReadOnlyModelAdmin):
    list_display = [
        'name', 'description', 'category_id', 'enabled', 'is_active'
    ]
    inlines = [TagInline]
    exclude = ['tags']
    list_filter = ['category', 'enabled', 'is_active']
    search_fields = ['id', 'name', 'description']


class IssuedLicenseAdmin(ReadOnlyModelAdmin):
    list_display = [
        'issued_at', 'script_id', 'license_key', 'issued_by',
        'issue_type', 'action', 'expires'
    ]
    list_filter = [
        'issued_at', 'script', 'issued_by',
        'action', 'issue_type', 'demo_lk'
    ]


class TagAdmin(ReadOnlyModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name', 'description']


class CategoryAdmin(ReadOnlyModelAdmin):
    list_display = ['id', 'name', 'description', 'parent']
    search_fields = ['id', 'name', 'description']


admin.site.register(Script, ScriptAdmin)
admin.site.register(IssuedLicense, IssuedLicenseAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Category, CategoryAdmin)
