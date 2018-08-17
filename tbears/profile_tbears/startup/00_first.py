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
import itertools

from IPython import get_ipython
from IPython.core.magic import magics_class, Magics, line_magic
from IPython.core import page
from IPython.terminal.prompts import Prompts, Token

from tbears.command.command import Command
from tbears.libs.icon_jsonrpc import IconClient, IconJsonrpc

ip = get_ipython()


@magics_class
class TbearsCommands(Magics):
    command_ins = Command()
    score_info = []
    deployed_id = itertools.count(start=1)

    def run_command(self, command):
        try:
            full_command_list = f'{command}'.split()
            if full_command_list[0] == 'console':
                return
            response = self.command_ins.run(full_command_list)
        except:
            return
        else:
            global _r
            _r = response
            if isinstance(response, int):
                return

            if full_command_list[0] == 'deploy' and not response.get("error", None):
                args = self.command_ins.parser.parse_args(full_command_list)
                conf = self.command_ins.cmdScore.get_icon_conf('deploy', args=vars(args))
                self.score_info.append(f"{next(self.deployed_id)}."
                                       f"path : {conf['project']}, txhash : {response['result']},"
                                       f" deployed in : {conf['uri']}")
            return

    @line_magic
    def tbears(self, line):
        return self.run_command(line)

    @line_magic
    def deployresults(self, line):
        return page.page("\n".join(self.score_info))

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

    @line_magic
    def genconf(self, line):
        return self.run_command(f"genconf {line}")

    @line_magic
    def sendtx(self, line):
        return self.run_command(f"sendtx {line}")

    @line_magic
    def call(self, line):
        return self.run_command(f"call {line}")


class MyPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [(Token.Prompt, 'tbears) ')]

    def out_prompt_tokens(self):
        return [(Token.OutPrompt, '')]


ip.register_magics(TbearsCommands)
ip.prompts = MyPrompt(ip)
