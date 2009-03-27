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
		node_properties = ["city"]
		edge_properties = ["distance"]
		self.g = Graph(node_properties, edge_properties)

	def testNodeCreation(self):
		g = self.g

		# try not to error out
		jimmy = g.add_node(city="New York")
		ted = g.add_node(city="Atlanta")
		dan = g.add_node(city="Seattle")
		paul = g.add_node(city="Austin")

		# try TO error out
		self.failUnlessRaises(TypeError, "g.add_node(name='tim')")
		self.failUnlessRaises(TypeError, "g.add_node()")
		self.failUnlessRaises(TypeError, "g.add_node('LA')")

		# ensure uids are being assigned right
		self.failUnlessEqual(jimmy, 1)
		self.failUnlessEqual(ted, 2)
		self.failUnlessEqual(dan, 3)
		self.failUnlessEqual(paul, 4)

		# try uid assignment after deletion
		del g[dan]
		john = g.add_node(city="Chicago")
		self.failUnlessEqual(john, 3)

		# test for equality between elements
		snowflake = g.add_node(city="Austin")
		self.failUnless(dan != snowflake)
		self.failUnlessEqual(g[paul], g[snowflake])

		# make sure that the nodes are what we want them to be
		self.failUnlessEqual(g[jimmy], ("New York",))
		self.failUnlessEqual(g[ted], ("Atlanta",))
		self.failUnlessEqual(g[paul], ("Austin",))
	
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

		# try TO error out
		self.failUnlessRaises(TypeError, "g.add_edge()")
		self.failUnlessRaises(TypeError, "g.add_edge(0, 0, 100)")
		self.failUnlessRaises(TypeError, "g.add_edge(jimmy, ted, travel_time='9 hours')")

		# ensure uids are being assigned right
		self.failUnlessEqual(j_to_t, -1)
		self.failUnlessEqual(t_to_d, -2)
		self.failUnlessEqual(d_to_p, -3)

		# ensure adjacency list is correct
		self.failUnlessEqual(g.adjacency_list[jimmy], {j_to_t})
		self.failUnlessEqual(g.adjacency_list[ted], {t_to_d})
		self.failUnlessEqual(g.adjacency_list[dan], {d_to_p})
		self.failUnlessEqual(g.adjacency_list[paul], set())

		# test uid assignment after deletion
		del g[j_to_t]
		new_trip = g.add_edge(jimmy, ted, distance=850)
		self.failUnlessEqual(new_trip, -1)

		# equivalence test
		lame_trip = g.add_edge(jimmy, ted, distance=850)
		self.failUnless(new_trip != lame_trip)
		self.failUnlessEqual(g[lame_trip], g[new_trip])

		# ensure that the edges properties are being set properly
		self.failUnlessEqual(g[lame_trip], (jimmy, ted, 850,))
		self.failUnlessEqual(g[d_to_p], (dan, paul, 2850,))

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
		self.failUnlessEqual(set(g.get_nodes()), set((g[jimmy], g[ted], g[dan], g[paul])))
		self.failUnlessEqual(set(g.search_nodes(city="New York")), set((g[jimmy],)))

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
		self.failUnlessEqual(set(g.get_edges()), set((g[j_to_t], g[t_to_d], g[d_to_p])))
		self.failUnlessEqual(set(g.search_edges(distance=2850)), set((g[d_to_p],)))

	def testNodeAdjacency(self):
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

		# test to make sure that path following works normally
		self.failUnlessEqual(set(g.get_adjacent_nodes(jimmy)), {g[ted], g[jimmy]})

		# test to make sure it works with opposite direction edges
		p_to_j = g.add_edge(paul, jimmy, distance=1100)
		self.failUnlessEqual(set(g.get_adjacent_nodes(jimmy)), {g[ted], g[jimmy]})

		# test to make sure it works with loops
		j_to_j = g.add_edge(jimmy, jimmy, distance=0)
		self.failUnlessEqual(set(g.get_adjacent_nodes(jimmy)), {g[ted], g[jimmy]})

		# ... and with deleted edges
		del g[t_to_d]
		self.failUnlessEqual(set(g.get_adjacent_nodes(ted)), {g[ted]})

	def testDepthFirstTraversal(self):
		# setup
		g = Graph(("name",), tuple())
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

		positions = {g[uid].name:pos for pos, uid in enumerate(g.depth_first_traversal(nodes["A"]))} 
		self.failUnless(positions["A"] < positions["B"])
		self.failUnless(positions["A"] < positions["C"])
		self.failUnless(positions["A"] < positions["E"])
		self.failUnless(positions["B"] < positions["D"])
		self.failUnless(positions["C"] < positions["G"])
		self.failUnless(positions["F"] > min(positions["B"], positions["E"]))

	def testBreadthFirstTraversal(self):
		# setup
		g = Graph(("name",), tuple())
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

		positions = {g[uid].name:pos for pos, uid in enumerate(g.breadth_first_traversal(nodes["A"]))}
		self.failUnless(positions["A"] < min(positions["B"], positions["C"], positions["E"]))
		self.failUnless(max(positions["B"], positions["C"], positions["E"]) < min(positions["D"], positions["F"], positions["G"]))

	def testGenerateSubgraph(self):
		# setup
		g = Graph(("name",), tuple())
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

		# generate a subgraph
		wanted_nodes = [nodes["A"], nodes["B"], nodes["E"]]
		wanted_edges = [edges[0], edges[6]]
		new_graph = g.generate_subgraph(*wanted_nodes)
		new_nodes = set(node for node in new_graph.get_nodes())
		new_edges = set(edge for edge in new_graph.get_edges())
		self.failUnlessEqual(set((g[n] for n in wanted_nodes)), new_nodes)
		self.failUnlessEqual(set((g[e] for e in wanted_edges)), new_edges)

class GraphPerformanceTest(unittest.TestCase):

	graph_setup = "from base import Graph; g = Graph(('name',), ('name',)); n = g.add_node(name='');"

	def testNodeAdditionPerformance(self):
		setup = self.graph_setup
		test = "for i in range(1000): g.add_node(name=i)"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to add 1M nodes" % t1)
		test = "for i in range(1000000): g.add_node(name=i)"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to add 1M nodes" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))

	def testNodeModificationPerformance(self):
		setup = self.graph_setup + " n = g.add_node(name=-1)"
		test = "for i in range(1000): n = g.modify_node(n, name=i%2)"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to modify 1M nodes" % t1)
		test = "for i in range(1000000): n = g.modify_node(n, name=i%2)"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to modify 1M nodes" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))

	def testNodeIterationPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_node(name=i)"
		test = "for i in g.get_nodes(): pass"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t1)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_node(name=i)"
		test = "for i in g.get_nodes(): pass"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))

	def testNodeSearchPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_node(name=i)"
		test = "[i for i in g.search_nodes(name=999)]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t1)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_node(name=i)"
		test = "[i for i in g.search_nodes(name=999999)]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))

	def testEdgeAdditionPerformance(self):
		setup = self.graph_setup
		test = "for i in range(1000): g.add_edge(n, n, name='a')"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to add 1M edges" % t1)
		test = "for i in range(1000000): g.add_edge(n, n, name='a')"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to add 1M edges" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))

	def testEdgeModificationPerformance(self):
		setup = self.graph_setup + "\ne = g.add_edge(n, n, name='a')"
		test = "for i in range(1000): \n\t e = g.modify_edge(e, name=i%2)"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to modify 1M edges" % t1)
		setup = self.graph_setup + "\ne = g.add_edge(n, n, name='a')"
		test = "for i in range(1000000): \n\t e = g.modify_edge(e, name=i%2)"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to modify 1M edges" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))

	def testEdgeIterationPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, name='a')"
		test = "for i in g.get_edges(): pass"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t1)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, name='a')"
		test = "for i in g.get_edges(): pass"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))

	def testEdgeSearchPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, name='a')"
		test = "[i for i in g.search_edges(start='')]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t1)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, name='a')"
		test = "[i for i in g.search_edges(start='')]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))

	def testTraversalPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, name='a')"
		test = "[i for i in g.depth_first_traversal(n)]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		self.failUnless(t1 < 20, msg="Performance check failed: it took %s seconds to traverse 1M node graphs" % t1)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, name='a')"
		test = "[i for i in g.depth_first_traversal(n)]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		self.failUnless(t2 < 20, msg="Performance check failed: it took %s seconds to traverse 1M node graphs" % t2)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))


if __name__ == "__main__":
	unittest.main()
