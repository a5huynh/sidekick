#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ahuynh
# @Date:   2015-06-18 20:15:30
# @Last Modified by:   ahuynh
# @Last Modified time: 2016-02-11 17:27:50
import unittest

from sidekick import announce_services, check_name, find_matching_container
from sidekick import check_health, public_ports, parse_args
from tests import MockEtcd
from unittest.mock import patch


class TestSidekick( unittest.TestCase ):

    def setUp( self ):

        self.args = parse_args( [ '--name', 'test', '--ip', 'localhost', '--check-ip', '0.0.0.0' ] )
        self.etcd_client  = MockEtcd()

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
        services = find_matching_container( [self.container], self.args )

        # Test successful health check
        with patch( 'sidekick.check_health', return_value=True ):
            announce_services( services.items(), 'test', self.etcd_client, 0, 0, False )
            self.assertEqual( len( self.etcd_client.written.keys() ), 2 )

        # Test unsuccessful health check
        with patch( 'sidekick.check_health', return_value=False ):
            announce_services( services.items(), 'test', self.etcd_client, 0, 0, False )
            self.assertEqual( len( self.etcd_client.deleted ), 2 )

        # Test correct etcd exception handling
        self.etcd_client = MockEtcd( raise_exception=True )
        with patch( 'logging.error' ) as mock_method:
            announce_services( services.items(), 'test', self.etcd_client, 0, 0, False )
            self.assertEquals( str(mock_method.call_args[0][0]), 'Test Exception' )

    def test_check_health( self ):
        """ Test `check_health` functionality """
        results = find_matching_container( [self.container], self.args )

        for value in results.values():
            # Unsuccessful socket connection
            self.assertFalse( check_health( value ) )

            # Successful socket connection
            with patch( 'socket.socket.connect' ) as mock_method:
                check_health( value )
                args = mock_method.call_args[0][0]
                self.assertEqual( args[0], value[ 'check_ip' ] )
                self.assertEqual( args[1], value[ 'port' ] )

    def test_check_name( self ):
        """ Test `check_name` functionality """
        self.assertTrue( check_name( self.container, 'test' ) )
        self.assertFalse( check_name( self.container, '/test' ) )

    def test_find_matching_container( self ):
        """ Test `find_matching_container` functionality """
        # Test a successful match
        results = find_matching_container( [self.container], self.args )
        self.assertEqual( len( results.items() ), 2 )

        # Test an unsuccessful match (no matching names)
        invalid_name = dict( self.container )
        invalid_name[ 'Names' ] = [ '/invalid_name' ]
        results = find_matching_container( [invalid_name], self.args )
        self.assertEqual( len( results.items() ), 0 )

        # Test an unsuccessful match (no public ports)
        no_open_ports = dict( self.container )
        no_open_ports['Ports'] = []
        with self.assertRaises( Exception ):
            find_matching_container( [no_open_ports], self.args )

    def test_public_ports( self ):
        """ Test `public_ports` functionality """
        self.assertEquals( len( public_ports( self.container ) ), 2 )
