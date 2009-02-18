#! /usr/bin/env python3.0

"""
graph_test.py

Written by Geremy Condra

Licensed under GPLv3

Released 17 Feb 2009

This contains all the test data for Graphine.
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

import unittest

from basegraph import Graph
from undirectedgraph import UndirectedGraphMixin
from acyclicgraph import AcyclicGraphMixin

class BaseGraphTest(unittest.TestCase):

	def setUp(self):
		self.graph = Graph()
		a = self.graph.add_node(name="A")
		b = self.graph.add_node(name="B")
		c = self.graph.add_node(name="C")
		d = self.graph.add_node(name="D")
		e = self.graph.add_node(name="E")
		f = self.graph.add_node(name="F")
		g = self.graph.add_node(name="G")
		self.graph.add_edge(a, b)
		self.graph.add_edge(b, d)
		self.graph.add_edge(b, f)
		self.graph.add_edge(f, e)
		self.graph.add_edge(a, c)
		self.graph.add_edge(c, g)
		self.graph.add_edge(a, e)
		self.start = a

	def testDepthFirstTraversal(self):
		self.assertEqual([node.name for node in self.graph.depth_first_traversal(self.start)], ["A", "B", "D", "F", "E", "C", "G"])

	def testBreadthFirstTraversal(self):
		self.assertEqual([node.name for node in self.graph.breadth_first_traversal(self.start)], ["A", "B", "C", "E", "D", "F", "G"])

class UndirectedGraphTest(unittest.TestCase):

	def setUp(self):
		class UndirectedGraph(UndirectedGraphMixin, Graph):
			pass

		self.graph = UndirectedGraph()
		a = self.graph.add_node(name="A")
		b = self.graph.add_node(name="B")
		c = self.graph.add_node(name="C")
		d = self.graph.add_node(name="D")
		e = self.graph.add_node(name="E")
		f = self.graph.add_node(name="F")
		g = self.graph.add_node(name="G")
		self.graph.add_edge(a, b)
		self.graph.add_edge(b, d)
		self.graph.add_edge(b, f)
		self.graph.add_edge(f, e)
		self.graph.add_edge(a, c)
		self.graph.add_edge(c, g)
		self.graph.add_edge(a, e)
		self.start = a

	def testDepthFirstTraversal(self):
		self.assertEqual([node.name for node in self.graph.depth_first_traversal(self.start)], ["A", "B", "D", "F", "E", "C", "G"])

	def testBreadthFirstTraversal(self):
		self.assertEqual([node.name for node in self.graph.breadth_first_traversal(self.start)], ["A", "B", "C", "E", "D", "F", "G"])

class AcyclicGraphTest(unittest.TestCase):
	
	def testCreation(self):
		class AcyclicGraph(AcyclicGraphMixin, Graph):
			pass

		self.graph = AcyclicGraph()
		a = self.graph.add_node(name="A")
		b = self.graph.add_node(name="B")
		c = self.graph.add_node(name="C")
		d = self.graph.add_node(name="D")
		e = self.graph.add_node(name="E")
		f = self.graph.add_node(name="F")
		g = self.graph.add_node(name="G")
		self.graph.add_edge(a, b)
		self.graph.add_edge(a, c)
		self.graph.add_edge(e, a)
		self.graph.add_edge(b, d)
		self.graph.add_edge(b, f)
		self.graph.add_edge(c, g)
		self.graph.add_edge(f, e)
		self.start = a

		
if __name__ == "__main__":
	unittest.main()
