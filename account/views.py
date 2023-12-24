"""
Views for accounting api
"""
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from datetime import datetime , timedelta

from django.utils.timezone import make_aware

from rest_framework import viewsets, mixins , status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from core.models import Accounting, Category , MonthTarget , SaveMoneyTarget
from account import serializers

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AccountingViewSet(viewsets.ModelViewSet):
    """View for managing accounting APIs"""
    serializer_class = serializers.AccountingDetailSerializer
    queryset = Accounting.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the accounting for the authenticated user"""
        categories = self.request.query_params.get('category')
        queryset = self.queryset
        if self.request.user.is_authenticated:
            if categories:
                category_ids = self._params_to_ints(categories)
                queryset = queryset.filter(category__id__in=category_ids)

            return queryset.filter(user=self.request.user).order_by('-date')
        else:
            return queryset.none()

    def get_serializer_class(self):
        """Return the serializer class for the request"""
        if self.action == 'list':
            return serializers.AccountingSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new accounting"""
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get accounting records within a date range \
                               (default: current month) ex: /api/accounting/?from=2021-01-01&end=2021-01-31\n \
                               Get accounting records within comma separated list of categoryIDs \
                               (default: all categories) ex: /api/accounting/?category=2,3",
        manual_parameters=[
            openapi.Parameter(
                name='from',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Start date',
                required=False,
            ),
            openapi.Parameter(
                name='end',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='End date',
                required=False,
            ),
            openapi.Parameter(
                name='category',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Category ID',
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """Handle GET requests for accounting records within a date range"""
        from_date = request.query_params.get('from')
        end_date = request.query_params.get('end')

        queryset = self.get_queryset()

        if from_date and end_date:
            from_date = make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

            queryset = queryset.filter(date__range=[from_date, end_date]).order_by('-date')
        else:
            now = datetime.now()
            first_day = now.replace(day=1)

            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)

            last_day = next_month - timedelta(days=1)
            from_date = first_day
            end_date = last_day

            queryset = self.get_queryset().filter(date__range=[first_day, last_day])

        serializer = self.get_serializer(queryset, many=True)
        response_data={
            'from': from_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'data': serializer.data
        }
        return Response(response_data)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """View for managing category APIs"""
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Get categories assigned to accounting \
                               (default: all categories) ex: /api/category/?assigned_only=1\n \
                               Get categories not assigned to accounting \
                               (default: all categories) ex: /api/category/?assigned_only=2",
        manual_parameters=[
            openapi.Parameter(
                name='assigned_only',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='1: assigned to accounting, 2: not assigned to accounting',
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """List categories"""
        return super(CategoryViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        """Retrieve the category for the authenticated user"""
        assigned_only = int(self.request.query_params.get('assigned_only', 0))
        queryset = self.queryset
        if assigned_only == 1:
            queryset = queryset.filter(accounting__isnull=False)
        elif assigned_only == 2:
            queryset = queryset.filter(accounting__isnull=True)

        return queryset.filter(user=self.request.user).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new category"""
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **pk):
        """Retrieve a specific category by ID"""
        try:
            category = self.get_object()
        except Category.DoesNotExist:
            return Response({'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(category)
        return Response(serializer.data)


class MonthTargetViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MonthTargetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    queryset = MonthTarget.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(user=self.request.user).order_by('-year', '-month')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, year, month):
        try:
            month_target = self.get_queryset().get(year=year, month=month)
        except MonthTarget.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(month_target)
        return Response(serializer.data)

class SaveMoneyTargetViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SaveMoneyTargetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    queryset = SaveMoneyTarget.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

