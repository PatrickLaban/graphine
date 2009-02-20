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
from errors import EdgeInitializationError

class BaseGraphTest(unittest.TestCase):

	graph_type = Graph

	def setUp(self):
		self.nodes = {}
		self.edges = []
		self.graph = self.graph_type()
		self.nodes["A"] = self.graph.add_node(name="A")
		self.nodes["B"] = self.graph.add_node(name="B")
		self.nodes["C"] = self.graph.add_node(name="C")
		self.nodes["D"] = self.graph.add_node(name="D")
		self.nodes["E"] = self.graph.add_node(name="E")
		self.nodes["F"] = self.graph.add_node(name="F")
		self.nodes["G"] = self.graph.add_node(name="G")
		self.edges += [self.graph.add_edge(self.nodes["A"], self.nodes["B"])]
		self.edges += [self.graph.add_edge(self.nodes["B"], self.nodes["D"])]
		self.edges += [self.graph.add_edge(self.nodes["B"], self.nodes["F"])]
		self.edges += [self.graph.add_edge(self.nodes["F"], self.nodes["E"])]
		self.edges += [self.graph.add_edge(self.nodes["A"], self.nodes["C"])]
		self.edges += [self.graph.add_edge(self.nodes["C"], self.nodes["G"])]
		self.edges += [self.graph.add_edge(self.nodes["A"], self.nodes["E"])]
		self.node_container = self.graph.nodes
		self.edge_container = self.graph.edges
		self.node_set = self.node_container.nodes.copy()
		self.edge_set = self.edge_container.edges.copy()

	def testOrder(self):
		self.failUnless(self.graph.order() == 7)

	def testSize(self):
		self.failUnless(self.graph.size() == 7)

	def testDepthFirstTraversal(self):
		# the tricky part about this is that there is no concept of left-right ordering in this, since node ordering
		# is not preserved. 
		# We can therefore test only the preorder property universally
		positions = {node.name:pos for pos, node in enumerate(self.graph.depth_first_traversal(self.nodes["A"]))} 
		self.failUnless(positions["A"] < positions["B"])
		self.failUnless(positions["A"] < positions["C"])
		self.failUnless(positions["A"] < positions["E"])
		self.failUnless(positions["B"] < positions["D"])
		self.failUnless(positions["C"] < positions["G"])
		self.failUnless(positions["F"] > min(positions["B"], positions["E"]))

	def testBreadthFirstTraversal(self):
		# we want to test to ensure that A is visited first, then its children, and so on
		positions = {node.name:pos for pos, node in enumerate(self.graph.breadth_first_traversal(self.nodes["A"]))}
		self.failUnless(positions["A"] < min(positions["B"], positions["C"], positions["E"]))
		self.failUnless(max(positions["B"], positions["C"], positions["E"]) < min(positions["D"], positions["F"], positions["G"]))

	def testNodeContainerGetAllNodes(self):
		all_nodes = set(node for node in self.node_container.get_all_nodes())
		self.failUnlessEqual(self.node_set, all_nodes)

	def testNodeContainerGetMatchingNodes(self):
		recognizer = lambda x: x.name == "A"
		nodes_returned = list(self.node_container.get_matching_nodes(recognizer))
		self.failUnlessEqual([self.nodes["A"]], nodes_returned)

	def testNodeContainerAddNode(self):
		n = self.graph.Node()
		self.node_container.add_node(n)
		self.failUnlessEqual(self.node_container.nodes.difference(self.node_set), {n})

	def testNodeContainerRemoveNode(self):
		self.node_container.remove_node(self.nodes["A"])
		self.failUnlessEqual(self.node_set.difference(self.node_container.nodes), {self.nodes["A"]})

	def testEdgeContainerGetAllEdges(self):
		all_edges = set(edge for edge in self.edge_container.get_all_edges())
		self.failUnlessEqual(self.edge_set, all_edges)

	def testEdgeContainerGetMatchingEdges(self):
		recognizer = lambda x: x.start == self.nodes["A"]
		edges_returned = set(self.edge_container.get_matching_edges(recognizer))
		self.failUnlessEqual({self.edges[0], self.edges[4], self.edges[6]}, edges_returned)


class UndirectedGraphTest(BaseGraphTest):

	class UndirectedGraph(UndirectedGraphMixin, Graph):
		pass

	graph_type = UndirectedGraph


class AcyclicGraphTest(BaseGraphTest):

	class AcyclicGraph(AcyclicGraphMixin, Graph):
		pass

	graph_type = AcyclicGraph
		
if __name__ == "__main__":
	unittest.main()
