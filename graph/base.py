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


from collections import deque, defaultdict, namedtuple


class Graph(object):
	"""Base class for all Graph mixins"""

	def __init__(self, node_properties, edge_properties):
		"""Base initializer for Graphs.

		To build a new Graph, just instantiate this with
		the properties you want your Nodes and Edges to
		have, eg, if I want named nodes and weighted edges:
		
		>>> g = Graph(["name"], ["weight"])
	
		I used a list here, but any iterable will suffice,
		including dictionaries.
		"""
		# add required attributes to edges
		edge_properties =  ("start", "end") + tuple(edge_properties)
		# instantiate node and edge classes
		self.Node = namedtuple("Node", node_properties)
		self.Edge = namedtuple("Edge", edge_properties)
		# keep track of relevant properties
		self.nodes = {}
		self.edges = {}
		# keep track of all adjacencies
		self.adjacency_list = defaultdict(set)
		# and of the available uid's
		self.unused_node_uids = deque()		# these are positive
		self.unused_edge_uids = deque()		# these are negative

	def __contains__(self, element):
		"""returns True if the element is a member of the graph"""
		if element.uid > 0:
			return element in self.nodes.values()
		else:
			return element in self.edges.values()

	def __getitem__(self, uid):
		"""retrieves the item corresponding to the given uid"""
		if uid > 0:
			return self.nodes[uid]
		else:
			return self.edges[uid]

	def __setitem__(self, uid, value):
		"""sets the value corresponding to the given uid"""
		# if its a node
		if uid > 0:
			self.nodes[uid] = value
		else:
			e = self.edges[uid]
			if e.start is value.start and e.end is value.end:
				self.edges[uid] = value
			else:
				# disconnect the edge
				self.adjacency_list[e.start].remove(e.end)
				# and reconnect it
				self.adjacency_list[value.start].add(value.end)

	def __delitem__(self, uid):
		"""deletes the item corresponding to the given uid"""
		# if its a node
		if uid > 0:
			return self.remove_node(uid)
		else:
			return self.remove_edge(uid)

	def get_node_uid(self):
		"""gets a natural number uid for a new node"""
		try:
			return self.unused_node_uids.pop()
		except:
			return len(self.nodes) + 1

	def get_edge_uid(self):
		"""gets an integral uid for a new edge"""
		try:
			return self.unused_edge_uids.pop()
		except:
			return -len(self.edges) - 1

	def node_uids(self):
		"""Iterates over all node uids"""
		for uid in self.nodes:
			yield uid

	def edge_uids(self):
		"""Iterates over all edge uids"""
		for uid in self.edges:
			yield uid

	def add_node(self, **kwargs):
		"""Adds a node to the current graph.

		kwargs should include all the fields required to
		instantiate your Node class, eg:
		
		>>> g = Graph(["name"], [])
		>>> g.add_node(name="bob")

		Giving fewer, more, or differently named fields
		will throw an error.
		"""
		uid = self.get_node_uid()
		self.nodes[uid] = self.Node(**kwargs)
		return uid

	def add_edge(self, start, end, **kwargs):
		"""Adds an edge to the current graph.

		The same notes on adding nodes apply here,
		eg, make sure that you provide a value for
		all the properties in your Edge.
		"""
		uid = self.get_edge_uid()
		self.edges[uid] = self.Edge(start=start, end=end, **kwargs)
		self.adjacency_list[start].add(end)
		return uid

	def modify_node(self, uid, **kwargs):
		"""Modifies an existing node.
		
		Essentially, this does a dictionary update on the
		node. Note that you can't add or remove attributes 
		this way, just set their values, eg:

		>>> bill = g.add_node(name="bill")
		>>> bob = g.modify_node(name="bob")
		>>> # bill and bob are uid's, not Nodes
		>>> bill is bob
		True
		>>> g[bob]
		Node(name="bob")
		>>> g[bill]
		Node(name="bob")
		>>> # trying to turn bob evil...
		>>> g.modify_node(bob, mustache=True)
		...stack trace...
		ValueError: Got unexpected field names: ...

		"""
		n = self[uid]
		n = n._replace(**kwargs)
		self[uid] = n
		return uid

	def modify_edge(self, uid, **kwargs):
		"""Modifies an existing edge.

		See the notes on modify_edges for more information.
		"""
		e = self[uid]
		e = e._replace(**kwargs)
		self[uid] = e
		return uid

	def remove_node(self, uid):
		"""Removes a node from the graph.

		Note that this does not remove the edges that
		had this node as a terminus, it simply removes
		them from the adjacency listing. It is up
		to the programmer to ensure that bad things
		don't happen:

		>>> # ok...
		>>> bob = g.add_node(name="bob")
		>>> bill = g.add_node(name="bill")
		>>> e = g.add_edge(bob, bill)
		>>> g.remove_node(bob)
		1
		>>> # still ok...
		>>> for node in g.get_adjacent_nodes(bob):
		>>> 	print(node)
		>>>
		>>> # BADBADBAD
		>>> for edge in g.get_edges_by_properties(start=bob, end=bill):
			print(edge)
		Edge(start=1, end=2)
		>>>

		"""
		# remove it from node storage
		n = self.nodes.pop(uid)
		# remove it from adjacency tracking
		try:
			del self.adjacency_list[uid]
		except:
			pass
		# add it to the untracked uids
		self.unused_node_uids.append(uid)
		# pass it back to the caller
		return n

	def remove_edge(self, uid):
		"""Removes an edge from the graph"""
		# remove it from edge storage
		e = self.edges.pop(uid)
		# remove it from adjacency tracking
		self.adjacency_list[e.start].remove(e.end)
		# add it to the untracked uids
		self.unused_edge_uids.append(uid)
		# pass it back to the caller
		return e

	def get_nodes(self):
		"""Iterates over all the nodes."""
		for node in self.nodes.values():
			yield node

	def get_edges(self):
		"""Iterates over all the edges."""
		for edge in self.edges.values():
			yield edge

	def search_nodes(self, **kwargs):
		"""Convenience function to get nodes based on some properties."""
		for node in self.get_nodes():
			for k, v in kwargs.items():
				if not v == getattr(node, k):
						continue
				yield node

	def search_edges(self, **kwargs):	
		"""Convenience function to get edges based on some properties."""
		for node in self.get_edges():
			for k, v in kwargs.items():
				if not v == getattr(node, k):
					continue
				yield node

	def get_adjacent_uids(self, uid):
		"""Convenience function to get uids based on adjacency"""
		yield uid
		for adjacent_uid in self.adjacency_list.get(uid, []):
			yield adjacent_uid

	def get_adjacent_nodes(self, uid):
		for uid in self.get_adjacent_uids(uid):
			yield self[uid]	

	def a_star_traversal(self, root_uid, selector):
		"""Traverses the graph using selector as a selection filter on the unvisited nodes."""
		unvisited = deque()
		visited = deque()
		unvisited.append(root_uid)
		while unvisited:
			next_uid = selector(unvisited)
			yield next_uid
			visited.append(next_uid)
			for uid in self.get_adjacent_uids(next_uid):
				if uid not in unvisited:
					if uid not in visited:
						unvisited.append(uid)

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
