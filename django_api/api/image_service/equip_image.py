from django.http import HttpResponse
from django.views import View
from django.http import JsonResponse
from api.models import DictionarySetting
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import collections
import json
import pymysql
import os
import requests
import base64
from api import models
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from api.share_functions.tools import *


class API_CALL_View(View):
    
    def get(self, request, *args, **kwargs):
        order_id = str(request.GET.get('order_id'))
        print("order_id>>", order_id)
        html_content = f"""
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">  
        <html>  
            <head>  
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <title> New Document </title>  
            </head >    
            <body>   
                no image
            </body>  
        </html> 
        """
       
        try:
            row = models.EquipImages.objects.filter(id=order_id)
            
            if row.count() and row[0].file_bytes_str:     
                image_data = base64.b64decode(row[0].file_bytes_str)
                print("OK")
                return HttpResponse(image_data, content_type='image/jpeg')
            HttpResponse(html_content)    
        except Exception as ex:
            print ("sql Error !!!",ex)
            return HttpResponse(html_content)         


class ImageBytesArray(View):
    def __init__(self, *args, **kwargs):
        print("run api : get images bytes array")

    def post(self, request):
        try:
            data = json.loads(request.body)
            row = models.EquipImages.objects.get(id=data["image_id"])
            res = codeStatus(1)
            res["image_bytes_array"]=row.file_bytes_str
        except Exception as ex:
            res = codeStatus(-1, msg=str(e))
        return JsonResponse(res)