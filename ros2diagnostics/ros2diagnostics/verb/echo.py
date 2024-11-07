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
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus
from ros2cli.node.strategy import NodeStrategy
from ros2cli.node.strategy import add_arguments
from ros2diagnostics.verb import VerbExtension
import rclpy
import re


class EchoVerb(VerbExtension):
    """Echo '/diagnostics_agg' topic content with a human friendly formatting and filtering."""

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
            '-l', '--level', action='store', default=DiagnosticStatus.WARN, type=int,
            help='''Print log statement with priority levels
            greater than this value''')
        parser.add_argument(
            '-f', '--follow', action='store_true', default=False,
            help='Follows the diagnostic messages continuously')
        parser.add_argument(
            '--topic', action='store', default='/diagnostics_agg', type=str,
            help='''Topic to read the diagnostics from,
            defaults to /diagnostics_agg''')
        parser.add_argument(
            '--filter', action='store', default='.*', type=str,
            help='''Regular expression to be applied as
            a filter to the diagnostics name''')
        parser.add_argument(
            '--no-color', action='store_true', default=False,
            help='''Disables the use of ASCII colors
            for the output of the command''')
        parser.add_argument(
            '-d', '--detail', action='store_true', default=False,
            help='Print timestamp, hardware_id and key/value pairs')

    def _get_ns(self, name):
        return '/'.join(name.split('/')[:-1])

    def _get_non_leaf_statuses(self, statuses):
        return [self._get_ns(s.name) for s in statuses]

    def _get_leaf_statuses(self, statuses):
        parent_namespaces = self._get_non_leaf_statuses(statuses)
        return [s for s in statuses if s.name not in parent_namespaces]

    def level_to_string(self, level):
        if type(level) is not bytes:
            level = level.to_bytes(1, 'big')

        match level:
            case DiagnosticStatus.OK:
                return " OK  "
            case DiagnosticStatus.WARN:
                return "WARN "
            case DiagnosticStatus.ERROR:
                return "ERROR"
            case DiagnosticStatus.STALE:
                return "STALE"
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
            case DiagnosticStatus.OK:
                return self.GREEN_TEXT
            case DiagnosticStatus.WARN:
                return self.YELLOW_TEXT
            case DiagnosticStatus.ERROR:
                return self.RED_TEXT
            case DiagnosticStatus.STALE:
                return self.BLUE_TEXT
            case _:
                return self.BOLD_TEXT

    def output_begin(self, msg):
        if not self.args_.follow:
            print('=====================================================================')
            print('Diagnostics generated on: {}'.format(self.stamp_to_string(msg.header.stamp)))
            print('---------------------------------------------------------------------')

    def output_end(self):
        if not self.args_.follow:
            print('=====================================================================')
            rclpy.shutdown()

    def diag_cb(self, msg):
        self.output_begin(msg)
        for diag in sorted(
                self._get_leaf_statuses(msg.status),
                key=lambda d: d.level, reverse=True):
            if type(self.args_.level) is not bytes:
                self.args_.level = self.args_.level.to_bytes(1, 'big')

            if diag.level < self.args_.level:
                continue
            if self.args_.filter and not re.search(
                    self.args_.filter, diag.name):
                continue

            color = self.get_color(diag.level)
            lvl = self.add_color(self.level_to_string(diag.level), color)
            text = f"[{lvl}] {diag.name} - {diag.message}"
            if self.args_.detail:
                dt = self.stamp_to_string(msg.header.stamp)
                text = text + "\n" + f"    timestamp:   {dt}"
                text = text + "\n" + f"    hardware_id: {diag.hardware_id}"
                for kv in diag.values:
                    text = text + "\n" + f"    - {kv.key}: {kv.value}"
            print(f"{text}")
        self.output_end()

    def main(self, *, args):
        self.args_ = args

        with NodeStrategy(args) as node:
            self.diag_ = node.node.create_subscription(
                DiagnosticArray, self.args_.topic, self.diag_cb, 1)
            rclpy.spin(node)
