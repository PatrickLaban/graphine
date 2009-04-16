#! /usr/bin/env python3.0

class DotGenerator:

	"""This produces dot files for compatibility with other graph libraries."""

	def __init__(self, node_label_getter, is_directed=True):
		"""Sets the general properties of the graph and how to get node and edge labels."""
		self.get_node_label = node_label_getter
		self.is_directed = is_directed

	def draw(self, graph, name):
		doc = ""
		if self.is_directed:
			doc += "digraph %s {\n" % name
			edge_marker = " -> "
		else:
			doc += "graph %s {\n" % name
			edge_marker = " -- "
		for node1 in graph.nodes:
			node1_label = self.get_node_label(node1)
			for edge in node1.outgoing:
				node2 = edge.other_end(node1)
				node2_label = self.get_node_label(node2)
				doc += "\t%s %s %s;\n" % (node1_label, edge_marker, node2_label)
		doc += "}"
		return doc
