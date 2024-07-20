from django.contrib import admin
from backend.models import CustomUser, PostCommunity, PostReview, PostBlog, PostMeta, PostNavItem, PostPackage, PostPackageDetail, \
    PostPackageFeature, PostPart, PostCharging, PostAccessories, PostPaint, PostImage, PostSubscribers, PostWheels, PostLandingPageImages

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(PostReview)
admin.site.register(PostBlog)
admin.site.register(PostMeta)
admin.site.register(PostImage)
admin.site.register(PostWheels)
admin.site.register(PostLandingPageImages)
admin.site.register(PostSubscribers)
admin.site.register(PostCommunity)

from adminsortable2.admin import SortableAdminMixin


class PostNavItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'parent', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    list_filter = ('title', 'is_active', 'parent')
    search_fields = ('title', 'title', 'content')

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            super().save_model(request, obj, form, change)
        else:
            print("===========", form.errors)  # Print form errors to console for debugging


admin.site.register(PostNavItem, PostNavItemAdmin)


class PackageInline(admin.TabularInline):
    model = PostPackage
    extra = 1


class PackageDetailsInline(admin.TabularInline):
    model = PostPackageDetail
    extra = 1


class PackageFeatureInline(admin.TabularInline):
    model = PostPackageFeature
    extra = 1


class PackagePartsInline(admin.TabularInline):
    model = PostPart
    extra = 1


class PackageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('nav_item', 'name', 'is_active', 'position')
    search_fields = ('nav_item__name', 'description')
    inlines = [PackageDetailsInline, PackageFeatureInline]


class PackageDetailAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'service_type', 'description', 'is_active', 'position')
    search_fields = ('package__title', 'service_type', 'description')


class PackageFeatureAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'name', 'value', 'is_active', 'position')
    search_fields = ('package__title', 'name', 'value')


class PackagePartsAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'parts_name', 'position')
    search_fields = ('package__title', 'parts_name')


class PackageChargingAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'charging_name', 'position')
    search_fields = ('package__title', 'charging_name')


class PackageAccessoriesAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'accessories_name', 'position')
    search_fields = ('package__title', 'accessories_name')


class PackagePaintAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('package', 'paint_name', 'position')
    search_fields = ('package__title', 'paint_name')


admin.site.register(PostPackage, PackageAdmin)
admin.site.register(PostPackageDetail, PackageDetailAdmin)
admin.site.register(PostPackageFeature, PackageFeatureAdmin)
admin.site.register(PostPart, PackagePartsAdmin)
admin.site.register(PostCharging, PackageChargingAdmin)
admin.site.register(PostAccessories, PackageAccessoriesAdmin)
admin.site.register(PostPaint, PackagePaintAdmin)