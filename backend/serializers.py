from rest_framework import serializers
from .models import BookedPackage, PostNavItem, CustomUser

class BookedPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedPackage
        fields = '__all__'
        read_only_fields = ('reservation_number',)
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_email'] = instance.user.email if instance.user else None
        representation['car_model_title'] = instance.car_model.title if instance.car_model else None
        return representation
    

