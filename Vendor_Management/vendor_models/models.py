from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from .model_manager import VendorManagementUserManager
from django.contrib.auth.models import PermissionsMixin
import random
import string
from django.core.validators import MinValueValidator, MaxValueValidator
class CommonTimePicker(models.Model):
    """
    An abstract model in Django that provides two fields, `created_at` and `updated_at`, which automatically record the date and time when an object is created or updated.
    """

    created_at = models.DateTimeField("Created Date", auto_now_add=True)
    updated_at = models.DateTimeField("Updated Date", auto_now=True)

    class Meta:
        abstract = True

class VendorManagementUser(AbstractBaseUser,PermissionsMixin, CommonTimePicker):
    USER_TYPE_CHOICES = (
        ('Buyer', 'Buyer'),
        ('Vendor', 'Vendor'),
    )
    user_type = models.CharField("User Type", max_length=10, choices=USER_TYPE_CHOICES)
    name = models.CharField("Name", max_length=255)
    email = models.EmailField("Email Address", unique=True)
    password = models.CharField("Password", max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = VendorManagementUserManager()


    is_superuser = models.BooleanField("Super User", default=False)
    is_active = models.BooleanField("Active", default=True)
    is_staff = models.BooleanField("Staff",default=False)
    def __str__(self):
        return f'{self.user_type}_{self.name}_{self.email} '

class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor')
    vendor_code = models.CharField(max_length=50, unique=True, blank=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.user.name}_{self.user.email} '

    def generate_vendor_code(self):
        vendor_id = str(self.id)
        random_component = ''.join(random.choices(string.digits + string.ascii_letters, k=4))
        vendor_code = f"V_{vendor_id}_{random_component}"
        return vendor_code
    
    def save(self, *args, **kwargs):
        if not self.vendor_code:
            self.vendor_code = self.generate_vendor_code()
        super().save(*args, **kwargs)



class Buyer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer')

    def __str__(self):
        return f'{self.user.name}_{self.user.email} '

class Item(CommonTimePicker):
    
    item_name = models.CharField("Item Name",max_length=255, blank=True, null=True,db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='items',db_index=True)
    available_quantity = models.PositiveIntegerField("Quantity")
    def __str__(self):
        return  f'{self.item_name} selling by {self.vendor.user.name} '
    class Meta:
        ordering = ['-id']

class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=100, unique=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    items = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1),])
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'),('acknowledged', 'Acknowledged') ,('issued','Issued'),('completed', 'Completed'), ('canceled', 'Canceled')], default='pending')
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(blank=True, null=True)
    acknowledgment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.items.item_name} ordered by {self.buyer.user.name} and sell by {self.vendor.user.name} '

    def generate_po_number(self):
        po_id = str(self.vendor.id)  # Use vendor's ID
        random_component = ''.join(random.choices(string.digits + string.ascii_letters, k=4))
        po_number = f"V_{po_id}_{random_component}"
        return po_number

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self.generate_po_number()
        super().save(*args, **kwargs)


class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)


    def __str__(self):
        return f"{self.vendor.user.name} - {self.date}"
