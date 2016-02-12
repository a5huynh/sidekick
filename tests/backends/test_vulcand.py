#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ahuynh
# @Date:   2016-02-11 14:28:02
# @Last Modified by:   ahuynh
# @Last Modified time: 2016-02-11 17:27:07
import unittest

from sidekick import announce_services, find_matching_container, parse_args
from tests import MockEtcd
from unittest.mock import patch


class TestVulcandBackend( unittest.TestCase ):

    def setUp( self ):

        self.args = parse_args([
            '--name', 'test',
            '--ip', 'localhost',
            '--check-ip', '0.0.0.0',
            '--vulcand', 'True'
        ])

        self.etcd_client = MockEtcd()
        self.container = {
            'Image': 'image:latest',
            'Ports': [{
                'PrivatePort': 9200,
                'IP': '0.0.0.0',
                'Type': 'tcp',
                'PublicPort': 9200
            }, {
                'PrivatePort': 9300,
                'IP': '0.0.0.0',
                'Type': 'tcp',
                'PublicPort': 9300
            }],
            'Created': 1427906382,
            'Names': ['/test'],
            'Status': 'Up 2 days'
        }

    def test_vulcand_announce( self ):
        """ Test `announce_services` functionality """
        services = find_matching_container( [ self.container ], self.args )

        # Successful health check
        with patch( 'sidekick.check_health', return_value=True ):
            announce_services( services.items(), 'test', self.etcd_client, 0, 0, True )
            self.assertEqual( len( self.etcd_client.written.keys() ), 4 )

        # Unsuccessful health check
        self.etcd_client._reset()
        with patch( 'sidekick.check_health', return_value=False ):
            announce_services( services.items(), 'test', self.etcd_client, 0, 0, True )
            self.assertEqual( len( self.etcd_client.deleted ), 4 )

        # Correct etcd exception handling
        self.etcd_client = MockEtcd( raise_exception=True )
        with patch( 'logging.error' ) as mock_method:
            announce_services( services.items(), 'test', self.etcd_client, 0, 0, True )
            self.assertEquals( str(mock_method.call_args[0][0]), 'Test Exception' )
