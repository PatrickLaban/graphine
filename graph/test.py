#! /usr/bin/env python3.0

"""
test.py

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
import timeit
from base import Graph

class GraphCorrectnessTest(unittest.TestCase):

	def setUp(self):
		self.g = Graph()

	def testNodeCreation(self):
		g = self.g

		# try not to error out
		jimmy = g.add_node(city="New York")
		ted = g.add_node(city="Atlanta")
		dan = g.add_node(city="Seattle")
		paul = g.add_node(city="Austin")

		# test for equality between elements
		snowflake = g.add_node(city="Austin")
		self.failIfEqual(dan, snowflake)
		self.failUnlessEqual(paul.data, snowflake.data)
		
		# test for non-identity
		self.failUnless(not paul.data != snowflake.data)

		# make sure that the nodes are what we want them to be
		self.failUnlessEqual(jimmy.data, {"city":"New York"})
		self.failUnlessEqual(ted.data, {"city":"Atlanta"})
		self.failUnlessEqual(paul.data, {"city":"Austin"})
	
		# make sure that change is reflected in the graph's order
		self.failUnlessEqual(g.order(), 5)

		# test to make sure that unlinking works
		# if they should be equal
		self.failUnlessEqual(paul.flatten(), snowflake.flatten())
		# if their data is the same, but their edges are
		# in the wrong place
		e1 = g.add_edge(paul, snowflake, distance=0)
		self.failIfEqual(paul.flatten(), snowflake.flatten())
		g.remove_edge(e1)
		# if their data is the same, and they have different
		# edges
		e1 = g.add_edge(paul, ted)
		e2 = g.add_edge(snowflake, jimmy)
		self.failIfEqual(paul.flatten(), snowflake.flatten())
		# if their data is the same and their edges go
		# to the same place
		g.remove_edge(e2)
		g.add_edge(snowflake, ted)
		self.failUnlessEqual(paul.flatten(), snowflake.flatten())

	def testEdgeCreation(self):

		g = self.g

		# make some nodes
		jimmy = g.add_node(city="New York")
		ted = g.add_node(city="Atlanta")
		dan = g.add_node(city="Seattle")
		paul = g.add_node(city="Austin")

		# try not to error out
		j_to_t = g.add_edge(jimmy, ted, distance=850)
		t_to_d = g.add_edge(ted, dan, distance=2150)
		d_to_p = g.add_edge(dan, paul, distance=2850)

		# ensure adjacency list is correct
		self.failUnlessEqual(jimmy.incoming, [])
		self.failUnlessEqual(jimmy.outgoing, [j_to_t])
		self.failUnlessEqual(ted.incoming, [j_to_t])
		self.failUnlessEqual(ted.outgoing, [t_to_d])
		self.failUnlessEqual(dan.incoming, [t_to_d])
		self.failUnlessEqual(dan.outgoing, [d_to_p])
		self.failUnlessEqual(paul.incoming, [d_to_p])
		self.failUnlessEqual(paul.outgoing, [])

		# and after deletion
		g.remove_edge(t_to_d)
		self.failUnlessEqual(ted.outgoing, [])
		self.failUnlessEqual(dan.incoming, [])
		new_trip = g.add_edge(ted, dan, distance=850)
		self.failUnlessEqual(ted.outgoing, [new_trip])
		self.failUnlessEqual(dan.incoming, [new_trip])

		# equivalence test
		lame_trip = g.add_edge(jimmy, ted, distance=850)
		self.failUnlessEqual(new_trip.data, lame_trip.data)

		# ensure that the edges properties are being set properly
		self.failUnlessEqual(dict(lame_trip.data), {"distance": 850})
		self.failUnlessEqual(dict(d_to_p.data), {"distance": 2850})

		# make sure that the change is reflected in the graph's size
		self.failUnlessEqual(g.size(), 4)

		# test to ensure that equal edges unlink equally
		new_lame_trip = g.add_edge(jimmy, ted, distance=850)
		self.failUnlessEqual(new_lame_trip.flatten(), lame_trip.flatten())

		# test to ensure that non-equal edges unlink unequally
		self.failIfEqual(j_to_t.flatten(), t_to_d.flatten())

		
	def testNodeGetting(self):
		g = self.g

		# make some nodes
		jimmy = g.add_node(city="New York")
		ted = g.add_node(city="Atlanta")
		dan = g.add_node(city="Seattle")
		paul = g.add_node(city="Austin")

		# try not to error out
		j_to_t = g.add_edge(jimmy, ted, distance=850)
		t_to_d = g.add_edge(ted, dan, distance=2150)
		d_to_p = g.add_edge(dan, paul, distance=2850)

		# test for equivalence
		self.failUnless(all(node in [jimmy, ted, dan, paul] for node in g.nodes))
		self.failUnless(all(node in g.nodes for node in [jimmy, ted, dan, paul]))
		self.failUnlessEqual([n for n in g.search_nodes(city="New York")], [jimmy])

	def testEdgeGetting(self):
		g = self.g

		# make some nodes
		jimmy = g.add_node(city="New York")
		ted = g.add_node(city="Atlanta")
		dan = g.add_node(city="Seattle")
		paul = g.add_node(city="Austin")

		# try not to error out
		j_to_t = g.add_edge(jimmy, ted, distance=850)
		t_to_d = g.add_edge(ted, dan, distance=2150)
		d_to_p = g.add_edge(dan, paul, distance=2850)

		# test for equivalence
		self.failUnless(all(edge in {j_to_t, t_to_d, d_to_p} for edge in g.edges))
		self.failUnless(all(edge in g.edges for edge in {j_to_t, t_to_d, d_to_p}))
		self.failUnlessEqual([e for e in g.search_edges(distance=2850)], [d_to_p])

	def testDepthFirstTraversal(self):
		# setup
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

		positions = {node.name:pos for pos, node in enumerate(g.depth_first_traversal(nodes["A"]))} 
		self.failUnless(positions["A"] < positions["B"])
		self.failUnless(positions["A"] < positions["C"])
		self.failUnless(positions["A"] < positions["E"])
		self.failUnless(positions["B"] < positions["D"])
		self.failUnless(positions["C"] < positions["G"])
		self.failUnless(positions["F"] > min(positions["B"], positions["E"]))

		# test for the equivalence problem
		g = Graph()
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
		# setup
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

		positions = {node.name:pos for pos, node in enumerate(g.breadth_first_traversal(nodes["A"]))}
		self.failUnless(positions["A"] < min(positions["B"], positions["C"], positions["E"]))
		self.failUnless(max(positions["B"], positions["C"], positions["E"]) < min(positions["D"], positions["F"], positions["G"]))

	def testInduceSubgraph(self):
		# setup
		g = Graph()
		kirk = g.add_node(name="kirk")
		spock = g.add_node(name="spock")
		bones = g.add_node(name="bones")
		uhura = g.add_node(name="uhura")
		e1 = g.add_edge(kirk, spock)
		e2 = g.add_edge(kirk, bones)
		e3 = g.add_edge(kirk, uhura)
		e4 = g.add_edge(uhura, spock)
		e5 = g.add_edge(uhura, bones)
		
		new_mission = g.induce_subgraph(spock, bones, uhura)
		self.failUnlessEqual([node.name for node in new_mission.nodes], ["spock", "bones", "uhura"])
		spock = new_mission.nodes[0]
		bones = new_mission.nodes[1]
		uhura = new_mission.nodes[2]
		self.failUnlessEqual(uhura.outgoing[0].end.name, "spock")
		self.failUnlessEqual(uhura.outgoing[1].end.name, "bones")

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
		self.failUnlessEqual(one_and_three.edges[0].start.name, 3)
		self.failUnlessEqual(one_and_three.edges[0].end.name, 1)
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
		self.failUnlessEqual([node.name for node in g3.nodes], ["Bob", "Dan", "Doug", "Jeff", "Paul"])
		self.failUnlessEqual([g3.nodes[0].outgoing[i].end.name for i in range(4)], ["Dan", "Doug", "Jeff", "Paul"])

	def testGetAllConnected(self):
		# setup
		g = Graph()
		# one connected component
		n1 = g.add_node(name="Bob")
		n2 = g.add_node(name="Bill")
		g.add_edge(n1, n2)
		component_1 = frozenset((n1, n2))
		# one solitary component
		n3 = g.add_node(name="Dan")
		component_2 = frozenset((n3,))
		# one looped component
		n4 = g.add_node(name="John")
		g.add_edge(n4, n4)
		component_3 = frozenset((n4,))
		# and test
		components = {component_1, component_2, component_3}
		self.failUnlessEqual(g.get_connected_components(), components)

	def testGetMinimumSpanningTree(self):
		g = Graph()
		# create a 3 node complete graph with 2 loops
		# and one unconnected vertex
		n1 = g.add_node()
		n2 = g.add_node()
		n3 = g.add_node()
		n4 = g.add_node()
		e1 = g.add_edge(n1, n1, weight=3)
		e2 = g.add_edge(n2, n2, weight=5)
		e3 = g.add_edge(n1, n2, weight=4)
		e4 = g.add_edge(n1, n3, weight=3)
		e5 = g.add_edge(n2, n1, weight=5)
		e6 = g.add_edge(n2, n3, weight=1)
		e7 = g.add_edge(n3, n1, weight=7)
		e8 = g.add_edge(n3, n2, weight=1)
		# the get_weight function
		f = lambda e: e.weight
		# get the minimum spanning tree
		minspan = g.minimum_spanning_tree(n1, get_weight=f)
		self.failUnlessEqual({edge.flatten() for edge in minspan.edges}, {edge.flatten() for edge in (e4, e8)})
		self.failUnlessEqual(minspan.order(), 3)

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
	unittest.main()
