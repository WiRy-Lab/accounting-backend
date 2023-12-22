from django.db.models import Sum, Case, When, IntegerField
from django.db.models.functions import TruncDay
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Accounting
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ChartsAPIView(APIView):
    """
    API View for generating accounting charts.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Accounting.objects.all()

    def get_queryset(self):
        """Retrieve the accounting for the authenticated user"""
        return Accounting.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        description="Generate accounting charts",
        manual_parameters=[
            openapi.Parameter(
                name='from',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Start date for chart range',
                required=True
            ),
            openapi.Parameter(
                name='end',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='End date for chart range',
                required=True
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        from_date = request.query_params.get('from')
        end_date = request.query_params.get('end')

        try:
            from_date = make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            if (end_date - from_date).days < 1:
                return Response({"error": "Date range too short"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()

        date_range = [from_date + timedelta(days=x) for x in range((end_date - from_date).days + 1)]

        aggregated_data = queryset.filter(date__range=[from_date, end_date]).annotate(
            day=TruncDay('date')
        ).values('day').annotate(
            income=Sum(Case(When(type='income', then='amount'), output_field=IntegerField())),
            outcome=Sum(Case(When(type='outcome', then='amount'), output_field=IntegerField()))
        ).order_by('day')

        aggregated_data_dict = {data['day']: data for data in aggregated_data}

        labels = []
        income = []
        outcome = []
        for day in date_range:
            day_data = aggregated_data_dict.get(day.date(), {'income': 0, 'outcome': 0})
            labels.append(day.strftime('%Y-%m-%d'))
            income.append(day_data['income'] or 0)
            outcome.append(day_data['outcome'] or 0)

        return Response({
            "from": from_date.strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d'),
            "labels": labels,
            "income": income,
            "outcome": outcome
        })
