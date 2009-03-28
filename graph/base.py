#! /usr/bin/env python3

"""
base.py

Written by Geremy Condra

Licensed under the GNU GPLv3

Released 25 Mar 2009

This module contains Graphine's base graph represenatation.

The goal of Graph is to provide a flexible, easy to use,
somewhat fast graph implementation. It should be seen as
a firm foundation for later extension, providing all the
tools a developer needs to create the appropriate data
structure for their task with only slight modification.

Interface summary:

To create a new Graph:

	>>> from graph.base import Graph
	>>> g = Graph()

To add nodes:

	>>> node_1 = g.add_node(name="bob")
	>>> node_2 = g.add_node(weight=5)
	>>> node_3 = g.add_node(color="red", flags=["visited"])

To add edges:

	>>> edge_1 = g.add_edge(node_2, node_3)
	
Notice that edges can have properties as well:

	>>> edge_2 = g.add_edge(node_1, node_2, weight=5)
	>>> edge_3 = g.add_edge(node_3, node_1, stuff={})
	
To remove nodes:

	>>> g.remove_node(node_3)
	Node(color="red", flags=["visited"])
	
And edges:

	>>> g.remove_edge(edge_3)
	Edge(stuff={})

To iterate over all the nodes in a graph:

	>>> for node in g.nodes:
	>>>	print(node)
	Node(name="bob")
	Node(weight=5)

And, for edges:

	>>> for edge in g.edges:
	>>> 	print(edge)
	Edge()
	Edge(weight=5)

If you only want certain nodes, the search
functions is provided for convenience:

	>>> for node in g.search_nodes(name="bob"):
	>>> 	print(node)
	Node(name="bob")
	
And for edges:

	>>> for edge in g.search_edges(weight=5):
	>>> 	print(edge)
	Edge(weight=5)

Three traversals are provided by default- A*,
depth first, and breadth first.

To do a depth first traversal:

	>>> for node in g.depth_first_traversal(node_1):
	>>> 	print(node)
	Node(name="bob")
	Node(weight=5)

and similar for depth first traversals.

A* traversals require an additional callable argument.
This callable will be passed a deque of unvisited nodes
and should select exactly one of them to return.

And to traverse a tree, going to those nodes first:

	>>> for node in g.a_star_traversal(node_1, get_heaviest):
	>>> 	print(node)
	Node(weight=5)
	Node(name="bob")
"""

# Copyright (C) 2009 Geremy Condra
#
# This file is part of Graphine.
# 
# Graphine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Graphine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Graphine.  If not, see <http://www.gnu.org/licenses/>.


from collections import deque, namedtuple

class GraphElement(object):
	"""Base class for Nodes and Edges."""

	__structure = None
	
	def __init__(self, structure, **kwargs):
		# contains the basic, should-not-be-modified
		# information the node needs to operate
		self.__structure = structure
		# all other values
		for k, v in kwargs.items():
			setattr(self, k, v)
	
	def __setattr__(self, attr, value):
		if hasattr(self.__structure, attr):
			msg = "Cannot set attribute '%s'" % attr
			raise AttributeError(msg)
		else:
			super().__setattr__(attr, value)

	def __getattr__(self, attr):
		return getattr(self.__structure, attr)

	def __repr__(self):
		classname = type(self).__name__
		attrs = ''.join(("%s=%s, " % (k, v) for k, v in self.data.items()))[:-2]
		return "%s(%s)" % (classname, attrs)

	@property
	def data(self):
		return {k:v for k, v in self.__dict__.items() if not k.startswith("_")}


class Node(GraphElement):
	"""Base node representation."""
	pass


class Edge(GraphElement):
	"""Base edge representation."""
	pass


class Graph(object):
	"""Base class for all Graph mixins"""

	Node = Node
	Edge = Edge
	node_attributes = ("incoming", "outgoing")
	edge_attributes = ("start", "end")
	NodeStructure = namedtuple("NodeStructure", node_attributes)
	EdgeStructure = namedtuple("EdgeStructure", edge_attributes)

	def __init__(self):
		"""Base initializer for Graphs"""
		self.nodes = []
		self.edges = []

	def __contains__(self, element):
		"""returns True if the element is a member of the graph"""
		if isinstance(element, self.Node):
			return element in self.nodes
		else:
			return element in self.edges

	def add_node(self, *args, **kwargs):
		"""Adds a node to the current graph."""
		# provide sensible defaults- no incoming, no outgoing
		args = args or (set(), set())
		# construct the control structure
		try:
			structure = self.NodeStructure(*args)
		except TypeError as error:
			msg = "Nodes require at least %d positional arguments (%d given)"
			num_required = len(self.node_attributes)
			num_recieved = len(args)
			raise TypeError(msg % (num_required, num_recieved)) from error
		# build the actual node
		node = self.Node(structure, **kwargs)
		self.nodes.append(node)
		return node

	def add_edge(self, *args, **kwargs):
		"""Adds an edge to the current graph."""
		# construct the control structure
		try:
			structure = self.EdgeStructure(*args)
		except TypeError as error:
			msg = "Edges require at least %d positional arguments (%d given)"
			num_required = len(self.node_attributes)
			num_recieved = len(args)
			raise TypeError(msg % (num_required, num_recieved)) from error
		# build the edge
		edge = self.Edge(structure, **kwargs)
		self.edges.append(edge)
		# take care of adjacency tracking
		structure.start.outgoing.add(edge)
		structure.end.incoming.add(edge)
		return edge

	def remove_node(self, node):
		"""Removes a node from the graph."""
		# remove it from adjacency tracking
		for edge in node.incoming:
			edges.pop(edge)
		for edge in node.outgoing:
			edges.pop(edge)
		# remove it from storage
		n = self.nodes.remove(node)
		return n

	def remove_edge(self, edge):
		"""Removes an edge from the graph."""
		# remove it from adjacency tracking
		edge.start.outgoing.remove(edge)
		edge.end.incoming.remove(edge)
		# remove it from storage
		e = self.edges.remove(edge)
		return e

	def search_nodes(self, **kwargs):
		"""Convenience function to get nodes based on some properties."""
		desired_properties = set(kwargs.items())
		for node in self.nodes:
			properties = set(node.data.items())
			if properties.issuperset(desired_properties):
				yield node

	def search_edges(self, **kwargs):
		"""Convenience function to get edges based on some properties."""
		desired_properties = set(kwargs.items())
		for edge in self.edges:
			properties = set(edge.data.items())
			if properties.issuperset(desired_properties):
				yield edge

	def a_star_traversal(self, root, selector):
		"""Traverses the graph using selector as a selection filter on the unvisited nodes."""
		discovered = deque()
		visited = set()
		discovered.append(root)
		# while there are unprocessed nodes
		while discovered:
			# select the next one
			next = selector(discovered)
			yield next
			# visit it
			visited.add(next)
			# get the adjacent nodes
			adjacent = {edge.end for edge in next.outgoing}
			# filter it against those we've already visited
			not_yet_visited = adjacent - visited
			# make sure we're not double-adding
			for node in not_yet_visited:
				if node not in discovered:
					discovered.append(node)

	def depth_first_traversal(self, root):
		"""Traverses the graph by visiting a node, then a child of that node, and so on."""
		for node in self.a_star_traversal(root, lambda s: s.pop()):
			yield node
		
	def breadth_first_traversal(self, root):
		"""Traverses the graph by visiting a node, then each of its children, then their children"""
		for node in self.a_star_traversal(root, lambda s: s.popleft()):
			yield node

	def size(self):
		"""Reports the number of edges in the graph"""
		return len(self.edges)

	def order(self):
		"""Reports the number of nodes in the graph"""
		return len(self.nodes)
