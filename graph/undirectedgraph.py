#! /usr/bin/env python3.0

"""
undirectedgraph.py

Written by Geremy Condra

Licensed under GPLv3

Released 16 Feb 2009

This module provides a mixin that provides for
an undirected graph. Notice that it only
overrides Graph's EdgeContainer class.
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

import copy

from basegraph import Graph

class UndirectedEdgeContainer(Graph.EdgeContainer):

	def add_edge(self, edge):
		self.edges.add(edge)
		new_edge = copy.deepcopy(edge)
		new_edge.start, new_edge.end = edge.end, edge.start
		self.edges.add(new_edge)

	def remove_edge(self, edge):
		def recognizer(self, x):
			if x.start == edge.start:
				if x.end == edge.end:
					return True
			elif x.start == edge.end:
				if x.end == edge.start:
					return True
			return False 
		edges = super().get_matching_edges(recognizer)
		for found_edge in edges:
			super().remove_edge(found_edge)

	def __len__(self):
		return len(self.edges)/2
	
class UndirectedGraphMixin:
	EdgeContainer = UndirectedEdgeContainer

class UndirectedGraph(UndirectedGraphMixin, Graph):
	pass	
