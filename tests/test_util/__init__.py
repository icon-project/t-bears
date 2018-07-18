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

from tbears.util import PROJECT_ROOT_PATH

TEST_DIRECTORY = os.path.abspath(os.path.join(PROJECT_ROOT_PATH, 'tests'))
TEST_UTIL_DIRECTORY = os.path.join(TEST_DIRECTORY, 'test_util')
IN_MEMORY_ZIP_TEST_DIRECTORY = os.path.join(TEST_UTIL_DIRECTORY, 'test_in_memory_zip')