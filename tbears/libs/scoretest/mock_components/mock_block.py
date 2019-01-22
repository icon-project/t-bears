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
from time import time


TIMESTAMP_FACT = 2 * 10 ** 6
START_TIME = int(time()*10**6)


class MockBlock:
    def __init__(self, height: int=0):
        self.height = height
        self.timestamp = START_TIME + height * TIMESTAMP_FACT

    @property
    def _height(self):
        return self.height

    @_height.setter
    def _height(self, height: int=0):
        self.height = height
        self.timestamp = START_TIME + height * TIMESTAMP_FACT


