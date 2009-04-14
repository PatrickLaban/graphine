#! /usr/bin/env python3.0

import sys

from graph.base import Graph

class StateMachine(Graph):
	"""Represents a FSM with a single starting point and indexed by labels."""	
	start = None
	labels = {}

	def add_state(self, label, is_accepting, is_start=False):
		"""Adds a new state (node) to the FSM and associates a label with it."""
		self.labels[label] = self.add_node(label=label, is_accepting=is_accepting)
		if is_start: self.start = label

	def add_transition(self, start, end, consumes):
		"""Adds a new transition (edge) to the FSM."""
		self.add_edge(self.labels[start], self.labels[end], consumes=consumes)

	def walk(self, data):
		"""Walks through the FSM, consuming one character at each step."""
		# get the starting point
		current_state = self.labels[self.start]
		# iterate over the data
		for character in data:
			# build a table of possible edges to go down
			options = {e.consumes: e for e in current_state.outgoing}
			# choose the one that matches the current character
			choice = options.get(character, False)
			# if there isn't one, return
			if not choice: return False
			# move to the new state
			current_state = choice.end
			print("Consumed %s" % character)
		# if you end up at an accept state...
		if current_state.is_accepting: return True
		# otherwise...
		return False

def build_state_machine():
	# create the new state machine
	fsm = StateMachine()
	# create the states
	fsm.add_state("consume_a_one", False, True)
	fsm.add_state("loop_on_zero", False)
	fsm.add_state("end_with_one", True)
	# make it so that the first state goes to the second if it hits a 1
	fsm.add_transition("consume_a_one", "loop_on_zero", "1")
	# ...so that the second returns to itself every time it hits a zero
	fsm.add_transition("loop_on_zero", "loop_on_zero", "0")
	# ... and so that the loop breaks when it hits a 1
	fsm.add_transition("loop_on_zero", "end_with_one", "1")
	return fsm

if __name__ == "__main__":

	data = sys.argv[1]

	fsm = build_state_machine()

	if fsm.walk(data): print("Matched!")
	else: print("Did not match!")
