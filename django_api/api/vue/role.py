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
from api.models import Role

class API_VUE_ListRoles(View):
  
    def __init__(self,*args,**kwargs) :
        print('API_VUE_ListRoles load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)               
            token_id=post_data['token_id']
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :
                if 'page_count' in post_data :
                    filter_role=post_data['role_id']
                    filter_description=post_data['description']
                    page_count=post_data['page_count']     
                    OFFSET=(page_count-1) * 10
                    LIMIT=10  #perpage
                    roles = Role.objects.filter(role_id__contains=filter_role, description__contains=filter_description).values("role_id", "description", "menus_id","actions_id")
                    total_rows=roles.count()
                    roles = list(roles[OFFSET:OFFSET+LIMIT])                                        
                    res={'msg_code':1,'msg':"success","msg_i18n":"",'data':roles,'total_rows':total_rows}
                    return JsonResponse(res)
                else :  #list all roles 
                    roles = list(Role.objects.all().values("role_id", "description", "menus_id","actions_id"))                                         
                    res={'msg_code':1,'msg':"success","msg_i18n":"",'data':roles,'total_rows':len(roles)}
                    return JsonResponse(res)    
            else :
                res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                return JsonResponse(res)    

        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)


class API_VUE_DeleteRole(View):
  
    def __init__(self,*args,**kwargs) :
        print('API_VUE_DeleteRole load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)               
            token_id=post_data['token_id']
            role_id=post_data['role_id']
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :
                 #get all users
                 roleObj = Role.objects.get(role_id=role_id)   
                 if roleObj is not None:   #renew token every time login
                    #should check this role has be used by other user?
                    #delete
                    roleObj.delete()
                    res={'msg_code':1,'msg':"success","msg_i18n":"role.id_has_deleted"}
                    return JsonResponse(res)    
                 else : 
                    res={'msg_code':0,'msg':"role is not exist","msg_i18n":"role.id_is_not_exist"}
                    return JsonResponse(res)   
            else :
                 res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                 return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)


class API_VUE_SaveRole(View):
   
    def __init__(self,*args,**kwargs) :
        print('API_VUE_Tokenview load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)
            print('post data =',post_data)   
            token_id=post_data['token_id']
            is_new=post_data['is_new']
            role_id=post_data['role_id']
            description=post_data['description']
            menus_id=post_data['menus_id']
            actions_id=post_data['actions_id']
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :            
                if is_new :   #create new one                                          
                    roleObj, created = Role.objects.get_or_create(role_id=role_id)               
                    print('created=',created)
                    if created:   #renew token every time login
                       #print(user,'old=',source_old_pass,'new=',source_new_pass)     .update(field=value)                                 
                       roleObj.description=description        
                       roleObj.menus_id=menus_id 
                       roleObj.actions_id=actions_id                     
                       roleObj.save()              
                       res={'msg_code':1,'msg':"role saved","msg_i18n":"role.saved"}
                       return JsonResponse(res)
                    else :
                       res={'msg_code':0,'msg':"this role id is exist","msg_i18n":"role.id_is_exist"}
                       return JsonResponse(res)    
                else:
                    roleObj = Role.objects.get(role_id=role_id)   
                    if roleObj is not None:   #renew token every time login
                       #print(user,'old=',source_old_pass,'new=',source_new_pass)     .update(field=value)                                 
                       roleObj.description=description        
                       roleObj.menus_id=menus_id 
                       roleObj.actions_id=actions_id                     
                       roleObj.save()              
                       res={'msg_code':1,'msg':"role saved","msg_i18n":"role.updated"}
                       return JsonResponse(res)
                    else :
                       res={'msg_code':0,'msg':"this role id is exist","msg_i18n":"role.id_is_exist"}
                       return JsonResponse(res)    
            else :
                 res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                 return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)    






