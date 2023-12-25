import csv

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

import boto3

from core.models import Accounting

from io import BytesIO, StringIO

from drf_yasg.utils import swagger_auto_schema


def generate_csv(user, year, month=None):
    filename = f"{year}年"
    if month:
        filename += f"{month}月"
    filename += "記帳明細.csv"

    csv_output = StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(['年份', '月份', '日期', '項目', '類別', '名稱', '收入金額', '支出金額', '小計餘額'])

    running_balance = 0
    accountings = Accounting.objects.filter(user=user, date__year=year)
    if month:
        accountings = accountings.filter(date__month=month)

    for accounting in accountings:
        year_str = accounting.date.year
        month_str = accounting.date.month
        day_str = accounting.date.day
        categories = ", ".join([category.name for category in accounting.category.all()])
        type_str = "收入" if accounting.type == 'income' else "支出"
        income_amount = accounting.amount if accounting.type == 'income' else ""
        expense_amount = accounting.amount if accounting.type == 'outcome' else ""
        running_balance += accounting.amount if accounting.type == 'income' else -accounting.amount

        writer.writerow([year_str, month_str, day_str, categories, type_str, accounting.title, income_amount, expense_amount, running_balance])

    csv_content = csv_output.getvalue()
    csv_output.close()

    return filename, csv_content.encode('utf_8_sig')


def store_csv_file(user_account, filename, csv_content):
    s3_client = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    s3_file_key = f"{user_account}/{filename}"

    csv_bytes = BytesIO(csv_content)

    s3_client.upload_fileobj(csv_bytes, bucket_name, s3_file_key)

    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': s3_file_key},
        ExpiresIn=180
    )

    return presigned_url

class MonthlyReportAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="get monthly report, the url will be expired in 180 seconds",
        responses={
            200: "success",
            401: "unauthorized",
        }
    )
    def get(self, request, year, month):
        filename, csv_content = generate_csv(request.user, year, month)
        file_url = store_csv_file(request.user.account, filename, csv_content)
        print(file_url)

        return Response({
            "filename": filename,
            "url": file_url
        })


class YearlyReportAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="get yearly report, the url will be expired in 180 seconds",
        responses={
            200: "success",
            401: "unauthorized",
        }
    )
    def get(self, request, year):
        filename, csv_content = generate_csv(request.user, year)
        file_url = store_csv_file(request.user.account, filename, csv_content)

        return Response({
            "filename": filename,
            "url": file_url
        })