from drf_spectacular.utils import(extend_schema, extend_schema_view, 
                                  OpenApiParameter, OpenApiExample, OpenApiTypes)
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.views import APIView

from django.utils.translation import gettext_lazy as _

from order.utils import OrderMixin
from voucher.models import UserCoupon
from order.serializers import(OrderItemsSerializer, OrderSerializer)
from order.models import Order
from voucher.models import UserCoupon
from customer.permissions import IsUserAddressOwner as IsUserOrderOwner


common_parameters = [
    OpenApiParameter(
        name='Accept-Language',
        location=OpenApiParameter.HEADER,
        description=_('Specify the language code for the response content. Supported values are "en" for English and "ar" for Arabic.'),
        required=False,
        type=str,
        examples=[
            OpenApiExample("English", value="en"),
            OpenApiExample("Arabic", value="ar")
        ]
    ),
]



@extend_schema_view(
    list=extend_schema(
        tags=['Orders'],
        summary="List current user's order basket",
        description="Retrieve the current items in the user's order basket.",
        parameters=common_parameters,
    ),
    create=extend_schema(
        tags=['Orders'],
        summary="Create a new order",
        description="Create a new order with the items in the user's basket.",
        parameters=common_parameters,
    ),
    get=extend_schema(
        tags=['Checkout'],
        summary="Retrieve checkout details",
        description="Retrieve checkout details such as payment options and order summary.",
        parameters=common_parameters,
    ),
    post=extend_schema(
        tags=['Checkout'],
        summary="Proceed with order checkout",
        description=(
            "Create a new order with the items in the user's basket.\n\n"
            "Required fields:\n"
            "- `shipping_info`: ID of the shipping address.\n"
            "- `billing_info`: ID of the billing address.\n"
            "- `payment_method`: Method of payment (1 = By cash, 2 = By card).\n"
            "- `delivery_method`: Method of delivery (1 = Courier, 2 = To the post office).\n"
            "- `coupon` (optional): Coupon code to apply to the order.\n"
        ),
        parameters=common_parameters,
    ),
)
class OrderAPIView(OrderMixin,
                   ListCreateAPIView):
    serializer_class = OrderSerializer
    items_serializer = OrderItemsSerializer
    queryset = Order.objects.all()
    permission_classes = [IsUserOrderOwner]

    def list(self, request, *args, **kwargs):
        data = self.get_basket_data(request)
        if len(data['items']) > 0:
            return Response(data=data)
        else:
            return Response({'basket': 'You dont have items in your basket!'})

    def create(self, request, *args, **kwargs):
        basket_data = self.get_basket_data(request)
        if len(basket_data['items']) > 0:
            response = super().create(request, *args, **kwargs)
            self.request = request
            return self.create_order(response)
        else:
            return Response({'basket': 'You don\'t have items in your basket!'}, status=400)



@extend_schema_view(
    get=extend_schema(
        tags=['Payments'],
        summary="in current time it's only by cash",
        description="in current time it's only by cash",
        parameters=common_parameters,
    ),
)
class OrderPaypalPaymentComplete(OrderMixin, APIView):

    def get(self, *args, **kwargs):
        mixin = OrderMixin()
        order_id = kwargs['order_id']
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=404)

        if self.request.user.is_authenticated:
            applicable_coupons = []
            coupon_details = []
            for item in order.items.all():
                coupon = item.check_coupon_eligibility(self.request.user)
                if coupon:
                    if not UserCoupon.objects.filter(coupon=coupon, user=self.request.user).exists():
                        user_coupon = UserCoupon.objects.create(coupon=coupon, user=self.request.user)
                        applicable_coupons.append(coupon)
                        coupon_details.append({
                            'coupon_code': coupon.coupon,
                            'product': item.product.title,
                            'valid_to': user_coupon.valid_to,
                            'message': f"This coupon is valid for your next purchase of {item.product.title} until {user_coupon.valid_to}."
                        })

            if applicable_coupons:
                return Response({
                    'success': 'Discounts applied successfully!',
                    'coupons_applied': coupon_details
                })
            else:
                return Response({'success': 'You successfully paid for order!'})