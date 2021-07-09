import os, django, sys
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.db import connection, connections
from django.utils import timezone
from django.db.models import Q, F, Avg, Max, Min
from django.db.models.functions import Cast
from django_mysql.models import JSONField
import requests, json, pytz, ast, re, base64, uuid
from datetime import datetime, timedelta
from api.share_functions.tools import *
from api import models
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

class MeetingEntryList(View):
    def __init__(self, *args, **kwargs):
        print("run api : get Meeting Entry list")

    def actionTable(self, data):

        res = codeStatus(1, msg="")
        
        data["sort"] = "-" if data["sort"]=="descending" or data["sort"]=="desc" else ""
        data["sort_column"] = data["sort_column"] if data["sort_column"] else "church_name"
        filter_item = data["filter"]
        filter_data = {}
        if "key_word" in filter_item and filter_item["key_word"]:
            filter_data["church_name__contains"] = filter_item["key_word"]
        
        meet_data = models.MeetingEntries.objects.filter(**filter_data).annotate(content_json=Cast("content", output_field=JSONField())).values("id","church_id","church_name","content_json").order_by(f"{data['sort']}{data['sort_column']}")
        
        res["data"] = list(meet_data)
        res["total"] = meet_data.count()
        return res
    
    def actionChurch(self, data):

        res = codeStatus(1, msg="")

        filter_data = {}
        filter_data["church_id"] =  data["church_id"]
        
        meet_data = models.MeetingEntries.objects.filter(**filter_data).annotate(content_json=Cast("content", output_field=JSONField())).values("church_id","church_name","content_json")
        
        res["data"] = list(meet_data)[0] if meet_data.count() else []
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
            print(f"get Meeting Entry exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg=str(e))
        return JsonResponse(res)


class UpdateMeetingEntry(View):
    def __init__(self, *args, **kwargs):
        print("run api : update Meeting Entry")

    def popFormKey(self, form):
        form.pop("content_json", None)
        return form

    def verifyField(self, Model, form, filter_dict, action=""):
        try:
            if not form["church_name"]: raise ErrorWithCode(0, "請輸入教會名稱")
            res = codeStatus(1)
        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)
        except:
            res = codeStatus(0, msg="common_msg.action_error")
        return res

    def checkDuplicate(self,Model,form):
        try:
            check_rows = Model.exclude(id=form["id"]) if "id" in form else  Model
            duplicate_row = check_rows.filter(church_id=form["church_id"])
            if duplicate_row.count():
                res = codeStatus(0, msg="重複的ID")
            else:
                res = codeStatus(1)

            duplicate_row = check_rows.filter(church_name=form["church_name"])
            if duplicate_row.count():
                res = codeStatus(0, msg="重複的名稱")
            else:
                res = codeStatus(1)

        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)
        except:
            res = codeStatus(0, msg="common_msg.action_error")
        return res


    def actionCreate(self, Model, form, trigger, request):
        print("action : create")
        filter_dict = {}
        verify_response = self.verifyField(Model, form, filter_dict, "create")
        
        if not verify_response["code"]: return verify_response
        try:
            form["church_id"] = form["church_id"]
            form["church_name"] = form["church_name"]
            form["content_json"] = sorted(form["content_json"], key=lambda k: k['order_id']) 
            form["content"] = json.dumps(form["content_json"])
            form["created_at"] = trigger
            form["updated_at"] = trigger
            res = codeStatus(1, msg="common_msg.save_ok")
            form = self.popFormKey(form)
            row = Model.create(**form)

        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)
        except Exception as e:
            print(f"update Meeting Entry [create] exception, details as below :\n{str(e)}")
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

            # form = self.popFormKey(form)
            form["church_id"] = form["church_id"]
            form["church_name"] = form["church_name"]
            form["content_json"] = sorted(form["content_json"], key=lambda k: k['order_id']) 
            form["content"] = json.dumps(form["content_json"])
            form["updated_at"] = trigger
            res = codeStatus(1, msg="common_msg.save_ok")
            form = self.popFormKey(form)
            Model.filter(**filter_dict).update(**form)

        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)
        except Exception as e:
            print(f"update Meeting Entry [update] exception, details as below :\n{str(e)}")
            res = codeStatus(0, msg="common_msg.action_error")
        return res

    def actionDelete(self, Model, form, trigger, request):
        print("action : delete")
        try:
            filter_dict = {"id":form["id"]}
            Model.filter(**filter_dict).delete()
            res = codeStatus(1, msg="common_msg.delete_ok")
        except ErrorWithCode as e:
            res = codeStatus(e.code, msg=e.msg)

        except Exception as e:
            print(f"update Meeting Entry [delete] exception, details as below :\n{str(e)}")
            res = codeStatus(0, msg="common_msg.action_error")
        return res

    def post(self, request):
        try:
            data = json.loads(request.body)
            print(data)
            status, err = checkDataParam(data, check_list=["action", "form"])
            if not status: return JsonResponse(codeStatus(0, msg=err))
            form = data["form"]

            work_table = models.MeetingEntries.objects
            trigger = datetime.now(tz=timezone.utc)
            print(f"action{data['action'].title()}")
            try:
                res = getattr(self, f"action{data['action'].title()}")(work_table, form, trigger, request)
            except Exception as e:
                print(str(e))
                res = codeStatus(0, msg="common_msg.action_error")
            
        except Exception as e:
            print(f"update Meeting Setting exception, details as below :\n{str(e)}")
            res = codeStatus(-1, msg=str(e))
        return JsonResponse(res)

