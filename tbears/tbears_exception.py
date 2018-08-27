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
from typing import Optional
from enum import IntEnum, unique


@unique
class TBearsExceptionCode(IntEnum):
    """Result code enumeration

    Refer to http://www.simple-is-better.org/json-rpc/jsonrpc20.html#examples
    """
    OK = 0
    COMMAND_ERROR = 1
    WRITE_FILE_ERROR = 2
    DELETE_TREE_ERROR = 3
    KEY_STORE_ERROR = 5
    DEPLOY_PAYLOAD_ERROR = 6
    ICON_CLIENT_ERROR = 7
    ZIP_MEMORY = 8

    def __str__(self) -> str:
        return str(self.name).capitalize().replace('_', ' ')


class TBearsBaseException(BaseException):

    def __init__(self, message: Optional[str], code: TBearsExceptionCode = TBearsExceptionCode.OK):
        if message is None:
            message = str(code)
        self.__message = message
        self.__code = code

    @property
    def message(self):
        return self.__message

    @property
    def code(self):
        return self.__code

    def __str__(self):
        return f'{self.message}'


class TBearsWriteFileException(TBearsBaseException):
    """Error while write file."""
    def __init__(self, message: Optional[str]):
        super().__init__(message, TBearsExceptionCode.WRITE_FILE_ERROR)


class TBearsDeleteTreeException(TBearsBaseException):
    """Error while delete file."""
    def __init__(self, message: Optional[str]):
        super().__init__(message, TBearsExceptionCode.DELETE_TREE_ERROR)


class KeyStoreException(TBearsBaseException):
    """"Error while make or load keystore file """
    def __init__(self, message: Optional[str]):
        super().__init__(message, TBearsExceptionCode.KEY_STORE_ERROR)


class ZipException(TBearsBaseException):
    """"Error while write zip in memory"""
    def __init__(self, message: Optional[str]):
        super().__init__(message, TBearsExceptionCode.ZIP_MEMORY)


class DeployPayloadException(TBearsBaseException):
    """Error while fill deploy payload"""
    def __init__(self, message: Optional[str]):
        super().__init__(message, TBearsExceptionCode.DEPLOY_PAYLOAD_ERROR)


class IconClientException(TBearsBaseException):
    """Error while send request"""
    def __init__(self, message: Optional[str]):
        super().__init__(message, TBearsExceptionCode.ICON_CLIENT_ERROR)


class JsonContentsException(TBearsBaseException):
    """Error when initialize JsonContent object"""
    def __init__(self, message: Optional[str]):
        super().__init__(message, TBearsExceptionCode.JSONRPC_CONTENT_ERROR)


class TBearsCommandException(TBearsBaseException):
    """Error when tbears cli options are wrong"""
    def __init__(self, message: Optional[str]):
        super().__init__(message, TBearsExceptionCode.COMMAND_ERROR)
