#! /usr/bin/env python3.0

from graph.base import Graph
import sys

def build_fsm():
	fsm = Graph()
	fsm.add_edge("consume_one", "loop_on_zero", consumes="1", accept=False)
	fsm.add_edge("loop_on_zero", "loop_on_zero", consumes="0", accept=False)
	fsm.add_edge("loop_on_zero", "end_with_one", consumes="1", accept=True)
	fsm["loop_on_zero"].accept = True
	fsm.start = "consume_one"
	return fsm

def walk_fsm(data, fsm):
	w = fsm.walk_path(fsm.start)
	for edges in w:
		next = {e.consumes: e for e in edges}.get([data.pop(0)], False)
		if next: accept = getattr(next.end, "accept", False)
		else: return accept
		w.send(next)

if __name__ == "__main__":
	fsm = build_fsm()
	accept = walk_fsm(list(sys.argv[1]), fsm)
	if accept: print("Accepted!")
	else: print("Not accepted!")
