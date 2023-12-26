import csv

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

import boto3

from core.models import Accounting , MonthTarget, SaveMoneyTarget

from io import BytesIO, StringIO

from drf_yasg.utils import swagger_auto_schema

import g4f

g4f.logging = True # enable logging
g4f.check_version = False # Disable automatic version checking


def generate_csv(user, year, month=None):
    filename = f"{year}年"
    if month:
        filename += f"{month}月"
    filename += "記帳明細.csv"

    csv_output = StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(['年份', '月份', '日期', '項目', '類別', '名稱', '收入金額', '支出金額', '小計餘額'])

    total_income = 0
    total_expense = 0
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
        if accounting.type == 'income':
            total_income += accounting.amount
        else:
            total_expense += accounting.amount

        writer.writerow([year_str, month_str, day_str, categories, type_str, accounting.title, income_amount, expense_amount, running_balance])

    writer.writerow(['總計', '', '', '', '', '', total_income, total_expense, running_balance])

    month_target = MonthTarget.objects.filter(user=user, year=year)
    if month:
        month_target = month_target.filter(month=month)

    if month_target.exists():
        target = month_target.first()
        income_rate = (total_income / target.income * 100) if target.income else 0
        outcome_rate = (total_expense / target.outcome * 100) if target.outcome else 0
        writer.writerow([f'{month}月目標金額', '', '', '', '', '收入目標', target.income, '支出目標', target.outcome])
        writer.writerow([f'{month}月目標達成率', '', '', '', '', '收入達成率', f"{income_rate:.2f}%", '支出達成率', f"{outcome_rate:.2f}%"])

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


DEFINE_WORD = '''
你現在是專業財務分析師，我會給你每日的記帳紀錄，請我用繁體中文，台灣慣用詞彙做這個月的收入與支出總結(需要提出具體數字)，
並以財務專家角度提供見解與建議。結果以純文字方式組成，並且不超過500字為限。
以下是一組範例回答，請按照此格式回答，只對必要部分修改(年月份、金額、建議)，若資料中沒有目標金額則以未設定說明。\n\n

2023年12月份收支總結：\n\n總收入：476,966元\n總支出：527,228元\n結餘：-50,262元\n\n
12月目標：\n收入目標：1,000,000元\n支出目標：1,000,000元\n\n
目標達成率：\n收入達成率：47.70%\n支出達成率：52.72%\n\n
見解與建議：\n
1. **收支狀況分析：** 由於收入為4 76,966元，支出為527,228元，結餘為負值-50,262元，顯示整體財務狀況不盡如人意，需要謹慎控制支出。\n\n
2. **目標達成率評估：** 收入達成率為47.70%，支出達成率為52.72%，均未達到預期目標，需要重新評估預算與花費計畫，嘗試節省開支。\n\n
3. **支出項目分析：** 衣物、樂活動以及住宿是主要的支出項目，其中衣物和樂活動支出偏高，可考慮在這些領域進行節制。\n\n
4. **收入來源建議：** 薪資和獎助金是主要的收入來源，建議努力提升工作穩定性，同時尋找額外的收入來源，以提高整體收入。\n\n
5. **儲蓄與投資：** 需要確保有足夠的儲蓄，建議設立緊急基金，同時考慮投資以實現財務增值。\n\n
6. **制定明確預算：** 制定一份清晰的預算，確保每個月的收入與支出都在掌控之中，盡可能避免出現負結餘情況。\n\n
建議您優先掌握支出，尋找降低成本的方式，同時積極提升收入。制定明確的預算，規劃未來的金融目標，有助於改善財務狀況。
'''
class MonthlyAnalysisAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, year, month):
        _, csv_content = generate_csv(request.user, year, month)
        content = csv_content.decode('utf-8-sig')
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            provider=g4f.Provider.GeekGpt,
            messages=[{"role": "user", "content": f"{DEFINE_WORD}\n{content}"}],
            stream=False,
        )

        return Response({
            'status': True,
            "result" : response,
        })