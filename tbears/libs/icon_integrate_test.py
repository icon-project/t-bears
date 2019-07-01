# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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

import hashlib
import inspect
import random
import sys
from collections import namedtuple
from shutil import rmtree
from time import time, sleep
from typing import Any
from typing import List
from unittest import TestCase

from iconcommons import IconConfig
from iconsdk.builder.call_builder import Call
from iconsdk.builder.transaction_builder import MessageTransactionBuilder
from iconsdk.converter import convert_transaction_result
from iconsdk.exception import IconServiceBaseException, URLException
from iconsdk.icon_service import IconService
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from iconservice.base.address import Address
from iconservice.base.block import Block
from iconservice.base.type_converter import TypeConverter, ParamType
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey, DATA_BYTE_ORDER
from iconservice.icon_inner_service import MakeResponse
from iconservice.icon_service_engine import IconServiceEngine
from iconservice.utils import to_camel_case

from tbears.config.tbears_config import TEST1_PRIVATE_KEY, tbears_server_config, ConfigKey as TbConf

SCORE_INSTALL_ADDRESS = f"cx{'0' * 40}"
Account = namedtuple('Account', 'name address balance')

TEST_ACCOUNTS = [
    b'\x17}\x1c\xdc\x87\xab\xd8\xd5\x15\xc5c\xdfb)M\x0b\xac\xa6\x17B\xf6<\xda;\xf2\x02.,\xa2.\x07\x80',
    b'\x96V\xcbL \xbe\xf3>\xc7\xd1\xe8i\xbc+\xe9t\xb0\x98H\xa7_\x001n1\xfdT~\xb2\xe4\xa0\x05',
    b'\xf3\xa7\xfd\xcdb\xfe\xd9\xff-\x9a\xdezVW\xe7\xf2.G\xf5\xce\x99hq\xa7\xca\x0f\xbe\xd2\xe0_k\x1b',
    b'\x92\x00\x1b\x12\x9da\x0c`7\xed\xb5\xef\xb8\xeez_\x1c\xdf&\x16E\xdb\xb4\xb1\x8aL\xd5;\x1dX\x9fn',
    b'\xc3\x8b\xa0\xad\xddI\x04D\xcb\x13#\xc8\xe3\xa8\xfd\xd9l\xa8\x84}Q\x19\xac\x89\x9bT\x19g4\x85&\x8c',
    b'\xec\xee\xf3+|\xf7\x8e&\xa6\xdc\xff">&\xd4\x00?\xa7\x80\x9b\xea\xa2\xc0Z\'\x9d\x08\xd4\x07i\xf0>',
    b'\x04\xff\xb1-\xfd\xaaK\x9c@\x91\x175\xf2\xde\xc8@\xf4\xfe\x1a^\x1bT\x0czT\xda\x0b+xI\xd8\xe1',
    b'\xb4\x0c\xa9\xc61\x8a\xa2\x1a!\x95\x13\xeb\xc1g\xd0Gm$\xce0J\xf6(\xf3\xd3\t\x8f\x1d\xf2\xac#\x92',
    b'\x11\x96sU\xde+\xf0\xf6\xe09\x1d\x86\xd1\xfb\xf5M:\xd0\xc3\x12\xea\x995\x16 \x93\x95\xdd6\x13\xb9o',
    b'p\x19X\xea&i\x91\xbd\x99\xe70=\x7fc\xabg`(2\x98\xbc\xf0YW\t\xf8\xb3\xcaI\x16F\xfd',
    b'y\xec\xca\xf4\x8b^\xf8\xa6Du6k\x0e\x04\xdfB\xcfYi\xf1z\xcc\xf3\xddP\xe88\xc0T*\x1aK',
    b"\x95\xc3\x08\xd9\xc9\xd4w\xd3\x16\xb0;\xc0=\x15Q]gg\xf0\x18\xf9\xf4\x0e'\x16\x0b\x81\x92~\x8d\x93\xd2",
    b'$#\xb2zv4#\xddOq9(\x99\xbd\xde\xb6p,P\xb8\x80\x07\xf9D\xdd\x1c\x06\xfd\xacF0\xb1',
    b'4\x86\xad}\x04\xfc@\x0188\xa49f>\x97\x18\x05Tb\xd9f\xda\xa2\xa4j\x13Tp\xc3i\x0b\x01',
    b'\x1ee[lv!\x16v\xfc\x0e<\xadP\x91\xda\xc9\xd59\x90\xc1\x93C\xfam\xa3p\x0f<\x06\xeb\xfb\xba',
    b'U\x92\xd1g#\x84;\x80\x01\x02c\x90\xbdPx\x8a\xa5Z\x08U\x02\xff\n\xa0\x94\x1c\xb9\x8c\tr\xf0\x96',
    b'\x0f\xf2I\x9f-x\xa7\xe7\x9d\xba\x9c\xdbKn(\xcb\x85\x82\xf9\xca\x18Hu:\xa2\xef\xa1\x0c\xb2\xfd\x1at',
    b'\xdf$\x89\xe1O\xd9\xe0\xeak\xdd\x15\xf0\xe3}B\xe3\x8a\xca#\\\xfex*8x\xbe\x97\x01\xafu:\xc6',
    b"\xd4^x\x98\xaee\xc7\xea-\xb3\x9c23\xa0\x11>\x87\xb8}\xb5\x90\xf3o']\x01\xc7\xbe\xc5i\x8b\xee",
    b'\x8e\x8b\xc9o6\xe5\x01~\xfb_\x862\x8a\xb8\x03\\\x84\xfe\x96R\x08\xe6\x027:\xd3\xdb\xff=!\xea\xda',
    b'\x0f\x07\xcd]>\xf8\xf4\xaeV\xe8 M\xd4\xcdb\xb6\xa4M\xff\x130\xa0\x9di\xdc\xd7\x0e\x8a@\xcb\xf1t',
    b'\x99\x1eD\xa3\xb8p\xcb\x0b\xd7\x80\xfd\xc6\xe7AN\x9e,|\xea\xc0\x9e\xf6)\xa6\xb0n\xe4\xa6\xcb\x07\x83\xbf',
    b'XG\xf8\x080\x8c\x7f\x977\x9c\x7f4lY\xf21\xfc\x82\x9b\xd1\x0f\xf6\x05kx&\xe6\x91d\x9e\xce\xf0',
    b'\xb2\x9e\xf1\x90\xee\xa5!\xaf*\x05;D#tD\x87aR#\x99\xb3\r\x1db\x98\xf8/=\xb01#\xe5',
    b'\r\xe8\x1a_e\x12\xd7cx\xcdd9k,"}\xf3\xe6\xe6\xf6(\xffH\x01\xfd\xea\xc8j\xf5M%\xde',
    b'%\x010\n\x7f;\xb0\x17\xb6\xf58yp\xa0\xa9\xac\x83\xa1\xfe\x83\xf6\x1d\x8b\xa5\xe4\x0e\xb9.\xcf\x9d\xd9:',
    b'\xa6\xa0\xf2\xe5wHpt\x87Ks\x1b\x91\x80\xb1\xa8\x86a\xfca;\xcf\xfd\x84\xd2<\xcaJ\xa7\xbc*\xce',
    b"i\xa7\n\xde\xc5\xd0T#\xde\x02E'^ _\xfe\xf5\\\x8c\x15\xb2\xa9]\xba\x97m\xd4\x0eHF+E",
    b'\xd3\xd0y\x7f\xafiA\x8dD\x87\x07\xff\x9f\xd9\x88S\x89\xac~\xdc\xc9ZE\x01\xd0\x93\x07\xcdEA\xb2\x13',
    b'&\x8do\x00Cw\x94\xc3h\x0ec\x1aUL\x1dEU\xe27\xd6\xa0\x17,\xd9\xe0=+\xa6\xa3\x81l\xf3',
    b'^\x1d\xf6\xf6.\xa7\x91f\x8d\x90\xaf\x96\xd7y\xd9P0\x96\xde\xa4\x96E\xd5\xae\xd2\xfa_\xdb\xa2J\x12\x9f',
    b'\xab51\x1c\xc5\x05\xa9,-\xd4\xe3K0\xa9Ga\xe5&\xb4\xa1\xfdb\xb9\x83\x7f\xfd\xb6\xec\xc0#\xb2m',
    b'\xb5\x19\x0eh\xa8\xcd\xc3\x12=\xa8\x9e\xef\xce\xbe~\x81\x90o\x18\xfd\xd9\x16\xf8a\xe5T\x0f$\xc9\xb9\xdbC',
    b'\xc1\x16\xd7\xb3H\xc7\xc0\x151\xe5\x00\x10\xbf:\xb8s\xc6[[zE\xc7}\xf7Bv\x1e\x82\xd8_\x1fe',
    b'\xa3\xb7"\x19\xfa0\x92\xd1\x80fS\xf8\x87\x07=3>\x04G^O\x9e\xf1u\xc1q\x85\x11\xd9\xf3~\xed',
    b'\x9dHG\x8b\x86\x0c\x94B\xa6\x15\x84\x9a=\xe7\xa6\xb8pK\x10\xe5\xec\xb0\xaf!\xd3\xfb*\xef\xeaq\xef\xa4',
    b'+^\xe4\xed*B\x7f\xe2\xd4\xe6_\xaby\x9d\xb6]z\x97T\xc1\x88\x10Q\xc4[\x9e\xaa\xb6\xaa\t\xf9\xba',
    b'\xb5\x1fA"\xda\xc8\x19\xc6W8\xa1\xd0\xd30c\xa0\x97j\x93x\x06\x19m:[\x18\x1e\xbe\x04\x11\x08/',
    b'\x00\x0c/\x14[\x0b\xd7V*\x84\x8b~\x8c\xd5B\x00\xd8M\xde^p5\xfb!n\xe4 \x03\xdc\xad\x1cR',
    b'\x03e\xa6\x1e\xa0\xc4S\x9fO\xa8\x14\xc7\xc8\x1d\xf8"\x80\x9eh\xc2~\xbds\xa1D;9\xa3\x9b\xc2z\x1c',
    b'7\x08\x95Ig\x1b\xf1\xb3\x1c\x89\xe7\x85#\x8a\xd3wk\x91L\xcc\x19\xf6\xa7A\x14\x82\xce\xff\xb56D=',
    b'\x95\x16\nkX\xc4\xee4\x10\\\x90X\xedm\xd4\xe3\x06K\x9bG\x98\xb3(}\x01#\x9d)\x17y:e',
    b'\x9c\xa5G\xfa\xe4\x8a\xbe]\xd4\x1d\xc5\xb4j\xba\x86\x8f\xe7\x18\xa3\x88k\xb9\x1a\x1ci\xb5{\xb5\xb3\x97\xf2\x87',
    b"$Y\xeei\xec\xbaa\xfa\x04ja\xdam\x03o\xf9\xed\t\x97\xb5\xaa\x97\x1e\x90\xed\x14\xbb\xc3\x13Q\x12'",
    b'!\xf8\x0c\x0b\x90\xf0ns\x06\xeeLe?\xca#\x17\xe3\xa2{=\xaeE\xd8\xe0\xc97\xee5mL\x99\xf3',
    b'\xf674\x0b\xd4dbr\xad],\xd4\x8bV84\x99D"~G\x82\xad\xd9\xdbr\x86\xa4\xfdw*\x06',
    b'*e\xac~@\xd4s\xc2\xaaj\xd9\x96\xd8Yl\xb9Wt9\t\x17\xe5\x1d[tn\xde2\x12\x1d\xd6\x97',
    b'`\xdf\x01\xe7\xc3\x88C\xff\xbb\x94\xfdf\xaa\x9c\x8cwY\x02q\x9c\xe0t"\x8fC\xdf\xde\xcc\x1f\xe5\xd9\xdb',
    b'\xf1\xfd\xec\x86!w\xf2\xc1\x89\xcc\xe8\xc08\xf3\x8c]\xf0\xae\x112\xf5\x81\xea2T;\x97)\xbd\x000\xa9',
    b'\x9f\xbd\x9c\xf2\xdb\xbe\xc1\x87[4\x03\xa4\xb7\x92\xd85\x1f,\xa0\xcb\xa3SyI\xd3\xa5{\xe1\xdfkt\x17',
    b'\xa3\xc3\xdd\x98;\xe5\xb38g\x9b\xa5\x92\xae\xafm\x14P}r"\xca;\\d]\xda\xb0\x880\xdf#\xb0',
    b'\xff\x8c\xd3\x1f\x14\x89\xaa\xb5k\xe6 M&\xa3\xd0\xdf\x1a\x97\x82"\x064\xeao\xdb\xf6\xc4]\x94\xeb\x87\xd9',
    b'\x9f\x93\xbe\xc9E\xcen.xn\x89\xa7HV\xa2\x80Y~X\xf1\xd0\xce\xd3\xb8\xf5\xbf\x05\xd5\xc0IG\xe0',
    b"\xb1{\x06X\xba\xb7\xceQD\xa3\xa7X\x04'\xb8qu\x10\xae\x87\xc2[F\xc4^\xcd>b#s\xd5\x01",
    b'${\xc7#\xa2\xb5(\xbc\x92>H9\r=\xaeS\xfbR*\x00?\xd2\xeb\x86WL/\xda8\x03W\x1d',
    b'c9I\xf9\xfe:\x1b%\x1d\xa3t\xf2\xa6\x9b\xb6c\x00CZ\xe6<\x10\xf5\xf31\xea|\x9c\xe3#\x99\x10',
    b'\x88~\xab\xec\xed\xdf.E\xd3\xae\xb5\xe0\xa8\x19,\xdd\xba\x89\x95\xf0\xc4\x93\xe6\xf2\xec\x1aW\x8c\xe0\xf9`\xec',
    b'\x89:\xbf]/\x9d\x9e\xc25~\xb1;\x912\xec\xec\x91\xd5 \xed\x8b\xc7\xf0\xc8\xdcn2S\xf1\x17-V',
    b'\xc1\xfc\xbd\xaaM\xa9\xc74\x82D\xa6_\x1bl&\x95\xaf\xbc\x93YO\xe3\xf0\x0eW\xf6f\xf4@\xe0v\xe1',
    b'A\xe9\x7f9\x85\\\x80d8C}$w|\xb2\x18\xdc\xff\xb3\xaaY\x8e%e\x1d\x9d%\xd8&A\xb1\xa9',
    b'Dr8\x1b\xab\xed\xe4\xd5\xb5\xdc3b\xb8\xf3\x81\x15\xf0\x0b;\xad$\xce\x86\x1a\x8d)\x1eVBi\x8b\x84',
    b'\x0b\xe4\xf5\x8e\xdf\xb5\x0b\x9a\x8d\xee\t\xd5W\xe96\xa3\x9c0\x98\xaa\xcc\xe3a\x07\xd93\x02\xfd\x89\x94+\xe1',
    b'I?J\xa4g\x89DGS5m\x96.>\xbenw\xf8+\xf7\xec5\xb8\xde \xf1\xeey\xce^\x16\xd8',
    b'\xc8y(\xb0\x9fn\xca\xb6\xc2~\xf4\xe0\xc2|\x0f\x1aTF\xf6l\xaa~7j\x18^\x08\xc5\xd9\xdf$\xb0',
    b'\xc8\r\xcc\x8aQ\xda\xb1\xe8\xef\x1c\xb5v\x01t\x7f\xea\x96/\xd0\x08CJO\x99Z6\xc2\x13P\x1f\xf5\x98',
    b'+rR\xbf\x03\xd7\x87\xe2;/\x992\xe4\xcb\x8c\xbc\x88i\xc8\x81H\x82Z\x8e\xea\xdc$\xac\r\x84\x017',
    b'\x81o\xf6\xc1\xd0\xee\x12\xaf\xc0\xec\x0b\x0e\x01\xa2a9Y\x95\xbc^\xabMg\x87\xd3\rN\xcb`\x88e\xbc',
    b'!\xcdO}\xb6\xd3\xc27\xfdl\x16w0\xd1D\x83&Ph\x04\x06\xf4B\xf8\x1c\xba\x00? \xea\x0e1',
    b'9t\xbc!O;\xa3\x85\xf4<M\xffQ\x9f\x04W\xff\x00\xb8\xd3C\xf5\x88\xef\x83i\xb4#\x16X\xed\x8d',
    b'\xa2\xa2\xb2\x82\x9e2@\xcf\xe1\x05\xb1\xdd\xcb\x96\xd0\x95\xad"\x8d\xf8/O\xeb\xd7\xdf\x14\x12#K-\x94@',
    b'A\x87\xaeb\r\xee\xca.\xb2\xe8\xf8\x0bU\x7f\xa1l\xb5\x0c= -cLY\xbesu\x0f$\xe7\xa7T',
    b'\xfe\xee<\xbd\xd2\x1f\xa8Q\xb1\x9a$\xe6\x95o\xa9u\xa8Y\xec#\xb4\xdbK]\xb5{\xd6&\x1d\x12\xfe\x94',
    b'\xa8\x15P@\xa2p\x84\x91@.\xd1\xcc\xb0\x13\x14\x03\x91\xca\x0c\x9ez"\xa4\xdfG\xa3\x86Q\xd0\x10W\x03',
    b'\xd87W\t\xdc<}+\x87\xdeT\x9a\xa3\x08q\xeb a\x9d\x06\xaf\xd9c\x16\x16\xf8\xb9y\xc4{WG',
    b'^>l_\xf8\xf6}\xcfi\x03\xfb\x17=P\xa6\x86\xf2\x91\xff\xa20Q\t<\x8d\x02\xbd\xe1qusO',
    b'\xf6\x83R\xb9\x02\xa0\x84\xc1-sm\x83\xfcd\xd1\x8a\xe5\xe5{\xc0Gz\xbdj<\xb2\xe7!\xed\xa9\x9f\x16',
    b'\x06f\xdb0\x90\x7f\x97A\x8f=j#^L\xb4\xf9&K\xa1\x99g\xf0\xa1l\xdbm\xc5\xfb\x12\xa2\xb7+',
    b"P\x0e\xc8\x98G\xc3D\x0f\xdd(D\xe3\x07'F<\xa5Y\xf7\xd7\x08\x08O\xdf\xd9\xb6\t\xcc2|*\xa5",
    b'\xaa\x94\x97KO\x19\x7f\xee\xaa\xc5\xc5\x04\x0f\xf3\xf2|\xc5\x075EMY~\xb3L\x08\x17nR[\xc2C',
    b'\xf9\xdf\xbf\xdf;v\x87\xbb\xd4\x00J\xa9\x8dJ\x0f\x11 \x82\x7f\x9c\xbd#\xe8&3\xda\xf9p\x0ehx\xe1',
    b'\xf1\xc3\x9e1]b\xc6_\xc0\x86\xcc\x96+\xa9\xa1\xe5\xea\xc2\xad\xb4\xbb4=mSe\xf8$\xc7XE[',
    b'G\xc0\x9f%h\xe6\xcc/\x8d\xaeptN686!\n\xd5\xd3g\xd4;$\x98B`a\xd8\x99P\xc0',
    b'\x0e\xfb\xf4\xc2\x05\xe8\xdc\xe7qK\x90s\xd6\x8c\xd0\x89\xa3\x04\x89\xdd\xc8\xe6_\xc6\x02<\x95"\x9b\x9171',
    b'\x05\x186\x14\xe4\xa2\x1f\x12\x92_>\xaah\xc4\x97\xdd\x98\x10\xbdB%\xd5\x0f\xd0\x96\xafB\xc6\x1b\xe5/M',
    b'YdR\x1e\xd5\x0e\x02M\xe3\xfb\x00\xc1v0\xfd=\x8ck\x14)H\xad\xdc\xf1\xf2M:\x14p"_\x8d',
    b'r7ax\xca\x9b9\x03\x15pl\x1b\xd0\\\x12\xd5A\x18Fb\xf1\x95\x14\x9e\x96\xe8\x97M \x1d#\xd2',
    b'\n\xb8\xd3b\x06\xbe\r\x1b\xc8s\xdd-r\x8bA,WW]E\x1eE\x96\xbek7N\x1d=}\xd7\x98',
    b'\t\xa3\xa8\xdc"r3]\x14H\x7f\xf4\xeeo\x18\xcao%"\\\x8fH\x9a\xaf\xf8\xc3\xc4x\xce\xa92\xb4',
    b'\x88\xce\xd1[\x8c\xe2R]\xd5\xf9\xc5\x80\x10nn\xf8\xaeN\x18\x0ct\xe83\xab\xbb\x05\xad\x00\xea\xcb)"',
    b'\x18}\xb7\xca\x81M\x86he\xb8\xfb!\x81\xce\x1e8bA\x9e$\xa7["\x8bG=\xf0\x92\x1a\x80\x93\x9d',
    b'}\xdc\xed\x1f\x94\xd5j\xe1\x98\xd9\xafOy@\n\xdb\xc9&>I~\x1d\x86\xa4\x8d\x1a\xe3\x90\x06\x8b\xe1&',
    b':z*\x80*9$\xfc\xe9V\xdb\xb0H\xc9\xc7\xb2\xc2\xc4\xdc\xe2\xba\xc7\xdbm\xc6u\xafm\xa8\xa2\x8f\xd0',
    b'2\xef\xee\xfb\x03\x16\xd3PP\x96t\x8f\x07g\xd0\xf5\xab\xff\x1a~f\xb1\xc5\x1e\xfa)\xd8]\xf0=\x01\xed',
    b'\xde\x18\x9a\x862\xe3\x17\xe7"j\xde\x84%\xdbo\xf0\rg\x9cp!#\x9d`k+\xb1\xd50<\x04\x80',
    b'\x16B*\xc5=$\x8c\xca\xc9l\xf1\xe0\xe0\x10\xe9\x9d\xe9] \x9c\xb6\xb5;\x82\x13c4\x93K\xfc\x8cc',
    b'z\x06+\xec)\xa1\x91\x95J\xb50p\x90\xdeZ\xbb\xe4o4\x92d\xb5\x96/v\xc3\x16\x1f\x88Lr\xbd',
    b'A\xfcx\x9d\xf3\xf1\x1d;\x81X\xe6\xd5.N\xdf\xeb\xd6\xb1\xc3\x9b \xb2\x8b\x9b\x9f\xd7q64\x00\x18}',
    b'\xad\xffY\xbf0\x9e\x92\x7f\r\xb7\xc5\x00\x8c\xf4\x0f\xf9\x0c\xcc\x92\xa2H\x8e\xd4+\x0c\xdc{\xa9yj\xc7\x93',
    b'\xec\x8d\xfbu\xc6\xcd<\x99\x07p\\\xae\xfe\xa2\xf6M\x07\xb7X\x02?Z\x97\xc6Qs~\xd8c\xfc\xd1\xe9',
    b'\x83\x87\xeb.{\xb3F;\xe8\x96\xe2j\xcf\x8fh\xb8\x88\x89\x9f\x06\xdc(V\xa6\x07\xf4(\x89Z;\xdf\xf2'
]


def create_hash_256(data: bytes = None) -> bytes:
    if data is None:
        max_int = sys.maxsize
        length = (max_int.bit_length() + 7) // 8
        data = int(random.randint(0, max_int)).to_bytes(length, DATA_BYTE_ORDER)

    return hashlib.sha3_256(data).digest()


def create_tx_hash(data: bytes = None) -> bytes:
    return create_hash_256(data)


def create_block_hash(data: bytes = None) -> bytes:
    return create_tx_hash(data)


def root_clear(score_path: str, state_db_path: str):
    rmtree(score_path, ignore_errors=True)
    rmtree(state_db_path, ignore_errors=True)


def create_timestamp():
    return int(time() * 10 ** 6)


class IconIntegrateTestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._score_root_path = '.testscore'
        cls._state_db_root_path = '.teststatedb'

        cls._icx_factor = 10 ** 18

        cls._genesis: 'KeyWallet' = KeyWallet.create()
        cls._fee_treasury: 'KeyWallet' = KeyWallet.create()
        cls._test1: 'KeyWallet' = KeyWallet.load(bytes.fromhex(TEST1_PRIVATE_KEY))

        cls._wallet_array = [KeyWallet.load(v) for v in TEST_ACCOUNTS]

    def setUp(self, genesis_accounts: List[Account] = None,
              block_confirm_interval: int = tbears_server_config[TbConf.BLOCK_CONFIRM_INTERVAL],
              network_only: bool = False):

        self._block_height = 0
        self._prev_block_hash = None
        self._block_confirm_interval = block_confirm_interval
        self._network_only: bool = network_only

        if self._network_only:
            return

        root_clear(self._score_root_path, self._state_db_root_path)

        config = IconConfig("", default_icon_config)
        config.load()
        config.update_conf({ConfigKey.BUILTIN_SCORE_OWNER: self._test1.get_address()})
        config.update_conf({ConfigKey.SCORE_ROOT_PATH: self._score_root_path,
                            ConfigKey.STATE_DB_ROOT_PATH: self._state_db_root_path})
        config.update_conf(self._make_init_config())
        self.icon_service_engine = IconServiceEngine()
        self.icon_service_engine.open(config)

        self._genesis_invoke(genesis_accounts)

    def tearDown(self):
        if not self._network_only:
            self.icon_service_engine.close()
        root_clear(self._score_root_path, self._state_db_root_path)

    def _make_init_config(self) -> dict:
        return {}

    @staticmethod
    def _append_list(tx: dict, genesis_accounts: List[Account]) -> None:
        """Appends additional genesis account list to genesisData

        :param genesis_accounts: additional genesis account list consisted of namedtuple named Account
        of which keys are name, address and balance
        :return: None
        """
        for account_as_namedtuple in genesis_accounts:
            tx["genesisData"]['accounts'].append({
                "name": account_as_namedtuple.name,
                "address": account_as_namedtuple.address,
                "balance": account_as_namedtuple.balance
            })

    def _genesis_invoke(self, genesis_accounts: List[Account]) -> list:
        tx_hash = create_tx_hash()
        timestamp_us = create_timestamp()
        request_params = {
            'txHash': tx_hash,
            'version': 3,
            'timestamp': timestamp_us
        }

        tx = {
            'method': 'icx_sendTransaction',
            'params': request_params,
            'genesisData': {
                "accounts": [
                    {
                        "name": "genesis",
                        "address": Address.from_string(self._genesis.get_address()),
                        "balance": 100 * self._icx_factor
                    },
                    {
                        "name": "fee_treasury",
                        "address": Address.from_string(self._fee_treasury.get_address()),
                        "balance": 0
                    },
                    {
                        "name": "_admin",
                        "address": Address.from_string(self._test1.get_address()),
                        "balance": 1_000_000 * self._icx_factor
                    }
                ]
            },
        }

        if genesis_accounts:
            self._append_list(tx, genesis_accounts)

        block_hash = create_block_hash()
        block = Block(self._block_height, block_hash, timestamp_us, None, 0)
        tx_results, _, _, _ = self.icon_service_engine.invoke(
            block,
            [tx]
        )
        if 'block' in inspect.signature(self.icon_service_engine.commit).parameters:
            self.icon_service_engine.commit(block)
        else:
            self.icon_service_engine.commit(block.height, block.hash, block.hash)

        self._block_height += 1
        self._prev_block_hash = block_hash

        return tx_results

    def _make_and_req_block(self, tx_list: list, block_height: int = None) -> tuple:
        if block_height is None:
            block_height: int = self._block_height
        block_hash = create_block_hash()
        timestamp_us = create_timestamp()

        block = Block(block_height, block_hash, timestamp_us, self._prev_block_hash)

        tx_results, state_root_hash, added_transactions, main_preps = self.icon_service_engine.invoke(block, tx_list)

        convert_tx_results = [tx_result.to_dict(to_camel_case) for tx_result in tx_results]
        results = {
            'txResults': convert_tx_results,
            'stateRootHash': bytes.hex(state_root_hash),
            'addedTransactions': added_transactions
        }
        if main_preps:
            results['prep'] = main_preps

        response = MakeResponse.make_response(results)

        return block, response

    def _write_precommit_state(self, block: 'Block') -> None:
        if 'block' in inspect.signature(self.icon_service_engine.commit).parameters:
            self.icon_service_engine.commit(block)
        else:
            self.icon_service_engine.commit(block.height, block.hash, block.hash)
        self._block_height += 1
        self._prev_block_hash = block.hash

    def _query(self, request: dict, method: str = 'icx_call') -> Any:
        response = self.icon_service_engine.query(method, request)

        # convert response
        if isinstance(response, int):
            response = hex(response)
        elif isinstance(response, Address):
            response = str(response)
        return response

    def _process_transaction_in_local(self, request: dict) -> dict:
        params = TypeConverter.convert(request, ParamType.TRANSACTION_PARAMS_DATA)
        params['txHash'] = create_tx_hash()
        tx = {
            'method': 'icx_sendTransaction',
            'params': params
        }

        prev_block, tx_results = self._make_and_req_block([tx])
        self._write_precommit_state(prev_block)

        # convert TX result as sdk style
        convert_transaction_result(tx_results[0])

        return tx_results[0]

    def process_transaction(self, request: SignedTransaction,
                            network: IconService = None,
                            block_confirm_interval: int = 0) -> dict:
        if self._network_only and network is None:
            raise URLException("Set network URL")

        if block_confirm_interval == 0:
            block_confirm_interval = self._block_confirm_interval

        try:
            if network is not None:
                # Send the transaction to network
                tx_hash = network.send_transaction(request)
                sleep(block_confirm_interval)
                # Get transaction result
                tx_result = network.get_transaction_result(tx_hash)
            else:
                # process the transaction in local
                tx_result = self._process_transaction_in_local(request.signed_transaction_dict)
        except IconServiceBaseException as e:
            tx_result = e.message

        return tx_result

    def process_transaction_bulk(self,
                                 requests: list,
                                 network: IconService = None,
                                 block_confirm_interval: int = 0) -> list:
        if self._network_only and network is None:
            raise URLException("Set network URL")

        if block_confirm_interval == 0:
            block_confirm_interval = self._block_confirm_interval

        tx_results: list = []

        try:
            if network is not None:
                tx_hashes: list = []
                for req in requests:
                    # Send the transaction to network
                    tx_hash = network.send_transaction(req)
                    tx_hashes.append(tx_hash)

                sleep(block_confirm_interval)

                # Get transaction result
                for h in tx_hashes:
                    tx_result = network.get_transaction_result(h)
                    tx_results.append(tx_result)
            else:
                for req in requests:
                    # process the transaction in local
                    tx_result = self._process_transaction_in_local(req.signed_transaction_dict)
                    tx_results.append(tx_result)
        except IconServiceBaseException as e:
            tx_result = e.message
            tx_results.append(tx_result)

        return tx_results

    def process_call(self, call: Call, network: IconService = None):
        if self._network_only and network is None:
            raise URLException("Set network URL")

        try:
            if network is not None:
                response = network.call(call)
            else:
                request = {
                    "from": Address.from_string(call.from_),
                    "to": Address.from_string(call.to),
                    "dataType": "call",
                    "data": {
                        "method": call.method
                    }
                }

                if isinstance(call.params, dict):
                    request["data"]["params"] = call.params

                response = self._query(request=request)
        except IconServiceBaseException as e:
            response = e.message

        return response

    def process_message_tx(self, network: IconService = None,
                           msg: str = "dummy",
                           block_confirm_interval: int = 0) -> dict:
        if self._network_only and network is None:
            raise URLException("Set network URL")

        if block_confirm_interval == 0:
            block_confirm_interval = self._block_confirm_interval

        msg_byte = msg.encode('utf-8')

        # build message tx
        transaction = MessageTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._test1.get_address()) \
            .step_limit(10000000000) \
            .nid(3) \
            .nonce(100) \
            .data(f"0x{msg_byte.hex()}") \
            .build()

        # signing message tx
        request = SignedTransaction(transaction, self._test1)

        try:
            if network is not None:
                # Send the transaction to network
                tx_hash = network.send_transaction(request)
                sleep(block_confirm_interval)
                # Get transaction result
                tx_result = network.get_transaction_result(tx_hash)
            else:
                # process the transaction in local
                tx_result = self._process_transaction_in_local(request.signed_transaction_dict)
        except IconServiceBaseException as e:
            tx_result = e.message

        return tx_result
