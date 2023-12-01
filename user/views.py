from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema


class ListUser(APIView):

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            "user_id": kwargs['user_id'],
            "message": "Hello World!"})


class CreateUser(APIView):

    def post(self, request, *args, **kwargs):
        return JsonResponse({
            "message": "Create User!"})
