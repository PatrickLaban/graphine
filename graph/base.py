#! /usr/bin/env python3.0

"""
base.py

Written by Geremy Condra

Licensed under the GNU GPLv3

Released 25 Mar 2009

This module contains the base GraphElement, Node, Edge,
and Graph implementations for Graphine, an easy-to-use,
easy-to-extend Graph library.

Graphs generated using this representation have directed 
edges, the ability to represent loops and parallel edges,
and can attach arbitrary data to nodes and edges.

Interface summary
=================

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
	
And edges:

	>>> g.remove_edge(edge_3)

Navigating Graphs
-----------------

In addition to storing your data, Nodes and Edges have
a few other special properties by default. For Nodes,
these properties are "incoming" and "outgoing", and
they contain the incoming and outgoing edges attached
to that node. For Edges, these properties are (again,
by default) "start" and "end".

To get all the outgoing edges of a particular node:

	>>> n1.outgoing
	[Edge(weight=5)]

And to get the incoming edges:

	>>> n2.incoming
	[Edge(weight=5)]

You can use this to get all the nodes adjacent to
an interesting Node:

	>>> adjacent = [edge.end for edge in node1.outgoing]

Or to get the degree of the given node:

	>>> degree = len(node1.outgoing) + len(node2.incoming)
	
You can combine this with Edges' "start" and "end" properties
to navigate your graph, if you know how your data is related
structurally. For example, to get the oldest outgoing edge attached
to the oldest node attached to node_1, I could do the following:

	>>> interesting_node = node_1.outgoing[0].end.outgoing[0]

Of course, there are scenarios in which you don't know how to
navigate your graph, or need to find a starting point that isn't
easily determined based on a given element's properties. For that,
Graph supports Node and Edge iteration for the simple cases, and
traversals for more complex behavior.

To iterate over all the nodes in a graph:

	>>> for node in g.nodes:
	>>>	print(node)
	Node(name="bob")
	Node(weight=5)

To do the same for edges:

	>>> for edge in g.edges:
	>>> 	print(edge)
	Edge()
	Edge(weight=5)

If you only want certain nodes, the search
functions are provided for convenience:

	>>> for node in g.search_nodes(name="bob"):
	>>> 	print(node)
	Node(name="bob")
	
And for edges:

	>>> for edge in g.search_edges(weight=5):
	>>> 	print(edge)
	Edge(weight=5)

You can also search for elements which demonstrate data
equality with a given element. This is often useful when
comparing elements from different graphs.

To get all equivalent nodes:

	>>> n = Node(name="bob")
	>>> g.get_equivalent_nodes(n)
	{Node(name="bob")}

And its edge-comparing equivalent

	>>> e = Edge(node_2, node_3, weight=5)
	>>> g.get_equivalent_edges(e)
	{Node(weight=5)}

Of course, the edge returned by this function *is* datawise
equivalent to the edge we just created. But more likely,
when you're looking at edges you're interested in the nodes
around them as much as you are the node itself. In the
example above, the edge returned is attached at different
points than the edge given. To solve this, you can use the 
optional "flatten" argument, which causes it to also compare
the data in edges incident to the node given or nodes 
incident to the edge given.

Three traversals are provided by default- A*, depth first,
and breadth first.

To do a depth first traversal:

	>>> for node in g.depth_first_traversal(node_1):
	>>> 	print(node)
	Node(name="bob")
	Node(weight=5)

Depth first traversals are similar in usage, simply
substituting "depth_first_traversal" for "breadth_first_traversal".

A* traversals require an additional callable argument.
This callable will be passed a list of unvisited nodes
and should select and remove exactly one of them to return.

For example, to navigate a graph by visiting the most
popular (ie, most incoming edges) nodes first, I could
write a getter function as follows:

	>>> def get_popularity(node):
	>>> 	return len(node.incoming)

A selector function:

	>>> def get_most_popular(nodes):
	>>> 	nodes.sort(nodes, key=get_popularity)
	>>>	return nodes.pop()

And traverse the graph:

	>>> for node in g.a_star_traversal(node_1, get_heaviest):
	>>> 	print(node)
	Node(weight=5)
	Node(name="bob")

Binary Graph Operations
-----------------------

Four basic operations are provided for the comparison
of graphs: 

	1. union (|), which creates a new graph containing all
	   the nodes and edges of its parents,

	2. intersection (&), which creates a new graph containing
	   all the nodes and edges not in both

	3. difference (-), which creates a new graph containing
	   all the nodes and edges in the first parent but
	   not in the second.

	4. merge (+), which creates a new graph with all the 
	   data-unique nodes from both parent graphs plus all 
	   their structurally and data unique edges.

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
import copy

class GraphElement(object):
	"""Base class for Nodes and Edges.

	A GraphEdge.data property is provided to give easier
	access to all of the element's non-structural member
	variables. It returns a dictionary.

	It also provides an __repr__ member function to make
	easier work of analyzing your graphs.
	"""

	def __repr__(self):
		classname = type(self).__name__
		attrs = ''.join(("%s=%s, " % (k, v) for k, v in self.data.items()))[:-2]
		return "%s(%s)" % (classname, attrs)

	@property
	def data(self):
		return {k:v for k, v in self.__dict__.items() if not k.startswith("_")}


class Node(GraphElement):
	"""Base node representation.

	Nodes have two properties, incoming and outgoing, which are
	tuples of the edges which are incident to the node.

	Nodes also have the flatten function, which provides a view
	of the node suitable for comparison with nodes from other graphs.

	They also inheirit the data property, which provides dictionary
	access to all the non-private portions of the node.
	"""

	def __init__(self, incoming=None, outgoing=None, **kwargs):
		self._incoming = incoming or []
		self._outgoing = outgoing or []
		for k, v in kwargs.items():
			setattr(self, k, v)

	def flatten(self):
		"""Returns a view of this node useful for comparison to nodes
		in other graphs.
		"""
		outgoing_data = [edge.flatten() for edge in self.outgoing]
		incoming_data = [edge.flatten() for edge in self.incoming]
		return (self.data, incoming_data, outgoing_data)

	@property
	def incoming(self):
		"""Returns a list of all the incoming edges for this node.

		Note that the list returned is a copy, so modifying it doesn't
		impact the structure of the graph.
		"""
		return copy.copy(self._incoming)

	@property
	def outgoing(self):
		"""Returns a list of all the outgoing edges for this node.

		Note that the list returned is a copy, so modifying it doesn't
		impact the structure of the graph.
		"""
		return copy.copy(self._outgoing)


class Edge(GraphElement):
	"""Base edge representation.

	Edges have two properties, start and end, which are
	Node objects incident to the edge.

	Edges also provide the flatten function, which gives
	a view of the edge suitable for comparison to edges in
	other graphs. 

	They also inhierit the data property, which provides
	dictionary access to all the non-private portions of
	the edge.
	"""

	def __init__(self, start, end, **kwargs):
		self._start = start
		self._end = end
		for k, v in kwargs.items():
			setattr(self, k, v)

	def flatten(self):
		"""Returns a representation of this suitable for
		comparison to edges in other graphs.

		It returns a threeple of this Edge's data, its
		starting node's data, and its endpoint's data.
		"""
		start_data = self.start.data
		end_data = self.end.data
		return (self.data, start_data, end_data)

	@property
	def start(self):
		"""Returns the starting point for this edge."""
		return self._start

	@property
	def end(self):
		"""Returns the ending point for this edge."""
		return self._end


class Graph(object):

	"""A basic graph class, and base for all Graph mixins.

	Details
	=======

	In graph theoretic terms, this represents a directed multigraph.

	Graph is designed to have a simple, easy-to-use, easy-to-extend
	architecture, which allows for easy and intuitive graph construction
	and traversal.

	Internally, nodes and edges are maintained in lists, each element of
	which is of the type specified by Graph.Node or Graph.Edge, as
	appropriate. Both types should have the property "data", which
	should return a dictionary represenation of its optional attributes,
	while nodes should provide "incoming" and "outgoing" properties, as
	well as writable private properties by the names "_incoming" and 
	"_outgoing". Edges should provide similarly conventioned "start"
	and "end" properties.

	Todo
	====

	- Add graph analysis tools
		- all_pairs_shortest_paths
		- shortest_path
		- minimum_spanning_tree	
	"""

	Node = Node
	Edge = Edge

	def __init__(self):
		"""Base initializer for Graphs.

		Usage:
			>>> g = Graph()
		"""
		self.nodes = []
		self.edges = []

	def __contains__(self, element):
		"""Returns True if the element is a member of the graph.

		Usage:
			>>> g = Graph()
			>>> n = g.add_node()
			>>> n in g
			True
		"""
		if isinstance(element, self.Node):
			return element in self.nodes
		else:
			return element in self.edges

	def __and__(self, other):
		"""Maps the & operator to the intersection operation."""
		return self.intersection(other)

	def __or__(self, other):
		"""Maps the | operator to the union operation."""
		return self.union(other)

	def __sub__(self, other):
		"""Maps the - operator to the difference operation."""
		return self.difference(other)

	def __add__(self, other):
		"""Maps the + operator to the merge operation."""
		return self.merge(other)

	def add_node(self, **kwargs):
		"""Adds a node with no edges to the current graph.

		Usage:
			>>> g = Graph()
			>>> n = g.add_node(weight=5)
			>>> n
			Node(weight=5)
		"""
		node = self.Node(**kwargs)
		self.nodes.append(node)
		return node

	def add_edge(self, start, end, **kwargs):
		"""Adds an edge to the current graph.

		Usage:	
			>>> g = Graph()
			>>> n1, n2 = g.add_node(), g.add_node()
			>>> e = g.add_edge(n1, n2, weight=5)
			>>> e
			Edge(weight=5)			
		"""
		# build the edge
		edge = self.Edge(start, end, **kwargs)
		self.edges.append(edge)
		# take care of adjacency tracking
		start._outgoing.append(edge)
		end._incoming.append(edge)
		return edge

	def remove_node(self, node):
		"""Removes a node from the graph.

		Usage:
			>>> g = Graph()
			>>> n = g.add_node()
			>>> g.remove_node(n)
			>>> n in g
			False
		"""
		# remove it from adjacency tracking
		for edge in node.incoming:
			edges.pop(edge)
		for edge in node.outgoing:
			edges.pop(edge)
		# remove it from storage
		n = self.nodes.remove(node)
		return n

	def remove_edge(self, edge):
		"""Removes an edge from the graph.

		Usage:
			>>> g = Graph()
			>>> n1, n2 = g.add_node(), g.add_node()
			>>> e = g.add_edge(n1, n2)
			>>> g.remove_edge(e)
			>>> e in g
			False
		"""
		# remove it from adjacency tracking
		start = edge.start
		end = edge.end
		start._outgoing.remove(edge)
		end._incoming.remove(edge)
		# remove it from storage
		e = self.edges.remove(edge)
		return e

	def search_nodes(self, **kwargs):
		"""Convenience function to get nodes based on some properties.

		Usage:
			>>> g = Graph()
			>>> n1 = g.add_node(name="bob")
			>>> n2 = g.add_node(name="bill")
			>>> for node in g.search_nodes(name="bob"):
			>>> 	print(node)
			Node(name="bob")
		"""
		desired_properties = set(kwargs.items())
		for node in self.nodes:
			properties = set(node.data.items())
			if properties.issuperset(desired_properties):
				yield node

	def search_edges(self, **kwargs):
		"""Convenience function to get edges based on some properties.

		Usage:
			>>> g = Graph()
			>>> n1, n2 = g.add_node(), g.add_node()
			>>> e1 = g.add_edge(n1, n2, weight=4)
			>>> e2 = g.add_edge(n1, n2, weight=5)
			>>> for edge in g.search_edges(weight=5):
			>>> 	print(edge)
			Edge(weight=5)
		"""
		desired_properties = set(kwargs.items())
		for edge in self.edges:
			properties = set(edge.data.items())
			if properties.issuperset(desired_properties):
				yield edge

	def get_equivalent_elements(self, element, container, flatten=False):
		"""Gets all the elements from container that are datawise equal to element.

		The optional argument "flatten" indicates whether to use element.data or
		element.flatten() for comparisons.

		Generally speaking, end users will be more interested in the convenience
		functions get_equivalent_nodes and get_equivalent edges, which omit the
		container argument.

		Usage:
			>>> g1 = Graph()
			>>> g2 = Graph()
			>>> n1 = g1.add_node(name="Geremy")
			>>> n2 = g2.add_node(name="Geremy")
			>>> g2.get_equivalent_elements(n1, g2.nodes)
			{Node(name="Geremy")}
		"""
		equivalent = set()
		if flatten:
			get_data = lambda e: e.flatten()
		else:
			get_data = lambda e: e.data
		data = get_data(element)
		for e2 in container:
			if get_data(e2) == data:
				equivalent.add(e2)
		return equivalent

	def get_equivalent_nodes(self, n1, flatten=False):
		"""Convenience function to find all equivalent nodes from this graph.

		The "flatten" argument indicates whether to use node.data or node.flatten()
		for comparison.

		Usage:
			>>> g1 = Graph()
			>>> g2 = Graph()
			>>> n1 = g1.add_node(name="Geremy")
			>>> n2 = g2.add_node(name="Geremy")
			>>> g2.get_equivalent_nodes(n1)
			{Node(name="Geremy")}
		"""
		return self.get_equivalent_elements(n1, self.nodes, flatten=flatten)

	def get_equivalent_edges(self, e1, flatten=False):
		"""Convenience function to find all equivalent edges from this graph.

		The "flatten" argument indicates whether to use edge.data or edge.flatten()
		for comparison.

		Usage is identical to get_equivalent_elements except for omitting the
		container argument.
		"""
		return self.get_equivalent_elements(e1, self.edges, flatten=flatten)

	def a_star_traversal(self, root, selector):
		"""Traverses the graph using selector as a selection filter on the unvisited nodes.

		Usage:
			>>> g = Graph()
			>>> n1, n2 = g.add_node(name="A"), g.add_node(name="B")
			>>> e = g.add_edge(n1, n2)
			>>> for node in g.a_star_traversal(n1, lambda s: s.pop()):
			>>> 	print(node)
			Node(name="A")
			Node(name="B")
		"""
		discovered = []
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
		"""Traverses the graph by visiting a node, then a child of that node, and so on.

		Usage:
			>>> g = Graph()
			>>> a, b = g.add_node(name="A"), g.add_node(name="B")
			>>> c, d = g.add_node(name="C"), g.add_node(name="D")
			>>> e1, e2 = g.add_edge(a, b), g.add_edge(a, c)
			>>> e3, e4 = g.add_edge(b, d), g.add_edge(c, d)
			>>> for node in g.depth_first_traversal(a):
			>>> 	print(node)
			Node(name="A")
			Node(name="B")
			Node(name="D")
			Node(name="C")
		"""
		for node in self.a_star_traversal(root, lambda s: s.pop()):
			yield node
		
	def breadth_first_traversal(self, root):
		"""Traverses the graph by visiting a node, then each of its children, then their children.

		Usage:
			>>> g = Graph()
			>>> a, b = g.add_node(name="A"), g.add_node(name="B")
			>>> c, d = g.add_node(name="C"), g.add_node(name="D")
			>>> e1, e2 = g.add_edge(a, b), g.add_edge(a, c)
			>>> e3, e4 = g.add_edge(b, d), g.add_edge(c, d)
			>>> for node in g.depth_first_traversal(a):
			>>> 	print(node)
			Node(name="A")
			Node(name="B")
			Node(name="C")
			Node(name="D")
		"""
		for node in self.a_star_traversal(root, lambda s: s.pop(0)):
			yield node

	def induce_subgraph(self, *nodes):
		"""Returns a new graph composed of only the specified nodes and their mutual edges.

		Usage:
		
		Set up your graph:

			>>> enterprise = Graph()
			>>> kirk = enterprise.add_node(name="kirk")
			>>> spock = enterprise.add_node(name="spock")
			>>> bones = enterprise.add_node(name="mccoy")
			>>> enterprise.add_edge(kirk, spock)
			>>> enterprise.add_edge(kirk, bones)

		As you can see, it has 3 nodes and two edges:

			>>> enterprise.order()
			3
			>>> enterprise.size()
			2

		Now we induce a subgraph that includes spock and bones but
		not the captain:

			>>> new_mission = enterprise.induce_subgraph(spock, bones)

		And can see that it has two nodes- spock and bones- but no edges:

			>>> new_mission.order()
			2
			>>> new_mission.size()
			0			
		"""
		g = type(self)()
		node_translator = {}
		for node in nodes:
			# copies node data
			n = g.add_node(**node.data)
			node_translator[node] = n
		for edge in self.edges:
			if edge.start in nodes:
				if edge.end in nodes:
					start = node_translator[edge.start]
					end = node_translator[edge.end]
					# copies edge data
					g.add_edge(start, end, **node.data)
		return g

	def union(self, other):
		"""Returns a new graph with all nodes and edges in either or both of its parents."""
		# create the graph
		g = type(self)()
		# add all of our nodes and edges
		translation_table = {}
		for node in self.nodes + other.nodes:
			n = g.add_node(**node.data)
			translation_table[node] = n
		for edge in self.edges + other.edges:
			start = translation_table[edge.start]
			end = translation_table[edge.end]
			g.add_edge(start, end, **edge.data)
		return g

	def intersection(self, other):
		"""Returns a graph containing only the nodes and edges in both of its parents.

		Because nodes and edges have no general meaning external to the graph in which
		they reside, this operation tests data equivalence for nodes and data and
		structural equivalence for edges. The net result of that is that this operation
		produces a graph containing all of the edges from this graph which have a
		structural equivalent in the other graph, and all the endpoints required for
		those edges to exist. It then tests all nodes without edges from this graph to
		ensure that the zero edge case is caught.
		"""
		# create the graph
		g = type(self)()
		added = {}
		# add all the edges and their endpoints
		for edge in self.edges:
			if other.get_equivalent_edges(edge, flatten=True):
				start = added.get(edge.start, False) or g.add_node(**edge.start.data)
				end = added.get(edge.end, False) or g.add_node(**edge.end.data)
				g.add_edge(start, end, **edge.data)
				added[edge.start] = start
				added[edge.end] = end
		# add all the zero degree nodes	
		for node in self.nodes:
			if len(node.incoming) + len(node.outgoing) == 0:
				if node not in added:
					if other.get_equivalent_nodes(node):
						added[node] = g.add_node(**node.data)
		return g
	
	def difference(self, other):
		"""Return a graph composed of the nodes and edges not in the other."""
		# create the new graph
		g = type(self)()
		added = {}
		# iterate over all the nodes
		for node in self.nodes:
			if node not in added:
				if not other.get_equivalent_nodes(node):
					added[node] = g.add_node(**node.data)
		# iterate over all the edges
		for edge in self.edges:
			if not other.get_equivalent_edges(edge, flatten=True):	
				if edge.start in added:
					if edge.end in added:
						start = added[edge.start]
						end = added[edge.end]
						g.add_edge(start, end, **edge.data)
		return g

	def merge(self, other):
		"""Returns a new graph with its nodes and edges merged by data equality."""
		# create the new graph
		g = type(self)()
		# create duplicate sets
		duplicate_nodes = set()
		duplicate_edges = set()
		# create unified lists
		all_nodes = self.nodes + other.nodes
		all_edges = self.edges + other.edges
		# create the translation table
		translate = {}
		# iterate over the nodes in both sets
		for node in all_nodes:
			if node not in duplicate_nodes:
				duplicates = self.get_equivalent_elements(node, all_nodes)
				duplicate_nodes |= duplicates
				translate[node] = g.add_node(**node.data)
			else:
				duplicate = g.get_equivalent_nodes(node)
				translate[node] = duplicate.pop()
		# iterate over all the edges in both sets
		for edge in all_edges:
			if edge not in duplicate_edges:
				duplicates = self.get_equivalent_elements(edge, all_edges, flatten=True)
				duplicate_edges &= duplicates
				start = translate.get(edge.start, False)
				end = translate.get(edge.end, False)
				if start and end:
					g.add_edge(start, end, **edge.data)
		return g

	def get_connected_components(self):
		"""Gets all the connected components from the graph."""
		# set of all connected components
		connected = set((frozenset(),))
		# iterate over the nodes
		for node in self.nodes:
			discovered = frozenset(self.depth_first_traversal(node))
			add_this = True
			for component in connected:
				if discovered.issubset(component):
					add_this = False
					break
				elif discovered.issuperset(component):
					add_this = False
					connected.remove(component)
					connected.add(discovered)
					continue
			if add_this:
				connected.add(discovered)
		return connected

	# XXX does not work
	def minimum_spanning_tree(self, root, get_weight=lambda e: 1):
		"""Finds the minimum spanning tree of the graph rooted at root.

		Note that if the graph is not fully connected, this will only
		return the elements which are connected to root.

		The optional argument "get_weight" should be a callable
		that evaluates the weight for a given edge.
		"""
		# set the distances to all nodes except root as infinite
		inf = float("inf")
		distance_from_root = {n: inf for n in self.depth_first_traversal(root)}
		del distance_from_root[root]
		# get all the edges in the tree		
		pass
			
	def size(self):
		"""Reports the number of edges in the graph.

		Usage:
			>>> g = Graph()
			>>> n1, n2 = g.add_node(), g.add_node()
			>>> g.size()
			0
			>>> e = g.add_edge(n1, n2)
			>>> g.size()
			1
		"""
		return len(self.edges)

	def order(self):
		"""Reports the number of nodes in the graph.

		Usage:
			>>> g = Graph()
			>>> g.order()
			0
			>>> n = g.add_node()
			>>> g.order()
			1
		"""
		return len(self.nodes)
