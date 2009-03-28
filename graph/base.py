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
	>>> # I need named nodes and weighted edges
	>>> g = Graph(["name"], ["weight"])

To add nodes:

	>>> node_1 = g.add_node(name="bob")
	>>> node_2 = g.add_node(name="agamemnon")

To add edges:

	>>> edge_1 = g.add_edge(node_1, node_2, weight=5)

Note that what you're getting back isn't a full
node or edge, eg:

	>>> node_1
	1
	>>> node_2
	2
	>>> edge_1
	-1

As you can see, its just an id used to uniquely
identify it to the graph. To get the full object,
just ask nicely:

	>>> g[node_1]
	Node(name="bob")

The same thing works for edges:

	>>> g[edge_1]
	Edge(start=1, end=2, weight=5)

Notice again that it uses those uids as reference
points. Don't forget them!

To iterate over all the nodes in a graph:

	>>> for node in g.get_nodes():
	>>>	print(node)
	Node(name="bob")
	Node(name="agamemnon")

And, for edges:

	>>> for edge in g.get_edges():
	>>> 	print(edge)
	Edge(start=1, end=2, weight=5)

Of course, if you want to get the uids, just use get_node_uids
or get_edge_uids.

Traversals are just as simple:

	>>> for node_uid in g.depth_first_traversal(node_1):
	>>> 	print(g[node_uid])
	Node(name="bob")
	Node(name="agamemnon")

and similar for depth first traversals. 
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

	def __init__(self, structure, **kwargs):
		# contains the basic, should-not-be-modified
		# information the node needs to operate
		super().__setattr__("_structure", structure)
		# all other values
		for k, v in kwargs.items():
			setattr(self, k, v)
	
	def __hash__(self):
		return hash(frozenset(((k,v) for k, v in self.get_properties())))

	def __eq__(self, other):
		return hash(self) == hash(other)

	def __ne__(self, other):
		return hash(self) != hash(other)

	def __setattr__(self, attr, value):
		if hasattr(self._structure, attr):
			msg = "Cannot set attribute %s" % attr
			raise AttributeError(msg)
		elif attr is "_structure":
			msg = "Attribute '_structure' is reserved."
			raise AttributeError(msg)
		else:
			super().__setattr__(attr, value)

	def __getattr__(self, attr):
		try:
			return getattr(self._structure, attr)
		except AttributeError:
			return super().__getattr__(attr)

	def get_properties(self):
		for k, v in self.__dict__.items():
			if k is not "_structure":
				yield k, v


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
		args = args or ([], [])
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
		structure.start.outgoing.append(edge)
		structure.end.incoming.append(edge)
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
			properties = set(node.get_properties())
			if properties.issuperset(desired_properties):
				yield node

	def search_edges(self, **kwargs):
		"""Convenience function to get edges based on some properties."""
		desired_properties = set(kwargs.items())
		for edge in self.edges:
			properties = set(edge.get_properties())
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
			# get the nodes we haven't visited from it
			adjacent = set()
			for edge in next.outgoing:
				adjacent.add(edge.end)
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
