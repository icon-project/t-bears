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
import json
import os
import types
import warnings
from functools import wraps
from inspect import getmembers, isfunction
from typing import Optional, Any, Dict
from unittest.mock import Mock, patch

from iconservice import InterfaceScore
from iconservice.base.address import Address, AddressPrefix
from iconservice.base.exception import InvalidPayableException, InvalidInterfaceException, InvalidRequestException
from iconservice.database.db import IconScoreDatabase
from iconservice.iconscore.icon_score_base2 import _create_address_with_key, _recover_key
from iconservice.iconscore.icon_score_constant import FORMAT_IS_NOT_DERIVED_OF_OBJECT, ScoreFlag
from iconservice.iconscore.icon_score_context_util import IconScoreContextUtil
from iconservice.iconscore.icx import Icx
from iconservice.iconscore.system import IconNetworkValueType
from iconservice.iconscore.typing.element import get_score_flag
from iconservice.utils import is_builtin_score, is_any_flag_on

from .context import Context, score_mapper, interface_score_mapper, context_db, icon_network_value
from ..mock.icx_engine import IcxEngine


def hooking_get_balance(address: 'Address'):
    """Hooking method for icx.get_balance"""
    return IcxEngine.get_balance(None, address)


def hooking_transfer(_to: 'Address', amount: int):
    """Hooking method for icx.transfer"""
    ctx = Context.get_context()
    sender = ctx.msg.sender
    IcxEngine.transfer(ctx, sender, _to, amount)


def hooking_sha_256(data):
    return hashlib.sha256(data).digest()


def hooking_sha3_256(data):
    return hashlib.sha3_256(data).digest(0)


def start_SCORE_APIs_patch(score_module_path: str):
    patch(f"{score_module_path}.json_dumps", side_effect=json.dumps).start()
    patch(f"{score_module_path}.json_loads", side_effect=json.loads).start()
    patch(f"{score_module_path}.sha_256", side_effect=hooking_sha_256).start()
    patch(f"{score_module_path}.sha3_256", side_effect=hooking_sha3_256).start()
    patch(f"{score_module_path}.create_address_with_key", side_effect=_create_address_with_key).start()
    patch(f"{score_module_path}.recover_key", side_effect=_recover_key).start()


def hooking_migrate_icon_network_value(self, data: Dict['IconNetworkValueType', Any]):
    for key, value in data.items():
        icon_network_value[key] = value


def hooking_get_icon_network_value(self, type_: 'IconNetworkValueType'):
    self._check_inv_type(type_)
    return icon_network_value.get(type_)


def hooking_set_icon_network_value(self, type_: 'IconNetworkValueType', value: Any):
    self._check_inv_type(type_)
    icon_network_value[type_] = value


def create_address(prefix: AddressPrefix = AddressPrefix.EOA) -> 'Address':
    return Address.from_bytes(prefix.to_bytes(1, 'big') + os.urandom(20))


def deprecated_method(param):
    warnings.warn("forbidden method", DeprecationWarning, stacklevel=2)


def patch_score_method(method):
    """Patch SCORE method.
    Refer to the decorator and patch the method to have the appropriate context

    :param method: method to patch
    :return: patched method
    """

    @wraps(method)
    def patched(*args, **kwargs):
        context: 'Mock' = Context.get_context()
        bottom_method_flag = method_flag = get_score_flag(method)
        _, method_name = method.__qualname__.split('.')
        context.current_address = method.__self__.address

        if method_name == 'fallback':
            if not (method_flag & ScoreFlag.PAYABLE) and context.msg.value > 0:
                raise InvalidPayableException(f"This method is not payable")

        if len(context.method_flag_trace) > 0:
            bottom_method_flag = context.method_flag_trace[0]
        if bottom_method_flag & ScoreFlag.READONLY:
            Context._set_query_context(context)
        else:
            Context._set_invoke_context(context)
        if bottom_method_flag & ScoreFlag.PAYABLE:
            IcxEngine.transfer(context, context.msg.sender, context.current_address, context.msg.value)

        context.method_flag_trace.append(method_flag)
        result = method(*args, **kwargs)
        context.method_flag_trace.pop()
        return result

    return patched


def get_interface_score(score_address):
    try:
        interface_score = interface_score_mapper[score_address]
    except KeyError:
        raise InvalidInterfaceException(FORMAT_IS_NOT_DERIVED_OF_OBJECT.format(InterfaceScore.__name__))
    else:
        return interface_score


def new_create_interface_score(score_address, interface_score):
    """Hooking method for SCORE.create_interface_score

    :param score_address: address of internal call SCORE
    :param interface_score:
    :return: mock instance
    """
    return get_interface_score(score_address)


class ScorePatcher:

    @staticmethod
    def get_score_db(score_address: Optional['Address'] = None):
        """Get db of SCORE that having score_address.
        create cx prefixed address and set it as SCORE's address if score_address is None

        :param score_address: address of score.
        :return: db SCORE use
        """
        if not score_address:
            score_address = create_address(AddressPrefix.CONTRACT)
        score_db = IconScoreDatabase(score_address, context_db)
        return score_db

    @staticmethod
    def initialize_score(score_class, score_db, owner: 'Address'):
        """Get an instance of the SCORE class passed as an score_class arguments

        :param score_class: SCORE class to instantiate
        :param score_db: database the SCORE use
        :param owner: owner of SCORE
        :return: Instantiated SCORE
        """
        Context.set_msg(owner, 0)
        score = score_class(score_db)
        ScorePatcher.patch_score_methods(score)
        ScorePatcher.patch_score_event_logs(score)
        ScorePatcher.patch_interface_scores(score)
        ScorePatcher.patch_deprecated_methods(score)
        score_mapper[score.address] = score
        if is_builtin_score(str(score.address)):
            ScorePatcher.patch_system_score(score)
        return score

    @staticmethod
    def patch_score_methods(score):
        """Patch all SCORE method by calling patch_score_method function

        :param score: SCORE to be patched
        """
        custom_methods = ScorePatcher.get_custom_methods(score.__class__)
        for custom_method in custom_methods:
            name = custom_method.__qualname__.split('.')[1]
            method = getattr(score, name)
            setattr(score, name, patch_score_method(method))

    @staticmethod
    def get_custom_methods(score):
        """Get user defined methods inside SCORE

        :param score: SCORE to get the custom method
        :return: user defined methods inside SCORE
        """
        custom_methods = ScorePatcher._get_custom_methods(score)
        methods = set()
        for method in custom_methods:
            flag = get_score_flag(method)
            if flag is ScoreFlag.NONE or is_any_flag_on(flag, ScoreFlag.FUNC):
                methods.add(method)

        methods.add(getattr(score, 'fallback'))
        return methods

    @staticmethod
    def _get_custom_methods(score):
        custom_methods = [method for key, method in getmembers(score, predicate=isfunction)
                          if method.__qualname__.split('.')[0] != 'IconScoreBase']
        return custom_methods

    @staticmethod
    def register_interface_score(internal_score_address: Address):
        """Register interface SCORE. This method must be called before testing internal call(Calling other SCORE method)

        :param internal_score_address: address of internal call SCORE
        """
        if not internal_score_address.is_contract:
            raise InvalidRequestException(f"{internal_score_address} is not SCORE")
        interface_score_mapper[internal_score_address] = Mock()

    @staticmethod
    def patch_interface_scores(score):
        """Patch internal call SCORE with mock instance"""
        setattr(score, 'create_interface_score', new_create_interface_score)

    @staticmethod
    def patch_internal_method(internal_score_address, method, new_method):
        """Patch internal method with given 'new_method'

        :param internal_score_address: address of the SCORE having method to be called
        :param method: method to be patched
        :param new_method: method to patch
        """
        interface_score = get_interface_score(internal_score_address)
        setattr(interface_score, method, Mock(side_effect=new_method))

    @staticmethod
    def patch_score_event_logs(score):
        """Patch all event_logs inside SCORE

        :param score: SCORE to be patched
        """
        custom_methods = ScorePatcher._get_custom_methods(score.__class__)
        for method in custom_methods:
            flag = get_score_flag(method)
            if flag == ScoreFlag.EVENTLOG:
                setattr(score, method.__name__, Mock())

    @staticmethod
    def patch_deprecated_methods(score):
        setattr(score, "get_owner", Mock(side_effect=deprecated_method))
        setattr(score, "is_score_active", Mock(side_effect=deprecated_method))
        setattr(score, "get_score_address_by_tx_hash", Mock(side_effect=deprecated_method))
        setattr(score, "get_tx_hashes_by_score_address", Mock(side_effect=deprecated_method))
        setattr(score, "deploy", Mock(side_effect=deprecated_method))

    @staticmethod
    def start_patches():
        patch('iconservice.iconscore.context.context.ContextContainer._get_context',
              side_effect=lambda: Context.get_context()).start()
        patch.object(Icx, "get_balance", side_effect=hooking_get_balance).start()
        patch.object(Icx, "transfer", side_effect=hooking_transfer).start()
        patch.object(IconScoreContextUtil, "get_owner",
                     side_effect=lambda context, score_address: context.msg.sender).start()

    @staticmethod
    def stop_patches():
        patch.stopall()

    @staticmethod
    def patch_system_score(score):
        score.get_icon_network_value = types.MethodType(hooking_get_icon_network_value, score)
        score.set_icon_network_value = types.MethodType(hooking_set_icon_network_value, score)
        score.migrate_icon_network_value = types.MethodType(hooking_migrate_icon_network_value, score)
        score.disqualify_prep = types.MethodType(lambda self, address: (True, ""), score)
