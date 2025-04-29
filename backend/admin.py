from django.contrib import admin
from backend.models import CustomUser, PostCommunity, PostReview, PostBlog, PostMeta, PostNavItem, PostPackage, PostPackageDetail, \
    PostPackageFeature, PostPart, PostCharging, PostAccessories, PostPaint, PostImage, PostSubscribers, PostWheels, PostLandingPageImages, PostPayment, PostOrderStatus, PostSubStatus,\
    CarConfiguration,BookedPackage,BookedPackageImage, DynamicPackages, FeaturesSection,PackageFeatureRoller, PackageFeatureRollerPlus, PackageFeatureBuilder, \
    PostCommunityJoiners,PostContactUs, ReservationFeaturesPayment, ReservationNewFeatures 


from django.contrib import messages


admin.site.register(CustomUser)
admin.site.register(PostReview)
admin.site.register(PostBlog)
admin.site.register(PostMeta)
admin.site.register(PostImage)
admin.site.register(PostWheels)
admin.site.register(PostLandingPageImages)
admin.site.register(PostSubscribers)
admin.site.register(PostCommunity)
admin.site.register(PostPayment)
admin.site.register(PostOrderStatus)
admin.site.register(PostSubStatus)
admin.site.register(CarConfiguration)
admin.site.register(BookedPackageImage)
admin.site.register(DynamicPackages)
admin.site.register(FeaturesSection)
admin.site.register(PackageFeatureRollerPlus)
admin.site.register(PackageFeatureBuilder)
admin.site.register(PostCommunityJoiners)
admin.site.register(PostContactUs)
admin.site.register(ReservationNewFeatures)
admin.site.register(ReservationFeaturesPayment)
@admin.register(PackageFeatureRoller)
class PackageFeatureRollerAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'type', 'price', 'checked', 'disabled')
    list_filter = ('section', 'type', 'checked', 'disabled', 'in_mark_I', 'in_mark_II', 'in_mark_IV')
    search_fields = ('name',)
    actions = ['copy_to_roller_plus', 'copy_to_builder']
    
    def copy_to_roller_plus(self, request, queryset):
        count = 0
        for feature in queryset:
            if not PackageFeatureRollerPlus.objects.filter(name=feature.name, section=feature.section).exists():
                roller_plus_feature = PackageFeatureRollerPlus(
                    section=feature.section,
                    name=feature.name,
                    type=feature.type,
                    price=feature.price,
                    option1=feature.option1,
                    option2=feature.option2,
                    option1_price=feature.option1_price,
                    option2_price=feature.option2_price,
                    checked=feature.checked,
                    disabled=feature.disabled,
                    in_mark_I=feature.in_mark_I,
                    in_mark_II=feature.in_mark_II,
                    in_mark_IV=feature.in_mark_IV
                )
                roller_plus_feature.save()
                count += 1
        messages.success(request, f'Successfully copied {count} features to Roller Plus')
    
    copy_to_roller_plus.short_description = "Copy selected features to Roller Plus"
    
    def copy_to_builder(self, request, queryset):
        count = 0
        for feature in queryset:
            if not PackageFeatureBuilder.objects.filter(name=feature.name, section=feature.section).exists():
                builder_feature = PackageFeatureBuilder(
                    section=feature.section,
                    name=feature.name,
                    type=feature.type,
                    price=feature.price,
                    option1=feature.option1,
                    option2=feature.option2,
                    option1_price=feature.option1_price,
                    option2_price=feature.option2_price,
                    checked=feature.checked,
                    disabled=feature.disabled,
                    in_mark_I=feature.in_mark_I,
                    in_mark_II=feature.in_mark_II,
                    in_mark_IV=feature.in_mark_IV
                )
                builder_feature.save()
                count += 1
        messages.success(request, f'Successfully copied {count} features to Builder')
    
    copy_to_builder.short_description = "Copy selected features to Builder"

@admin.register(BookedPackage)
class BookedPackageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car_model', 'title', 'price', 'status']
    search_fields = ['title', 'user__username', 'car_model__title']
    list_filter = ['status']
    ordering = ['-id']
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