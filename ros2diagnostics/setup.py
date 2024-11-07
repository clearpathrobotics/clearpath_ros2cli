"""This script configures the packaging of the 'ros2diagnostics' project."""

from setuptools import find_packages
from setuptools import setup

package_name = 'ros2diagnostics'

setup(
    name=package_name,
    python_requires='>=3.10',
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['ros2cli'],
    zip_safe=True,
    author='Yolanda Huang',
    author_email='yhuang@ottomotors.com',
    maintainer='Clearpath OS Team',
    maintainer_email='cposteam@clearpath.ai',
    keywords=[],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: 3-Clause BSD License',
        'Programming Language :: Python',
    ],
    description="""\
    A convenient command to display the diagnostics info \
    for ROS 2 command line tools""",
    long_description="""\
    The package provides a cli tool to echo \
    the diagnostics logs in a ROS 2 system""",
    license='BSD',
    tests_require=['pytest'],
    entry_points={
        'ros2cli.command': [
            'diagnostics = ros2diagnostics.command.diagnostics:DiagCommand',
        ],
        'ros2cli.extension_point': [
            'ros2diagnostics.verb = ros2diagnostics.verb:VerbExtension',
        ],
        'ros2diagnostics.verb': [
            'echo = ros2diagnostics.verb.echo:EchoVerb'
        ]
    }
)
