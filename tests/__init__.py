#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ahuynh
# @Date:   2016-01-28 10:04:58
# @Last Modified by:   ahuynh
# @Last Modified time: 2016-02-11 14:30:08


class MockEtcd( object ):
    def delete( self, value ):
        pass

    def write( self, value, ttl ):
        pass
