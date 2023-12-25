from django.db.models import Sum, Case, When, IntegerField
from django.db.models.functions import TruncDay
from django.utils.timezone import make_aware

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Accounting, MonthTarget, SaveMoneyTarget

from datetime import datetime, timedelta

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


class TargetAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, year, month):
        try:
            target = MonthTarget.objects.get(user=request.user, year=year, month=month)
        except MonthTarget.DoesNotExist:
            target = None

        if target is None:
            target_income = 0
            target_outcome = 0
        else:
            target_income = target.income
            target_outcome = target.outcome

        income_achieved = self.calculate_achieved_amount(request.user, year, month, 'income')
        outcome_achieved = self.calculate_achieved_amount(request.user, year, month, 'outcome')

        response_data = {
            "year": year,
            "month": month,
            "target_income": target_income,
            "target_outcome": target_outcome,
            "income": [income_achieved, target_income - income_achieved if target_income - income_achieved > 0 else 0],
            "outcome": [outcome_achieved, target_outcome - outcome_achieved if target_outcome - outcome_achieved > 0 else 0]
        }

        return Response(response_data)

    def calculate_achieved_amount(self, user, year, month, type):
        start_date = make_aware(datetime(year, month, 1))

        if month == 12:
            end_year = year + 1
            end_month = 1
        else:
            end_year = year
            end_month = month + 1

        end_date = make_aware(datetime(end_year, end_month, 1)) - timedelta(days=1)

        return Accounting.objects.filter(user=user, date__range=[start_date, end_date], type=type).aggregate(Sum('amount'))['amount__sum'] or 0


class TypeCostAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        description="Generate type cost chart",
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
    def get(self, request):
        from_date = request.query_params.get('from')
        end_date = request.query_params.get('end')

        try:
            from_date = make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
        except (ValueError, TypeError):
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Accounting.objects.filter(user=request.user, date__range=[from_date, end_date], type='outcome')

        total_outcome_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0

        category_outcomes = queryset.values('category__name').annotate(total=Sum('amount')).order_by('-total')

        data = []
        total_percent = 0
        for category in category_outcomes:
            category_name = category['category__name']
            category_total = category['total']
            percent = int(round(((category_total / total_outcome_amount) * 100), 0)) if total_outcome_amount else 0
            data.append({
                "name": category_name,
                "percent": f"{percent}%",
                "data": [percent, 100 - percent]
            })
            total_percent += percent

        if data and total_percent != 100:
            last_percent = data[-1]["data"][0] + (100 - total_percent)
            data[-1]["data"][0] = last_percent
            data[-1]["percent"] = f"{last_percent}%"
            data[-1]["data"][1] = 100 - last_percent

        return Response({
            "from": from_date.strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d'),
            "data": data
        })


class CompareAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        description="Compare accounting data between two periods",
        manual_parameters=[
            openapi.Parameter(
                name='from',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Start date for current period',
                required=True
            ),
            openapi.Parameter(
                name='end',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='End date for current period',
                required=True
            )
        ],
    )
    def get(self, request):
        from_date = request.query_params.get('from')
        end_date = request.query_params.get('end')

        try:
            from_date = make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
        except (ValueError, TypeError):
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        duration = end_date - from_date

        prev_end_date = from_date - timedelta(days=1)
        prev_start_date = prev_end_date - duration

        current_data = self.aggregate_data(request.user, from_date, end_date)

        prev_data = self.aggregate_data(request.user, prev_start_date, prev_end_date)

        income_diff = current_data['income'] - prev_data['income']
        outcome_diff = current_data['outcome'] - prev_data['outcome']

        income_percentage_change = self.calculate_percentage_change(prev_data['income'], current_data['income'])
        outcome_percentage_change = self.calculate_percentage_change(prev_data['outcome'], current_data['outcome'])

        response_data = {
            "from": from_date.strftime('%Y-%m-%d'),
            "end": end_date.strftime('%Y-%m-%d'),
            'prev_from': prev_start_date.strftime('%Y-%m-%d'),
            'prev_end': prev_end_date.strftime('%Y-%m-%d'),
            'income_change': income_percentage_change,
            'outcome_change': outcome_percentage_change,
        }

        return Response(response_data)

    def aggregate_data(self, user, start_date, end_date):
        queryset = Accounting.objects.filter(user=user, date__range=[start_date, end_date])
        total_income = queryset.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_outcome = queryset.filter(type='outcome').aggregate(Sum('amount'))['amount__sum'] or 0

        return {"income": total_income, "outcome": total_outcome}

    def calculate_percentage_change(self, old_value, new_value):
        if old_value == 0:
            return -101.0
        return round(((new_value - old_value) / old_value) * 100, 2)

