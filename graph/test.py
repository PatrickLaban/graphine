#! /usr/bin/env python3.0

"""
test.py

Written by Geremy Condra and Patrick Laban

Licensed under GPLv3

Released 17 Feb 2009

This contains all the test data for Graphine.
"""

# Copyright (C) 2009 Geremy Condra and Patrick Laban
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
import timeit
from base import Graph

class NodeCreationTest(unittest.TestCase):

	def setUp(self):
		# WARNING: g = Graph() & g.add_node() MUST work to perform tests
		self.g = Graph()
		self.jimmy = self.g.add_node(city="New York")
		self.ted = self.g.add_node(city="Atlanta")
		self.dan = self.g.add_node(city="Seattle")
		self.paul = self.g.add_node(city="Austin")

	def testData(self):
		""" test node.data against set values """
		self.failUnlessEqual(self.jimmy.data, {"city":"New York"})
		self.failUnlessEqual(self.ted.data, {"city":"Atlanta"})
		self.failUnlessEqual(self.paul.data, {"city":"Austin"})

	def testKey(self):
		""" test node.key against set values """
		self.failUnlessEqual(self.jimmy.key, frozenset({("city", "New York")}))
		self.failUnlessEqual(self.ted.key, frozenset({("city", "Atlanta")}))
		self.failUnlessEqual(self.dan.key, frozenset({("city", "Seattle")}))
		self.failUnlessEqual(self.paul.key, frozenset({("city", "Austin")}))

	def testEquality(self):
		""" test for equality between nodes """
		snowflake = self.g.add_node(city="Austin")
		self.failIfEqual(self.dan, snowflake)
		self.failUnlessEqual(self.paul.data, snowflake.data)
		self.failUnlessEqual(self.paul.key, snowflake.key)
		self.failUnlessEqual(self.paul.city, snowflake.city)

	def testOrder(self):
		""" compare order to known number of nodes """
		self.failUnlessEqual(self.g.order(), 4)
		temp_node = self.g.add_node()
		self.failUnlessEqual(self.g.order(), 5)
		self.g.remove_node(temp_node)
		self.failUnlessEqual(self.g.order(), 4)
	"""
	def testCreationFail(self):
		# test node creation fail points
		self.assertRaises(TypeError, self.g.add_node())
	"""

class EdgeCreationTest(unittest.TestCase):

	def setUp(self):
		self.g = Graph()
		g = self.g
		# make some nodes
		self.jimmy = g.add_node(city="New York")
		self.ted = g.add_node(city="Atlanta")
		self.dan = g.add_node(city="Seattle")
		self.paul = g.add_node(city="Austin")
		self.zeke = g.add_node(city="LA")
		self.kurt = g.add_node(city="Chicago")
		# try not to error out
		self.j_to_t = g.add_edge(self.jimmy, self.ted, distance=850)
		self.t_to_d = g.add_edge(self.ted, self.dan, distance=2150)
		self.d_to_p = g.add_edge(self.dan, self.paul, distance=2850)
		# for directional tests
		self.z_to_k = g.add_edge(self.zeke, self.kurt, distance=1300, is_directed=False)

	def testAdjacency(self):
		# ensure adjacency list is correct
		self.failUnlessEqual(self.jimmy.incoming, [])
		self.failUnlessEqual(self.jimmy.outgoing, [self.j_to_t])
		self.failUnlessEqual(self.ted.incoming, [self.j_to_t])
		self.failUnlessEqual(self.ted.outgoing, [self.t_to_d])
		self.failUnlessEqual(self.ted.bidirectional, [])
		self.failUnlessEqual(self.dan.incoming, [self.t_to_d])
		self.failUnlessEqual(self.dan.outgoing, [self.d_to_p])
		self.failUnlessEqual(self.paul.incoming, [self.d_to_p])
		self.failUnlessEqual(self.zeke.incoming, [self.z_to_k])
		self.failUnlessEqual(self.zeke.outgoing, [self.z_to_k])
		self.failUnlessEqual(self.zeke.bidirectional, [self.z_to_k])
		self.failUnlessEqual(self.kurt.incoming, [self.z_to_k])
		self.failUnlessEqual(self.kurt.outgoing, [self.z_to_k])
		self.failUnlessEqual(self.kurt.bidirectional, [self.z_to_k])
		self.failUnlessEqual(self.paul.outgoing, [])

	def testDeletion(self):
		# and after deletion
		self.g.remove_edge(self.t_to_d)
		self.failUnlessEqual(self.ted.outgoing, [])
		self.failUnlessEqual(self.dan.incoming, [])
		new_trip = self.g.add_edge(self.ted, self.dan, distance=850)
		self.failUnlessEqual(self.ted.outgoing, [new_trip])
		self.failUnlessEqual(self.dan.incoming, [new_trip])

	def testEquivalence(self):
		# equivalence test
		new_trip = self.g.add_edge(self.ted, self.dan, distance=850)
		lame_trip = self.g.add_edge(self.jimmy, self.ted, distance=850)
		self.failUnlessEqual(new_trip.data, lame_trip.data)
		self.failIfEqual(new_trip.key, lame_trip.key)

	def testEdgeProperties(self):
		# ensure that the edges properties are being set properly
		self.failUnlessEqual(self.t_to_d.data, {"distance": 2150})
		self.failUnlessEqual(self.d_to_p.data, {"distance": 2850})
		self.failUnlessEqual(self.z_to_k.data, {"distance": 1300})

	def testSize(self):
		# make sure that the change is reflected in the graph's size
		self.failUnlessEqual(self.g.size(), 4)

	def testBidirection(self):
		# test to ensure that there is now a bidirectional link
		self.failUnlessEqual(self.zeke.outgoing[-1].other_end(self.zeke).city, "Chicago")
		self.failUnlessEqual(self.kurt.outgoing[-1].other_end(self.kurt).city, "LA")


class GraphPropertiesTest(unittest.TestCase):

	def setUp(self):
		self.g = Graph()
		self.n1 = self.g.add_node(name="Geremy")
		self.n2 = self.g.add_node(name="Bob")
		self.n3 = self.g.add_node(name="Bill")
		self.e1 = self.g.add_edge(self.n1, self.n2)
		self.e2 = self.g.add_edge(self.n2, self.n3)
		self.g.remove_node(self.n1)

	def testIn(self):
		self.failUnlessEqual(self.n1 in self.g, False)
		self.failUnlessEqual(self.n2 in self.g, True)
		self.failUnlessEqual(self.e1 in self.g, False)
		self.failUnlessEqual(self.e2 in self.g, True)

	def testGetItem(self):
		self.failUnlessEqual(self.g[self.n2.key], self.n2)
		self.failUnlessEqual(self.g[self.e2.key], self.e2)
		self.failUnlessRaises(KeyError, lambda: self.g[self.e1.key])

	def testOrder(self):
		self.failUnlessEqual(self.g.order(), 2)

	def testSize(self):
		self.failUnlessEqual(self.g.size(), 1)


class GraphSearchTest(unittest.TestCase):

	def setUp(self):
		self.g = Graph()
		self.n1 = self.g.add_node(name="Geremy")
		self.n2 = self.g.add_node(name="Bob")
		self.n3 = self.g.add_node(name="Bill")
		self.n4 = self.g.add_node(name="Bill")
		self.e1 = self.g.add_edge(self.n1, self.n2)
		self.e2 = self.g.add_edge(self.n2, self.n3)
		self.e3 = self.g.add_edge(self.n4, self.n3, weight=5)
		self.g.remove_node(self.n1)

	def testNodeSearch(self):
		l = list(self.g.search_nodes(name="Geremy"))
		self.failUnlessEqual(l, [])
		l = list(self.g.search_nodes(name="Bob"))
		self.failUnlessEqual(l, [self.n2])
		l = list(self.g.search_nodes(name="Bill"))
		self.failUnlessEqual(l, [self.n3, self.n4])

	def testEdgeSearch(self):
		l = list(self.g.search_edges(weight=5))
		self.failUnlessEqual(l, [self.e3])
		s = set(self.g.search_edges(end=self.n3))
		self.failUnlessEqual(s, {self.e2, self.e3})
		l = list(self.g.search_edges(start=self.n2))
		self.failUnlessEqual(l, [self.e2])

class EdgeMovementTest(unittest.TestCase):

	def setUp(self):
		self.g = Graph()
		self.geremy = self.g.add_node(name="Geremy")
		self.bill = self.g.add_node(name="Bill")
		self.bob = self.g.add_node(name="Bob")
		self.tom = self.g.add_node(name="Tom")
		self.e = self.g.add_edge(self.geremy, self.bob, name="people")

	def testEdgeMoving(self):
		e2 = self.g.move_edge(self.e, start=self.bill, end=self.tom)
		self.failUnless(self.e is e2)
		self.failUnlessEqual(self.e, e2)
		self.failUnlessEqual(e2.name, "people")
		self.failUnlessEqual(e2.start, self.bill)
		self.failUnlessEqual(e2.end, self.tom)


class GetElementsTest(unittest.TestCase):

	def setUp(self):
		self.g = Graph()

		# make some nodes
		self.jimmy = self.g.add_node(city="New York")
		self.ted = self.g.add_node(city="Atlanta")
		self.dan = self.g.add_node(city="Seattle")
		self.paul = self.g.add_node(city="Austin")

		# try not to error out
		self.j_to_t = self.g.add_edge(self.jimmy, self.ted, distance=850)
		self.t_to_d = self.g.add_edge(self.ted, self.dan, distance=2150)
		self.d_to_p = self.g.add_edge(self.dan, self.paul, distance=2850)

	def testNodeGetting(self):
		# test for equivalence
		self.failUnless(all(node in [self.jimmy, self.ted, self.dan, self.paul] for node in self.g.nodes))
		self.failUnless(all(node in self.g.nodes for node in [self.jimmy, self.ted, self.dan, self.paul]))
		self.failUnlessEqual([n for n in self.g.search_nodes(city="New York")], [self.jimmy])

	def testEdgeGetting(self):
		# test for equivalence
		self.failUnless(all(edge in {self.j_to_t, self.t_to_d, self.d_to_p} for edge in self.g.edges))
		self.failUnless(all(edge in self.g.edges for edge in {self.j_to_t, self.t_to_d, self.d_to_p}))
		self.failUnlessEqual([e for e in self.g.search_edges(distance=2850)], [self.d_to_p])


class TraversalTest(unittest.TestCase):

	def setUp(self):
		g = Graph()
		nodes = {}
		edges = []
		nodes["A"] = g.add_node(name="A")
		nodes["B"] = g.add_node(name="B")
		nodes["C"] = g.add_node(name="C")
		nodes["D"] = g.add_node(name="D")
		nodes["E"] = g.add_node(name="E")
		nodes["F"] = g.add_node(name="F")
		nodes["G"] = g.add_node(name="G")
		edges += [g.add_edge(nodes["A"], nodes["B"])]
		edges += [g.add_edge(nodes["B"], nodes["D"])]
		edges += [g.add_edge(nodes["B"], nodes["F"])]
		edges += [g.add_edge(nodes["F"], nodes["E"])]
		edges += [g.add_edge(nodes["A"], nodes["C"])]
		edges += [g.add_edge(nodes["C"], nodes["G"])]
		edges += [g.add_edge(nodes["A"], nodes["E"])]
		self.g = g
		self.nodes = nodes
		self.edges = edges

	def testDepthFirstTraversal(self):
		nodes = self.nodes
		edges = self.edges
		g = self.g
		positions = {node.name:pos for pos, node in enumerate(g.depth_first_traversal(nodes["A"]))} 
		self.failUnless(positions["A"] < positions["B"])
		self.failUnless(positions["A"] < positions["C"])
		self.failUnless(positions["A"] < positions["E"])
		self.failUnless(positions["B"] < positions["D"])
		self.failUnless(positions["C"] < positions["G"])
		self.failUnless(positions["F"] > min(positions["B"], positions["E"]))

		# test for equivalence problem
		a = g.add_node(name="A")
		b1 = g.add_node(name="B")
		b2 = g.add_node(name="B")
		c = g.add_node(name="C")
		d = g.add_node(name="D")
		g.add_edge(a, b1)
		g.add_edge(a, b2)
		g.add_edge(b1, c)
		g.add_edge(b2, d)
		self.failUnlessEqual(set((node for node in g.depth_first_traversal(a))), {a, b1, b2, c, d})

	def testBreadthFirstTraversal(self):
		g = self.g
		nodes = self.nodes
		edges = self.edges
		positions = {node.name:pos for pos, node in enumerate(g.breadth_first_traversal(nodes["A"]))}
		self.failUnless(positions["A"] < min(positions["B"], positions["C"], positions["E"]))
		self.failUnless(max(positions["B"], positions["C"], positions["E"]) < min(positions["D"], positions["F"], positions["G"]))


class InductionTest(unittest.TestCase):

	def setUp(self):
		g = Graph()
		kirk = g.add_node(name="kirk")
		spock = g.add_node(name="spock")
		bones = g.add_node(name="bones")
		uhura = g.add_node(name="uhura")
		self.e1 = g.add_edge(kirk, spock)
		self.e2 = g.add_edge(kirk, bones)
		self.e3 = g.add_edge(kirk, uhura)
		self.e4 = g.add_edge(uhura, spock)
		self.e5 = g.add_edge(uhura, bones)
		self.g = g
		self.kirk = kirk
		self.spock = spock
		self.bones = bones
		self.uhura = uhura

	def testNodeInduction(self):
		g = self.g
		kirk = self.kirk
		spock = self.spock
		bones = self.bones
		uhura = self.uhura
		new_mission = g.induce_subgraph(spock, bones, uhura)
		self.failUnlessEqual([node.name for node in new_mission.nodes], ["spock", "bones", "uhura"])
		spock = new_mission.nodes[0]
		bones = new_mission.nodes[1]
		uhura = new_mission.nodes[2]
		self.failUnlessEqual(uhura.outgoing[0].end.name, "spock")
		self.failUnlessEqual(uhura.outgoing[1].end.name, "bones")

	def testEdgeInduction(self):
		g = self.g
		kirk = self.kirk
		spock = self.spock
		bones = self.bones
		uhura = self.uhura
		new_mission = g.edge_induce_subgraph(self.e4, self.e5)
		self.failUnlessEqual({node.name for node in new_mission.nodes}, {"spock", "bones", "uhura"})
		spock = set(new_mission.search_nodes(name="spock")).pop()
		bones = set(new_mission.search_nodes(name="bones")).pop()
		uhura = set(new_mission.search_nodes(name="uhura")).pop()
		self.failUnlessEqual(uhura.outgoing[0].end.name, "spock")
		self.failUnlessEqual(uhura.outgoing[1].end.name, "bones")

"""
class GraphFailureTest(unittest.TestCase):
    
	def setUp(self):
		self.g = Graph()
        
	def testUnhasableNodeData(self):
		""" node.key should fail if unhashable """
		self.failUnlessRaises(self.g.TypeError, self.g.add_node(stuff="a"))
"""
	"""
	Tests to be written:
	unnamed node or edge removal
	nonexistant node or edge removal
	"""


class GraphCorrectnessTest(unittest.TestCase):

	def setUp(self):
		self.g = Graph()

	def testGetCommonEdges(self):
		""" Testing common edges correctness """
		g = self.g
		n1 = g.add_node()
		n2 = g.add_node()
		n3 = g.add_node()
		n4 = g.add_node()
		e1 = g.add_edge(n1, n2)
		e2 = g.add_edge(n2, n1)
		e3 = g.add_edge(n1, n3)
		e4 = g.add_edge(n2, n3)
		e5 = g.add_edge(n4, n4)
		e6 = g.add_edge(n4, n4)
		self.failUnlessEqual(g.get_common_edges(n1, n2), {e1, e2})
		self.failUnlessEqual(g.get_common_edges(n4, n4), {e5, e6})
		self.failUnlessEqual(g.get_common_edges(n1, n1), {e1, e2, e3})

	def testEdgeContraction(self):
		g = self.g
		n1 = g.add_node(value=1)
		n2 = g.add_node(value=2)
		n3 = g.add_node(value=3)
		n4 = g.add_node(value=4)
		n5 = g.add_node(value=6)
		n6 = g.add_node(value=7)
		# n1-n3 are completely connected
		g.add_edge(n1, n2)
		i1 = g.add_edge(n1, n3)
		g.add_edge(n2, n1)
		i2 = g.add_edge(n2, n3)
		o1 = g.add_edge(n3, n1)
		o2 = g.add_edge(n3, n2)
		# n4-n6 are completely connected
		o3 = g.add_edge(n4, n5)
		o4 = g.add_edge(n4, n6)
		i3 = g.add_edge(n5, n4)
		g.add_edge(n5, n6)
		i4 = g.add_edge(n6, n4)
		g.add_edge(n6, n5)
		# n3 and n4 have one edge between them
		e = g.add_edge(n3, n4)
		# you'll add the values of the two nodes
		# together to get the new value
		getter = lambda s: s.value
		get_new_data = lambda x, y: {"value": getter(x) + getter(y)}
		# contract the graph
		n = g.contract_edge(e, get_new_data)
		# test n's properties
		self.failUnlessEqual(set(n.incoming), {i1, i2, i3, i4})
		self.failUnlessEqual(set(n.outgoing), {o1, o2, o3, o4})
		self.failUnlessEqual(n.value, 7)
		# test the graph's properties
		self.failUnlessEqual(g.order(), 5)
		self.failUnlessEqual(g.size(), 12)

	def testUnion(self):
		evens = Graph()
		odds = Graph()
		evens_table = {}
		odds_table = {}
		for i in range(0, 10, 2): evens_table[i] = evens.add_node(label=i)
		for i in range(1, 10, 2): odds_table[i] = odds.add_node(label=i)
		for i in range(0, 10, 2):
			for j in range(0, 10, 2):
				evens.add_edge(evens_table[i], evens_table[j], weight=i-j)
		for i in range(1, 10, 2):
			for j in range(1, 10, 2):
				odds.add_edge(odds_table[i], odds_table[j], weight=i-j+1)
		digits = evens | odds
		numerals = {node.label for node in digits.nodes}
		self.failUnlessEqual(numerals, {i for i in range(10)})
		difference = [edge.weight for edge in digits.edges]
		differences = {diff for diff in difference}
		self.failUnlessEqual(len(difference), 50)
		self.failUnlessEqual(differences, {d for d in range(-8, 10, 1)})

	def testIntersection(self):
		g1 = Graph()
		g2 = Graph()
		one = g1.add_node(name=1)
		two = g1.add_node(name=2)
		three = g1.add_node(name=3)
		g1.add_edge(one, two)
		g1.add_edge(two, three)
		g1.add_edge(three, one)
		one_2 = g2.add_node(name=1)
		three_2 = g2.add_node(name=3)
		five = g2.add_node(name=5)
		g2.add_edge(one_2, five)
		g2.add_edge(five, three_2)
		g2.add_edge(three_2, one_2)
		one_and_three = g1 & g2
		self.failUnlessEqual({1, 3}, {node.name for node in one_and_three.nodes})
		self.failUnlessEqual(one_and_three.order(), 2)
		self.failUnlessEqual(one_and_three.size(), 1)

	def testDifference(self):
		g1 = Graph()
		g2 = Graph()
		zero = g1.add_node(name=0)
		one = g1.add_node(name=1)
		two = g1.add_node(name=2)
		three = g1.add_node(name=3)
		g1.add_edge(zero, two)
		g1.add_edge(one, two)
		g1.add_edge(two, three)
		g1.add_edge(three, one)
		one_2 = g2.add_node(name=1)
		three_2 = g2.add_node(name=3)
		five = g2.add_node(name=5)
		g2.add_edge(one_2, five)
		g2.add_edge(five, three_2)
		g2.add_edge(three_2, one_2)
		diff = g1 - g2
		self.failUnlessEqual({0, 2}, {node.name for node in diff.nodes})
		self.failUnlessEqual(diff.order(), 2)
		self.failUnlessEqual(diff.size(), 1)
		self.failUnlessEqual(diff.edges[0].start.name, 0)
		self.failUnlessEqual(diff.edges[0].end.name, 2)

	def testMerge(self):
		# setup
		g1 = Graph()
		g2 = Graph()
		bob1 = g1.add_node(name="Bob")
		dan = g1.add_node(name="Dan")
		doug = g1.add_node(name="Doug")
		g1.add_edge(bob1, dan)
		g1.add_edge(bob1, doug)
		g1.add_edge(dan, doug)
		bob2 = g2.add_node(name="Bob")
		jeff = g2.add_node(name="Jeff")
		paul = g2.add_node(name="Paul")
		g2.add_edge(bob2, jeff)
		g2.add_edge(bob2, paul)
		g2.add_edge(jeff, paul)
		g3 = g1 + g2
		self.failUnlessEqual(g3.order(), 5)
		self.failUnlessEqual(g3.size(), 6)
		self.failUnlessEqual({node.name for node in g3.nodes}, {"Bob", "Dan", "Doug", "Jeff", "Paul"})
		bob = list(g3.search_nodes(name="Bob"))[0]
		self.failUnlessEqual({bob.outgoing[i].end.name for i in range(4)}, {"Dan", "Doug", "Jeff", "Paul"})

	def testGetAllConnected(self):
		# setup
		g = Graph()
		# one connected component
		n1 = g.add_node(name="Bob")
		n2 = g.add_node(name="Bill")
		g.add_edge(n1, n2)
		component_1 = {n1, n2}
		# one solitary component
		n3 = g.add_node(name="Dan")
		component_2 = {n3}
		# one looped component
		n4 = g.add_node(name="John")
		g.add_edge(n4, n4)
		component_3 = {n4}
		# and test
		components = [component_1, component_2, component_3]
		self.failUnlessEqual(g.get_connected_components(), components)

	def testGetShortestPaths(self):
		# trivial graph
		g = Graph()
		n1 = g.add_node(name="Geremy")
		paths = g.get_shortest_paths(n1)
		self.failUnlessEqual(paths, {n1: (0, [])})
		# less trivial graph
		g = Graph()
		n1 = g.add_node(name="Geremy")
		n2 = g.add_node(name="Bob")
		n3 = g.add_node(name="Snowflake")
		e1 = g.add_edge(n1, n2, weight=4)
		e2 = g.add_edge(n1, n3, weight=5)
		paths = g.get_shortest_paths(n1, get_weight=lambda e: e.weight)
		self.failUnlessEqual(paths, {n1: (0, []), n2: (4, [e1]), n3: (5, [e2])})
		# tricksy graph
		g = Graph()
		n1 = g.add_node(name="Geremy")
		n2 = g.add_node(name="Bob")
		n3 = g.add_node(name="Snowflake")
		# normal edges
		e1 = g.add_edge(n1, n2, weight=5)
		e2 = g.add_edge(n2, n3, weight=1)
		# notice that the path from n1 to n2 to n3 is
		# shorter than the path from n1 to n3
		e3 = g.add_edge(n1, n3, weight=7)
		# form a loop
		e4 = g.add_edge(n3, n3, weight=1)
		# form a cycle
		e5 = g.add_edge(n3, n2, weight=1)
		paths = g.get_shortest_paths(n1, get_weight=lambda e: e.weight)
		self.failUnlessEqual(paths, {n1: (0, []), n2: (5, [e1]), n3: (6, [e1, e2])})

	def testStronglyConnectedComponents(self):
		g = Graph()
		n1 = g.add_node(value=1)
		n2 = g.add_node(value=2)
		n3 = g.add_node(value=3)
		n4 = g.add_node(value=4)
		n5 = g.add_node(value=6)
		n6 = g.add_node(value=7)
		# n1-n3 are completely connected
		g.add_edge(n1, n2)
		g.add_edge(n1, n3)
		g.add_edge(n2, n1)
		g.add_edge(n2, n3)
		g.add_edge(n3, n1)
		g.add_edge(n3, n2)
		# n4-n6 are completely connected
		g.add_edge(n4, n5)
		g.add_edge(n4, n6)
		g.add_edge(n5, n4)
		g.add_edge(n5, n6)
		g.add_edge(n6, n4)
		g.add_edge(n6, n5)
		# get strongly connected components
		comp = g.get_strongly_connected()
		self.failUnlessEqual([{n1, n2, n3}, {n4, n5, n6}], comp)

class GraphPerformanceTest(unittest.TestCase):

	graph_setup = "from base import Graph; g = Graph(); n = g.add_node(name='');"

	def testNodeAdditionPerformance(self):
		setup = self.graph_setup
		test = "for i in range(1000): g.add_node(name=i)"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		test = "for i in range(1000000): g.add_node(name=i)"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to add 1M nodes" % t1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to add 1M nodes" % t2)

	def testNodeIterationPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_node(name=i)"
		test = "for i in g.nodes: pass"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_node(name=i)"
		test = "for i in g.nodes: pass"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t2)

	def testNodeSearchPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_node(name=i)"
		test = "[i for i in g.search_nodes(name=999)]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_node(name=i)"
		test = "[i for i in g.search_nodes(name=999999)]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t2)

	def testEdgeAdditionPerformance(self):
		setup = self.graph_setup
		test = "for i in range(1000): g.add_edge(n, n, name='a')"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		test = "for i in range(1000000): g.add_edge(n, n, name='a')"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to add 1M edges" % t1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to add 1M edges" % t2)

	def testEdgeIterationPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, name='a')"
		test = "for i in g.edges: pass"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, name='a')"
		test = "for i in g.edges: pass"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t2)

	def testEdgeSearchPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, name='a')"
		test = "[i for i in g.search_edges(start='')]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, name='a')"
		test = "[i for i in g.search_edges(start='')]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t2)

	def testTraversalPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, name='a')"
		test = "[i for i in g.depth_first_traversal(n)]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, name='a')"
		test = "[i for i in g.depth_first_traversal(n)]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to traverse 1M node graphs" % t1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to traverse 1M node graphs" % t2)


if __name__ == "__main__":
	GraphCorrectnessTest = unittest.TestLoader().loadTestsFromTestCase(GraphCorrectnessTest)
	GraphPropertiesTest = unittest.TestLoader().loadTestsFromTestCase(GraphPropertiesTest)
	GraphFailureTest = unittest.TestLoader().loadTestsFromTestCase(GraphFailureTest)
	GraphSearchTest = unittest.TestLoader().loadTestsFromTestCase(GraphSearchTest)
	NodeCreationTest = unittest.TestLoader().loadTestsFromTestCase(NodeCreationTest)
	EdgeCreationTest = unittest.TestLoader().loadTestsFromTestCase(EdgeCreationTest)
	EdgeMovementTest = unittest.TestLoader().loadTestsFromTestCase(EdgeMovementTest)
	GetElementsTest = unittest.TestLoader().loadTestsFromTestCase(GetElementsTest)
	TraversalTest = unittest.TestLoader().loadTestsFromTestCase(TraversalTest)
	InductionTest = unittest.TestLoader().loadTestsFromTestCase(InductionTest)
	suites = [GraphCorrectnessTest, NodeCreationTest, EdgeCreationTest, GraphPropertiesTest, GraphSearchTest, EdgeMovementTest, GetElementsTest, TraversalTest, InductionTest, GraphFailureTest]
	CorrectnessTest = unittest.TestSuite(suites)
	unittest.main()
