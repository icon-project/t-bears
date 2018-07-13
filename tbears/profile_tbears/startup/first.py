from ipaddress import ip_address

from IPython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import magics_class, Magics, line_magic
from IPython.terminal.prompts import Prompts, Token

from tbears.tbears_cli import command_deploy, command_clear, command_samples, command_init, command_stop, \
    command_keystore
from tbears.libs.icon_json import *
from tbears.libs.icon_client import IconClient

@magics_class
class TbearsCommands(Magics):
    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('project', help='Project name')
    @magic_arguments.argument('score_class', help='SCORE class name')
    def init(self, line):
        args = magic_arguments.parse_argstring(self.init, line)
        return command_init(args)

    @line_magic
    @magic_arguments.magic_arguments()
    def samples(self, line):
        args = magic_arguments.parse_argstring(self.samples, line)
        return command_samples(args)

    @line_magic
    @magic_arguments.magic_arguments()
    def clear(self, line):
        args = magic_arguments.parse_argstring(self.clear, line)
        return command_clear(args)

    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('project')
    @magic_arguments.argument('-u', '--node-uri', help='URI of node (default: http://127.0.0.1:9000/api/v3)',
                              dest='uri')
    @magic_arguments.argument('-t', '--type', help='Deploy SCORE type ("tbears" or "icon". default: tbears',
                              choices=['tbears', 'icon'], dest='scoreType')
    @magic_arguments.argument('-m', '--mode', help='Deploy mode ("install" or "update". default: install',
                              choices=['install', 'update'], dest='mode')
    @magic_arguments.argument('-f', '--from', help='From address. i.e. SCORE owner address', dest='from')
    @magic_arguments.argument('-o', '--to', help='To address. i.e. SCORE address', dest='to')
    @magic_arguments.argument('-k', '--key-store', help='Key store file for SCORE owner', dest='keyStore')
    @magic_arguments.argument('-c', '--config', help='deploy config path (default: ./deploy.json')
    def deploy(self, line):
        args = magic_arguments.parse_argstring(self.deploy, line)

        return command_deploy(args)

    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-a', '--address', help='Address to host on (default: 0.0.0.0)', type=ip_address)
    @magic_arguments.argument('-p', '--port', help='Listen port (default: 9000)', type=int)
    @magic_arguments.argument('-c', '--config', help='tbears configuration file path (default: ./tbears.json)')
    def start(self, line):
        args = magic_arguments.parse_argstring(self.start, line)
        return command_clear(args)

    @line_magic
    @magic_arguments.magic_arguments()
    def stop(self, line):
        args = magic_arguments.parse_argstring(self.stop, line)
        return command_stop(args)

    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('keystore', help='Create keystore file in passed path')
    @magic_arguments.argument('path', help='determine where to store your keystore file.')
    def keystore(self, line):
        args = magic_arguments.parse_argstring(self.keystore, line)
        return command_keystore(args)


class MyPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [(Token.Prompt, 'tbears) ')]

    def out_prompt_tokens(self, cli=None):
        return [(Token.Prompt, 'result) ')]


ip = get_ipython()
ip.register_magics(TbearsCommands)
ip.prompts = MyPrompt(ip)
