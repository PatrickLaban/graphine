#! /usr/bin/env python3.0

"""
graphml.py

Written by Geremy Condra

Licensed under GPLv3

Released 15 April 2009

This module contains the machinery needed to load and store
graphs represented in the GraphML format.

It contains two functions of interest to the end user: load,
which takes a file as an argument and returns the parsed graph,
and store, which takes a graph and a file as arguments and
stores the graph in the given file.

It also contains Reader, a GraphML reader, and Writer, which
does its obvious opposite.
"""

from xml.sax.handler import ContentHandler
from xml.sax.saxutils import XMLGenerator
from xml.sax import parse

from graph.base import Graph

class Reader(ContentHandler):
	"""Generates a Graph from GraphML data."""

	def startDocument(self):
		"""Handles the beginning of a given document."""
		self.current_graph = None
		self.elements = []
		self.ids = {}
		self.defaults = {}

	def startElement(self, name, attrs):
		"""Dispatches opening tags to the appropriate handler."""
		try:
			handler = getattr(self, "handle_%s_start" % name)
			print("Handling %s" % name)
			handler(attrs)
		except AttributeError as error:
			print(error)
			print("Warning: ignoring unsupported tag %s" % name)

	def endElement(self, name):
		"""Dispatches closing tags to the appropriate handler."""
		try:
			handler = getattr(self, "handle_%s_end" % name)
			handler()
		except AttributeError as error:
			print(error)
			print("Warning: ignoring unsupported tag %s" % name)

	def handle_graphml_start(self, attrs):
		pass

	def handle_graphml_end(self):
		pass

	def handle_graph_start(self, attrs):
		"""Creates a new node and puts it on the stack."""
		# create the new graph
		self.current_graph = Graph()
		# associate it with its id
		self.ids[attrs["id"]] = self.current_graph
		# set the default edge direction
		self.defaults["edgedefault"] = attrs["edgedefault"]
		# add it to the graphs stack
		self.elements.append(self.current_graph)
		
	def handle_graph_end(self):
		"""Pops the graph off the graph stack."""
		if isinstance(self.elements[-1], Graph):
			self.elements.pop()
		else:
			raise ParseError("Invalid closing tag.")

	def handle_node_start(self, attrs):
		"""Creates a new Node and puts it on the stack."""
		# create the node
		node = self.current_graph.add_node()
		# associate it with its id
		self.ids[attrs["id"]] = node
		# put it on the stack
		self.elements.append(node)

	def handle_node_end(self):
		"""Ties off the node and removes it from the stack."""
		if isinstance(self.elements[-1], Graph.Node):
			self.elements.pop()
		else:
			raise ParseError("Invalid closing tag.")

	def handle_edge_start(self, attrs):
		"""Creates a new edge and puts it on the stack."""
		# get the edge's id
		id = attrs["id"]
		# get the edge's start and end
		start = self.ids[attrs["source"]]
		end = self.ids[attrs["target"]]
		# verify them
		if not isinstance(start, Graph.Node) or not isinstance(end, Graph.Node):
			raise ParseError("Encountered invalid node ids while parsing edge %s" % id)
		# get the edge's directed state
		is_directed = attrs.get("directed", self.defaults["edgedefault"])
		# build the edge
		edge = self.current_graph.add_edge(start, end, is_directed=is_directed)
		# associate its id with it
		self.ids[id] = edge
		# and push it onto the stack
		self.elements.append(edge)

	def handle_edge_end(self):
		"""Ties off the edge and removes it from the stack."""
		if isinstance(self.elements[-1], Graph.Edge):
			self.elements.pop()
		else:
			raise ParseError("Invalid closing tag.")

	def handle_key_start(self, attrs):
		"""Creates a new key and puts it on the stack."""
		# keys are represented as dictionaries
		key = {'_data_type': 'key'}
		# now, so are attrs
		attrs = dict(attrs.items())
		# with two attributes: id and for
		key["id"] = attrs.pop("id")
		key["for"] = attrs.pop("for")
		# now figure out the other ones
		for k, v in attrs.items():
			if k.startswith("attr."):
				key[k[5:]] = v
		# and put the miserable concoction on the stack
		self.elements.append(key)
		# and into the ids dict
		self.ids[key["id"]] = key

	def handle_key_end(self):
		"""Ties off the key and removes it from the stack."""
		if self.elements[-1]["_data_type"] == "key":
			self.elements.pop()
		else:
			raise ParseError("Invalid closing tag.")

	def handle_data_start(self, attrs):
		"""Creates a new data structure and puts it onto the stack."""
		data = {}
		key_id = attrs["key"]
		data["key"] = self.ids[key_id]
		self.elements.append(data)
		
	def handle_data_end(self):
		"""Ties off the data structure and removes it from the stack."""
		data = self.elements.pop()
		key = data["key"]
		data_name = key["name"]
		data_type = key["type"]
		default_value = key.get("default", False)
		data_value = data.get("default", default_value)
		types = {"obj": eval, "string": str, "boolean": bool, "int": int, "float": float, "double": float, "long": float}
		setattr(self.elements[-1], data_name, types[data_type](data_value))

	def handle_default_start(self, attrs):
		"""Creates a new default and attaches it to the parent key."""
		self.elements[-1]["default"] = None

	def handle_default_end(self):
		"""Ties off the default value."""
		pass

	def handle_desc_start(self):
		"""Creates a new key and puts it on the stack."""
		print("Warning: ignoring description")

	def handle_desc_end(self):
		"""Ties off the key and removes it from the stack."""
		print("Warning: ignoring description")

	def characters(self, data):
		"""If valid, associates the characters with the last element on the stack."""
		try:
			data = data.strip()
			if data:
				self.elements[-1]["default"] = data.strip()
		except:
			pass


class Writer:
	"""Generates a GraphML representation of a given graph."""

	data = ""

	def to_string(self, graph):
		"""Converts the given graph into GraphML format."""
		return self.data

	def to_file(self, f):
		"""Writes the data to a file."""
		f.write(self.data)


def load(source):
	r = Reader()
	parse(open(source), r)
	return r.current_graph

def store(graph, f):
	raise NotImplementedError
