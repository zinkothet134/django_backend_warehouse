from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F, DecimalField, ExpressionWrapper, Value
from django.db.models.functions import TruncDate, Coalesce
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# 🌟 IMPORTANT: Adjust these imports to match your actual file structure!
# If Customer is in a different app (like 'users.models'), import it from there.
from .models import Order, OrderItem, Customer 
from .serializers import OrderSerializer, CustomerSerializer
from .pagination import StandardResultsSetPagination

# ==========================================
# 1. STANDARD VIEWSETS (For your router)
# ==========================================

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # 👈 2. Attach the pagination class here
    pagination_class = StandardResultsSetPagination

    # 👈 3. Enable the filter backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # 👈 4. Exact match filters (Great for dropdowns in React)
    filterset_fields = ['status', 'order_type', 'payment_method', 'cashier']
    
    # 👈 5. Text search fields (Great for a search bar in React)
    # The double underscore allows you to search across foreign keys!
    search_fields = ['customer_name', 'customer__name', 'customer__email', 'customer__phone', 'cashier__username']
    
    # 👈 6. Optional: Allow React to sort columns
    ordering_fields = ['created_at']
    def perform_create(self, serializer):
    # self.request.user is the person currently logged in (via their JWT token)
        serializer.save(cashier=self.request.user)

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]

    search_fields = ["name", "email", "phone"]

    def get_queryset(self):

        completed_orders = Q(order__status="COMPLETED")

        return (

            Customer.objects.annotate(

                total_orders=Count(

                    "order",

                    filter=completed_orders,

                    distinct=True,

                ),

                total_spent=Coalesce(

                    Sum(

                        "order__total_amount",

                        filter=completed_orders,

                    ),

                    Value(

                        Decimal("0.00"),

                        output_field=DecimalField(

                            max_digits=12,

                            decimal_places=2,

                        ),

                    ),

                ),

            )

            .order_by( "-id")

        )


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        range_value = request.query_params.get("range", "30d")

        range_days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "year": 365,
        }
        days = range_days.get(range_value, 30)

        today = timezone.localdate()
        start_date = today - timedelta(days=days - 1)

        completed_orders = Order.objects.filter(
            status="COMPLETED",
            created_at__date__range=(start_date, today),
        )

        completed_items = OrderItem.objects.filter(

            order__status="COMPLETED",

            order__created_at__date__range=(start_date, today),

        )

        profit_expression = ExpressionWrapper(
            (F("price_at_sale") - F("cost_at_sale")) * F("quantity"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )

        revenue_expression = ExpressionWrapper(
            F("price_at_sale") * F("quantity"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )

        summary = completed_items.aggregate(
            total_revenue=Coalesce(Sum(revenue_expression), Decimal("0.00")),
            retail_revenue=Coalesce(
                Sum(
                    revenue_expression,
                    filter=Q(order__order_type="RETAIL"),
                ),
                Decimal("0.00"),
            ),
            wholesale_revenue=Coalesce(
                Sum(
                    revenue_expression,
                    filter=Q(order__order_type="WHOLESALE"),
                ),
                Decimal("0.00"),
            ),
            total_profit=Coalesce(Sum(profit_expression), Decimal("0.00")),
            retail_profit=Coalesce(
                Sum(
                    profit_expression,
                    filter=Q(order__order_type="RETAIL"),
                ),
                Decimal("0.00"),
            ),
            wholesale_profit=Coalesce(
                Sum(
                    profit_expression,
                    filter=Q(order__order_type="WHOLESALE"),
                ),
                Decimal("0.00"),
            ),
        )

        total_orders = completed_orders.count()
        total_revenue = summary["total_revenue"]
        total_profit = summary["total_profit"]

        profit_margin = (
            (total_profit / total_revenue * 100)
            if total_revenue > 0
            else Decimal("0.00")
        )

        daily_profit = (
            completed_items.annotate(date=TruncDate("order__created_at"))
            .values("date")
            .annotate(
                retail_profit=Coalesce(
                    Sum(
                        profit_expression,
                        filter=Q(order__order_type="RETAIL"),
                    ),
                    Decimal("0.00"),
                ),
                wholesale_profit=Coalesce(
                    Sum(
                        profit_expression,
                        filter=Q(order__order_type="WHOLESALE"),
                    ),
                    Decimal("0.00"),
                ),
            )
            .order_by("date")
        )

        daily_revenue = (
            completed_items.annotate(date=TruncDate("order__created_at"))
            .values("date")
            .annotate(
                retail_revenue=Coalesce(
                    Sum(
                        revenue_expression,
                        filter=Q(order__order_type="RETAIL"),
                    ),
                    Decimal("0.00"),
                ),
                wholesale_revenue=Coalesce(
                    Sum(
                        revenue_expression,
                        filter=Q(order__order_type="WHOLESALE"),
                    ),
                    Decimal("0.00"),
                ),
                order_count=Count("order", distinct=True),
            )
            .order_by("date")
        )

        sales_mix = [
            {
                "sale_type": "Retail",
                "revenue": summary["retail_revenue"],
            },
            {
                "sale_type": "Wholesale",
                "revenue": summary["wholesale_revenue"],
            },
        ]

        top_products = (
            completed_items.values(
                "variant__product__name",
                "variant__sku",
            )
            .annotate(total_revenue=Sum(revenue_expression))
            .order_by("-total_revenue")[:8]
        )

        return Response(
            {
                "summary": {
                    "total_revenue": total_revenue,
                    "retail_revenue": summary["retail_revenue"],
                    "wholesale_revenue": summary["wholesale_revenue"],
                    "total_profit": total_profit,
                    "retail_profit": summary["retail_profit"],
                    "wholesale_profit": summary["wholesale_profit"],
                    "profit_margin": profit_margin,
                    "total_orders": total_orders,
                    "average_order_value": (
                        total_revenue / total_orders
                        if total_orders > 0
                        else Decimal("0.00")
                    ),
                },
                "revenue_by_date": [
                    {
                        "date": item["date"].strftime("%b %d"),
                        "retail_revenue": item["retail_revenue"],
                        "wholesale_revenue": item["wholesale_revenue"],
                    }
                    for item in daily_revenue
                ],
                "profit_by_date": [
                    {
                        "date": item["date"].strftime("%b %d"),
                        "retail_profit": item["retail_profit"],
                        "wholesale_profit": item["wholesale_profit"],
                    }
                    for item in daily_profit
                ],
                "sales_mix": sales_mix,
                "top_products": [
                    {
                        "product_name": item["variant__product__name"],
                        "sku": item["variant__sku"],
                        "total_revenue": item["total_revenue"],
                    }
                    for item in top_products
                ],
                "order_volume_by_date": [
                    {
                        "date": item["date"].strftime("%b %d"),
                        "order_count": item["order_count"],
                    }
                    for item in daily_revenue
                ],
            }
        )