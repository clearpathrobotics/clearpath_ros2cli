from setuptools import find_packages
from setuptools import setup

package_name = 'ros2graph'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['ros2cli'],
    zip_safe=True,
    author='Guillaume Autran',
    author_email='gautran@clearpath.ai',
    maintainer='Clearpath OS Team',
    maintainer_email='cposteam@clearpath.ai',
    keywords=[],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: 3-Clause BSD License',
        'Programming Language :: Python',
    ],
    description='The graph command for ROS 2 command line tools.',
    long_description="""\
The package provides the graph command for the ROS 2 command line tools.""",
    license='BSD',
    tests_require=['pytest'],
    entry_points={
        'ros2cli.command': [
            'graph = ros2graph.command.graph:GraphCommand',
        ],
        'ros2cli.extension_point': [
            'ros2graph.verb = ros2graph.verb:VerbExtension',
        ],
        'ros2graph.verb': [
            'dot = ros2graph.verb.dot:DotVerb',
        ],
    }
)
