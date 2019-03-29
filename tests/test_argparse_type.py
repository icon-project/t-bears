# -*- coding: utf-8 -*-
# Copyright 2017-2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import shutil
import unittest

from tbears.util.argparse_type import *


class TestArgparseType(unittest.TestCase):
    @staticmethod
    def touch(path):
        with open(path, 'a'):
            os.utime(path, None)

    def test_icon_path(self):
        file_path = './icon_path_test'

        # 'r' mode
        icon_path = IconPath()
        self.assertRaises(ArgumentTypeError, icon_path, file_path)

        self.touch(file_path)
        self.assertEqual(icon_path(file_path), file_path)

        # 'w' mode
        icon_path = IconPath('w')
        self.assertRaises(ArgumentTypeError, icon_path, file_path)

        os.remove(file_path)
        self.assertEqual(icon_path(file_path), file_path)

        # 'd' mode
        icon_path = IconPath('d')
        dir_path = 'dir_not_exist'
        self.assertRaises(ArgumentTypeError, icon_path, dir_path)

        dir_path = 'dir_path_test_file'
        self.touch(dir_path)
        self.assertRaises(ArgumentTypeError, icon_path, dir_path)
        os.remove(dir_path)

        dir_path = 'dir_path_test'
        os.mkdir(dir_path)
        self.assertEqual(icon_path(dir_path), dir_path)
        shutil.rmtree(dir_path)

    def test_icon_address(self):
        icon_addr = IconAddress('all')

        # valid address
        addr = f'cx{"a"*40}'
        self.assertEqual(icon_addr(addr), addr)
        addr = f'hx{"b"*40}'
        self.assertEqual(icon_addr(addr), addr)
        addr = f'hx{"0"*40}'
        self.assertEqual(icon_addr(addr), addr)

        # length < 42
        self.assertRaises(ArgumentTypeError, icon_addr, f'cx1')

        # length > 42
        self.assertRaises(ArgumentTypeError, icon_addr, f'cx{"0"*40}1')

        # upper case
        self.assertRaises(ArgumentTypeError, icon_addr, f'cx{"0"*39}A')

        # None hex
        self.assertRaises(ArgumentTypeError, icon_addr, f'cx{"0"*39}k')

        # hx prefix
        icon_addr = IconAddress('hx')

        addr = f'hx{"b"*40}'
        self.assertEqual(icon_addr(addr), addr)

        self.assertRaises(ArgumentTypeError, icon_addr, f'cx{"b"*40}')

        # cx prefix
        icon_addr = IconAddress('cx')

        addr = f'cx{"b"*40}'
        self.assertEqual(icon_addr(addr), addr)

        self.assertRaises(ArgumentTypeError, icon_addr, f'hx{"b"*40}')

    def test_hash_type(self):
        # valid hash
        hash_str = f'0x{"b"*64}'
        self.assertEqual(hash_type(hash_str), hash_str)

        # invalid type
        hash_str = 0x1234567890123456789012345678901234567890123456789012345678901234
        self.assertRaises(ArgumentTypeError, hash_type, hash_str)

        # invalid prefix
        hash_str = f'hx{"b"*64}'
        self.assertRaises(ArgumentTypeError, hash_type, hash_str)

        # length < 66
        self.assertRaises(ArgumentTypeError, hash_type, '0x1')

        # length > 66
        hash_str = f'0x{"b"*64}1'
        self.assertRaises(ArgumentTypeError, hash_type, hash_str)

        # upper case
        hash_str = f'0x{"b"*63}B'
        self.assertRaises(ArgumentTypeError, hash_type, hash_str)

        # None hex
        hash_str = f'0x{"b"*63}k'
        self.assertRaises(ArgumentTypeError, hash_type, hash_str)

    def test_port_type(self):
        # valid port
        port_str = "9000"
        self.assertEqual(port_type(port_str), int(port_str, 10))

        # invalid type
        port_str = 9000
        self.assertRaises(ArgumentTypeError, port_type, port_str)

        # invalid hex string
        port_str = '0x1'
        self.assertRaises(ArgumentTypeError, port_type, port_str)

        # value < 0
        port_str = '-1'
        self.assertRaises(ArgumentTypeError, port_type, port_str)

        # value > 65535
        port_str = '65536'
        self.assertRaises(ArgumentTypeError, port_type, port_str)

    def test_non_negative_num_type(self):
        # valid int
        int_str = "1"
        self.assertEqual(non_negative_num_type(int_str), hex(int(int_str, 10)))
        int_str = "1a"
        self.assertEqual(non_negative_num_type(int_str), hex(int(int_str, 16)))
        int_str = "0x1a"
        self.assertEqual(non_negative_num_type(int_str), int_str)
        int_str = "0"
        self.assertEqual(non_negative_num_type(int_str), hex(int(int_str, 10)))
        int_str = "0x0"
        self.assertEqual(non_negative_num_type(int_str), int_str)

        # invalid type
        int_str = 9000
        self.assertRaises(ArgumentTypeError, non_negative_num_type, int_str)

        # invalid hex string
        int_str = '1k'
        self.assertRaises(ArgumentTypeError, non_negative_num_type, int_str)
        int_str = '0x1k'
        self.assertRaises(ArgumentTypeError, non_negative_num_type, int_str)

        # invalid negative number
        int_str = "-1"
        self.assertRaises(ArgumentTypeError, non_negative_num_type, int_str)
        int_str = "-0x1"
        self.assertRaises(ArgumentTypeError, non_negative_num_type, int_str)
