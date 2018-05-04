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
import zipfile


CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


def check_required_args(**kwargs) -> 'bool':

    flag = True
    for key, value in kwargs.items():
        flag = flag and bool(value)
    return flag


def write_file(parent_directory: 'str', file_name: 'str', contents: 'str') -> 'None':
    if not os.path.exists(parent_directory):
        os.mkdir(parent_directory)
    with open(f'./{parent_directory}/{file_name}', mode='w') as file:
        file.write(contents)


def get_score_main_template(score_class: 'str') -> 'str':
    """

    :return:
    """
    template = """from .iconscore.icon_score_base import IconScoreBase


class UserScore(IconScoreBase):
    
    def __init__(self):
        \"\"\"Initialize SCORE.
        
        \"\"\"
    
    def genesis_init(self, *args, **kwargs) -> None:
        \"\"\" genesis_init
        \"\"\"
        
    def invoke(self, transaction, block):
        \"\"\"Handler of 'invoke' requests.
        
        It's event handler of invoke request. You need to implement this handler like below.
        0. Define the interface of functions in 'invoke' field of package.json.
        1. Parse transaction data and get the name of function by reading 'method' field of transaction.
        2. Call that function.
        
        :param transaction: transaction data. 
        :param block: block data has transaction data.
        :return: response: Invoke result
        \"\"\"
    
    def query(self, params):
        \"\"\" Handler of 'Query' requests.
        
        It's event handler of query request. You need to implement this handler like below.
        0. Define the interface of functions in 'query' field of package.json.
        1. Parse transaction data and get the name of function by reading 'method' field of transaction.
        2. Call that function
        
        :param params: parmeters.
        :return: response: Query result.
        \"\"\""""
    return template.replace("UserScore", score_class)


def get_package_json_dict(project: 'str', score_class: 'str') -> 'dict':
    package_json_dict = {
        "id": "loopchain-default",
        "version": "1.0.0",
        "auth": {
            "name": "LoopChain Dev Team",
            "email": "dev@theloop.co.kr",
            "org": "Theloop inc"
        },
        "dependencies": {},
        "description": "LoopChain Mock Token Score",
        "repository": {},
        "homepage": "http://www.theloop.co.kr",
        "function": {
            "query": [],
            "invoke": []
        },
        "main_file": f"{project}",
        "main_score": f"{score_class}"
    }
    return package_json_dict


def extract_zip(install_path: 'str') -> None:
    archive_path = os.path.join(CURRENT_DIRECTORY, '../iconservice.zip')
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_file:
            file_name_list = zip_file.namelist()
            file_name_prefix_list = [prefix.split('/')[0] for prefix in file_name_list
                                     if not prefix.startswith('__MACOSX')]
            for file_name in file_name_list:
                if (not file_name.startswith("__MACOSX")) and file_name.find("__pycache__") == -1:
                    zip_file.extract(file_name, install_path)

    except FileNotFoundError:
        print(f"{archive_path} not found. check file path.")
    except IsADirectoryError:
        print(f"{archive_path} is a directory. check file path.")
    except zipfile.BadZipFile:
        print(f"{archive_path}, bad zip file.")
    except NotADirectoryError:
        print(f"{install_path} is not a directory")
    except PermissionError:
        print("permission error")
