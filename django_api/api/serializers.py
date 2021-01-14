#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @file    : serializers.py
# @Date    : 2018/3/19 19:01
# @Author  : Tony Liu ()
# @Contact : tony.sy.liu@foxconn.com
# @Version : $
# @Version History:
#    

from .models import AsrReceiveDataModel
from rest_framework import serializers

class AsrReceiveDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AsrReceiveDataModel
        fields = ('user_id', 'session_id', 'device_id',
                  'asr_result', 'asr_data', 'timestamp',
                  'sig',)

