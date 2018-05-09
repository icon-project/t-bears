from .sub_process import SubProcess
import os
from .util import post


class RunProcess(object):
    __PYTHON_VERSION = 'python'
    __TBEARS_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    __FLASK_SERVER_PATH = os.path.join(__TBEARS_ROOT_PATH, 'tools/test.py')

    def __init__(self):
        self.__sub_process = None

    def run(self, proj_name: str):
        if self.__sub_process is None or not self.__sub_process.is_run():
            process_args = [self.__PYTHON_VERSION, self.__FLASK_SERVER_PATH]
            print(process_args)
            self.__sub_process = SubProcess(process_args)

    def stop(self):
        if self.__sub_process:
            self.__sub_process.stop()

    @staticmethod
    def install_request(project: str):
        url = "~~~"
        post(url, project)
