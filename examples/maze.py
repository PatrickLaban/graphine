#! /usr/bin/env python3.0

# maze.py

import random

from graph.base import Graph

def build_maze():
	maze = Graph()
	p1_start = maze.add_node(name="p1_start")
	p2_start = maze.add_node(name="p2_start")
	end = maze.add_node(name="END")
	nodes = [p1_start, p2_start, end]
	for i in range(25):
		nodes.append(maze.add_node(name=i))
	for i in range(250):
		connected = maze.get_connected_components()
		component_1 = random.choice(connected)
		component_2 = random.choice(connected)
		if component_1 != component_2:
			node_1 = random.choice(list(component_1))
			if len(node_1.outgoing) < 5:
				node_2 = random.choice(list(component_2))
				if len(node_2.outgoing) < 5:
					maze.add_edge(node_1, node_2, is_directed=False)
	maze.add_edge(p1_start, random.choice(maze.nodes), is_directed=False)
	maze.add_edge(p2_start, random.choice(maze.nodes), is_directed=False)
	maze.add_edge(end, random.choice(maze.nodes), is_directed=False)
	return p1_start, p2_start, maze

def ai_path(start, maze):
	def selector(candidates):
		best = (0, -1, None)
		for pos, room in enumerate(candidates):
			if room.name == "END":
				best = (0, pos, room)
				break
			num_doors = len(room.outgoing)
			if num_doors > best[0]:
				best = (num_doors, pos, room)
		return candidates.pop(best[1])
	distance = 0
	previous = start
	for node in maze.a_star_traversal(start, selector):
		distance += maze.get_shortest_paths(previous)[node][0]
		if node.name == "END":
			return distance
		previous = node

def player_select(options):
	selections = {}
	print("You have %s options:" % (len(options)))
	for pos, option in enumerate(options):
		selections[pos] = option
		print("%d. Room %s, with %s doors" % (pos, option.name, len(option.outgoing)))
	choice = int(input("Which do you want to take? "))
	return selections[choice]
	
def handle_player(start, maze, max_length):
	w = maze.walk_nodes()
	w.send(None)
	next = w.send(start)
	while next and max_length:
		max_length -= 1
		selection = player_select(next)
		if selection.name == "END":
			print("You win!")
			return
		next = w.send(selection)
	print("You lose!")
	return

if __name__ == "__main__":
	
	# build the maze
	p1_start, p2_start, maze = build_maze()

	# run the simulation for the AI
	path_to_beat = ai_path(p1_start, maze)

	# get the player's moves
	handle_player(p2_start, maze, path_to_beat)
