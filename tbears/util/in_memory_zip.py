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

import io
import os
import zipfile


class InMemoryZip:

    def __init__(self):
        self._in_memory = io.BytesIO()

    @property
    def data(self):
        self._in_memory.seek(0)
        return self._in_memory.read()

    def zip_in_memory(self, path):
        with zipfile.ZipFile(self._in_memory, 'a', zipfile.ZIP_DEFLATED, False) as zf:
            if os.path.isfile(path):
                zf.write(path)
            else:
                for root, folders, files in os.walk(path):
                    if root.find('__pycache__') != -1:
                        continue
                    if root.find('/.') != -1:
                        continue
                    for file in files:
                        if file.startswith('.'):
                            continue
                        full_path = os.path.join(root, file)
                        zf.write(full_path)
