#! /usr/bin/env python3.0

import sys

from graph.base import Graph

class StateMachine(Graph):
	
	start = None
	labels = {}

	def add_state(self, label, is_accepting, is_start=False):
		self.labels[label] = self.add_node(label=label, is_accepting=is_accepting)
		if is_start: self.start = label

	def add_transition(self, start, end, consumes):
		self.add_edge(self.labels[start], self.labels[end], consumes=consumes)

	def walk(self, data):
		current_state = self.labels[self.start]
		for character in data:
			options = {e.consumes: e for e in current_state.outgoing}
			choice = options.get(character, False)
			if not choice: return False
			current_state = choice.end
			print("Consumed %s" % character)
		if current_state.is_accepting: return True
		return False

def build_state_machine():
	fsm = StateMachine()
	fsm.add_state("consume_a_one", False, True)
	fsm.add_state("loop_on_zero", False)
	fsm.add_state("end_with_one", True)
	fsm.add_transition("consume_a_one", "loop_on_zero", "1")
	fsm.add_transition("loop_on_zero", "loop_on_zero", "0")
	fsm.add_transition("loop_on_zero", "end_with_one", "1")
	return fsm

if __name__ == "__main__":

	data = sys.argv[1]

	fsm = build_state_machine()

	if fsm.walk(data): print("Matched!")
	else: print("Did not match!")
