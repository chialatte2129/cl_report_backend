#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @file    : urls.py
# @Date    : 2019/5/24
# @Author  : Jack
# @Contact : 
# @Version : $
# @Version History:
#

"""apisvr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import url, include
from api.vue import account, role, dictionary
from api.image_service import equip_image

from api.equipment import equip_categories
from api.equipment import equipment

#路徑以"/版本/api名稱(小寫+底線)" 表示
urlpatterns = [
   
    ###account
    url('v1/login',account.API_VUE_Login.as_view()),  
    url('v1/check_token',account.API_VUE_Token.as_view()),
    url('v1/change_password',account.API_VUE_ChangePassword.as_view()),
    url('v1/list_account',account.API_VUE_ListAccounts.as_view()),
    url('v1/save_account',account.API_VUE_SaveAccount.as_view()),
    url('v1/delete_account',account.API_VUE_DeleteAccount.as_view()),
    
    ###role
    url('v1/list_role',role.API_VUE_ListRoles.as_view()),
    url('v1/save_role',role.API_VUE_SaveRole.as_view()),
    url('v1/delete_role',role.API_VUE_DeleteRole.as_view()),
    ###dictionary
    url('v1/save_dictionary',dictionary.API_VUE_SaveDictionary.as_view()),
    url('v1/delete_dictionary',dictionary.API_VUE_DeleteDictionary.as_view()),
    url('v1/get_dictionary',dictionary.API_VUE_GetDictionary.as_view()),
    url('v1/dict_tree',dictionary.API_VUE_DictionaryTree.as_view()),  

    url('hello',dictionary.API_VUE_Hello.as_view()),  

    url('v1/equip/image',equip_image.API_CALL_View.as_view()),  
    url('v1/equip/bytes_array/image',equip_image.ImageBytesArray.as_view()),  

    url('v1/equip/categories/get_list',equip_categories.EquipCategoriesList.as_view()), 
    url('v1/equip/categories/update',equip_categories.UpdateEquipCategory.as_view()), 

    url('v1/equip/get_list',equipment.EquipmentsList.as_view()), 
    url('v1/equip/update',equipment.UpdateEquipments.as_view()), 

]

