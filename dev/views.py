import random
from datetime import date, timedelta
from core.models import Category, Accounting

def generate_random_accounting_records(user):
    start_date = date(year=date.today().year, month=1, day=1)
    end_date = date(year=date.today().year, month=12, day=31)
    current_date = start_date

    while current_date <= end_date:
        for _ in range(3):
            Accounting.objects.create(
                user=user,
                date=current_date,
                type=random.choice(['income', 'outcome']),
                amount=random.uniform(1000, 10000),
                title='隨機生成的記帳紀錄'
            ).category.add(random.choice(Category.objects.filter(user=user)))

        current_date += timedelta(days=1)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class GenerateAccountingRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        generate_random_accounting_records(request.user)
        return Response({'message': '隨機記帳紀錄已生成'}, status=status.HTTP_201_CREATED)