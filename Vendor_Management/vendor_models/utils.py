from django.db.models import F, Sum, Avg ,ExpressionWrapper, fields
from .models import PurchaseOrder,HistoricalPerformance
from django.utils import timezone
from datetime import datetime


def create_historical_performance(vendor):
    HistoricalPerformance.objects.create(
        vendor=vendor,
        date=timezone.now(),
        on_time_delivery_rate=vendor.on_time_delivery_rate,
        quality_rating_avg=vendor.quality_rating_avg,
        average_response_time=vendor.average_response_time,
        fulfillment_rate=vendor.fulfillment_rate
    )


def calculate_on_time_delivery_rate(vendor):
    completed_orders_count = PurchaseOrder.objects.filter(
        vendor=vendor,
        status='completed'
    ).count()
    on_time_orders_count = PurchaseOrder.objects.filter(
        vendor=vendor,
        status='completed',
        completed_date__lte=F('delivery_date')
    ).count()
    if completed_orders_count > 0:
        on_time_delivery_rate = on_time_orders_count / completed_orders_count
        print("on_time_delivery_rate--------->",on_time_delivery_rate)
        vendor.on_time_delivery_rate = on_time_delivery_rate
        vendor.save()
        print("create_historical_performance before--------->",create_historical_performance(vendor))
        create_historical_performance(vendor)
        print("create_historical_performance--------->",create_historical_performance(vendor))
    else:
        on_time_delivery_rate = 0.0
    return on_time_delivery_rate

# pass
def calculate_quality_rating_avg(vendor):
    completed_orders = PurchaseOrder.objects.filter(
        vendor=vendor,
        status='completed',
        quality_rating__isnull=False
    )
    if completed_orders.exists():
        quality_rating_sum = completed_orders.aggregate(total=Sum('quality_rating'))['total']
        quality_rating_count = completed_orders.count()
        quality_rating_avg = quality_rating_sum / quality_rating_count
        vendor.quality_rating_avg = quality_rating_avg
        vendor.save()
        create_historical_performance(vendor)
    else:
        quality_rating_avg = 0.0
    return quality_rating_avg
# pass
def calculate_average_response_time(vendor):
    acknowledged_orders = PurchaseOrder.objects.filter(
        vendor=vendor,
        status='acknowledged',
        acknowledgment_date__isnull=False
    )
    acknowledged_orders_with_issue_date = acknowledged_orders.filter(issue_date__isnull=False)
    if not acknowledged_orders_with_issue_date.exists():
        existing_average_response_time = vendor.average_response_time
        return existing_average_response_time
    response_times = acknowledged_orders_with_issue_date.annotate(
        response_time=ExpressionWrapper(
            F('acknowledgment_date') - F('issue_date'),
            output_field=fields.DurationField()
        )
    )
    print("response_times--------->",response_times)
    average_response_time = response_times.aggregate(avg_response_time=Avg('response_time'))['avg_response_time']
    print("average_response_time--------->",average_response_time)
    if average_response_time:
        vendor.average_response_time = average_response_time.total_seconds()
        vendor.save()
        create_historical_performance(vendor)
        return average_response_time.total_seconds()
        print("average_response_time.total_seconds()--------->",average_response_time.total_seconds())
    else:
        return 0.0
# pass
def calculate_fulfillment_rate(vendor):
    total_orders = PurchaseOrder.objects.filter(vendor=vendor)
    fulfilled_orders = total_orders.filter(status='completed', issue_date__isnull=True)
    if total_orders.exists():
        fulfillment_rate = fulfilled_orders.count() / total_orders.count()
        vendor.fulfillment_rate = fulfillment_rate
        vendor.save()
        create_historical_performance(vendor)
    else:
        fulfillment_rate = 0.0
    return fulfillment_rate
