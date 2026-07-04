# sales/serializers.py
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from inventory.models import Stock
from .models import Order, OrderItem, Customer


class OrderItemSerializer(serializers.ModelSerializer):
    sku = serializers.ReadOnlyField(source="variant.sku")
    product_name = serializers.ReadOnlyField(source="variant.product.name")

    line_total = serializers.ReadOnlyField()
    cost_total = serializers.ReadOnlyField()
    profit_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "variant",
            "sku",
            "product_name",
            "quantity",
            "price_at_sale",
            "cost_at_sale",
            "line_total",
            "cost_total",
            "profit_total",
        ]
        read_only_fields = [
            "cost_at_sale",
            "line_total",
            "cost_total",
            "profit_total",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    cashier_name = serializers.CharField(
        source="cashier.username",
        read_only=True,
    )

    customer_email = serializers.EmailField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    customer_phone = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    customer_address = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "cashier",
            "cashier_name",
            "customer",
            "customer_name",
            "status",
            "total_amount",
            "payment_method",
            "created_at",
            "items",
            "order_type",
            "customer_email",
            "customer_phone",
            "customer_address",
        ]
        read_only_fields = ["cashier", "total_amount"]

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")

        c_email = validated_data.pop("customer_email", None)
        c_phone = validated_data.pop("customer_phone", None)
        c_address = validated_data.pop("customer_address", None)
        c_name = validated_data.get("customer_name", "")

        customer_instance = validated_data.get("customer")

        if not customer_instance and c_name:
            if c_email:
                customer_instance = Customer.objects.filter(
                    email=c_email,
                ).first()

            if not customer_instance:
                customer_instance = Customer.objects.create(
                    name=c_name,
                    email=c_email or None,
                    phone=c_phone,
                    address=c_address,
                )

        validated_data["customer"] = customer_instance

        order = Order.objects.create(**validated_data)
        calculated_total = Decimal("0.00")

        for item_data in items_data:
            variant = item_data["variant"]
            qty = item_data["quantity"]

            # The backend controls the final selling price.
            # This prevents a user from manually changing prices in the browser.
            if order.order_type == "WHOLESALE":
                price_at_sale = variant.wholesale_price
            else:
                price_at_sale = variant.retail_price

            # Lock the stock row during checkout to reduce overselling risk.
            stock_record = (
                Stock.objects.select_for_update()
                .filter(
                    variant=variant,
                    quantity_on_hand__gte=qty,
                )
                .first()
            )

            if not stock_record:
                raise serializers.ValidationError(
                    {
                        "items": (
                            f"Insufficient stock for SKU: {variant.sku}. "
                            "Cannot complete order."
                        )
                    }
                )

            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=qty,
                price_at_sale=price_at_sale,
                cost_at_sale=variant.cost_price,
            )

            calculated_total += price_at_sale * qty

            stock_record.quantity_on_hand -= qty
            stock_record.save(update_fields=["quantity_on_hand"])

        order.total_amount = calculated_total
        order.save(update_fields=["total_amount"])

        return order


class CustomerSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "address",
            "total_orders",
            "total_spent",
            "created_at",
        ]