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
loops and parallel edges, and can attach arbitrary data 
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

To add edges:

	>>> edge_1 = g.add_edge(node_2, node_3)
	
Notice that edges can have properties as well:

	>>> edge_2 = g.add_edge(node_1, node_2, weight=5)
	>>> edge_3 = g.add_edge(node_3, node_1, stuff="things")
	
To remove nodes:

	>>> g.remove_node(node_3)
	
And edges:

	>>> g.remove_edge(edge_3)

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

And, if you're dealing with a graph containing undirected edges,
you can use the "other_end" function, which takes a node and,
if it leads from there to another node, returns that node.

	>>> endpoint = edge_1.other_end(node_2)
	>>> endpoint == node_3
	True
	>>> edge_1.other_end(node_3)
	...
	AttributeError: Edge() contains no endpoint opposite to Node()

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
optional "key" argument, which causes it to also compare
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


from collections import deque, namedtuple, defaultdict
import heapq
import copy

class GraphElement:
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

	@property
	def key(self):
		return hash(frozenset((k,v) for k, v in self.data.items()))


class Node(GraphElement):
	"""Base node representation.

	Nodes have two properties, incoming and outgoing, which are
	tuples of the edges which are incident to the node.

	Nodes also have the flatten function, which provides a view
	of the node suitable for comparison with nodes from other graphs.

	They also inheirit the data property, which provides dictionary
	access to all the non-private portions of the node.
	"""

	def __init__(self, incoming=None, outgoing=None, bidirectional=None, **kwargs):
		self._incoming = incoming or []
		self._outgoing = outgoing or []
		self._bidirectional = bidirectional or []
		for k, v in kwargs.items():
			setattr(self, k, v)

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
		return copy.copy(self._incoming + self._outgoing + self._bidirectional)

	@property
	def degree(self):
		return len(self.edges)

	@property
	def key(self):
		"""Returns a value suitable as a key in a dictionary."""
		attributes = tuple((k,v) for k, v in self.data.items())
		return frozenset(attributes)


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

	def __init__(self, start, end, is_directed=True, **kwargs):
		self._start = start
		self._end = end
		self._directed = is_directed
		for k, v in kwargs.items():
			setattr(self, k, v)

	def other_end(self, starting_point):
		"""Returns the other end of the edge from the given point."""
		if starting_point is self.start:
			return self.end
		elif not self.is_directed:
			if starting_point is self.end:
				return self.start
		raise AttributeError("%s has no endpoint opposite to %s" % (self, starting_point))

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

	@property
	def key(self):
		"""Returns a value suitable as a key in a dictionary."""
		endpoints = (("start", self.start.key), ("end", self.end.key))
		direction = (("is_directed", self.is_directed),)
		attributes = tuple((k,v) for k, v in self.data.items())
		return frozenset(endpoints + direction + attributes)


class Graph:

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
		if isinstance(element, self.Node):
			return element in self.nodes
		else:
			return element in self.edges

	def __getitem__(self, key):
		"""Returns the item corresponding to the given key.

		Raises KeyError if it is not found.
		"""
		d = {n.key: n for n in self.nodes + self.edges}
		return d[key]

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

	#################################################################
	#		    Graph Construction Tools			#
	#################################################################

	def add_node(self, **kwargs):
		"""Adds a node with no edges to the current graph.

		Usage:
			>>> g = Graph()
			>>> g.add_node(weight=5)
			Node(weight=5)
		"""
		node = self.Node(**kwargs)
		self.nodes.append(node)
		return node

	def add_edge(self, start, end, is_directed=True, **kwargs):
		"""Adds an edge to the current graph.

		The optional argument "is_directed" specifies whether
		the given edge should be directed or undirected.

		Usage:	
			>>> g = Graph()
			>>> n1, n2 = g.add_node(), g.add_node()
			>>> g.add_edge(n1, n2, weight=5)
			Edge(weight=5)			
		"""
		# build the edge
		edge = self.Edge(start, end, is_directed=is_directed, **kwargs)
		self.edges.append(edge)
		# take care of adjacency tracking
		if is_directed:
			start._outgoing.append(edge)
			end._incoming.append(edge)
		else:
			start._bidirectional.append(edge)
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
		# remove it from adjacency tracking
		for edge in node.edges:
			self.edges.remove(edge)
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
		if edge.is_directed:
			start._outgoing.remove(edge)
			end._incoming.remove(edge)
		else:
			start._bidirectional.remove(edge)
			end._bidirectional.remove(edge)
		# remove it from storage
		e = self.edges.remove(edge)
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
		desired_properties = set(kwargs.items())
		for edge in self.edges:
			attrs = set(edge.data.items())
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
			>>> 
		"""
		n1_edges = set(n1.incoming + n1.outgoing)
		n2_edges = set(n2.incoming + n2.outgoing)
		return n1_edges & n2_edges

	def walk_nodes(self, next):
		"""Provides a generator for application-defined walks."""
		while next:
			adjacent = {edge.other_end(next) for edge in next.outgoing}
			next = (yield adjacent)

	def walk_edges(self, next):
		"""Provides a generator for application-defined walks."""
		while next:
			incident = set(next.other_end(next.start).outgoing)
			next = (yield incident)

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
			adjacent = {edge.other_end(next) for edge in next.outgoing}
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
			[{Node(group=1), Node(group=1)}, {Node(group=2}]
		"""
		# set of all connected components
		connected = [set()]
		# iterate over the nodes
		for node in self.nodes:
			discovered = set(self.depth_first_traversal(node))
			add_this = True
			for component in connected:
				if discovered.issubset(component):
					add_this = False
					break
				elif discovered.issuperset(component):
					add_this = False
					connected.remove(component)
					connected.append(discovered)
					continue
			if add_this:
				connected.append(discovered)
		return connected

	def get_strongly_connected(self):
		"""Returns a list of all strongly connected components.

		Each SCC is expressed as a set of vertices.

		Usage is identical to get_connected_components.
		"""
		strongly_connected_components = []
		for c in self.get_connected_components():
			arbitrary = c.pop()
			visited = [node for node in self.depth_first_traversal(arbitrary)]
			self.transpose()
			current_component = set()
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

		Returns a dictionary of node -> (path_length, [nodes_traversed])
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
			>>> g.get_shortest_paths(n1, get_weight=lambda e: e.weight)[n4]
			(1, [Node(name="D")])
		"""
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
		"""Moves the edge, leaving its data intact."""
		if edge.is_directed:
			edge.start._outgoing.remove(edge)
			edge.end._incoming.remove(edge)
		else:
			edge.start._bidirectional.remove(edge)
			edge.end._bidirectional.remove(edge)
		edge._start = start or edge.start
		edge._end = end or edge.end
		if edge.is_directed:
			edge.start._outgoing.append(edge)
			edge.end._incoming.append(edge)
		else:
			edge.start._bidirectional.append(edge)
			edge.end._bidirectional.append(edge)
		return edge

	def contract_edge(self, edge, node_data):
		"""Contracts the given edge, calling node_data on its endpoints.

		node_data should return a dictionary that will be used to initialize
		the new node.
		"""
		# check to make sure that the given edge is the only edge between
		# it endpoints
		start = edge.start
		end = edge.end
		if self.get_common_edges(start, end) != {edge}:
			raise
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
		self.remove_node(start)
		self.remove_node(end)
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

	def edge_induce_subgraph(self, *edges):
		"""Similar to induce_subgraph but accepting edges rather than nodes."""
		# create the new graph
		g = type(self)()
		# get all common nodes
		nodes = {}
		for edge in edges:
			# and add them if they don't already exist
			if edge.start not in nodes:
				nodes[edge.start] = g.add_node(**edge.start.data)
			if edge.end not in nodes:
				nodes[edge.end] = g.add_node(**edge.end.data)
		# iterate over the provided edges
		for edge in edges:
			# and add them, translating nodes as we go
			g.add_edge(nodes[edge.start], nodes[edge.end], **edge.data)
		return g
			
	#########################################################################
	#			Graph Comparison Tools				#
	#########################################################################

	def get_equivalent_elements(self, other):
		"""Returns a dictionary of element -> equivalentce set mappings."""
		equivalent_nodes = {}
		equivalent_edges = {}
		for element in self.nodes:
			equivalent_nodes[element.key] = set()
		for element in self.edges:
			equivalent_edges[element.key] = set()
		for element in other.nodes:
			k = element.key
			if k in equivalent_nodes:
				equivalent_nodes[k].add(element)
		for element in other.edges:
			k = element.key
			attrs = dict(k)
			if k in equivalent_edges:
				equivalent_edges[k].add(element)
		return equivalent_nodes, equivalent_edges

	def union(self, other):
		"""Returns a new graph with all nodes and edges in either of its parents."""
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
		# get the equivalent elements
		equivalent_nodes, equivalent_edges = self.get_equivalent_elements(other)
		# create the translation tables
		translator = {}
		# create all the equivalent nodes
		for k, v in equivalent_nodes.items():
			if v:
				translator[k] = g.add_node(**dict(k))
		# create all the equivalent edges
		for k, v in equivalent_edges.items():
			if v:
				attributes = dict(k)
				start = translator.get(attributes.pop("start"), False)
				end = translator.get(attributes.pop("end"), False)
				if start and end:
					g.add_edge(start, end, **attributes)
		return g
	
	def difference(self, other):
		"""Return a graph composed of the nodes and edges not in the other."""
		# create the graph
		g = type(self)()
		# get the equivalent elements
		equivalent_nodes, equivalent_edges = self.get_equivalent_elements(other)
		# create the translation tables
		translator = {}
		# create all the equivalent nodes
		for k, v in equivalent_nodes.items():
			if not v:
				translator[k] = g.add_node(**dict(k))
		# create all the equivalent edges
		for k, v in equivalent_edges.items():
			if not v:
				attributes = dict(k)
				start = translator.get(attributes.pop("start"), False)
				end = translator.get(attributes.pop("end"), False)
				if start and end:
					g.add_edge(start, end, **attributes)
		return g

	def merge(self, other):
		"""Returns a new graph with its nodes and edges merged by data equality."""
		# create the new graph
		g = type(self)()
		# create the translation table
		translator = {}
		# get equivalent elements
		my_nodes, my_edges = self.get_equivalent_elements(other)
		other_nodes, other_edges = other.get_equivalent_elements(self)
		equivalent_nodes = {}
		equivalent_edges = {}
		for k, v in my_nodes.items():
			equivalent_nodes.setdefault(k, set()).union(v)
		for k, v in other_nodes.items():
			equivalent_nodes.setdefault(k, set()).union(v)
		for k, v in my_edges.items():
			equivalent_edges.setdefault(k, set()).union(v)
		for k, v in other_edges.items():
			equivalent_edges.setdefault(k, set()).union(v)
		# add all the equivalent nodes
		for node in equivalent_nodes:
			translator[node] = g.add_node(**dict(node))
		# add all the equivalent edges
		for edge in equivalent_edges:
			attributes = dict(edge)
			start = translator[attributes.pop("start")]
			end = translator[attributes.pop("end")]
			g.add_edge(start, end, **attributes)
		return g
