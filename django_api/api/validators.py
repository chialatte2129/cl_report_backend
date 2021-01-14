#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @file    : validators.py
# @Date    : 2018/3/19 19:42
# @Author  : Tony Liu ()
# @Contact : tony.sy.liu@foxconn.com
# @Version : $
# @Version History:
#    
from django.core.validators import BaseValidator


class SignitureValidator(BaseValidator):

    def compare(self, a, b):
        return a != b

    def clean(self, x):
        return x