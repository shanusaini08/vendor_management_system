from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from apis.serializers import  *
from vendor_models.models import Vendor , PurchaseOrder
from django.db.models import Count, Avg, ExpressionWrapper, F, FloatField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
import string
from django.shortcuts import get_object_or_404
import datetime
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny
from rest_framework import serializers, status
from .serializers import BuyerSignupSerializer
from rest_framework import status
from .serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from vendor_models.utils import (
    calculate_on_time_delivery_rate,
    calculate_quality_rating_avg,
    calculate_average_response_time,
    calculate_fulfillment_rate
)
from django.utils import timezone
User = get_user_model()
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from .serializers import VendorProfileUpdateSerializer

class BuyerSignupView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
         request_body=BuyerSignupSerializer,
        responses={
            201: openapi.Response(description='Created', schema=BuyerSignupSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = BuyerSignupSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Buyer created successfully.',
                        'responseData': serializer.data,
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': [f"{error[1][0]}" for error in dict(serializer.errors).items()][0],
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except serializers.ValidationError as e:
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': [f"{error[1][0]}" for error in dict(e).items()][0],
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print("BuyerSignupView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VendorSignupView(APIView):
    @swagger_auto_schema(
         request_body=VendorSignupSerializer,
        responses={
            201: openapi.Response(description='Created', schema=VendorSignupSerializer),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = VendorSignupSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Vendor created successfully.',
                        'responseData': serializer.data,
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': [f"{error[1][0]}" for error in dict(serializer.errors).items()][0],
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print("VendorSignupView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class VendorView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="Name of the vendor", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page Number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('size', openapi.IN_QUERY, description="Elements per page", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description='OK', schema=VendorCreateSerializer(many=True)),
            500: "Internal Server Error"
        }
    )
    def get(self, request):
        """
        List all vendors.
        """
        try:
            name = request.query_params.get('name')
            vendors = Vendor.objects.all()
            if name:
                vendors = vendors.filter(user__name__icontains=name)

            page = request.query_params.get('page', 1)
            size = request.query_params.get('size', 10)

            paginator = Paginator(vendors, size)
            try:
                vendors = paginator.page(page)
            except PageNotAnInteger:
                vendors = paginator.page(1)
            except EmptyPage:
                vendors = paginator.page(paginator.num_pages)

            serializer = VendorDetailSerializer(vendors, many=True)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendors retrieved successfully.',
                    'responseData': serializer.data,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print("VendorListView (GET) Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong",
                    'responseData': None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VendorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING,required=True),
        ],
        responses={
            200: openapi.Response(description='OK', schema=VendorSerializer),
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def get(self, request):
        """
        Retrieve the details of the authenticated vendor.
        """
        try:
            vendor = request.user.vendor
            serializer = VendorDetailByIdSerializer(vendor)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor details retrieved successfully.',
                    'responseData': serializer.data,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print("VendorDetailView (GET) Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong",
                    'responseData': None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING,required=True),
            openapi.Parameter('name', openapi.IN_QUERY, description="Name of the vendor", type=openapi.TYPE_STRING),
            openapi.Parameter('email', openapi.IN_QUERY, description="Email address", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Password", type=openapi.TYPE_STRING),
            openapi.Parameter('contact_details', openapi.IN_QUERY, description="Contact details", type=openapi.TYPE_STRING),
            openapi.Parameter('address', openapi.IN_QUERY, description="Address", type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Vendor account updated successfully.',
            400: 'Bad request.',
            401: 'Unauthorized.',
            404: 'Vendor not found.',
            500: 'Internal server error.'
        }
    )
    def put(self, request):
        try:
            vendor = request.user.vendor  # Assuming vendor is logged in
            name = request.query_params.get('name', vendor.user.name)
            email = request.query_params.get('email', vendor.user.email)
            password = request.query_params.get('password')
            contact_details = request.query_params.get('contact_details', vendor.user.contact_details)
            address = request.query_params.get('address', vendor.user.address)

            # Update user details
            vendor.user.name = name
            vendor.user.email = email
            if password:
                vendor.user.set_password(password)  # Set password securely
            vendor.user.contact_details = contact_details
            vendor.user.address = address
            vendor.user.save()

            # Update vendor details
            vendor.save()

            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Vendor account updated successfully.',
                    'responseData': {
                        'name': name,
                        'email': email,
                        'contact_details': contact_details,
                        'address': address
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING,required=True),
        ],
        responses={
            204: "No Content",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def delete(self, request):
        """
        Delete the authenticated vendor's account.
        """
        try:
            vendor = request.user.vendor
            vendor.delete()
            return Response(
                {
                    'responseCode': status.HTTP_204_NO_CONTENT,
                    'responseMessage': 'Vendor account deleted successfully.',
                    'responseData': None,
                },
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            print("VendorDetailView (DELETE) Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': "Something went wrong",
                    'responseData': None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# class PurchaseOrderDetailView(APIView):
#     @swagger_auto_schema(
#         responses={
#             200: openapi.Response(description='OK', schema=PurchaseOrderSerializer),
#             404: "Not Found",
#             500: "Internal Server Error"
#         }
#     )
#     def get(self, request, po_id):
#         """
#         Retrieve details of a specific purchase order.
#         """
#         try:
#             purchase_order = PurchaseOrder.objects.get(id=po_id)
#             serializer = PurchaseOrderSerializer(purchase_order)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except PurchaseOrder.DoesNotExist:
#             return Response("Purchase order not found", status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             print("PurchaseOrderDetailView (GET) Error -->", e)
#             return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     @swagger_auto_schema(
#         request_body=PurchaseOrderSerializer,
#         responses={
#             200: openapi.Response(description='OK', schema=PurchaseOrderSerializer),
#             400: "Bad Request",
#             404: "Not Found",
#             500: "Internal Server Error"
#         }
#     )
#     def put(self, request, po_id):
#         """
#         Update a purchase order.
#         """
#         try:
#             purchase_order = PurchaseOrder.objects.get(id=po_id)
#             serializer = PurchaseOrderSerializer(purchase_order, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except PurchaseOrder.DoesNotExist:
#             return Response("Purchase order not found", status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             print("PurchaseOrderDetailView (PUT) Error -->", e)
#             return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     @swagger_auto_schema(
#         responses={
#             204: "No Content",
#             404: "Not Found",
#             500: "Internal Server Error"
#         }
#     )
#     def delete(self, request, po_id):
#         """
#         Delete a purchase order.
#         """
#         try:
#             purchase_order = PurchaseOrder.objects.get(id=po_id)
#             purchase_order.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except PurchaseOrder.DoesNotExist:
#             return Response("Purchase order not found", status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             print("PurchaseOrderDetailView (DELETE) Error -->", e)
#             return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py


class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(description='OK', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response(description='Bad Request', schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        'responseCode': status.HTTP_200_OK,
                        'responseMessage': 'Login successful.',
                        'responseData': {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                        }
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Bad Request',
                    'responseData': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ItemCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING, required=True)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'item_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the item'),
                'available_quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Available quantity of the item'),
            }
        ),
        responses={
            201: 'Item created successfully.',
            400: 'Failed to create item.'
        }
    )
    def post(self, request):
        try:
            serializer = ItemCreateSerializer(data=request.data)
            if serializer.is_valid():
                vendor = Vendor.objects.get(user=request.user)
                serializer.save(vendor=vendor)
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Item created successfully.',
                        'responseData': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        'responseCode': status.HTTP_400_BAD_REQUEST,
                        'responseMessage': 'Failed to create item.',
                        'responseData': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Vendor.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Vendor does not exist.',
                    'responseData': None
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': str(e),
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer <token>', required=False),
            openapi.Parameter('item_name', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by item name', required=False),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number', required=False),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page size', required=False),
        ],
        responses={
            200: "Items retrieved successfully",
            400: "Bad Request",
            500: "Internal Server Error",
        }
    )
    def get(self, request):
        try:
            # Get query parameters
            item_name = request.query_params.get('item_name')
            page_number = request.query_params.get('page')
            page_size = request.query_params.get('page_size')

            # Check if bearer token is provided
            if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
                # Filter items by item name if provided
                vendor = request.user.vendor
                items = Item.objects.filter(vendor=vendor)
                if item_name:
                    items = items.filter(item_name__icontains=item_name)
            else:
                # No bearer token provided, return all items
                items = Item.objects.all()
                if item_name:
                    items = items.filter(item_name__icontains=item_name)

            # Pagination
            paginator = Paginator(items, page_size) if page_size else Paginator(items, 10)
            page_obj = paginator.get_page(page_number)

            # Serialize items
            serializer = ItemSerializer(page_obj, many=True)

            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Items retrieved successfully.',
                    'responseData': serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer <token>', required=True),
            openapi.Parameter('item_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the item to be updated', required=True),
            openapi.Parameter('item_name', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='New name of the item'),
            openapi.Parameter('available_quantity', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='New available quantity of the item'),
        ],
        responses={
            200: "Item updated successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
            500: "Internal Server Error",
        }
    )
    def put(self, request):
        try:
            item_id = request.query_params.get('item_id')
            if not item_id:
                return Response(
                    {'responseCode': status.HTTP_400_BAD_REQUEST, 'responseMessage': 'Item ID is required in the query parameters.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                return Response(
                    {'responseCode': status.HTTP_404_NOT_FOUND, 'responseMessage': 'Item does not exist.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            item_name = request.query_params.get('item_name', item.item_name)
            available_quantity = request.query_params.get('available_quantity', item.available_quantity)

            # Update item details
            if item_name:
                item.item_name = item_name
            if available_quantity is not None:
                item.available_quantity = available_quantity
            item.save()

            return Response(
                {'responseCode': status.HTTP_200_OK, 'responseMessage': 'Item updated successfully.'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print("ItemUpdateView Error -->", e)
            return Response(
                {'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR, 'responseMessage': 'Something went wrong! Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description='Bearer <token>', type=openapi.TYPE_STRING),
            openapi.Parameter('item_id', openapi.IN_PATH, description='ID of the item to be deleted', type=openapi.TYPE_INTEGER)
        ],
        responses={
            204: 'Item deleted successfully.',
            400: 'Bad Request',
            403: 'Forbidden - You are not authorized to delete this item.',
            404: 'Not Found - Item does not exist or does not belong to you.',
            500: 'Internal Server Error'
        }
    )
    def delete(self, request, item_id):  # Add item_id parameter
        try:
            # Get the item by ID
            item = Item.objects.get(id=item_id)

            # Check if the logged-in user is the owner of the item (assuming user is a vendor)
            if item.vendor.user == request.user:
                item.delete()
                return Response(
                    {'responseCode': status.HTTP_204_NO_CONTENT, 'responseMessage': 'Item deleted successfully.'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'responseCode': status.HTTP_403_FORBIDDEN, 'responseMessage': 'Forbidden - You are not authorized to delete this item.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        except Item.DoesNotExist:
            return Response(
                {'responseCode': status.HTTP_404_NOT_FOUND, 'responseMessage': 'Not Found - Item does not exist or does not belong to you.'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR, 'responseMessage': 'Internal Server Error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PurchaseOrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING, required=True)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'item_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the item to order'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of the item to order'),
            }
        ),
        responses={
            201: 'Purchase order created successfully.',
            400: 'Failed to create purchase order.'
        }
    )
    def post(self, request):
        try:
            serializer = PurchaseOrderSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                purchase_order = serializer.save()
                detail_serializer = PurchaseOrderDetailSerializer(purchase_order)
                return Response(
                    {
                        'responseCode': status.HTTP_201_CREATED,
                        'responseMessage': 'Purchase order created successfully.',
                        'responseData': detail_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {
                        'responseCode': status.HTTP_400_BAD_REQUEST,
                        'responseMessage': 'Failed to create purchase order.',
                        'responseData': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': str(e),
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('item_name', openapi.IN_QUERY, description="Filter by item name", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER, required=False)
        ],
        responses={
            200: 'Purchase orders retrieved successfully.',
            400: 'Failed to retrieve purchase orders.'
        }
    )
    def get(self, request):
        try:
            buyer = request.user.buyer
            purchase_orders = PurchaseOrder.objects.filter(buyer=buyer)
            
            # Filtering by item name if provided
            item_name = request.query_params.get('item_name')
            if item_name:
                purchase_orders = purchase_orders.filter(items__item_name__icontains=item_name)

            # Pagination
            page_number = request.query_params.get('page')
            page_size = request.query_params.get('page_size')
            paginator = Paginator(purchase_orders, page_size) if page_size else Paginator(purchase_orders, 10)
            page_obj = paginator.get_page(page_number)

            serializer = PurchaseOrderDetailSerializer(page_obj, many=True)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase orders retrieved successfully.',
                    'responseData': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': str(e),
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BuyerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, type=openapi.TYPE_STRING, description='Bearer <token>', required=True),
        ],
        responses={
            200: 'Buyer profile retrieved successfully.',
            401: 'Unauthorized',
            404: 'Buyer profile does not exist.',
            500: 'Internal Server Error',
        }
    )
    def get(self, request):
        try:
            buyer = request.user.buyer
            serializer = BuyerProfileSerializer(buyer)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'response_message': 'Buyer profile retrieved successfully.',
                    'response_data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Buyer.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'response_message': 'Buyer profile does not exist.',
                    'response_data': None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print("BuyerProfileView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'response_message': 'Something went wrong! Please try again.',
                    'response_data': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING),
            openapi.Parameter('name', openapi.IN_QUERY, description="Name of the buyer", type=openapi.TYPE_STRING),
            openapi.Parameter('email', openapi.IN_QUERY, description="Email address", type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description="Password", type=openapi.TYPE_STRING),
            openapi.Parameter('contact_details', openapi.IN_QUERY, description="Contact details", type=openapi.TYPE_STRING),
            openapi.Parameter('address', openapi.IN_QUERY, description="Address", type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Buyer profile updated successfully.',
            400: 'Bad request.',
            401: 'Unauthorized.',
            404: 'Buyer not found.',
            500: 'Internal server error.'
        }
    )
    def put(self, request):
        try:
            buyer = request.user.buyer  # Assuming buyer is logged in
            name = request.query_params.get('name', buyer.user.name)
            email = request.query_params.get('email', buyer.user.email)
            password = request.query_params.get('password')
            contact_details = request.query_params.get('contact_details', buyer.user.contact_details)
            address = request.query_params.get('address', buyer.user.address)

            # Update user details
            buyer.user.name = name
            buyer.user.email = email
            if password:
                buyer.user.set_password(password)  # Set password securely
            buyer.user.contact_details = contact_details
            buyer.user.address = address
            buyer.user.save()

            # Update buyer details
            buyer.save()

            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Buyer profile updated successfully.',
                    'responseData': {
                        'name': name,
                        'email': email,
                        'contact_details': contact_details,
                        'address': address
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
            500: "Internal Server Error",
        }
    )
    def delete(self, request):
        try:
            buyer = request.user.buyer
            buyer.user.delete()
            buyer.delete()
            return Response(
                {
                    'responseCode': status.HTTP_204_NO_CONTENT,
                    'response_message': 'Buyer account deleted successfully.',
                    'response_data': None
                },
                status=status.HTTP_204_NO_CONTENT
            )
        except AttributeError:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'response_message': 'Buyer account not found.',
                    'response_data': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'response_message': 'Buyer account does not exist.',
                    'response_data': None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print("BuyerDeleteView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'response_message': 'Something went wrong! Please try again.',
                    'response_data': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



from django.core.exceptions import ObjectDoesNotExist

class BuyerDeleteView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
            500: "Internal Server Error",
        }
    )
    def delete(self, request):
        try:
            buyer = request.user.buyer
            buyer.user.delete()
            buyer.delete()
            return Response(
                {
                    'responseCode': status.HTTP_204_NO_CONTENT,
                    'response_message': 'Buyer account deleted successfully.',
                    'response_data': None
                },
                status=status.HTTP_204_NO_CONTENT
            )
        except AttributeError:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'response_message': 'Buyer account not found.',
                    'response_data': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'response_message': 'Buyer account does not exist.',
                    'response_data': None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print("BuyerDeleteView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'response_message': 'Something went wrong! Please try again.',
                    'response_data': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BuyerListView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('buyer_name', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by buyer name', required=False),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page number', required=False),
            openapi.Parameter('page_size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page size', required=False),
        ],
        responses={
            200: openapi.Response(description='OK', schema=BuyerProfileSerializer(many=True)),
            400: "Bad Request",
            500: "Internal Server Error",
        }
    )
    def get(self, request):
        try:
            buyer_name = request.query_params.get('buyer_name')
            buyers = Buyer.objects.all()

            # Filter by buyer name if provided
            if buyer_name:
                buyers = buyers.filter(user__name__icontains=buyer_name)

            # Pagination
            page_number = request.query_params.get('page')
            page_size = request.query_params.get('page_size')

            paginator = Paginator(buyers, page_size) if page_size else Paginator(buyers, 10)

            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            serializer = BuyerProfileSerializer(page_obj, many=True)

            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Buyers retrieved successfully.',
                    'responseData': serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print("BuyerListView Error -->", e)
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Something went wrong! Please try again.',
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelPurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description='Bearer <token>', type=openapi.TYPE_STRING),
            openapi.Parameter('purchase_order_id', openapi.IN_PATH, description='ID of the purchase order to be canceled', type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: 'Purchase order canceled successfully.',
            400: 'Bad Request',
            403: 'Forbidden - You are not authorized to cancel this purchase order.',
            404: 'Not Found - Purchase order does not exist.',
            409: 'Conflict - Purchase order status is not pending.',
            500: 'Internal Server Error'
        }
    )
    def post(self, request, purchase_order_id):  # Add purchase_order_id argument
        try:
            # Get the purchase order by ID
            purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)

            # Check if the logged-in user is the buyer of the purchase order
            if purchase_order.buyer.user == request.user:
                # Check if the purchase order status is pending
                if purchase_order.status == 'pending':
                    # Set the status to canceled
                    purchase_order.status = 'canceled'
                    purchase_order.save()
                    return Response(
                        {
                            'responseCode': status.HTTP_200_OK,
                            'responseMessage': 'Purchase order canceled successfully.',
                            'responseData': None
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            'responseCode': status.HTTP_409_CONFLICT,
                            'responseMessage': ' Purchase order status is already cancelled or not pending.',
                        },
                        status=status.HTTP_409_CONFLICT
                    )
            else:
                return Response(
                    {
                        'responseCode': status.HTTP_403_FORBIDDEN,
                        'responseMessage': 'Forbidden - You are not authorized to cancel this purchase order.',
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Not Found - Purchase order does not exist.',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class RatePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description='Bearer <token>', type=openapi.TYPE_STRING),
            openapi.Parameter('purchase_order_id', openapi.IN_PATH, description='ID of the purchase order to be rated', type=openapi.TYPE_INTEGER),
            openapi.Parameter('quality_rating', openapi.IN_QUERY, description='Quality rating out of 5 (float with up to 1 decimal point)', type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
        ],
        responses={
            200: 'Purchase order rated successfully.',
            400: 'Bad Request',
            403: 'Forbidden - You are not authorized to rate this purchase order.',
            404: 'Not Found - Purchase order does not exist.',
            409: 'Conflict - Purchase order status is not completed or rating has already been provided.',
            500: 'Internal Server Error'
        }
    )
    def post(self, request, purchase_order_id):
        try:
            # Get the purchase order by ID
            purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)

            # Check if the logged-in user is the buyer of the purchase order
            if purchase_order.buyer.user != request.user:
                return Response(
                    {
                        'responseCode': status.HTTP_403_FORBIDDEN,
                        'responseMessage': 'Forbidden - You are not authorized to rate this purchase order.',
                        'responseData': None
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if the purchase order status is completed
            if purchase_order.status != 'completed':
                return Response(
                    {
                        'responseCode': status.HTTP_409_CONFLICT,
                        'responseMessage': 'Conflict - Purchase order status is not completed.',
                        'responseData': None
                    },
                    status=status.HTTP_409_CONFLICT
                )

            # Check if a rating has already been provided for the purchase order
            if purchase_order.quality_rating is not None:
                return Response(
                    {
                        'responseCode': status.HTTP_409_CONFLICT,
                        'responseMessage': 'Conflict - Rating has already been provided for this purchase order.',
                        'responseData': None
                    },
                    status=status.HTTP_409_CONFLICT
                )

            # Get the quality rating from the query parameters
            quality_rating = request.query_params.get('quality_rating')
            if quality_rating is not None:
                quality_rating = float(quality_rating)
                # Check if quality rating is within the valid range (0-5)
                if 0 <= quality_rating <= 5:
                    # Save the quality rating to the purchase order
                    purchase_order.quality_rating = quality_rating
                    purchase_order.save()
                    calculate_quality_rating_avg(purchase_order.vendor)
                    return Response(
                        {
                            'responseCode': status.HTTP_200_OK,
                            'responseMessage': 'Purchase order rated successfully.',
                            'responseData': None
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    raise ValidationError('Quality rating must be between 0 and 5.')
            else:
                raise ValidationError('Quality rating is required.')

        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Not Found - Purchase order does not exist.',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except ValidationError as e:
            return Response(
                {
                    'responseCode': status.HTTP_400_BAD_REQUEST,
                    'responseMessage': 'Bad Request',
                    'responseData': {'error': str(e)}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': 'Something went wrong! Please try again.'}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class CompletePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description='Bearer <token>', type=openapi.TYPE_STRING),
            openapi.Parameter('purchase_order_id', openapi.IN_PATH, description='ID of the purchase order to be completed', type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: 'Purchase order status updated to "completed".',
            400: 'Bad Request',
            403: 'Forbidden - You are not authorized to complete this purchase order.',
            404: 'Not Found - Purchase order does not exist.',
            409: 'Conflict - Purchase order status is already completed or cancelled.',
            500: 'Internal Server Error'
        }
    )
    def post(self, request, purchase_order_id):
        try:
            # Get the purchase order by ID
            purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)

            # Check if the logged-in user is the vendor of the purchase order
            if purchase_order.vendor.user != request.user:
                return Response(
                    {
                        'responseCode': status.HTTP_403_FORBIDDEN,
                        'responseMessage': 'Forbidden - You are not authorized to complete this purchase order.',
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if the purchase order status is pending or acknowledged
            if purchase_order.status not in ['pending', 'acknowledged', 'issued']:
                return Response(
                    {
                        'responseCode': status.HTTP_409_CONFLICT,
                        'responseMessage': 'Purchase order status is already completed or cancelled.',
                    },
                    status=status.HTTP_409_CONFLICT
                )

            # Update the status of the purchase order to completed
            purchase_order.status = 'completed'
            purchase_order.completed_date = timezone.now()
            purchase_order.save()
            calculate_on_time_delivery_rate(purchase_order.vendor)
            calculate_fulfillment_rate(purchase_order.vendor)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase order status updated to completed.',
                },
                status=status.HTTP_200_OK
            )

        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Not Found - Purchase order does not exist.',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal Server Error',
                    'responseData': {'error': 'Something went wrong! Please try again.'}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class AcknowledgePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Purchase order acknowledged successfully.',
            400: 'Bad request.',
            401: 'Unauthorized.',
            404: 'Purchase order not found.',
            409: 'Purchase order already acknowledged.',
            500: 'Internal server error.'
        }
    )
    def post(self, request, purchase_order_id):
        try:
            vendor = request.user.vendor  # Assuming vendor is logged in
            purchase_orders = PurchaseOrder.objects.get(id=purchase_order_id)

            # Check if the logged-in user is the vendor of the purchase order
            if purchase_orders.vendor.user != request.user:
                return Response(
                    {
                        'responseCode': status.HTTP_403_FORBIDDEN,
                        'responseMessage': 'Forbidden - You are not authorized to complete this purchase order.',
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            purchase_order = get_object_or_404(PurchaseOrder, id=purchase_order_id, vendor=vendor)
            if purchase_order.status == 'acknowledged' or purchase_order.status == 'completed' or purchase_order.status == 'canceled':
                return Response(
                    {
                        'responseCode': status.HTTP_409_CONFLICT,
                        'responseMessage': 'Purchase order already acknowledged or cancelled.',
                    },
                    status=status.HTTP_409_CONFLICT
                )

            purchase_order.status = 'acknowledged'
            purchase_order.acknowledgment_date = timezone.now()
            purchase_order.save()
            print('calculate_average_response_time-STARTS')
            calculate_average_response_time(vendor)
            print('calculate_average_response_time-PASS')
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase order acknowledged successfully.',
                },
                status=status.HTTP_200_OK
            )
        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Purchase order not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal server error.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class IssuePurchaseOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Purchase order issued successfully.',
            400: 'Bad request.',
            401: 'Unauthorized.',
            404: 'Purchase order not found.',
            409: 'Purchase order already issued.',
            500: 'Internal server error.'
        }
    )
    def post(self, request, purchase_order_id):
        try:
            vendor = request.user.vendor  # Assuming vendor is logged in
            purchase_orders = PurchaseOrder.objects.get(id=purchase_order_id)

            # Check if the logged-in user is the vendor of the purchase order
            if purchase_orders.vendor.user != request.user:
                return Response(
                    {
                        'responseCode': status.HTTP_403_FORBIDDEN,
                        'responseMessage': 'Forbidden - You are not authorized to complete this purchase order.',
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            purchase_order = get_object_or_404(PurchaseOrder, id=purchase_order_id, vendor=vendor)

            if purchase_order.status in ['issued', 'acknowledged', 'completed', 'canceled']:
                return Response(
                    {
                        'responseCode': status.HTTP_409_CONFLICT,
                        'responseMessage': 'Purchase order already issued ,acknowledged or cancelled.',
                    },
                    status=status.HTTP_409_CONFLICT
                )
            purchase_order.status = 'issued'
            purchase_order.issue_date = timezone.now()
            purchase_order.save()
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase order issued successfully.',
                },
                status=status.HTTP_200_OK
            )
        except PurchaseOrder.DoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Purchase order not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal server error.',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PurchaseOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer token", type=openapi.TYPE_STRING),
            openapi.Parameter('buyer_name', openapi.IN_QUERY, description="Filter by buyer name", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: 'Purchase order list retrieved successfully.',
            400: 'Bad request.',
            401: 'Unauthorized.',
            404: 'Purchase orders not found.',
            500: 'Internal server error.'
        }
    )
    def get(self, request):
        try:
            vendor = request.user.vendor  # Assuming vendor is logged in
            buyer_name = request.query_params.get('buyer_name', '')
            purchase_orders = PurchaseOrder.objects.filter(vendor=vendor)
            if buyer_name:
                purchase_orders = purchase_orders.filter(buyer__user__name__icontains=buyer_name)

            paginator = Paginator(purchase_orders, request.query_params.get('page_size', 10))
            page_number = request.query_params.get('page', 1)
            page_obj = paginator.get_page(page_number)

            serializer = PurchaseOrderDetailSerializer(page_obj, many=True)
            return Response(
                {
                    'responseCode': status.HTTP_200_OK,
                    'responseMessage': 'Purchase order list retrieved successfully.',
                    'responseData': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal server error.',
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PerformanceMetricsAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('vendor_id', openapi.IN_QUERY, description='ID of the vendor', type=openapi.TYPE_INTEGER,required=True)
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'on_time_delivery_rate': openapi.Schema(type=openapi.TYPE_STRING, description='On-Time Delivery Rate'),
                    'quality_rating_avg': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quality Rating Average'),
                    'average_response_time': openapi.Schema(type=openapi.TYPE_STRING, description='Average Response Time'),
                    'fulfillment_rate': openapi.Schema(type=openapi.TYPE_STRING, description='Fulfillment Rate'),
                }
            ),
            400: 'Bad Request',
            404: 'Vendor with this ID does not exist.',
            500: 'Internal Server Error'
        }
    )
    def get(self, request):
        try:
            vendor_id = request.query_params.get('vendor_id')

            try:
                vendor = Vendor.objects.get(id=vendor_id)
            except ObjectDoesNotExist:
                return Response(
                    {
                        'responseCode': status.HTTP_404_NOT_FOUND,
                        'responseMessage': 'Vendor not found.',
                        'responseData': None
                    },
                    status=status.HTTP_404_NOT_FOUND
                )



            on_time_delivery_rate = round(vendor.on_time_delivery_rate * 100, 2)
            quality_rating_avg = round(vendor.quality_rating_avg,2)

            # Convert average response time to days, hours, minutes, and seconds
            total_seconds = vendor.average_response_time
            days = total_seconds // (24 * 3600)
            total_seconds %= (24 * 3600)
            hours = total_seconds // 3600
            total_seconds %= 3600
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            average_response_time = f"{int(days)} days {int(hours)} hours {int(minutes)} mins {int(seconds)} seconds"

            fulfillment_rate = round(vendor.fulfillment_rate * 100, 2)

            return Response({
                'responseCode': status.HTTP_200_OK,
                'responseMessage': 'Performance metrics retrieved successfully.',
                'responseData': {
                    'on_time_delivery_rate': f"{on_time_delivery_rate}%",
                    'quality_rating_avg': quality_rating_avg,
                    'average_response_time': average_response_time,
                    'fulfillment_rate': f"{fulfillment_rate}%"
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    'responseCode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'responseMessage': 'Internal server error.',
                    'responseData': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VendorHistoricalPerformance(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('vendor_id', openapi.IN_QUERY, description="Vendor ID", type=openapi.TYPE_INTEGER,required=True),
            openapi.Parameter('page_number', openapi.IN_QUERY, description="Page Number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page Size", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description='Successful', schema=HistoricalPerformanceSerializer(many=True)),
            400: 'Bad request.',
            404: 'Vendor not found.',
            500: 'Internal server error.'
        }
    )
    def get(self, request):
        vendor_id = request.query_params.get('vendor_id')
        page_number = request.query_params.get('page_number', 1)
        page_size = request.query_params.get('page_size', 10)

        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except ObjectDoesNotExist:
            return Response(
                {
                    'responseCode': status.HTTP_404_NOT_FOUND,
                    'responseMessage': 'Vendor not found.',
                    'responseData': None
                },
                status=status.HTTP_404_NOT_FOUND
            )

        historical_performances = HistoricalPerformance.objects.filter(vendor=vendor)
        paginator = Paginator(historical_performances, page_size)

        try:
            historical_performances_page = paginator.page(page_number)
        except PageNotAnInteger:
            historical_performances_page = paginator.page(1)
        except EmptyPage:
            historical_performances_page = paginator.page(paginator.num_pages)

        serializer = HistoricalPerformanceSerializer(historical_performances_page, many=True)
        response_data = serializer.data

        return Response(
            {
                'responseCode': status.HTTP_200_OK,
                'responseMessage': 'Success',
                'responseData': response_data
            },
            status=status.HTTP_200_OK
        )
