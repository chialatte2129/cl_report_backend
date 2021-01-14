#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @file    : 
# @Date    : 
# @Author  :
# @Contact : 
# @Version : 
# @Version History:
#
import os
from django.http import HttpResponse
from django.views import View
from datetime import datetime
from elasticsearch import Elasticsearch
from ssl import create_default_context
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import base64
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .token_helper import token_expire_handler,is_token_expired
from passlib.context import CryptContext
from django.core import serializers
from api.models import Role
from api.models import Profile
from api import models
import xmlrpc.client as xmlrpclib

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    print(request.META)    
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_odoo(dbname,url,username,pwd):
    # 登入odoo系統
    sock_common = xmlrpclib.ServerProxy (f'{url}/xmlrpc/common')
    uid = sock_common.login(dbname, username, pwd)
    
    if uid:
        print("Successfully login")
        print(uid)
        # 取得odoo用戶基本資料
        sock = xmlrpclib.ServerProxy(f'{url}/xmlrpc/object')
        args = [('user_id', '=', uid)]
        user_id = sock.execute(dbname, uid, pwd, 'hr.employee', 'search', args)
        user_data = sock.execute(dbname, uid, pwd, 'hr.employee', 'read', user_id, ['name',"user_id","work_email"])[0]
        print(user_data)
        user_data["uid"] = uid
        print("return")
        return True,user_data
    else:
        print("Invalid User")
        return False,{}
  
    
class API_VUE_Login(View):
    def __init__(self,*args,**kwargs) :
        print('Vue backend view load!')
         
    def post(self, request):        
        try :
            
            post_data=json.loads(request.body)
            print('post data =',post_data)
               
            base64_pass=post_data['passwd']  
            level1_pass=base64.urlsafe_b64decode(base64_pass.encode('ascii'))            
            source_pass=base64.urlsafe_b64decode(level1_pass.decode('ascii')).decode('ascii') 

            # user = authenticate(username=post_data['username'], password=source_pass)
            # print(user)

            # if user is not None:   #renew token every time login
            #     roles_id=user.profile.roles_id                
            #     roles=roles_id.split(",")
            #     user_menus=[]
            #     user_actions=[]
            #     print('login user roles=',roles)
            #     for role_id in roles :
            #         roleObj = Role.objects.get(role_id=role_id)  
            #         if roleObj is not None :
            #            menus=roleObj.menus_id.split(",")
            #            actions=roleObj.actions_id.split(",")
            #            for menu in menus :
            #                if menu not in user_menus :
            #                   user_menus.append(menu)
            #            for action in actions :
            #                if action not in user_actions :
            #                   user_actions.append(action) 

            #     tk,created =Token.objects.get_or_create(user=user)
            #     tk.delete()   #delete old
            #     tk,created =Token.objects.get_or_create(user=user)                 
            #     print(user.id,'token=',tk.key,datetime.utcnow(),'meuns=',user_menus,' actions=',user_actions)        
            #     res={
            #         'msg_code':1,
            #         'msg':'success',
            #         'data':{
            #             'token':tk.key,
            #             'username':user.username,
            #             'account_id':user.id,
            #             'user_full_name':user.get_full_name(),
            #             'user_menus':user_menus,
            #             'user_actions':user_actions,
            #             'is_admin':user.is_superuser
            #         }
            #     }
            
            # else:
            #    # No backend authenticated the credentials              
            #     res={
            #         'msg_code':0,
            #         'msg':'user name or password is not correct',
            #         'msg_i18n':'account.name_and_pass_not_match'
            #     }

            # res={
            #     'msg_code':1,
            #     'msg':'success',
            #     'data':{
            #         'token':tk.key,
            #         'username':user.username,
            #         'account_id':user.id,
            #         'user_full_name':user.get_full_name(),
            #         'user_menus':user_menus,
            #         'user_actions':user_actions,
            #         'is_admin':user.is_superuser
            #     }
            # }

            res={
                'msg_code':1,
                'msg':'success',
                'data':{
                    'token':"thisisexamplekey",
                    'username':"admin",
                    'account_id':1,
                    'user_full_name':"Admin",
                    'user_menus':["dictionary_setting"],
                    'is_admin':1
                }
            }
            return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e)}
            print(res) 
            return JsonResponse(res)  

    def get(self, request, *args, **kwargs):
        print('get',request.META)
        return HttpResponse('Hi !')


class API_VUE_Token(View):
   
    def __init__(self,*args,**kwargs) :
        print('API_VUE_Tokenview load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)
            print('post data =',post_data)   
            token_id=post_data['token_id']
            #rs=TokenAuthentication.authenticate_credentials(self,key=token_id)
            #print('rs=',rs) 
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            print(is_expire," token=",token,token.user_id)
            res={'msg_code':1,'user_id':token.user_id}
            return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e)}
            print(res) 
            return JsonResponse(res)  



class API_VUE_ChangePassword(View):
   
    def __init__(self,*args,**kwargs) :
        print('API_VUE_Tokenview load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)
            print('post data =',post_data)   
            token_id=post_data['token_id']
            old_pass=post_data['old_pass']
            new_pass=post_data['new_pass']
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :
                 level1_old_pass=base64.urlsafe_b64decode(old_pass.encode('ascii'))            
                 source_old_pass=base64.urlsafe_b64decode(level1_old_pass.decode('ascii')).decode('ascii')

                 level1_new_pass=base64.urlsafe_b64decode(new_pass.encode('ascii'))            
                 source_new_pass=base64.urlsafe_b64decode(level1_new_pass.decode('ascii')).decode('ascii') 

                 userObj = User.objects.get(id=token.user_id)  
                 user = authenticate(username=userObj.username, password=source_old_pass)
                 if user is not None:   #renew token every time login
                    #print(user,'old=',source_old_pass,'new=',source_new_pass)                                      
                    user.set_password(source_new_pass)
                    user.save()
                    res={'msg_code':1,'msg':"password changed","msg_i18n":"account.new_pass_changed"}
                    return JsonResponse(res)
                 else :
                    res={'msg_code':0,'msg':"old password not match","msg_i18n":"account.old_password_not_match"}
                    return JsonResponse(res)    
            else :
                 res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                 return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)    



class API_VUE_ListAccounts(View):
   
    def __init__(self,*args,**kwargs) :
        print('API_VUE_ListAccounts load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)               
            token_id=post_data['token_id']
            page_count=post_data['page_count']
            filter_account=post_data['account']
            filter_alias=post_data['alias']
            OFFSET=(page_count-1) * 10
            LIMIT=10  #perpage
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :
                users = User.objects.filter(username__contains=filter_account, last_name__contains=filter_alias)
                total_rows=users.count()
                users = users[OFFSET:OFFSET+LIMIT]              
                users_data =[]
                for user in users :                                      
                    new_user={'username':user.username,'first_name':user.first_name,'last_name':user.last_name,'email':user.email,'roles_id':user.profile.roles_id,"info":user.profile.user_info,"is_odoo_user":user.profile.is_odoo_user}
                    users_data.append(new_user)
                res={'msg_code':1,'msg':"password changed","msg_i18n":"account.new_pass_changed",'data':users_data,'total_rows':total_rows}
                return JsonResponse(res)    
            else :                
                res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)


class API_VUE_SaveAccount(View):
   
    def __init__(self,*args,**kwargs) :
        print('API_VUE_Tokenview load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)
            print('post data =',post_data)   
            token_id=post_data['token_id']
            is_new=post_data['is_new']
            username=post_data['username']
            last_name=post_data['last_name']
            email=post_data['email']
            roles_id=post_data['roles']
            info=post_data['info'] 
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :            
                if is_new :   #create new one        
                    new_pass=post_data['new_pass']                             
                    userObj, created = User.objects.get_or_create(username=username)               
                    print('created=',created)
                    if created:   #renew token every time login
                       #print(user,'old=',source_old_pass,'new=',source_new_pass)     .update(field=value)  
                       level1_new_pass=base64.urlsafe_b64decode(new_pass.encode('ascii'))            
                       source_new_pass=base64.urlsafe_b64decode(level1_new_pass.decode('ascii')).decode('ascii')    
                       userObj.set_password(source_new_pass)
                       userObj.profile.is_odoo_user=0 
                       userObj.profile.odoo_user_id=0
                       userObj.profile.roles_id=roles_id   
                       userObj.profile.user_info=info   
                       userObj.email=email  
                       userObj.last_name=last_name                 
                       userObj.save()              
                       res={'msg_code':1,'msg':"role saved","msg_i18n":"common_msg.save_ok"}
                       return JsonResponse(res)
                    else :
                       res={'msg_code':0,'msg':"this account id is exist","msg_i18n":"account.id_is_exist"}
                       return JsonResponse(res)    
                else:
                    userObj = User.objects.get(username=username)   
                    if userObj is not None:   #renew token every time login
                       #print(user,'old=',source_old_pass,'new=',source_new_pass)     .update(field=value)       
                       
                       userObj.profile.roles_id=roles_id 
                       userObj.profile.user_info=info
                       userObj.email=email   
                       userObj.last_name=last_name                 
                       userObj.save()               
                       res={'msg_code':1,'msg':"role saved","msg_i18n":"common_msg.save_ok"}
                       return JsonResponse(res)
                    else :
                       res={'msg_code':0,'msg':"this account id is exist","msg_i18n":"account.id_is_exist"}
                       return JsonResponse(res)    
            else :
                 res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                 return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)    



class API_VUE_DeleteAccount(View):
  
    def __init__(self,*args,**kwargs) :
        print('API_VUE_DeleteAccount load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)               
            token_id=post_data['token_id']
            username=post_data['username']
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :
                 #get all users
                 userObj = User.objects.get(username=username)   
                 if userObj is not None:   #renew token every time login
                    #delete
                    userObj.delete()
                    res={'msg_code':1,'msg':"success","msg_i18n":"account.id_has_deleted"}
                    return JsonResponse(res)    
                 else : 
                    res={'msg_code':0,'msg':"role is not exist","msg_i18n":"account.id_is_not_exist"}
                    return JsonResponse(res)   
            else :
                 res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                 return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)


class API_VUE_SyncOdooAccount(View):
  
    def __init__(self,*args,**kwargs) :
        print('API_VUE_SyncOdooAccount load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body) 
            odoo_conn = json.loads(models.DictionarySetting.objects.get(keystr="SYSTEM-odoo_connection").jsonvalue)
            sock = xmlrpclib.ServerProxy(f'{odoo_conn["url"]}/xmlrpc/object')
            employee_ids = sock.execute(odoo_conn["dbname"], post_data["uid"], post_data["pwd"], 'hr.employee', 'search', [])
            employee_data = sock.execute(odoo_conn["dbname"], post_data["uid"], post_data["pwd"], 'hr.employee', 'read', employee_ids, ['name',"user_id","work_email"])
            
            user_ids = sock.execute(odoo_conn["dbname"], post_data["uid"], post_data["pwd"], 'res.users', 'search', [])
            user_data = sock.execute(odoo_conn["dbname"], post_data["uid"], post_data["pwd"], 'res.users', 'read', user_ids, ['login',"id"])
            user_map = { user["id"]:user for user in user_data}
            print(employee_data)
            for data in employee_data:
                print(data)
                print(user_map[data["user_id"][0]]["login"])
                userObj, created = User.objects.get_or_create(username=user_map[data["user_id"][0]]["login"])               
                print('created=',created)
                if created:   #renew token every time login
                    userObj.profile.is_odoo_user=1 
                    userObj.profile.odoo_user_id=data["user_id"][0]
                    userObj.profile.roles_id=["staff"]
                    userObj.profile.user_info = data["name"]
                    userObj.email = data["work_email"]
                    userObj.last_name = data["name"]                          
                    userObj.save()        
                else :
                    pass              
            return JsonResponse({"msg_code":1,'msg':"success","msg_i18n":"success"})
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)
