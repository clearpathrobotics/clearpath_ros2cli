# ros2diagnostics

This is the `ros2 diagnostics echo` utility command which displays the content, by default, of `/diagnostics_agg` topic in a nicely formatted and colorized output.

## Usage

Run `ros2 diagnostics echo` to fetch and output diagnostics.

Run `ros2 diagnostics echo -h/--help` to print all available command arguments.

## Output format

The command outputs the diagnostics with the following format:
[ _level_ ] _name_ - _message_

By default, _level_ is printed in color to match their priority level.

The `--no-color` switch is provided to disable coloring.

The `-f/--follow` switch is provided to follow the diagnostics continously.

The `-d/--detail` switch is provided to display timestamp, hardware_id and values.
