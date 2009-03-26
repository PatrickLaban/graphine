#! /usr/bin/env python3

"""
base.py

Written by Geremy Condra

Licensed under the GNU GPLv3

Released 25 Mar 2009

This module contains Graphine's base graph represenatation.
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


from collections import deque, defaultdict, namedtuple


class Graph(object):
	"""Base class for all Graph mixins"""

	def __init__(self, node_properties, edge_properties):
		"""base initializer"""
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
		else:
			# remove it from edge storage
			e = self.edges.pop(uid)
			# remove it from adjacency tracking
			self.adjacency_list[e.start].remove(e.end)
			# add it to the untracked uids
			self.unused_edge_uids.append(uid)
			# pass it back to the caller
			return e

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

	def get_node_uids(self):
		"""Iterates over all node uids"""
		for uid in self.nodes:
			yield uid

	def get_edge_uids(self):
		"""Iterates over all edge uids"""
		for uid in self.edges:
			yield uid

	def add_node(self, **kwargs):
		"""Adds a node to the current graph."""
		uid = self.get_node_uid()
		self.nodes[uid] = self.Node(**kwargs)
		return uid

	def add_edge(self, start, end, **kwargs):
		"""Adds an edge to the current graph."""
		uid = self.get_edge_uid()
		self.edges[uid] = self.Edge(start=start, end=end, **kwargs)
		self.adjacency_list[start].add(end)
		return uid

	def modify_node(self, uid, **kwargs):
		"""Modifies an existing node according to kwargs"""
		n = self[uid]
		n = n._replace(**kwargs)
		self[uid] = n
		return uid

	def modify_edge(self, uid, **kwargs):
		"""Modifies an existing edge according to kwargs"""
		e = self[uid]
		e = e._replace(**kwargs)
		self[uid] = e
		return uid

	def get_all_nodes(self):
		"""Iterates over all the nodes."""
		for node in self.nodes.values():
			yield node

	def get_all_edges(self):
		"""Iterates over all the edges."""
		for edge in self.edges.values():
			yield edge

	def get_nodes_by_properties(self, **kwargs):
		"""Convenience function to get nodes based on some properties."""
		for node in self.get_all_nodes():
			for k, v in kwargs.items():
				try:
					if not v == getattr(node, k):
						continue
				except:
					continue
				yield node

	def get_edges_by_properties(self, **kwargs):	
		"""Convenience function to get edges based on some properties."""
		for node in self.get_all_edges():
			for k, v in kwargs.items():
				try:
					if not v == getattr(node, k):
						continue
				except:
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
