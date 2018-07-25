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
from IPython import get_ipython
from IPython.core.magic import magics_class, Magics, line_magic
from IPython.terminal.prompts import Prompts, Token

from tbears.command.command import Command

command_ins = Command()

@magics_class
class TbearsCommands(Magics):

    def run_command(self, line):
        try:
            full_command_list = f'{line}'.split()
            result = command_ins.run(full_command_list)
        except:
            pass
        else:
            return result

    @line_magic
    def tbears(self, line):
        return self.run_command(line)

    @line_magic
    def init(self, line):
        return self.run_command(f"init {line}")

    @line_magic
    def samples(self, line):
        return self.run_command(f"samples {line}")

    @line_magic
    def clear(self, line):
        return self.run_command(f"clear {line}")

    @line_magic
    def deploy(self, line):
        return self.run_command(f"deploy {line}")

    @line_magic
    def start(self, line):
        return self.run_command(f"start {line}")

    @line_magic
    def stop(self, line):
        return self.run_command(f"stop {line}")

    @line_magic
    def keystore(self, line):
        return self.run_command(f"keystore {line}")

    @line_magic
    def transfer(self, line):
        return self.run_command(f"transfer {line}")

    @line_magic
    def txresult(self, line):
        return self.run_command(f"txresult {line}")

    @line_magic
    def balance(self, line):
        return self.run_command(f"balance {line}")

    @line_magic
    def totalsupply(self, line):
        return self.run_command(f"totalsupply {line}")

    @line_magic
    def scoreapi(self, line):
        return self.run_command(f"scoreapi {line}")

    @line_magic
    def txbyhash(self, line):
        return self.run_command(f"txbyhash {line}")

    @line_magic
    def lastblock(self, line):
        return self.run_command(f"lastblock {line}")

    @line_magic
    def blockbyhash(self, line):
        return self.run_command(f"blockbyhash {line}")

    @line_magic
    def blockbyheight(self, line):
        return self.run_command(f"blockbyhegith {line}")


class MyPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [(Token.Prompt, 'tbears) ')]

    def out_prompt_tokens(self, cli=None):
        return [(Token.Prompt, 'result) ')]


ip = get_ipython()
ip.register_magics(TbearsCommands)
ip.prompts = MyPrompt(ip)
