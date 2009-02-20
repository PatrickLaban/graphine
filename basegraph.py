#! /usr/bin/env python3

"""
basegraph.py

Written by Geremy Condra

Licensed under the GNU GPLv3

Released 15 Feb 2009

This module contains Graphine's base hypergraph represenatation.
"""

# Copyright (C) 2009 Geremy Condra and OpenMigration, LLC
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

import errors

class Graph:
	"""Base class for all Graph mixins"""

	class Node:
		"""Basic node type.

		The base node accepts arbitrary keyword arguments to permit multiple IDRs."""

		def __init__(self, *args, **kwargs):
			try:
				for key, value in kwargs.items():
					self.__dict__[key] = value
			except Exception as error:
				raise NodeInitializationError from error

	class Edge:
		"""Basic edge type.

		The base edge accepts arbitrary keyword arguments to permit multiple IDRs."""

		def __init__(self, start, end, *args, **kwargs):
			try:
				self.start = start
				self.end = end
				for key, value in kwargs.items():
					self.__dict__[key] = value
			except Exception as error:
				raise EdgeInitializationError from error

	class NodeContainer:
		"""Basic container type for Node objects."""

		def __init__(self):
			"""Sets the internal backing store."""
			try:
				self.nodes = []
			except Exception as error:
				raise ContainerInitializationError from error

		def get_all_nodes(self):
			"""Gets all the nodes in the backing data store.

			Returns an iterator over the set of all nodes"""
			try:
				for node in self.nodes:
					yield node
			except Exception as error:
				raise ContainerOperationError from error
			raise StopIteration

		def get_matching_nodes(self, recognizer):
			"""Filters nodes in the data store against the recognizer.

			Returns an iterator."""
			try:
				for node in self.get_all_nodes():
					if recognizer(node):
						yield node
			except Exception as error:
				raise ContainerOperationError from error

		def get_nodes_by_properties(self, mappings):
			"""Convenience function to iterate over nodes matching the desired property:value mappings."""
			try:
				def recognizer(x):
					for property, value in mappings.items():
						if getattr(x, property) != value:
							return False
					return True
				for node in self.get_matching_nodes(recognizer):
					yield node
			except Exception as error:
				raise ContainerOperationError from error

		def add_node(self, node):
			"""Inserts the given node into the data store."""
			try:
				self.nodes.append(node)
			except Exception as error:
				raise ContainerOperationError from error

		def remove_node(self, node):
			"""Removes the given node from the data store."""
			try:
				self.nodes.remove(node)
			except Exception as error:
				raise ContainerOperationError from error

		def __len__(self):
			"""Returns the size of the data store"""
			return len(self.nodes)

	class EdgeContainer:
		"""Basic container type for Edge objects."""
	
		def __init__(self):
			"""Backing store is a list."""
			try:
				self.edges = []
			except Exception as error:
				raise ContainerInitializationError from error

		def get_all_edges(self):
			"""Gets all the edges in the data store.

			Returns an iterator"""
			try:
				for edge in self.edges:
					yield edge
			except Exception as error:
				raise ContainerOperationError from error

		def get_matching_edges(self, recognizer):
			"""Filters the data store against the recognizer.

			The recognizer should always return a boolean."""
			try:
				for edge in self.edges:
					if recognizer(edge):
						yield edge
			except Exception as error:
				raise ContainerOperationError from error

		def get_edges_by_properties(self, mappings):
			"""Convenience function to yield edges satisfying the property:value mappings"""
			try:
				def recognizer(x):
					for property, value in mappings.items():
						if getattr(x, property) != value:
							return False
					return True
				for edge in self.get_matching_edges(recognizer):
					yield edge
			except Exception as error:
				raise ContainerOperationError from error

		def add_edge(self, edge):
			"""Inserts the edge into the data store."""
			try:
				self.edges.append(edge)
			except Exception as error:
				raise ContainerOperationError from error

		def remove_edge(self, edge):
			"""Removes the edge from the data store."""
			try:
				self.edges.remove(edge)
			except Exception as error:
				raise ContainerOperationError from error

		def __len__(self):
			"""Return the size of the data store"""
			return len(self.edges)

	def __init__(self):
		"""base initializer"""
		try:
			self.nodes = self.NodeContainer()
			self.edges = self.EdgeContainer()
		except Exception as error:
			raise GraphInitializationError from error

	def add_node(self, *args, **kwargs):
		"""Adds a node to the current graph.

		All arguments are passed to its constructor."""
		try:
			new_node = self.Node(*args, **kwargs)
			self.nodes.add_node(new_node)
			return new_node
		except Exception as error:
			raise GraphOperationError from error

	def get_all_nodes(self):
		"""Iterates over all the nodes."""
		try:
			for node in self.nodes.get_all_nodes():
				yield node
		except Exception as error:
			raise GraphOperationError from error

	def get_matching_nodes(self, recognizer):
		"""Toplevel access to the get_matching_nodes function in the node container.

		The recognizer should return True on a match and False on non-match."""
		try:
			for node in self.nodes.get_matching_nodes(recognizer):
				yield node	
		except Exception as error:
			raise GraphOperationError from error

	def get_nodes_by_properties(self, mappings):
		"""Convenience function to get nodes based on some properties."""
		try:
			for node in self.get_nodes_by_properties(mappings):
				yield node
		except Exception as error:
			raise GraphOperationError from error

	def get_nodes_by_property(self, property, value):
		"""Convenience function to get nodes based on some identifier."""
		try:
			for node in self.get_nodes_by_properties({property:value}):
				yield node
		except Exception as error:
			raise GraphOperationError from error

	def get_adjacent_nodes(self, node):
		"""Convenience function to get nodes based on adjacency"""
		try:
			yield node
			for edge in self.get_edges_by_property("start", node):
				yield edge.end
		except Exception as error:
			raise GraphOperationError from error

	def remove_node(self, node):
		"""Removes a node from the current graph.

		Requires the node itself."""
		try:
			self.nodes.remove_node(node)
		except Exception as error:
			raise GraphOperationError from error

	def add_edge(self, start, end, *args, **kwargs):
		"""Adds an edge to the current graph.

		The properties start and end are mandatory, but others are likely to occur"""
		try:
			new_edge = self.Edge(start, end, *args, **kwargs)
			self.edges.add_edge(new_edge)
			return new_edge
		except Exception as error:
			raise GraphOperationError from error

	def get_all_edges(self):
		"""Iterates over the edges of the graph"""
		try:
			for edge in self.edges.get_all_edges():
				yield edge
		except Exception as error:
			raise GraphOperationError from error

	def get_matching_edges(self, recognizer):
		"""Filters the edge list against the recognizer.

		The recognizer should return True on a match and False on a non-match"""
		try:
			for edge in self.edges.get_matching_edges(recognizer):
				yield edge
		except Exception as error:
			raise GraphOperationError from error

	def get_edges_by_properties(self, mappings):
		"""Convenience function to get the matching edges"""
		try:
			for edge in self.edges.get_edges_by_properties(mappings):
				yield edge
		except Exception as error:
			raise GraphOperationError from error

	def get_edges_by_property(self, property, value):
		"""Convenience function to get edges based on some property."""
		try:
			for edge in self.edges.get_edges_by_properties({property:value}):
				yield edge
		except Exception as error:
			raise GraphOperationError from error

	def remove_edge(self, edge):
		"""Removes the given edge from the current graph."""
		try:
			self.edges.remove_edge(edge)
		except Exception as error:
			raise GraphOperationError from error

	def depth_first_traversal(self, root, visited=None):
		"""Traverses the graph by visiting a node, then a child of that node, and so on."""
		try:
			if visited == None:
				visited = []
			for node in self.get_adjacent_nodes(root):
				if node not in visited:
					yield node
					visited.append(node)
					for child_node in self.depth_first_traversal(node, visited):
						yield child_node
		except Exception as error:
			raise GraphOperationError from error

	def breadth_first_traversal(self, root):
		"""Traverses the graph by visiting a node, then each of its children, then their children"""
		try:
			not_yet_visited = [root]
			visited = []
			while len(not_yet_visited):
				node = not_yet_visited.pop(0)
				visited.append(node)
				yield node
				for child in self.get_adjacent_nodes(node):
					if child not in not_yet_visited and child not in visited:
						not_yet_visited.append(child)
		except Exception as error:
			raise GraphOperationError from error

	def size(self):
		"""Reports the number of edges in the graph"""
		return len(self.edges)

	def order(self):
		"""Reports the number of nodes in the graph"""
		return len(self.nodes)
				
			
