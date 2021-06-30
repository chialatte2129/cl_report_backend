import os, django, sys
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.db import connection, connections
from django.utils import timezone
from django.db.models import Q, F, Avg, Max, Min
import requests, json, pytz, ast, re, base64, uuid
from datetime import datetime, timedelta
from api.share_functions.tools import *
from api import models
import uuid



def getUUID():
    return str(uuid.uuid4()).split("-")[0].upper()

class EquipItemsList(View):
    def __init__(self, *args, **kwargs):
        print("run api : get Equipments list")

   
    def actionItems(self, data):
        res = codeStatus(1, msg="")
        equip_items = list(models.EquipItems.objects.filter(equip_id=data["id"]).values("id","equip_id","order","status","buy_date","end_date","description"))
        res["equip_items"] = equip_items
        return res

    def post(self, request):
        try:
            data = json.loads(request.body)
            status, err = checkDataParam(data, check_list=["action","id"])
            if not status: return JsonResponse(codeStatus(0, msg=err))
            try:
                res = getattr(self, f"action{data['action'].title()}")(data)
            except Exception as e:
                print(str(e))
                res = codeStatus(0, msg="common_msg.action_error")
        except Exception as e:
            print(f"get Equip Item exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg=str(e))
        return JsonResponse(res)

class UpdateEquipItems(View):
    def __init__(self, *args, **kwargs):
        print("run api : update equip items")

    def popFormKey(self, form):
        form.pop("equip_name", None)
        return form

    def verifyField(self, Model, form, filter_dict, action=""):
        try:
            if not form["name"]: raise ErrorWithCode(0, "請輸入設備名稱")
            res = codeStatus(1)
        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)
        except:
            res = codeStatus(0, msg="common_msg.action_error")
        return res

    def handleItemID(self,prefix,order):
        new_order = str(int(order)+1).zfill(4)
        print(new_order)
        return f"{prefix}-{new_order}" , new_order

    def actionCreate(self, Model, form, trigger, request):
        print("action : create")
        filter_dict = {"equip_id":form["equip_id"]}
        # verify_response = self.verifyField(Model, form, filter_dict, "create")
        # if not verify_response["code"]: return verify_response
        print("Go GO GO")
        try:
            data = Model.filter(**filter_dict).order_by("-order")
            if data.count():
                order = data[0].order
            else:
                order = "0000"
            form = self.popFormKey(form)
            form["id"],form["order"]= self.handleItemID(form["equip_id"],order)

            form["created_at"] = trigger
            form["updated_at"] = trigger
            form["status"] = "P"
            form["is_lend"] = 0
            form["is_return"] = 1
            form["is_broke"] = 0
            res = codeStatus(1, msg="common_msg.save_ok")
            row = Model.create(**form)

        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)
        except Exception as e:
            print(f"update Equip Items [create] exception, details as below :\n{str(e)}")
            res = codeStatus(0, msg="common_msg.action_error")
        return res

    

    def actionUpdate(self, Model, form, trigger, request):
        print("action : update")
        try:
            filter_dict = {"id":form["id"]}
            verify_response = self.verifyField(Model, form, filter_dict)
            if not verify_response["code"]: return verify_response

            duplicate_response = self.checkDuplicate(Model, form)
            if not duplicate_response["code"]: return duplicate_response


            form = self.popFormKey(form)
            
            form["updated_at"] = trigger
            res = codeStatus(1, msg="common_msg.save_ok")
            Model.filter(**filter_dict).update(**form)

        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)
        except Exception as e:
            print(f"update Equip Items [update] exception, details as below :\n{str(e)}")
            res = codeStatus(0, msg="common_msg.action_error")
        return res

    def actionDelete(self, Model, form, trigger, request):
        print("action : delete")
        try:
            filter_dict = {"id":form["id"]}
            data = Model.filter(**filter_dict)
            data.delete()
            res = codeStatus(1, msg="common_msg.delete_ok")
        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)

        except Exception as e:
            print(f"update Equip Items [delete] exception, details as below :\n{str(e)}")
            res = codeStatus(0, msg="common_msg.action_error")
        return res

    def post(self, request):
        try:
            data = json.loads(request.body)
            print(data)
            status, err = checkDataParam(data, check_list=["action", "form"])
            if not status: return JsonResponse(codeStatus(0, msg=err))
            form = data["form"]
            status, err = checkDataParam(form, check_list=[])
            if not status: return JsonResponse(codeStatus(0, msg=err))
            
            equip_items = models.EquipItems.objects
            trigger = datetime.now(tz=timezone.utc)
            print(f"action{data['action'].title()}")
            try:
                res = getattr(self, f"action{data['action'].title()}")(equip_items, form, trigger, request)
            except Exception as e:
                print(str(e))
                res = codeStatus(0, msg="common_msg.action_error")
            
        except Exception as e:
            print(f"update Equip Items exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg=str(e))
        return JsonResponse(res)
