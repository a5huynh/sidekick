#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ahuynh
# @Date:   2016-01-28 10:04:58
# @Last Modified by:   ahuynh
# @Last Modified time: 2016-02-11 17:25:54
import etcd


class MockEtcd( object ):

    def __init__( self, raise_exception=False ):
        self._reset()
        self.raise_exception = raise_exception

    def _check_raise( self ):
        if self.raise_exception:
            raise etcd.EtcdException( 'Test Exception' )

    def _reset( self ):
        self.deleted = set([])
        self.written = {}

    def delete( self, key ):
        self._check_raise()
        self.deleted.add( key )

    def write( self, key, value, ttl ):
        self._check_raise()
        self.written[ key ] = value
