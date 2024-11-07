# Copyright (c) 2024, Clearpath Robotics, Inc., All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from datetime import datetime
from rcl_interfaces.msg import Log
from ros2cli.node.strategy import NodeStrategy
from ros2cli.node.strategy import add_arguments
from ros2rosout.verb import VerbExtension
import rclpy
import re


class PrintVerb(VerbExtension):
    """Outputs the '/rosout' content in a nicely formatted way."""

    BLACK_TEXT = "\033[30;1m"
    BLUE_TEXT = "\033[34;1m"
    BOLD_TEXT = "\033[1m"
    CYAN_TEXT = "\033[36;1m"
    GREEN_TEXT = "\033[32;1m"
    MAGENTA_TEXT = "\033[35;1m"
    RED_TEXT = "\033[31;1m"
    WHITE_TEXT = "\033[37;1m"
    YELLOW_TEXT = "\033[33;1m"

    COLOR_RESET = "\033[0m"

    def add_arguments(self, parser, cli_name):
        add_arguments(parser)
        parser.add_argument(
            '-l', '--level', default=Log.INFO, type=int,
            help='''Print log statement with priority level '
            greater than this value''')
        parser.add_argument(
            '-n', '--node-regex', default=None,
            help='''Only print log statements from node(s) matching the
            regular expression provided''')
        parser.add_argument(
            '--no-color', action='store_true', default=False,
            help='''Disables the use of ASCII colors
            for the output of the command''')
        parser.add_argument(
            '-f', '--function-detail', action='store_true', default=False,
            help='Output function name, file, and line number')

    def level_to_string(self, level):
        if type(level) is not bytes:
            level = level.to_bytes(1, 'big')

        match level:
            case Log.DEBUG:
                return "DEBUG"
            case Log.INFO:
                return "INFO "
            case Log.WARN:
                return "WARN "
            case Log.ERROR:
                return "ERROR"
            case Log.FATAL:
                return "FATAL"
            case _:
                return "_____"

    def stamp_to_string(self, stamp):
        dt = datetime.fromtimestamp(stamp.sec)
        s = dt.strftime('%Y-%m-%d %H:%M:%S')
        s += '.' + str(int(stamp.nanosec % 1000000000)).zfill(9)
        return f"{s}"

    def add_color(self, txt, color=WHITE_TEXT):
        if self.args_.no_color:
            return txt

        return f"{color}{txt}{self.COLOR_RESET}"

    def get_color(self, level):
        if type(level) is not bytes:
            level = level.to_bytes(1, 'big')

        match level:
            case Log.DEBUG:
                return self.GREEN_TEXT
            case Log.INFO:
                return self.WHITE_TEXT
            case Log.WARN:
                return self.YELLOW_TEXT
            case Log.ERROR:
                return self.RED_TEXT
            case Log.FATAL:
                return f"{self.RED_TEXT}{self.BOLD_TEXT}"
            case _:
                return self.BOLD_TEXT

    def rosout_cb(self, msg):
        if msg.level < self.args_.level:
            return
        if self.args_.node_regex and not re.search(
                self.args_.node_regex, msg.name):
            return
        color = self.get_color(msg.level)
        lvl = self.add_color(self.level_to_string(msg.level), color)
        dt = self.add_color(self.stamp_to_string(msg.stamp), color)
        name = self.add_color(msg.name, color)
        mmsg = self.add_color(msg.msg, color)
        text = f"[{dt}] [{lvl}] [{name}]: {mmsg}"
        if self.args_.function_detail:
            file = self.add_color(msg.file, self.BLUE_TEXT)
            line = self.add_color(msg.line, self.BLUE_TEXT)
            function = self.add_color(msg.function, self.CYAN_TEXT)
            text += f" [{file}:{line}({function})]"
        print(f"{text}")

    def main(self, *, args):
        self.args_ = args

        with NodeStrategy(args) as node:
            self.rosout_ = node.node.create_subscription(
                Log, '/rosout', self.rosout_cb, 10)
            rclpy.spin(node)
