#! /usr/bin/env python3.0

class DotGenerator:

	"""This produces dot files for compatibility with other graph libraries."""

	def __init__(self, node_label_getter, edge_label_getter, is_directed=True):
		"""Sets the general properties of the graph and how to get node and edge labels."""
		self.get_node_label = node_label_getter
		self.get_edge_label = edge_label_getter
		self.is_directed = is_directed

	def draw(self, graph, name):
		doc = ""
		if self.is_directed:
			doc += "digraph %s {" % name
		else:
			doc += "graph %s {" % name
		nodes = set(graph.nodes)
		while nodes:
			current = nodes.pop()
			adjacent = {e.end for e in current.outgoing}
			nodes -= adjacent
			doc += "\t%s " % self.get_node_label(current)
			for node in adjacent:
				doc += "-> %s " % self.get_node_label(current)
			doc += "\n" 
			
