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
from ssl import create_default_context
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate
import base64
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from .token_helper import token_expire_handler,is_token_expired
from django.core import serializers
from api.models import DictionarySetting
import pymysql
from dotenv import load_dotenv
load_dotenv()


class API_VUE_Hello(View):
   
    def __init__(self,*args,**kwargs) :
        print('API_VUE_SaveDictionary load!')

    def post(self, request):    
        
        return JsonResponse({"success":True,"result":"hello"})    

class API_VUE_SaveDictionary(View):
   
    def __init__(self,*args,**kwargs) :
        print('API_VUE_SaveDictionary load!')

    def post(self, request):    
        try :
            post_data=json.loads(request.body)
            print('post data =',post_data)   
            token_id=post_data['token_id']
            dataContent=post_data['content']
            is_new=dataContent['is_new']
            category=dataContent['category']
            keystr=dataContent['keystr']
            description=dataContent['description']
            jsonvalue=dataContent['jsonvalue'] 
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :            
                if is_new :   #create new one        
                    dictObj, created = DictionarySetting.objects.get_or_create(keystr=keystr)               
                    if created:   #renew token every time login                      
                       dictObj.category=category 
                       dictObj.keystr=keystr 
                       dictObj.description=description 
                       dictObj.jsonvalue=jsonvalue                 
                       dictObj.save()              
                       res={'msg_code':1,'msg':"dictionary saved","msg_i18n":"common_msg.save_ok"}
                       return JsonResponse(res)
                    else :
                       res={'msg_code':0,'msg':"this dictionary id is exist","msg_i18n":"common_msg.key_is_exist"}
                       return JsonResponse(res)
                else:  #update
                    dictObj = DictionarySetting.objects.get(keystr=keystr)    
                    if dictObj is not None:   #renew token every time login
                       dictObj.category=category     
                       dictObj.description=description 
                       dictObj.jsonvalue=jsonvalue                 
                       dictObj.save()                 
                       res={'msg_code':1,'msg':"dictionary saved","msg_i18n":"common_msg.update_ok"}
                       return JsonResponse(res)
                    else :
                       res={'msg_code':0,'msg':"this dictionary id is not exist","msg_i18n":"common_msg.key_is_not_exist"}
                       return JsonResponse(res)     
            else :
                 res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                 return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)    


class API_VUE_DeleteDictionary(View):
  
    def __init__(self,*args,**kwargs) :
        print('API_VUE_DeleteDictionary load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)   
            print('post data =',post_data)               
            token_id=post_data['token_id']
            keystr=post_data['keystr']
            token = Token.objects.get(key=token_id)            
            is_expire, token=token_expire_handler(token)
            if is_expire :
               #do delete
               dictObj = DictionarySetting.objects.get(keystr=keystr)   
               if dictObj is not None:   #renew token every time login
                    #delete
                    dictObj.delete()
                    res={'msg_code':1,'msg':"success","msg_i18n":"common_msg.delete_ok"}
                    return JsonResponse(res)    
               else : 
                    res={'msg_code':0,'msg':"role is not exist","msg_i18n":"common_msg.key_is_not_exist"}
                    return JsonResponse(res)       
            else :
                 res={'msg_code':0,'msg':"token is not expire","msg_i18n":"account.token_over_exprie"}
                 return JsonResponse(res)
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)




class API_VUE_GetDictionary(View):
  
    def __init__(self,*args,**kwargs) :
        print('API_VUE_GetDictionary load!')
         
    def post(self, request):    
        try :
            post_data=json.loads(request.body)                            
            keystr=post_data['keystr']     
            print('post data =',post_data)      
            dictObj = DictionarySetting.objects.get(keystr=keystr)   
            if dictObj is not None:   #renew token every time login
                    #jsonvalue=json.loads(dictObj.jsonvalue)
                    dictJson={}
                    dictJson["keystr"]=dictObj.keystr
                    dictJson["category"]=dictObj.category
                    dictJson["description"]=dictObj.description
                    dictJson["jsonvalue"]=dictObj.jsonvalue
                    res={'msg_code':1,'msg':"success","msg_i18n":"","data":dictJson}
                    return JsonResponse(res)    
            else : 
                    res={'msg_code':0,'msg':"role is not exist","msg_i18n":"common_msg.key_is_not_exist"}
                    return JsonResponse(res)       
            
        except Exception as e:
            res={'msg_code':-1,'msg':str(e),"msg_i18n":str(e)}
            print(res) 
            return JsonResponse(res)            



class API_VUE_DictionaryTree(View):  
    cursor=None
    mysql_host=os.getenv("DB_HOST")
    mysql_port=os.getenv("DB_PORT")
    mysql_acc=os.getenv("DB_USERNAME")
    mysql_pw=os.getenv("DB_PASSWORD")
   
    def db_connect(self,db_name):
        #print(self.mysql_host,self.mysql_acc,self.mysql_pw,db_name)
        self.db = pymysql.connect(self.mysql_host,self.mysql_acc,self.mysql_pw,db_name)
        self.cursor = self.db.cursor()
    def db_close(self) :
        self.cursor.close()
        self.db.close()

    def __init__(self,*args,**kwargs) :
        print('API_VUE_GetDictionary load!')
         
    def post(self, request):           
          db_name=os.getenv("DB_NAME")
          dict_tree=[]
          self.db_connect(db_name)
          query_sql=f"""  
               SELECT category,keystr,description,count(keystr) as count 
               FROM dictionary_setting group by category,keystr,description                 
               """   
          try:
             # 执行SQL语句             
             self.cursor.execute(query_sql)
             # 获取所有记录列表
             category_list=[]
             results = self.cursor.fetchall()
             full_tree={} 
             setting_count = len(results)
             for row in results:                 
                 category=row[0]
                 key=row[1]
                 desc=row[2]
                 count=row[3]
                 if category not in category_list :
                    category_list.append(category) 
                    full_tree[category]={'level':1,'id':category,'label':category,'children':[]}
                    full_tree[category]['children'].append({'level':2,'id':key,'label':desc,'count':count})
                 else :
                    full_tree[category]['children'].append({'level':2,'id':key,'label':desc,'count':count})
             #print('full tree=',full_tree)       
             for k,v in full_tree.items() : 
                 #print(k,v)      
                 dict_tree.append(v)     
                         
          except Exception as ex:
             print ("sql Error !!!",ex)
          self.db_close()      
          res={'msg_code':1,'data':dict_tree, 'setting_count':setting_count}
          return JsonResponse(res)  


 

