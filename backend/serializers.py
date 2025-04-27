from rest_framework import serializers
from .models import (
    PostLandingPageImages,
    PostNavItem,
    PostPackage,
    DynamicPackages,
    FeaturesSection,
    PackageFeatureRoller,
    PackageFeatureRollerPlus,
    PackageFeatureBuilder,
    BookedPackage,
    CustomUser,
)

class LandingPageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLandingPageImages
        fields = ['id', 'section', 'title', 'subtitle', 'image', 'web_image', 'is_active', 'position']

class NavItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostNavItem
        fields = ['id', 'title', 'slug', 'content', 'is_active', 'position']

# class PackageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PostPackage
#         fields = ['id', 'name', 'description', 'amount_due', 'image', 'is_active', 'position']

class CarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostNavItem
        fields = ['id', 'title', 'slug', 'content', 'estimated_delivery', 'is_active']

class DynamicPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicPackages
        fields = ['id', 'name', 'description', 'reserveAmount', 'package_type', 'baseAmount', 'discountAmount']

class FeatureSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturesSection
        fields = ['id', 'name', 'description']

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'id', 'name', 'type', 'price', 'option1', 'option2', 
            'option1_price', 'option2_price', 'checked', 'disabled', 
            'included', 'in_mark_I', 'in_mark_II', 'in_mark_IV'
        ]

    def __init__(self, *args, **kwargs):
        feature_type = kwargs.pop('feature_type', None)
        if feature_type == 'roller':
            self.Meta.model = PackageFeatureRoller
        elif feature_type == 'rollerplus':
            self.Meta.model = PackageFeatureRollerPlus
        elif feature_type == 'builder':
            self.Meta.model = PackageFeatureBuilder
        super().__init__(*args, **kwargs)

class BookedPackageSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    car_model_title = serializers.CharField(source='car_model.title', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)

    class Meta:
        model = BookedPackage
        fields = [
            'id', 'reservation_number', 'user_email', 'car_model_title', 
            'title', 'package_name', 'price', 'status', 'build_type', 
            'build_status', 'build_payment_amount', 'build_message', 
            'remaining_price', 'initial_payment_percentage', 
            'midway_payment_percentage', 'final_payment_percentage', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ('reservation_number',)


class PackageFeatureRollerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageFeatureRoller
        fields = '__all__'  # or you can manually list fields if you want more control


class PackageFeatureRollerPlusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageFeatureRollerPlus
        fields = '__all__'


class PackageFeatureBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageFeatureBuilder
        fields = '__all__'