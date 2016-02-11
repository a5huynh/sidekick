#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ahuynh
# @Date:   2016-02-11 14:28:02
# @Last Modified by:   ahuynh
# @Last Modified time: 2016-02-11 14:49:02
import unittest

from sidekick import announce_services, find_matching_container, parse_args

from tests import MockEtcd


class TestVulcandBackend( unittest.TestCase ):

    def setUp( self ):

        self.args = parse_args([
            '--name', 'test',
            '--ip', 'localhost',
            '--check-ip', '0.0.0.0',
            '--vulcand'
        ])

        self.etcd_client = MockEtcd()

        self.container = {
            'Image': 'image:latest',
            'Ports': [{
                'PrivatePort': 9200,
                'IP': '0.0.0.0',
                'Type': 'tcp',
                'PublicPort': 9200 }, {
                'PrivatePort': 9300,
                'IP': '0.0.0.0',
                'Type': 'tcp',
                'PublicPort': 9300}],
            'Created': 1427906382,
            'Names': ['/test'],
            'Status': 'Up 2 days'
        }

        def test_announce_services( self ):
            """ Test `announce_services` functionality """
            services = find_matching_container( [ self.container ], self.args )
            announce_services( services.items(), 'test', self.etcd_client, 0, 0, True )
