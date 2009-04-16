#! /usr/bin/env python3.0

def node_properties(n):
	"""Returns default properties for nodes adjusted by the contents of n."""
	defaults = {"label": None, "color": "black", "shape": "circle", "style": None, "fillcolor": "white"}
	data = n.data
	for k in defaults:
		if k in data:
			defaults[k] = data[k]
	if defaults["label"] == None:
		defaults.pop("label")
	if defaults["style"] == None:
		defaults.pop("style")
	return defaults

def edge_properties(e):
	"""Returns default properties for edges adjusted by the contents of e."""
	defaults = {"label": "", "color": "black", "style": None}
	data = e.data
	for k in defaults:
		if k in data:
			defaults[k] = data[k]
	if defaults["label"] == None: defaults.pop("label")
	if defaults["style"] == None: defaults.pop("style")
	return defaults


class DotGenerator:

	"""This produces dot files for compatibility with other graph libraries."""

	def __init__(self, node_property_getter=node_properties, edge_property_getter=edge_properties, is_directed=True):
		"""Sets the general properties of the graph and how to get node and edge labels."""
		self.get_node_properties = node_property_getter
		self.get_edge_properties = edge_property_getter
		self.is_directed = is_directed

	def draw(self, graph, name):

		doc = ""

		if self.is_directed:
			doc += "digraph %s {\n" % name
			edge_marker = " -> "
		else:
			doc += "graph %s {\n" % name
			edge_marker = " -- "

		for node in graph.nodes:
			node_properties = self.get_node_properties(node)
			property_strings = []
			for k, v in node_properties.items():
				property_strings.append("%s=%s" % (k, v))
			property_strings = str(property_strings).replace("'", "")
			doc += "\t%s %s\n" % (node_properties["label"], property_strings)

		for edge in graph.edges:
			start = edge.start
			end = edge.end
			start_label = self.get_node_properties(start)["label"]
			end_label = self.get_node_properties(end)["label"]
			edge_properties = self.get_edge_properties(edge)
			label = edge_properties["label"]
			color = edge_properties["color"]
			style = edge_properties["style"]
			edge_string = "\t%s %s %s [label=%s, color=%s, style=%s];\n" 
			edge_string %= (start_label, edge_marker, end_label, label, color, style)
			doc += edge_string

		doc += "}"

		return doc
