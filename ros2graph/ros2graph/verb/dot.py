# Software License Agreement (proprietary)
#
# @author    Guillaume Autran <gautran@clearpath.ai>
# @copyright (c) 2023, Clearpath Robotics, Inc., All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, is not permitted without the
# express permission of Clearpath Robotics.

from collections import namedtuple
from ros2cli.node.strategy import add_arguments
from ros2cli.node.strategy import NodeStrategy
from ros2graph.api import get_node_names
from ros2graph.api import get_publisher_info
from ros2graph.api import get_service_client_info
from ros2graph.api import get_service_server_info
from ros2graph.api import get_action_client_info
from ros2graph.api import get_action_server_info
from ros2graph.api import get_subscriber_info
from ros2graph.api import DotWriter
from ros2graph.api import get_id
from ros2graph.verb import VerbExtension


class DotVerb(VerbExtension):
    """Output a DOT graph of the listed nodes."""

    ignore_list = {'/rosout', '/parameter_events', 'describe_parameters', 'get_parameter_types', 'list_parameters', 'set_parameters', 'get_parameters', 'set_parameters_atomically'}

    def add_arguments(self, parser, cli_name):
        add_arguments(parser)
        parser.add_argument(
            '-a', '--all', action='store_true', default=False,
            help='Display all nodes even hidden ones')
        parser.add_argument(
            '-t', '--types', action='store_true', default=True,
            help='Display topic types')
        parser.add_argument(
            '-u', '--unconnected', action='store_true', default=True,
            help='Display also the unconnected topics/services/actions')
        parser.add_argument(
            '--select', choices=['topics', 'services', 'actions'], nargs="+", default=['topics', 'services', 'actions'],
            help='Select which components to graph: topics/services/actions')


    def ignore(self, name):
        if name in self.ignore_list or name.split('/')[-1] in self.ignore_list:
            return True
        else:
            return False

    def main(self, *, args):
        Edge = namedtuple('Edge', ('topic', 'src', 'dst', 'id', 'colour'))

        with NodeStrategy(args) as node:
            node_names = get_node_names(node=node, include_hidden_nodes=args.all)

            namespaces = {n.namespace for n in node_names}

            grouped_node = dict()
            for ns in namespaces:
                grouped_node[ns] = [n for n in node_names if ns == n.namespace ]

            dw = DotWriter()
            dw.begin_graph(rankdir='LR', concentrate=True)
            # Write the legend
            dw.begin_subgraph(get_id('cluster_'), label='legend')
            key_id = get_id('key_')
            key2_id = get_id('key2_')
            dw.write(f'{key_id} [shape=plaintext, label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">\n'
                    '\t<tr><td align="right" port="i1">Topics</td></tr>\n'
                    '\t<tr><td align="right" port="i2">Services</td></tr>\n'
                    '\t<tr><td align="right" port="i3">Actions</td></tr>\n'
                    '\t</table>>]\n')
            dw.write(f'{key2_id} [shape=plaintext, label=<<table border="0" cellpadding="2" cellspacing="0" cellborder="0">\n'
                    '\t<tr><td port="i1">&nbsp;</td></tr>\n'
                    '\t<tr><td port="i2">&nbsp;</td></tr>\n'
                    '\t<tr><td port="i3">&nbsp;</td></tr>\n'
                    '\t</table>>]\n')

            dw.write(f'{key_id}:i1:e -> {key2_id}:i1:w [color=blue]\n')
            dw.write(f'{key_id}:i2:e -> {key2_id}:i2:w [color=orange]\n')
            dw.write(f'{key_id}:i3:e -> {key2_id}:i3:w [color=olive]\n')

            dw.end_subgraph()

            # Go through all the nodes and write them down
            for ns in namespaces:
                if ns:
                    dw.begin_subgraph(get_id('cluster_'), label=ns)
                for n_node in grouped_node[ns]:
                    dw.node(n_node.id, label=n_node.name)
                if ns:
                    dw.end_subgraph()

            # Generate the node edges
            edges = dict()
            for node_name in node_names:
                if 'topics' in args.select:
                    subscribers = get_subscriber_info(
                        node=node, remote_node_name=node_name.full_name, include_hidden=args.all)

                    for sub in subscribers:
                        if self.ignore(sub.name):
                            continue
                        edges.setdefault(sub.name, Edge(
                            topic=sub,
                            dst=[],
                            src=[],
                            id=get_id('edge_'),
                            colour='blue',
                        ))
                        edges[sub.name].dst.append(node_name.id)

                    publishers = get_publisher_info(
                        node=node, remote_node_name=node_name.full_name, include_hidden=args.all)

                    for pub in publishers:
                        if self.ignore(pub.name):
                            continue
                        edges.setdefault(pub.name, Edge(
                            topic=pub,
                            dst=[],
                            src=[],
                            id=get_id('edge_'),
                            colour='blue',
                        ))
                        edges[pub.name].src.append(node_name.id)

                if 'services' in args.select:
                    service_clients = get_service_client_info(
                        node=node, remote_node_name=node_name.full_name, include_hidden=args.all)

                    for client in service_clients:
                        if self.ignore(client.name):
                            continue
                        edges.setdefault(client.name, Edge(
                            topic=client,
                            dst=[],
                            src=[],
                            id=get_id('edge_'),
                            colour='orange',
                        ))
                        edges[client.name].src.append(node_name.id)

                    service_servers = get_service_server_info(
                        node=node, remote_node_name=node_name.full_name, include_hidden=args.all)

                    for server in service_servers:
                        if self.ignore(server.name):
                            continue
                        edges.setdefault(server.name, Edge(
                            topic=server,
                            dst=[],
                            src=[],
                            id=get_id('edge_'),
                            colour='orange',
                        ))
                        edges[server.name].dst.append(node_name.id)

                if 'actions' in args.select:
                    action_clients = get_action_client_info(
                        node=node, remote_node_name=node_name.full_name, include_hidden=args.all)

                    for client in action_clients:
                        if self.ignore(client.name):
                            continue
                        edges.setdefault(client.name, Edge(
                            topic=client,
                            dst=[],
                            src=[],
                            id=get_id('edge_'),
                            colour='olive',
                        ))
                        edges[client.name].src.append(node_name.id)

                    action_servers = get_action_server_info(
                        node=node, remote_node_name=node_name.full_name, include_hidden=args.all)

                    for server in action_servers:
                        if self.ignore(server.name):
                            continue
                        edges.setdefault(server.name, Edge(
                            topic=server,
                            dst=[],
                            src=[],
                            id=get_id('edge_'),
                            colour='olive',
                        ))
                        edges[server.name].dst.append(node_name.id)

            for edge in edges.values():
                if args.unconnected and not edge.src:
                    # Topic only has listeners but no publishers
                    blank = get_id('blank_r_')
                    dw.node(blank, style='invis')
                    edge.src.append(blank)
                if args.unconnected and not edge.dst:
                    # Topic only has publishers but no listeners
                    blank = get_id('blank_w_')
                    dw.node(blank, style='invis')
                    edge.dst.append(blank)

                for src in edge.src:
                    for dst in edge.dst:
                        label = edge.topic.name
                        src_cnt = len(edge.src)
                        if src_cnt > 1:
                            label = f'{label}({src_cnt})'
                        if args.types:
                            label = f"{label} [{edge.topic.types[0]}]"
                        dw.edge(src, dst, label=label, fontcolor=edge.colour, color=edge.colour, penwidth=src_cnt)

        dw.end_graph()
