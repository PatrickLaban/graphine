#! /usr/bin/env python3.0

"""
acyclicgraph.py

Written by Geremy Condra

Licensed under GPLv3

Released 16 Feb 2009

This module provides a mixin that provides for
an acyclic graph. Notice that it only
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

from basegraph import Graph, EdgeInitializationError

class AcyclicEdgeContainer(Graph.EdgeContainer):
	def add_edge(self, edge):
		start_points = set()
		end_points = set()
		edges = set()
		for edge in self.edges:
			start_points.add(edge.start)
			end_points.add(edge.end)
			edges.add(edge)
		sources = start_points.difference(end_points)
		while start_points:
			start = start_points.pop()
			for edge in super().get_matching_edges(lambda x: x.start == start):
				end = edge.end
				edges.remove(edge)
				if len(list(super().get_matching_edges(lambda x: x.end == end))) == 0:
					start_points.append(end)
		if edges:
			raise EdgeInitializationError
		super().add_edge(edge)

class AcyclicGraphMixin:
	EdgeContainer = AcyclicEdgeContainer 
