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
		self.failUnlessEqual(jimmy.incoming, set())
		self.failUnlessEqual(jimmy.outgoing, {j_to_t})
		self.failUnlessEqual(ted.incoming, {j_to_t})
		self.failUnlessEqual(ted.outgoing, {t_to_d})
		self.failUnlessEqual(dan.incoming, {t_to_d})
		self.failUnlessEqual(dan.outgoing, {d_to_p})
		self.failUnlessEqual(paul.incoming, {d_to_p})
		self.failUnlessEqual(paul.outgoing, set())

		# and after deletion
		g.remove_edge(t_to_d)
		self.failUnlessEqual(ted.outgoing, set())
		self.failUnlessEqual(dan.incoming, set())
		new_trip = g.add_edge(ted, dan, distance=850)
		self.failUnlessEqual(ted.outgoing, {new_trip})
		self.failUnlessEqual(dan.incoming, {new_trip})

		# equivalence test
		lame_trip = g.add_edge(jimmy, ted, distance=850)
		self.failUnlessEqual(new_trip.data, lame_trip.data)

		# ensure that the edges properties are being set properly
		self.failUnlessEqual(dict(lame_trip.data), {"distance": 850})
		self.failUnlessEqual(dict(d_to_p.data), {"distance": 2850})

		# make sure that the change is reflected in the graph's size
		self.failUnlessEqual(g.size(), 4)

		
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
