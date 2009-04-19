#! /usr/bin/env python3.0

"""
base.py

Written by Geremy Condra

Licensed under the GNU GPLv3

Released 25 Mar 2009

This module contains the base GraphElement, Node, Edge,
and Graph implementations for Graphine, an easy-to-use,
easy-to-extend Graph library.

Graphs generated using this representation can have 
directed or undirected edges, the ability to represent 
loops and parallel edges, and can attach any hashable data 
to nodes and edges.

Interface summary
=================

To create a new Graph:

	>>> from graph.base import Graph
	>>> g = Graph()

To add nodes:

	>>> node_1 = g.add_node(name="bob")
	>>> node_2 = g.add_node(weight=5)
	>>> node_3 = g.add_node(color="red", visited=False)
	>>> node_4 = g.add_node()

To add edges:

	>>> edge_1 = g.add_edge(node_2, node_3)
	
Notice that edges can have properties as well:

	>>> edge_2 = g.add_edge(node_1, node_2, weight=5)
	>>> edge_3 = g.add_edge(node_3, node_1, stuff="things")

The most important keyword property on edges is the "is_directed"
keyword argument, which, when set to False, will cause the edge
created to be bidirectional. Its default value is True, ie,
edges are by default directed.

	>>> edge_4 = g.add_edge(node_1, node_4, is_directed=False)
	
To remove nodes:

	>>> g.remove_node(node_3)
	
And edges:

	>>> g.remove_edge(edge_4)

Note that removing one or more of an Edge's endpoints will
remove that edge as well.

Navigating Graphs
-----------------

In addition to storing your data, Nodes and Edges have
a few other special properties by default.

For Nodes, these properties are "incoming" and "outgoing", 
and they contain the incoming and outgoing edges attached
to that node. The "bidirectional" property is also there
in case you only want the edges which go both ways. An
additional property "edges" contains all of these elements.

For Edges, these properties are (again, by default) 
"start" and "end". Because edges can be bidirectional,
they also have an "is_directed" property, and provide
the convenience function "other_end", which takes a
node and, if possible, returns the opposite endpoint
incident to that edge.

The "key" attribute is also provided for use in
dictionaries and other settings where the essential
question is whether two graph elements are equivalent,
not whether they are the exact same element.

To get all the outgoing edges of a particular node:

	>>> n1.outgoing
	[Edge(weight=5)]

And to get the incoming edges:

	>>> n2.incoming
	[Edge(weight=5)]

The same sorts of things work for the properties
"bidirectional" and "edges".

You can use this to get all the nodes adjacent to
an interesting Node:

	>>> adjacent = [edge.end for edge in node_1.outgoing]

To get the degree of the given node:

	>>> degree = node1.degree
	
You can combine this with Edges' "start" and "end" properties
to navigate your graph, if you know how your data is related
structurally. For example, to get the oldest outgoing edge attached
to the oldest node attached to node_1, I could do the following:

	>>> interesting_node = node_1.outgoing[0].end.outgoing[0]

In addition to the "start" and "end" properties, you can use the 
"other_end" function, which takes a node and, if possible, returns
the edge's other end. If it cannot follow the edge to a point 
opposite the given node- for instance, because the edge is directed
the other way- it raises AttributeError.

	>>> endpoint = edge_1.other_end(node_2)
	>>> endpoint == node_3
	True
	>>> edge_1.other_end(node_3)
	...
	AttributeError: Edge() contains no endpoint opposite to Node()

You will frequently see "other_end" used in situations where it is
possible that the given edge could be either directed or undirected,
or where the orientation of a directed edge is unknown.

Of course, there are scenarios in which you don't know how to
navigate your graph, or need to find a starting point that isn't
easily determined based on a given element's properties. For that,
Graph supports Node and Edge iteration for the simple cases, and
traversals and walks for more complex behavior.

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

You can also get the elements which are equivalent to a
given one, for example to compare elements between graphs.
This is done using the "key" attribute and dictionary-style
access.

	>>> g[node_1.key]
	Node(weight=5)

This technique also works for edges.

In addition to the datawise and unordered views of graphs,
several methods for ordering based on structural properties
are provided. The most important of these are traversals
and walks.

Three traversals are provided by default- A*, depth first,
and breadth first. They are all guarenteed to only visit
a given node once, and visit nodes in a different order
based on how they are related structurally.

To do a depth first traversal:

	>>> for node in g.depth_first_traversal(node_1):
	>>> 	print(node)
	Node(name="bob")
	Node(weight=5)

Breadth first traversals are similar in usage, simply
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

	>>> for node in g.a_star_traversal(node_1, get_most_popular):
	>>> 	print(node)
	Node(weight=5)
	Node(name="bob")

The walks, in contrast to the traversals, can visit a node
or edge more than once. They are the most powerful structural
technique provided for navigating graphs, but are also probably
the hardest to use.

The walks are implemented as generators, with each step yielding
a set of nodes (for walk_nodes) or edges (for walk_edges) that
are potentially "next" in terms of adjacency. The application
should select one of those and use send() to send it back.

The trick is that generators must be fed None in their first
send(), which can complicate application logic. For example:

	>>> w = g.walk_nodes()
	>>> w.send(None)

Now we send it the node we're interested in walking away from:

	>>> candidates = w.send(node_1)
	>>> candidates
	{Node(weight=5)}

We get back the set of nodes to which we can walk. We should
select one and send it back:

	>>> w.send(candidates.pop())
	set()

To end the generator's run:

	>>> w.send(None)
	...
	StopIteration

walk_edges operates identically but accepts edges and yields
sets of edges.
	
Binary Graph Operations
-----------------------

Four basic operations are provided for the comparison
of graphs: 

	1. union (|), which creates a new graph containing all
	   the nodes and edges in either of its parents,

	2. intersection (&), which creates a new graph containing
	   all the nodes and edges in both of its parents,

	3. difference (-), which creates a new graph containing
	   all the nodes and edges in the first parent but
	   not in the second.

	4. merge (+), which creates a new graph with all the 
	   data-unique nodes from both parent graphs plus all 
	   their structurally and data unique edges.

For more information on the usage of these functions, consult their
individual docstrings.
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


from collections import deque, namedtuple, defaultdict
import heapq
import copy
from itertools import chain

class GraphElement:
	"""Base class for Nodes and Edges.

	A GraphElement.data property is provided to give easier
	access to all of the element's non-structural member
	variables. It returns a dictionary.

	It also provides an __repr__ member function to make
	easier work of analyzing your graphs.
	"""

	def __repr__(self):
		"""Pretty prints this element."""
		classname = type(self).__name__
		name = "name=%s, " % str(self.name)
		attrs = name + ''.join(("%s=%s, " % (k, v) for k, v in self.data.items()))
		attrs = attrs[:-2]
		return "%s(%s)" % (classname, attrs)

	def __lt__(self, other):
		"""Name-based comparison for sorting."""
		return self.name < other.name

	def __hash__(self):
		"""Returns the hash of this object's name."""
		return hash(self._name)

	def __eq__(self, other):
		"""Compares the two elements based on name."""
		if type(self) != type(other): return False
		return self.name == other.name

	def __ne__(self, other):
		"""Compares the two elements based on name."""
		return not self == other

	@property
	def name(self):
		"""Returns this object's name."""
		return self._name

	@property
	def data(self):
		"""Returns a dictionary representing the data values of this element.

		Note that elements which are marked private- ie, start with a single
		underscore- will not appear in this dictionary.
		"""
		return {k:v for k, v in self.__dict__.items() if not k.startswith("_")}


class Node(GraphElement):
	"""Base node representation.

	Nodes have seven properties:

	- incoming, which is a list of all edges coming into this node
	- outgoing, which is a list of all edges going away from this node
	- bidirectional, which is a list of all bidirectional edges incident
	  to this node
	- edges, which is a list of all edges with this node as an endpoint
	- degree, which is the number of edges incident to this node
	- data, which is a dictionary of all non-private (ie, user-defined)
	  attributes of this node
	- and name, which is a unique, non-None value optionally passed in
	  at instantiation time, and used for hashing comparisons. 

	In the event that a name is not passed in, the object's id will be used.
	"""

	def __init__(self, name=None, **kwargs):
		if name is not None: self._name = name
		else: self._name = id(self)
		self._incoming = []
		self._outgoing = []
		self._bidirectional = []
		for k, v in kwargs.items():
			setattr(self, k, v)

	def get_adjacent(self, outgoing=True, incoming=False):
		"""Returns a list of all adjacent nodes.

		The optional arguments outgoing and incoming indicate
		whether to include those edge sets in the search field.
		Their defaults are True and False, accordingly.

		If provided, outgoing and incoming should be booleans.
		"""
		adjacent = []
		seen = set()
		if outgoing:
			for edge in self._outgoing:
				if edge.end not in seen:
					adjacent.append(edge.end)
					seen.add(edge.end)
		if incoming:
			for edge in self._incoming:
				if edge.start not in seen:
					adjacent.append(edge.start)
					seen.add(edge.start)
		if outgoing or incoming:
			for edge in self._bidirectional:
				if edge.other_end(self) not in seen:
					adjacent.append(edge.other_end(self))
					seen.add(edge.other_end(self))
		return adjacent 

	@property
	def incoming(self):
		"""Returns a list of all the incoming edges for this node.

		Note that the list returned is a copy, so modifying it doesn't
		impact the structure of the graph.
		"""
		return copy.copy(self._incoming + self._bidirectional)

	@property
	def outgoing(self):
		"""Returns a list of all the outgoing edges for this node.

		Note that the list returned is a copy, so modifying it doesn't
		impact the structure of the graph.
		"""
		return copy.copy(self._outgoing + self._bidirectional)

	@property
	def bidirectional(self):
		"""Returns a list of all bidirectional edges for this node.

		Note that the list returned is a copy, so modifying it doesn't
		impact the structure of the graph.
		"""
		return copy.copy(self._bidirectional)

	@property
	def edges(self):
		"""Returns a list of all edges for this node.

		Note that the list returned is a copy, so modifying it doesn't
		impact the structure of the graph.
		"""
		# we have to ensure that all these elements are unique, since loops can be
		# both incoming and outgoing.
		return copy.copy(list(set(self._incoming + self._outgoing + self._bidirectional)))

	@property
	def degree(self):
		"""Returns the degree of this Node, ie, the number of edges."""
		return len(self.edges)


class Edge(GraphElement):
	"""Base edge representation.

	Edges have two properties, start and end, which are
	Node objects incident to the edge, as well as name
	and data, inhierited from GraphElement, which provide
	convenient access to the edge's application defined
	attributes.

	Because defining equality between edges in two different
	graphs is ambiguous, the unlink() function is provided.
	By default, this will produce an object suitable for
	membership comparisons based on the edge's data,
	direction, and the names of its endpoints.
	"""

	def __init__(self, start, end, name=None, is_directed=True, **kwargs):
		# remember, name must be hashable, therefore [] is invalid
		if name is not None: self._name = name
		else: self._name = id(self)
		self._start = start
		self._end = end
		self._directed = is_directed
		for k, v in kwargs.items():
			setattr(self, k, v)

	def other_end(self, starting_point):
		"""Returns the other end of the edge from the given point.

		If the point given is not an endpoint on this edge or the 
		endpoint on a directed edge, this raises AttributeError.
		"""
		if starting_point is self.start or starting_point is self.start.name:
			return self.end
		elif not self.is_directed:
			if starting_point is self.end or starting_point is self.end.name:
				return self.start
		raise AttributeError("%s has no endpoint opposite to %s" % (self, starting_point))

	def unlink(self):
		"""Allows a structural comparison between edges."""
		direction = ("direction", self.is_directed)
		start = ("start", self.start.name)
		end = ("end", self.end.name)
		name = ("name", self.name)
		return frozenset((direction, start, end, name))
		
	@property
	def start(self):
		"""Returns the starting point for this edge."""
		return self._start

	@property
	def end(self):
		"""Returns the ending point for this edge."""
		return self._end

	@property
	def is_directed(self):
		"""Returns whether this is a directed edge or not."""
		return self._directed


class Graph:

	"""A basic graph class, and base for all Graph mixins.

	In graph theoretic terms, this represents a bridge multigraph.
	This means that it supports both directed and undirected edges,
	loops, parallel and identical edges, and identical nodes.

	Because of its generality, it is suitable as a general-purpose
	Graph representation.
	"""

	Node = Node
	Edge = Edge

	def __init__(self):
		"""Base initializer for Graphs.

		Usage:
			>>> g = Graph()
		"""
		self._nodes = {}
		self._edges = {}

	#################################################################
	#			Operators				#
	#################################################################

	def __contains__(self, element):
		"""Returns True if the element is a member of the graph.

		Usage:
			>>> g = Graph()
			>>> n = g.add_node()
			>>> n in g
			True
		"""
		# if its a node
		if isinstance(element, self.Node):
			return element.name in self._nodes
		# if its an edge
		elif isinstance(element, self.Edge):
			return element.name in self._edges
		# if its a name
		else:
			return element in self._nodes or element in self._edges

	def __getitem__(self, name):
		"""Returns the element corresponding to the given name or the
		given element's name.

		Raises KeyError if it is not found.
		"""
		name = self.get_name(name)
		# get the element if it exists
		element = self._nodes.get(name, False)
		element = element or self._edges.get(name, False)
		if not element: raise KeyError("%s not in %s" % (name, self))
		return element

	def __and__(self, other):
		"""Maps the & operator to the intersection operation."""
		return self.intersection(other)

	def __or__(self, other):
		"""Maps the | operator to the union operation."""
		return self.union(other)

	def __sub__(self, other):
		"""Maps the - operator to the difference operation."""
		return self.difference(other)

	#################################################################
	#			Properties				#
	#################################################################

	@property
	def nodes(self):
		return self._nodes.values()

	@property
	def edges(self):
		return self._edges.values()

	#################################################################
	#		     Convenience Functions			#
	#################################################################

	def get_element(self, item):
		"""Takes an element or a name and returns an element.

		If no element corresponds to the given name, raises
		KeyError.
		"""
		if isinstance(item, GraphElement):
			element = self._edges.get(item.name, False)
			element = element or self._nodes.get(item.name, False)
			if not element: raise KeyError("%s not in %s" % (item, self))
			return element
		else:
			element = self._edges.get(item, False)
			element = element or self._nodes.get(item, False)
			if not element: raise KeyError("%s not in %s" % (item, self))
			return element

	def get_name(self, item):
		"""Takes an element or a name and returns a name.

		If no element corresponds to the given name, raises
		KeyError
		"""
		if isinstance(item, GraphElement):
			item = item.name
		else:
			item = item
		if item in self._nodes: return item
		if item in self._edges: return item
		raise KeyError("%s not in %s" % (item, self))

	#################################################################
	#		    Graph Construction Tools			#
	#################################################################

	def add_node(self, name=None, **kwargs):
		"""Adds a node with no edges to the current graph.

		The name argument, if given, should be hashable and
		unique in this graph.

		Usage:
			>>> g = Graph()
			>>> g.add_node(weight=5)
			Node(weight=5)
		"""
		node = self.Node(name, **kwargs)
		self._nodes[node._name] = node
		return node

	def add_edge(self, start, end, name=None, is_directed=True, **kwargs):
		"""Adds an edge to the current graph.

		The start and end arguments can be either nodes or node names.

		The name argument, if given, should be hashable and unique
		in this graph.

		The optional argument "is_directed" specifies whether
		the given edge should be directed or undirected.

		Usage:	
			>>> g = Graph()
			>>> n1, n2 = g.add_node(), g.add_node()
			>>> g.add_edge(n1, n2, weight=5)
			Edge(weight=5)			
		"""
		# get the start and end points
		start = self.get_element(start)
		end = self.get_element(end)
		# build the edge
		edge = self.Edge(start, end, name, is_directed=is_directed, **kwargs)
		self._edges[edge.name] = edge
		# take care of adjacency tracking
		if is_directed:
			start._outgoing.append(edge)
			end._incoming.append(edge)
		else:
			start._bidirectional.append(edge)
			# stops the edge from being added twice if it is an undirected
			# loop
			if start is not end:
				end._bidirectional.append(edge)
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
		# get the actual node if a name is passed in
		node = self.get_element(node)
		# remove it from adjacency tracking
		for edge in node.edges:
			self.remove_edge(edge)
		# remove it from storage
		n = self._nodes.pop(node.name)
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
		# get the actual edge if a name is passed
		edge = self.get_element(edge)
		# remove it from adjacency tracking
		start = edge.start
		end = edge.end
		if edge.is_directed:
			start._outgoing.remove(edge)
			end._incoming.remove(edge)
		else:
			start._bidirectional.remove(edge)
			# fix the undirected loop problem
			if start is not end:
				end._bidirectional.remove(edge)
		# remove it from storage
		e = self._edges.pop(edge.name)
		return e

	#########################################################################
	#			Graph Inspection Tools  			#
	#########################################################################

	def search_nodes(self, **kwargs):
		"""Convenience function to get nodes based on some properties.

		Usage:
			>>> g = Graph()
			>>> n1 = g.add_node(name="bob")
			>>> n2 = g.add_node(name="bill")
			>>> for node in g.search_nodes(name="bob"):
			... 	print(node)
			Node(name="bob")
		"""
		desired_properties = set(kwargs.items())
		for node in self.nodes:
			properties = set(node.data.items())
			if "name" in kwargs:
				properties.add(("name", node.name))
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
			... 	print(edge)
			Edge(weight=5)
		"""
		if "start" in kwargs:
			kwargs["start"] = self.get_element(kwargs["start"])
		if "end" in kwargs:
			kwargs["end"] = self.get_element(kwargs["end"])
		desired_properties = set(kwargs.items())
		for edge in self.edges:
			attrs = set(edge.data.items())
			if "name" in kwargs:
				attrs.add(("name", edge.name))
			if "start" in kwargs:
				attrs.add(("start", edge.start))
			if "end" in kwargs:
				attrs.add(("end", edge.end))
			if attrs.issuperset(desired_properties):
				yield edge

	def get_common_edges(self, n1, n2):
		"""Gets the common edges between the two nodes.

		Usage:
			>>> g = Graph()
			>>> n1 = g.add_node()
			>>> n2 = g.add_node()
			>>> e = g.add_edge(n1, n2, name="fluffy")
			>>> g.get_common_edges(n1, n2)
			{Edge(name="Fluffy")}
		"""
		# get the actual nodes if names are passed in
		n1 = self.get_element(n1)
		n2 = self.get_element(n2)
		n1_edges = set(n1.incoming + n1.outgoing)
		n2_edges = set(n2.incoming + n2.outgoing)
		return n1_edges & n2_edges

	def walk_nodes(self, start, reverse=False):
		"""Provides a generator for application-defined walks.

		The start argument can be either a name or a label.

		The optional reverse argument can be used to do a reverse
		walk, ie, only walking down incoming edges.

		Usage:
			>>> g = Graph()
			>>> n1 = g.add_node()
			>>> n2 = g.add_node()
			>>> e1 = g.add_edge(n1, n2)
			>>> w = g.walk_nodes()
			>>> for adjacent_nodes in w:
			>>> 	next_node = adjacent_nodes.pop()
			>>>	w.send(next_node)
		"""
		# make sure we have a real node
		start = self.get_element(start)
		# the actual generator function, wrapped for prettitude
		def walker():
			next = start
			while next:
				if not reverse: adjacent = next.get_adjacent()
				else: adjacent = next.get_adjacent(outgoing=False, incoming=True)
				next = yield(adjacent)
		# the wrapper
		w = walker()
		candidates = next(w)
		while 1:
			selection = (yield candidates)
			candidates = w.send(selection)
			yield

	def walk_edges(self, start):
		"""Provides a generator for application-defined walks.

		Usage is identical to walk_nodes, excepting only that it accepts,
		and yields, Edges in the place of Nodes.
		"""
		# make sure we have a real edge
		start = self.get_element(start)
		# the actual generator function
		def walker():
			next = start
			while next:
				incident = list(next.other_end(next.start).outgoing)
				next = yield(incident)
		# convenience wrapper
		w = walker()
		candidates = next(w)
		while 1:
			selection = (yield candidates)
			candidates = w.send(selection)
			yield

	def heuristic_walk(self, start, selector, reverse=False):
		"""Traverses the graph using selector as a selection filter on the adjacent nodes.

		The optional reverse argument allows you to do a reverse walk, ie, only finding
		adjacencies according to incoming edges rather than outgoing edges.

		Usage:
			>>> g = Graph()
			>>> g.add_node("A")
			>>> g.add_node("B")
			>>> g.add_edge("A", "B", "AB")
			>>> def selector(adjacent_nodes):
			...	return adjacent_nodes.pop()
			...
			>>> for node in g.heuristic_walk("A", selector):
			... 	print(node.name)
			B
		"""
		w = self.walk_nodes(start, reverse=reverse)
		for candidates in w:
			selection = selector(candidates)
			w.send(selection)
			yield selection
			
	def heuristic_traversal(self, root, selector):
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
		# handle the its-a-name case
		root = self.get_element(root)
		# stores nodes that are known to the algorithm but not yet visited
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
			adjacent = set(next.get_adjacent())
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
		for node in self.heuristic_traversal(root, lambda s: s.pop()):
			yield node
		
	def breadth_first_traversal(self, root):
		"""Traverses the graph by visiting a node, then each of its children, then their children.

		Usage:
			>>> g = Graph()
			>>> a, b = g.add_node(name="A"), g.add_node(name="B")
			>>> c, d = g.add_node(name="C"), g.add_node(name="D")
			>>> e1, e2 = g.add_edge(a, b), g.add_edge(a, c)
			>>> e3, e4 = g.add_edge(b, d), g.add_edge(c, d)
			>>> for node in g.breadth_first_traversal(a):
			>>> 	print(node)
			Node(name="A")
			Node(name="B")
			Node(name="C")
			Node(name="D")
		"""
		for node in self.heuristic_traversal(root, lambda s: s.pop(0)):
			yield node

	def get_connected_components(self):
		"""Gets all the connected components from the graph.

		Returns a list of sets of vertices.

		Usage:
			>>> g = Graph()
			>>> n1 = g.add_node(group=1)
			>>> n2 = g.add_node(group=1)
			>>> n3 = g.add_node(group=2)
			>>> e1 = g.add_edge(n1, n2)
			>>> g.get_connected_components()
			[{Node(group=1), Node(group=1)}, {Node(group=2)}]
		"""
		# set of all connected components
		connected = []
		# iterate over the nodes
		for node in self.nodes:
			# get all the nodes that are reachable from this node
			discovered = set(self.depth_first_traversal(node))
			add_this = True
			for component in connected:
				# if the newly discovered component is part of
				# an existing component
				if discovered.issubset(component):
					# don't add it
					add_this = False
					break
				# if the existing component is a part of the
				# newly discovered component
				elif discovered.issuperset(component):
					# don't add it
					add_this = False
					# but replace the old component with
					# the new one
					connected.remove(component)
					connected.append(discovered)
					continue
			# if this component was not a part of an existing
			# component or vice versa...
			if add_this:
				# add it to the components list
				connected.append(discovered)
		return connected

	def get_strongly_connected(self):
		"""Returns a list of all strongly connected components.

		Each SCC is expressed as a set of vertices.

		Usage is identical to get_connected_components.
		"""
		# list of all SCCs
		strongly_connected_components = []
		# iterate over all connected components
		for c in self.get_connected_components():
			# get an arbitrary node
			arbitrary = c.pop()
			# get all the nodes visitable from there
			visited = [node for node in self.depth_first_traversal(arbitrary)]
			# reverse the direction of the edges in the graph
			self.transpose()
			# while there are still elements which aren't reachable
			while visited:
				current_component = set()
				for node in self.depth_first_traversal(visited.pop(0)):
					current_component.add(node)
					try:
						visited.remove(node)
					except:
						pass
			strongly_connected_components.append(current_component)
			self.transpose()
		return strongly_connected_components

	def get_shortest_paths(self, source, get_weight=lambda e: 1):
		"""Finds the shortest path to all connected nodes from source.

		The optional get_weight argument should be a callable that
		accepts an edge and returns its weight.

		Returns a dictionary of node -> (path_length, [edges_traversed])
		mappings.

		Usage:
			>>> g = Graph()
			>>> n1 = g.add_node(name="A")
			>>> n2 = g.add_node(name="B")
			>>> n3 = g.add_node(name="C")
			>>> n4 = g.add_node(name="D")
			>>> e1 = g.add_edge(n1, n2, weight=10)
			>>> e2 = g.add_edge(n1, n4, weight=1)
			>>> e3 = g.add_edge(n2, n3, weight=1)
			>>> e4 = g.add_edge(n3, n4, weight=1)
			>>> d = g.get_shortest_paths(n1, get_weight=lambda e: e.weight)
			>>> d[n1]
			(0, [])
			>>> d[n2]
			(10, [Edge(weight=10)])
			>>> d[n3]
			(11, [Edge(weight=10), Edge(weight=1)])
			>>> d[n4]
			(1, [Edge(weight=1)])
		"""
		# handle the its-a-name case
		source = self.get_element(source)
		# create the paths table
		paths = defaultdict(lambda: (float("inf"), []))
		paths[source] = (0, [])
		# create the minimum distance heap
		unoptomized = [(0, source)]
		# main loop
		while unoptomized:
			# pop the minimum distanced node
			distance, current = heapq.heappop(unoptomized)
			# iterate over its outgoing edges
			for edge in current.outgoing:
				# get the old path to the endpoint
				old_weight, old_path = paths[edge.other_end(current)]
				# get the weight of this path to the edge's end
				weight, path = paths[current]
				weight += get_weight(edge)
				# if the new path is better than the old path
				if weight < old_weight:
					# relax it
					paths[edge.other_end(current)] = (weight, path + [edge])
					# and put it on the heap
					heapq.heappush(unoptomized, (weight, edge.other_end(current)))
		return paths
	
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

	#########################################################################
	#			Graph Rewriting Tools				#
	#########################################################################

	def move_edge(self, edge, start=None, end=None):
		"""Moves the edge, leaving its data intact.

		Does not reverse direction.
		"""
		# get the edge if its a name
		edge = self.get_element(edge)
		if edge.is_directed:
			edge.start._outgoing.remove(edge)
			edge.end._incoming.remove(edge)
		else:
			try:	# to fix the problem with undirected loops
				edge.start._bidirectional.remove(edge)
				edge.end._bidirectional.remove(edge)
			except:
				pass
		edge._start = start or edge.start
		edge._end = end or edge.end
		if edge.is_directed:
			edge.start._outgoing.append(edge)
			edge.end._incoming.append(edge)
		else:
			edge.start._bidirectional.append(edge)
			# fix the problem with undirected loops
			if start is not end:
				edge.end._bidirectional.append(edge)
		return edge

	def contract_edge(self, edge, node_data):
		"""Contracts the given edge, merging its endpoints.

		node_data should be a callable that returns a dictionary.
		That dictionary will be used to initialize the new node.

		There are two caveats about using this:

		1) The name passed back by node_data, if present, must
		   still be unique- and the old nodes can't be deleted
		   until after the new one is added.

		2) Note that if multiple edges exist between the two nodes,
		   this will still contract them!
		"""
		# get the edge if its a name
		edge = self.get_element(edge)
		# check to make sure that the given edge is the only edge between
		# it endpoints
		start = edge.start
		end = edge.end
		new_node = self.add_node(**node_data(start, end))
		# delete the given edge
		self.remove_edge(edge)
		# move all incoming edges
		for edge in start.incoming + end.incoming:
			self.move_edge(edge, end=new_node)
		# move all outgoing edges
		for edge in start.outgoing + end.outgoing:
			self.move_edge(edge, start=new_node)
		# delete the existing endpoints
		# remember, this may be a loop, so you may
		# only be able to remove one.
		try:
			self.remove_node(start)
			self.remove_node(end)
		except KeyError:
			pass
		return new_node

	def transpose(self):
		"""Reverses the directions on all edges in the current graph"""
		for e in self.edges:
			self.move_edge(e, start=e.end, end=e.start)
			
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
		for node in nodes:
			node = self.get_element(node)
			name = node.name
			data = node.data
			n = g.add_node(name, **data)
		for edge in self.edges:
			if edge.start in g:
				if edge.end in g:
					name = edge.name
					start = edge.start.name
					end = edge.end.name
					is_directed = edge.is_directed
					data = edge.data
					g.add_edge(start, end, name, **data)
		return g

	def edge_induce_subgraph(self, *edges):
		"""Similar to induce_subgraph but accepting edges rather than nodes."""
		# create the new graph
		g = type(self)()
		for edge in edges:
			edge = self.get_element(edge)
			# and add them if they don't already exist
			if edge.start not in g:
				g.add_node(edge.start.name, **edge.start.data)
			if edge.end not in g:
				g.add_node(edge.end.name, **edge.end.data)
		# iterate over the provided edges
		for edge in edges:
			# and add them, translating nodes as we go
			g.add_edge(edge.start.name, edge.end.name, edge.name, **edge.data)
		return g
			
	#########################################################################
	#			Graph Comparison Tools				#
	#########################################################################

	def union(self, other):
		"""Returns a new graph with all nodes and edges in either of its parents.

		Usage:
			>>> g1 = Graph()
			>>> g2 = Graph()
			>>> a = g1.add_node(1)
			>>> b = g1.add_node(3)
			>>> c = g1.add_node(5)
			>>> ab = g1.add_edge(a, b, 2)
			>>> bc = g1.add_edge(b, c, 4)
			>>> d = g2.add_node(3)
			>>> e = g2.add_node(5)
			>>> f = g2.add_node(7)
			>>> de = g2.add_edge(d, e, 4)
			>>> ef = g2.add_edge(e, f, 6)
			>>> g3 = g1 | g2
			>>> [node.value for node in g3.nodes]
			[1, 3, 5, 7]
			>>> [edge.value for edge in g3.edges]
			[2, 4, 6]
		"""
		# create the graph
		g = type(self)()
		# add our nodes
		for node in chain(self.nodes, other.nodes):
			g.add_node(node.name, **node.data)
		# and for edges
		for edge in chain(self.edges, other.edges):
			g.add_edge(edge.start.name, edge.end.name, edge.name, edge.is_directed, **node.data)
		return g

	def intersection(self, other):
		"""Returns a graph containing only the nodes and edges in both of its parents.

		Note that both endpoints must exist in the new graph for an edge to exist.

		Usage:
			>>> g1 = Graph()
			>>> g2 = Graph()
			>>> a = g1.add_node(value=1)
			>>> b = g1.add_node(value=3)
			>>> c = g1.add_node(value=5)
			>>> ab = g1.add_edge(a, b, value=2)
			>>> bc = g1.add_edge(b, c, value=4)
			>>> d = g2.add_node(value=3)
			>>> e = g2.add_node(value=5)
			>>> f = g2.add_node(value=7)
			>>> de = g2.add_edge(d, e, value=4)
			>>> ef = g2.add_edge(e, f, value=6)
			>>> g3 = g1 & g2
			>>> [node.value for node in g3.nodes]
			[3, 5]
			>>> [edge.value for edge in g3.edges]
			[4]
		"""
		# create the graph
		g = type(self)()
		# iterate through our nodes
		for node in self.nodes:
			if node in other:
				name = node.name
				data = node.data
				g.add_node(name, **data)
		# and theirs
		for node in other.nodes:
			if node in self:
				name = node.name
				data = node.data
				g.add_node(name, **data)
		# ...and our edges...
		for edge in self.edges:
			if edge in other:
				name = edge.name
				start = edge.start
				end = edge.end
				if start in g and end in g:
					is_directed = edge.is_directed
					data = edge.data
					g.add_edge(start.name, end.name, name, is_directed, **data)
		# ...and theirs
		for edge in other.edges:
			if edge in self:
				name = edge.name
				start = edge.start
				end = edge.end
				if start in g and end in g:
					is_directed = edge.is_directed
					data = edge.data
					g.add_edge(start.name, end.name, name, is_directed, **data)
		return g
	
	def difference(self, other):
		"""Return a graph composed of the nodes and edges not in the other.

		Usage:
			>>> g1 = Graph()
			>>> g2 = Graph()
			>>> a = g1.add_node(1)
			>>> b = g1.add_node(3)
			>>> c = g1.add_node(5)
			>>> ab = g1.add_edge(a, b, 2)
			>>> bc = g1.add_edge(b, c, 4)
			>>> d = g2.add_node(3)
			>>> e = g2.add_node(5)
			>>> f = g2.add_node(7)
			>>> de = g2.add_edge(d, e, 4)
			>>> ef = g2.add_edge(e, f, 6)
			>>> g3 = g1 & g2
			>>> [node.value for node in g3.nodes]
			[1]
			>>> [edge.value for edge in g3.edges]
			[]
		"""
		# create the graph
		g = type(self)()
		# create all the equivalent nodes
		for node in self.nodes:
			if node not in other:
				g.add_node(node.name, **node.data)
		# create all the equivalent edges
		for edge in self.edges:
			if edge not in other:
				if edge.start in g and edge.end in g:
					g.add_edge(edge.start, edge.end, edge.name, **edge.data)
		return g
