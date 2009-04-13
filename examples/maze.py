#! /usr/bin/env python3.0

# maze.py

import random

from graph.base import Graph

def build_maze():
	# create the maze
	maze = Graph()
	# add the player's starting positions
	p1_start = maze.add_node(name="p1_start")
	p2_start = maze.add_node(name="p2_start")
	# ...and the endpoint
	end = maze.add_node(name="END")
	# create a list of connected components
	nodes = [[p1_start], [p2_start], [end]]
	# add all the rooms, making each its own component
	for i in range(25):
		nodes.append([maze.add_node(name=i)])
	# while some components are unconnected
	while len(nodes) > 1:
		# choose two components at random
		component_1, component_2 = random.sample(nodes, 2)
		# and one node from each component
		node_1 = random.choice(component_1)
		node_2 = random.choice(component_2)
		# and if they don't have too many doors...
		if len(node_1.outgoing) < 5 and len(node_2.outgoing) < 5:
			# connect them
			maze.add_edge(node_1, node_2, is_directed=False)
			# then merge the components
			nodes.remove(component_1)
			nodes.remove(component_2)
			nodes.append(component_1 + component_2)
	# finally, make sure that the start and end points have doors.
	maze.add_edge(p1_start, random.choice(maze.nodes), is_directed=False)
	maze.add_edge(p2_start, random.choice(maze.nodes), is_directed=False)
	maze.add_edge(end, random.choice(maze.nodes), is_directed=False)
	return p1_start, p2_start, maze

def ai_path(start, maze):
	# selector is the selection heuristic that the AI will use
	# to decide what door to go through next
	def selector(candidates):
		# the current best candidate
		best = (0, -1, None)
		# for each possible room...
		for pos, room in enumerate(candidates):
			# select this one if its the end
			if room.name == "END":
				best = (0, pos, room)
				break
			# otherwise, see if its the best door
			num_doors = len(room.outgoing)
			if num_doors > best[0]:
				best = (num_doors, pos, room)
		# now return the best room to go to
		return candidates.pop(best[1])
	# the total distance traveled
	distance = 0
	previous = start
	# traverse the maze, using selector() as your heuristic
	for node in maze.a_star_traversal(start, selector):
		# take all the steps between dead ends
		distance += maze.get_shortest_paths(previous)[node][0]
		# and end if you're at the end
		if node.name == "END":
			return distance
		previous = node

def player_select(options):
	"""Prints the player's options and gets their choice."""
	selections = {}
	print("You have %s options:" % (len(options)))
	for pos, option in enumerate(options):
		selections[pos] = option
		print("%d. Room %s, with %s doors" % (pos, option.name, len(option.outgoing)))
	choice = int(input("Which do you want to take? "))
	return selections[choice]
	
def handle_player(start, maze, max_length):
	"""Walks the maze, giving the player the choice of where to go."""
	w = maze.walk_nodes()
	w.send(None)
	next = w.send(start)
	# while the AI hasn't beat you and you've got places to go
	while next and max_length:
		max_length -= 1
		# go where the player tells you
		selection = player_select(next)
		# win if you're at the end spot before the AI
		if selection.name == "END":
			print("You win!")
			return
		next = w.send(selection)
	# otherwise, lose
	print("You lose!")
	return

if __name__ == "__main__":
	
	# build the maze
	p1_start, p2_start, maze = build_maze()

	# run the simulation for the AI
	path_to_beat = ai_path(p1_start, maze)

	# get the player's moves
	handle_player(p2_start, maze, path_to_beat)
