#! /usr/bin/env python3.0

"""
acyclicgraph.py

Written by Geremy Condra

Licensed under GPLv3

Released 16 Feb 2009

This module provides a mixin that provides for
an acyclic graph. Notice that it only
overrides Graph's add_edge method.
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

from basegraph import Graph
from errors import EdgeInitializationError

class AcyclicGraphMixin:
	def add_edge(self, start, end, *args, **kwargs):
		"""Adds the specified edge to the graph.

		Also performs a test to ensure that a cycle will not be formed."""
		if start in self.depth_first_traversal(end): raise EdgeInitializationError
		super().add_edge(start, end, *args, **kwargs)

class DirectedAcyclicGraph(AcyclicGraphMixin, Graph):
	pass
