# -*- coding: utf-8 -*-
# Copyright 2017-2018 theloop Inc.
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

import os
import shutil

from .address import Address, AddressPrefix, create_address  # 바껴야함.
# from iconservice.base.address import Address, AddressPrefix, create_address 로

TBEARS_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))


def write_file(parent_directory: 'str', file_name: 'str', contents: 'str') -> 'None':
    if not os.path.exists(parent_directory):
        os.mkdir(parent_directory)
    with open(f'./{parent_directory}/{file_name}', mode='w') as file:
        file.write(contents)


def get_score_main_template(score_class: 'str') -> 'str':
    """
    :param score_class: Your score class name.
    :return:
    """
    template = """############################################# 
                  #                                           #
                  #  Refer this contents to write 'score'.    #
                  #                                           #
                  #############################################
# @score
# class SampleToken(IconScoreBase):
# 
#     _BALANCES = 'balances'
#     _TOTAL_SUPPLY = 'total_supply'
# 
#     def __init__(self, db: IconScoreDatabase) -> None:
#         super().__init__(db)
#         self._total_supply = VarDB(self._TOTAL_SUPPLY, db, value_type=int)
#         self._balances = DictDB(self._BALANCES, db, value_type=int)
# 
#     def genesis_init(self, *args, **kwargs) -> None:
#         super().genesis_init(*args, **kwargs)
# 
#         init_supply = 1000
#         decimal = 18
#         total_supply = init_supply * 10 ** decimal
# 
#         self._total_supply.set(total_supply)
#         self._balances[self.address] = total_supply
# 
#     @external(readonly=True)
#     def total_supply(self) -> int:
#         return self._total_supply.get()
# 
#     @external(readonly=True)
#     def balance_of(self, addr_from: Address) -> int:
#         var = self._balances[addr_from]
#         if var is None:
#             var = 0
#         return var
# 
#     def _transfer(self, _addr_from: Address, _addr_to: Address, _value: int) -> bool:
# 
#         if self.balance_of(_addr_from) < _value:
#             raise IconScoreBaseException(f"{_addr_from}'s balance < {_value}")
# 
#         self._balances[_addr_from] = self.balance_of(_addr_from) - _value
#         self._balances[_addr_to] = _value
#         return True
# 
#     @external()
#     def transfer(self, addr_to: Address, value: int) -> bool:
#         return self._transfer(self.msg.sender, addr_to, value)
# 
#     def fallback(self) -> None:
#         pass

        \"\"\""""
    return template.replace("SampleToken", score_class)


def get_package_json_dict(project: 'str', score_class: 'str') -> 'dict':
    package_json_dict = {
        "version": "0.0.1",
        "main_file": f"{project}",
        "main_score": f"{score_class}"
    }
    return package_json_dict


def _install_score_for_develop(project: 'str'):
    """

    :param project:
    :return:
    """
    score_address = create_address(AddressPrefix.CONTRACT, project.encode('utf-8'))
    tmp_score_id = "00_00"
    score_path = os.path.join(TBEARS_ROOT_PATH, 'tools', 'score', str(score_address), tmp_score_id)
    if not os.path.exists(score_path):
        os.makedirs(score_path)
        copytree(os.path.join('./', project), score_path)


def copytree(src, dst):
    for item in os.listdir(src):
        source = os.path.join(src, item)
        dest = os.path.join(dst, item)
        if os.path.isdir(source):
            shutil.copytree(source, dest, False, None)
