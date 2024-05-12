from rest_framework import serializers
from vendor_models.models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
class VendorCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )
    contact_details = serializers.CharField(
        error_messages={
            'required': 'Contact details are required.',
        }
    )
    address = serializers.CharField(
        error_messages={
            'required': 'Address is required.',
        }
    )

    class Meta:
        model = Vendor
        exclude = ['vendor_code', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']

    def create(self, validated_data):
        return Vendor.objects.create(
            name=validated_data.get('name'),
            contact_details=validated_data.get('contact_details'),
            address=validated_data.get('address')
        )

class VendorListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email')
    contact_details = serializers.CharField(source='user.contact_details')
    address = serializers.CharField(source='user.address')
    class Meta:
        model = Vendor
        fields = ['name','email', 'contact_details', 'address', 'vendor_code']

class VendorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email')
    contact_details = serializers.CharField(source='user.contact_details')
    address = serializers.CharField(source='user.address')
    class Meta:
        model = Vendor
        fields = ['name','email', 'contact_details', 'address', 'vendor_code']
from rest_framework import serializers
from rest_framework import serializers

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_name', 'available_quantity']

class VendorDetailByIdSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email')
    items = ItemSerializer(many=True, source='items.all')
    contact_details = serializers.CharField(source='user.contact_details')
    address = serializers.CharField(source='user.address')

    class Meta:
        model = Vendor
        fields = ['id', 'name','email', 'contact_details', 'address', 'vendor_code', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate',  'items']

class VendorDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email')
    contact_details = serializers.CharField(source='user.contact_details')
    address = serializers.CharField(source='user.address')

    class Meta:
        model = Vendor
        fields = ['id', 'name','email', 'contact_details', 'address', 'vendor_code', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate', ]

# class PurchaseOrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PurchaseOrder
#         fields = '__all__'

class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']


class BuyerSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
            'blank': 'Email cannot be blank',
        }
    )

    password = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 8 characters long.',
        },
        write_only=True,
        min_length=8  # Minimum length validation
    )

    confirm_password = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Confirm Password is required.',
        },
        write_only=True
    )

    name = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Name is required.',
            'blank': 'Name cannot be blank',
        }
    )
    address = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Address is required.',
            'blank': 'Address cannot be blank',
        }
    )
    contact_details = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Contact Details are required.',
            'blank': 'Contact Details cannot be blank',
        }
    )
    class Meta:
        model = User
        fields = ['name', 'email', 'contact_details','address' ,'password', 'confirm_password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email has already been registered.")

        if password != confirm_password:
            raise serializers.ValidationError("The password fields do not match.")

        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        name = validated_data.get('name')  # Add this line to retrieve name from validated data
        contact_details = validated_data.get('contact_details')  # Add this line to retrieve name from validated data
        address = validated_data.get('address')  # Add this line to retrieve name from validated data

        user = User.objects.create_user(email=email, password=password, name=name, user_type='Buyer',address=address,contact_details=contact_details)
        Buyer.objects.create(user=user)
        return user


class VendorSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.',
            'blank': 'Email cannot be blank',
        }
    )

    password = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 8 characters long.',
        },
        write_only=True,
        min_length=8  # Minimum length validation
    )

    confirm_password = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Confirm Password is required.',
        },
        write_only=True
    )

    name = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Name is required.',
            'blank': 'Name cannot be blank',
        }
    )

    contact_details = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Contact details are required.',
            'blank': 'Contact details cannot be blank',
        }
    )

    address = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Address is required.',
            'blank': 'Address cannot be blank',
        }
    )

    class Meta:
        model = VendorManagementUser
        fields = ['name', 'email', 'password', 'confirm_password', 'contact_details', 'address']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if VendorManagementUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email has already been registered.")

        if password != confirm_password:
            raise serializers.ValidationError("The password fields do not match.")

        return data

    def create(self, validated_data):
        name = validated_data.get('name')
        email = validated_data.get('email')
        password = validated_data.get('password')
        contact_details = validated_data.get('contact_details')
        address = validated_data.get('address')

        # Create a VendorManagementUser instance
        user = VendorManagementUser.objects.create_user(email=email, name=name, password=password,contact_details=contact_details, address=address)

        # Create a Vendor instance
        Vendor.objects.create(user=user)

        return user

from rest_framework import serializers

class VendorProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    contact_details = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid email or password.')

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')

            return user
        else:
            raise serializers.ValidationError('Email and password are required.')


class ItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_name', 'available_quantity']

    def validate_available_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'item_name', 'available_quantity']

from django.utils import timezone
from datetime import timedelta
class PurchaseOrderSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(write_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['item_id', 'quantity']

    def validate_item_id(self, value):
        try:
            item = Item.objects.get(id=value)
            return item
        except Item.DoesNotExist:
            raise serializers.ValidationError("Item with this ID does not exist.")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    def create(self, validated_data):
        item = validated_data.pop('item_id')
        quantity = validated_data['quantity']
        if quantity > item.available_quantity:
            raise serializers.ValidationError("Selected quantity is greater than available quantity.")
        # Update available quantity of the item
        item.available_quantity -= quantity
        item.save()

        validated_data['vendor'] = item.vendor
        validated_data['buyer'] = self.context['request'].user.buyer
        validated_data['order_date'] = timezone.now()
        validated_data['delivery_date'] = timezone.now() + timedelta(days=7)
        validated_data['items'] = item
        return PurchaseOrder.objects.create(**validated_data)


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class BuyerProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email')
    contact_details = serializers.CharField(source='user.contact_details')
    address = serializers.CharField(source='user.address')

    class Meta:
        model = Buyer
        fields = ['id', 'name', 'email', 'contact_details', 'address']


class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.user.name', read_only=True)

    class Meta:
        model = HistoricalPerformance
        fields = ['id', 'vendor_name','date', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time', 'fulfillment_rate']
