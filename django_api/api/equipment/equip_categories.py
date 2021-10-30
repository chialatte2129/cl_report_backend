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
from api.models import EquipCategories
import uuid

def getTableAndTotal(query, query_total=""):
    total = 0
    with connection.cursor() as cursor:
        if query_total:
            cursor.execute(query_total)
            rows = cursor.fetchall()
            total = rows[0][0]
        cursor.execute(query)
        cols = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        table = [dict(zip(cols, row)) for row in rows]
    connection.close()
    return table, total

def getUUID():
    return str(uuid.uuid4()).split("-")[0].upper()

class EquipCategoriesList(View):
    def __init__(self, *args, **kwargs):
        print("run api : get Equip Categories list")

    def actionTable(self, data):
        res = codeStatus(1, msg="")
        data["sort"] = "desc" if data["sort"]=="descending" or data["sort"]=="desc" else "asc"
        data["sort_column"] = data["sort_column"] if data["sort_column"] else "whole_name"
        filter_data = data["filter"]
        filter_data["key_word"] = f" whole_name like '%{filter_data['key_word']}%'" if 'key_word' in filter_data and filter_data["key_word"] else ""

        where_condition = ""
        for item in filter_data:
            if filter_data[item]:
                where_condition = f"where {filter_data[item]}" if not where_condition else f"{where_condition} and {filter_data[item]}"
        
        query = f"""
            SELECT id,name, parent_id ,whole_name 
            FROM equip_categories
            {where_condition}
            order by {data['sort_column']} {data['sort']}
        """
        
            # limit {data['start_row']}, {data['page_size']};
        query_total = f"""
            SELECT count(*)
            FROM equip_categories
            {where_condition};
        """
        res["categories"], res["total"] = getTableAndTotal(query, query_total)
        return res

    def post(self, request):
        try:
            data = json.loads(request.body)
            status, err = checkDataParam(data, check_list=["action"])
            if not status: return JsonResponse(codeStatus(0, msg=err))
            try:
                res = getattr(self, f"action{data['action'].title()}")(data)
            except Exception as e:
                print(str(e))
                res = codeStatus(0, msg="common_msg.action_error")
        except Exception as e:
            print(f"get Equip Categories exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg=str(e))
        return JsonResponse(res)

def get_whole_name(name, parent_id, all_equip):
    if parent_id==None:
        return name
    if len(name.split("/")) > 10:
        return name
    parent_odject = all_equip.get(id=int(parent_id))
    name = f"{parent_odject.name}/{name}"
    print(parent_odject.parent_id)
    if parent_odject.parent_id!=None:
        name = get_whole_name(name, parent_odject.parent_id, all_equip)
    return name

class UpdateEquipCategory(View):
    def __init__(self, *args, **kwargs):
        print("run api : update person daily report")

    def popFormKey(self, form):
        form.pop("day_of_week", None)
        form.pop("copy_date", None)
        form.pop("created_at", None)
        form.pop("updated_by", None)
        return form

    def verifyField(self, Model, form, filter_dict, action=""):
        try:
            if not form["name"]: raise ErrorWithCode(0, "請輸入類別名稱")
            res = codeStatus(1)
        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)
        except:
            res = codeStatus(0, msg="common_msg.action_error")
        return res
    
    def updateWholeName(self):
        print("update whole name")
        all_equip = EquipCategories.objects.all()
        for equip_object in all_equip:
            whole_name = get_whole_name(equip_object.name , equip_object.parent_id ,all_equip) 
            print(whole_name)
            equip_object.whole_name = whole_name
            equip_object.save()
        return True
        
    def checkDuplicate(self,Model,form):
        try:
            check_rows = Model.exclude(id=form["id"]) if "id" in form else  Model
            duplicate_row = check_rows.filter(name=form["name"],parent_id=form["parent_id"])
            if duplicate_row.count():
                res = codeStatus(0, msg="重複的類別設定")
            else:
                res = codeStatus(1)

        except ErrorWithCode as e:
            print(str(e))
            res = codeStatus(0, msg="common_msg.action_error")
        return res

    def actionCreate(self, Model, form, trigger, request):
        print("action : create")
        filter_dict = {}
        verify_response = self.verifyField(Model, form, filter_dict, "create")
        
        if not verify_response["code"]: return verify_response

        try:
            if not form["parent_id"]:
                form["parent_id"] = None
            form["whole_name"] = ""
            form["created_at"] = trigger
            form["updated_at"] = trigger
            res = codeStatus(1, msg="common_msg.save_ok")
            row = Model.create(**form)

            self.updateWholeName()

        except Exception as e:
            print(f"update Equip Categories [create] exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg="common_msg.action_error")
        return res

    

    def actionUpdate(self, Model, form, trigger, request):
        print("action : update")
        try:
            filter_dict = {"id":form["id"]}
            verify_response = self.verifyField(Model, form, filter_dict)
            if not verify_response["code"]: return verify_response

            if not form["parent_id"]:
                form["parent_id"] = None

            duplicate_response = self.checkDuplicate(Model, form)
            if not duplicate_response["code"]: return duplicate_response

            form["whole_name"] = ""
            form["updated_at"] = trigger
            res = codeStatus(1, msg="common_msg.save_ok")
            
            Model.filter(**filter_dict).update(**form)

            self.updateWholeName()
            print("OK")

        except Exception as e:
            print(f"update Equip categories [update] exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg="common_msg.action_error")
        return res

    def actionDelete(self, Model, form, trigger, request):
        print("action : delete")
        try:
            filter_dict = {"id":form["id"]}
            Model.filter(**filter_dict).delete()
            res = codeStatus(1, msg="common_msg.delete_ok")

        except Exception as e:
            print(f"update Equip Categories [delete] exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg="common_msg.action_error")
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
            personDailyJobs = models.EquipCategories.objects
            trigger = datetime.now(tz=timezone.utc)
            print(f"action{data['action'].title()}")
            try:
                res = getattr(self, f"action{data['action'].title()}")(personDailyJobs, form, trigger, request)
            except Exception as e:
                print(str(e))
                res = codeStatus(0, msg="common_msg.action_error")
            
        except Exception as e:
            print(f"update Equip Categories exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg=str(e))
        return JsonResponse(res)

