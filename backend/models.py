from PIL import Image
from django.core.exceptions import ValidationError
from django.db import models
import uuid
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from common.utils import validate_file_extension


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role='customer', **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_alpha_validator = RegexValidator(r'^[a-zA-Z]', message='name must be alphabet')
    first_name = models.CharField(max_length=30, blank=True, null=True, validators=[is_alpha_validator])
    last_name = models.CharField(max_length=30, blank=True, null=True, validators=[is_alpha_validator])
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10,10}$',
                                 message="Phone number must be entered Up to 10 digits allowed")
    phone_number = models.CharField(validators=[phone_regex], max_length=10,
                                    blank=True, null=True, unique=True,
                                    error_messages={
                                        'unique': _("A user with this Phone Number already Registered"), }, )
    role = models.CharField(max_length=20, blank=True, null=True)
    street_address_1 = models.CharField(max_length=250, null=True, blank=True)
    street_address_2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=5, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_img/', validators=[validate_file_extension], null=True,
                                      blank=True)
    social_user_image = models.CharField(max_length=512, null=True, blank=True)
    provider = models.CharField(max_length=64, null=True, blank=True, default='genz40')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_number_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'custom_users'


REVIEW_STATUS = (
    (1, "Approved"),
    (0, "Pending"),
    (2, "Declined")
)


class PostReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, blank=True, null=True, )
    city = models.CharField(max_length=120, blank=True, null=True, )
    rating = models.CharField(max_length=120, blank=True, null=True, )
    review = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True, choices=REVIEW_STATUS, default='0', )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'reviews'


# Blog models.
class PostBlog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    publish = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day, self.slug])

    class Meta:
        db_table = 'blogs'


# Meta data models.
class PostMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, editable=False)
    meta_title = models.CharField(max_length=70)
    meta_keywords = models.CharField(max_length=100, blank=True, null=True)
    meta_desc = models.TextField(blank=True, null=True, max_length=170)
    page_title = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'meta_datas'


class PostNavItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    estimated_delivery = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.is_active:
            self.children.update(is_active=False)

    def get_active_children(self):
        return self.children.filter(is_active=True).order_by('position')

    def get_absolute_url(self):
        return reverse('navitem_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['position']
        db_table = 'nav_items'


def validate_image_count(value):
    if value.nav_item.images.count() >= 10:
        raise ValidationError('You can only upload up to 10 images.')


class PostImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nav_item = models.ForeignKey(PostNavItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            validate_image_count(self)
        super().save(*args, **kwargs)
        if not self.thumbnail:
            self.thumbnail = self.make_thumbnail(self.image)
            super().save(*args, **kwargs)

    def make_thumbnail(self, image, size=(300, 200)):
        from PIL import Image as PILImage
        from io import BytesIO
        from django.core.files.base import ContentFile

        img = Image.open(image).convert('RGB')
        # img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG')
        thumb_file = ContentFile(thumb_io.getvalue(), 'thumb_' + image.name)
        return thumb_file


class PostPackage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nav_item = models.ForeignKey(PostNavItem, on_delete=models.CASCADE, related_name='details')
    name = models.CharField(max_length=100)
    amount = models.IntegerField(blank=True, default=0)
    amount_reserve = models.IntegerField(blank=True, default=0)
    amount_due = models.IntegerField(blank=True, default=0)
    estimated_delivery = models.DateTimeField(default=timezone.now)
    offer_valid = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    image = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['position']
        db_table = 'packages'


class PostPackageDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='package_details')
    service_type = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.package.name} - {self.service_type}"

    class Meta:
        ordering = ['position']
        db_table = 'package_details'


class PostPackageFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='feature_details')
    name = models.CharField(max_length=100)
    amount = models.IntegerField(blank=True, default=0)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.package.name} - {self.name}"

    class Meta:
        ordering = ['position']
        db_table = 'package_features'


class PostPart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='part_details')
    parts_name = models.CharField(max_length=70)
    parts_desc = models.TextField(blank=True, null=True, max_length=170)
    amount = models.IntegerField(blank=True, default=0)
    image = models.ImageField(upload_to='parts_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'parts'


class PostCharging(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='charging_details')
    charging_name = models.CharField(max_length=70)
    charging_desc = models.TextField(blank=True, null=True, max_length=170)
    amount = models.IntegerField(blank=True, default=0)
    image = models.ImageField(upload_to='charging_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'charging'


class PostAccessories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='accessories_details')
    accessories_name = models.CharField(max_length=70)
    accessories_desc = models.TextField(blank=True, null=True, max_length=170)
    amount = models.IntegerField(blank=True, default=0)
    image = models.ImageField(upload_to='accessories_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'accessories'


class PostPaint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='paint_details')
    paint_name = models.CharField(max_length=70)
    paint_desc = models.TextField(blank=True, null=True, max_length=170)
    amount = models.IntegerField(blank=True, default=0)
    image = models.ImageField(upload_to='paint_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'paint'


class PostWheels(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(PostPackage, on_delete=models.CASCADE, related_name='wheels_details')
    wheel_name = models.CharField(max_length=70)
    wheel_desc = models.TextField(blank=True, null=True, max_length=170)
    wheel_amount = models.IntegerField(blank=True, default=0)
    wheel_size = models.CharField(max_length=64, blank=True, default=0)
    wheel_color = models.CharField(max_length=64, blank=True, default=0)
    wheel_offset = models.CharField(max_length=64, blank=True, default=0)
    image = models.ImageField(upload_to='wheels_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['position']
        db_table = 'wheels'


class PostLandingPageImages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nav_item = models.ForeignKey(PostNavItem, on_delete=models.CASCADE, related_name='landing_images')
    title = models.CharField(max_length=100)
    title_data = models.CharField(max_length=100, blank=True)
    subtitle = models.CharField(max_length=400)
    section = models.IntegerField(blank=True, default=0)
    tag = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='landing_pages_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.title

    class Meta:
        ordering = ['position']
        db_table = 'landing_pages_images'


class PostSubscribers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.id

    class Meta:
        db_table = 'subscribers'


class PostCommunity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='communities')
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.id

    class Meta:
        db_table = 'community'


class PostCommunityJoiners(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='community_joiners')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.id

    class Meta:
        db_table = 'community_joiners'


class PostContactUs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.IntegerField(blank=True, null=True)
    car = models.CharField(max_length=30, blank=True, null=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.id

    class Meta:
        db_table = 'contact_us'