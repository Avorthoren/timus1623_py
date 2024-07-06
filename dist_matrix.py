"""
Module for fractal labyrinth described in:
https://acm.timus.ru/problem.aspx?space=1&num=1623

Imagine a house with 2 <= N <= 20 doors.
Inside it, there are 0 <= K <= 5 houses, each of them an entire copy
of the "outer" one. Some doors are connected by roads. And, of course, if,
for example, i-th door of outer house connected to j-th door to k-th inner
house, then the same applies to each inner house: i-th door of each inner house
is connected to j-th door of k-th house inside that inner house, and so on.

In this module we use term 'room' instead of 'house'.
"""
import os

from template import Template, NodeIndex
import test

type _Data_T = list[int | None]
type _Locations_T = [list[list[int]]]


LOG = bool(int(os.environ.get('LOG', '0')))


class DistMatrix:
	__slots__ = '_template', '_total_nodes', '_data',  '_counter',  # '_LOCATION'

	def __init__(self, template: Template):
		self._template = template
		# Get index of the last node.
		self._total_nodes = self._get_node_index(template.rooms + 1, template.doors)
		# Flat version of one 'half' of square matrix of `_total_nodes` size,
		# except for main diagonal.
		self._data: _Data_T = [None] * (self._total_nodes * (self._total_nodes - 1) >> 1)

		# Turns out, caching here doesn't make a difference in speed,
		# but only uses more memory.
		# self._LOCATION: _Locations_T = self._prepare_locations()

		# Calculate all distances:
		self._counter = 0
		self._fill()

	@property
	def counter(self) -> int:
		return self._counter

	def get(self, node1: NodeIndex, node2: NodeIndex) -> int | None:
		"""Get the shortest path length between two nodes."""
		return self._get(self._get_node_index(*node1), self._get_node_index(*node2))

	def _get_node_index(self, room: int, door: int) -> int:
		return room * self._template.doors + door

	def _reverse_get_node_index(self, node_index: int) -> NodeIndex:
		room, door = divmod(node_index, self._template.doors)
		return NodeIndex(room, door)

	def count_defined(self):
		return sum(int(value is not None) for value in self._data)

	def show(self, only_defined: bool = True):
		"""Show current state of `self._data` in a nice way."""
		for node1_index in range(self._total_nodes - 1):
			node1 = NodeIndex(*self._reverse_get_node_index(node1_index))
			for node2_index in range(node1_index + 1, self._total_nodes):
				node2 = NodeIndex(*self._reverse_get_node_index(node2_index))
				dist = self._get(node1_index, node2_index)
				if only_defined and dist is None:
					continue
				print(f'dist({node1}, {node2}) = {dist}')

	def _get(self, node1_index: int, node2_index: int) -> int | None:
		"""Get the shortest path length between two nodes."""
		if node1_index == node2_index:
			return 0
		return self._data[self._get_location(node1_index, node2_index)]

	def _set(self, node1_index: int, node2_index: int, dist: int):
		self._data[self._get_location(node1_index, node2_index)] = dist

	# def _prepare_locations(self) -> _Locations_T:
	# 	"""Prepare indices of `self._data` elements for each pair of
	# 	DISTINCT node indices.
	#
	# 	NOTE: Turns out, it doesn't make a difference in speed,
	# 	but only uses more memory.
	# 	"""
	# 	return [[
	# 		self._get_location(node1_index, node2_index)
	# 		for node2_index in range(self._total_nodes)
	# 	] for node1_index in range(self._total_nodes)]

	def _get_location(self, node1_index: int, node2_index: int) -> int:
		"""Get index of respective element in `self._data`"""
		if node1_index > node2_index:
			node2_index, node1_index = node1_index, node2_index

		# Let's assume for simplicity `self._total_nodes == 10`.
		# Then `self._data` is flat representation of upper triangle of
		# 10x10 matrix (excluding main diagonal).
		# Let's denote:
		# i, j = node1_index, node2_index
		# Let's call that 10x10 matrix: T. Then we are looking for index of
		# element T[i][j] in `self._data`. For the sake of example let's set
		# i, j = 4, 7
		# Let's draw first 6 rows of T:
		#     0  1  2  3  4  5  6  j  8  9
		#     ----------------------------
		# 0 | a  x  x  x  x  x  x  x  x  x | elements of `self._data` denoted 'x'
		# 1 | a  a  x  x  x  x  x  x  x  x | we read the left to right,
		# 2 | a  a  a  x  x  x  x  x  x  x | top to bottom.
		# 3 | a  a  a  a  x  x  x  x  x  x |
		# i | a  a  a  a  a  b  b  !  x  x | 'b's are last two elements of
		# 5 | a  a  a  a  a  a  x  x  x  x | `self._data` before T[i][j]
		# ..................................
		return (
			# Number of elements in first `i` rows of T:
			self._total_nodes * node1_index
			# Minus number of those not belonging to upper triangle
			# (denoted 'a')
			- (node1_index * (node1_index + 1) >> 1)
			# Plus number of elements in upper triangle in the i-th row before
			# T[i][j] (denoted 'b')
			+ (node2_index - node1_index - 1)
		)

	def get_complexity(self) -> int:
		rooms, doors, nodes = self._template.rooms, self._template.doors, self._total_nodes
		return (doors - 2) * doors * (doors - 1) // 2 * rooms * nodes ** 3

	def _fill(self):
		"""Fill `self._data` with proper values."""
		if LOG:
			print("ANALYZING...")
			print(f"Estimated complexity: {self.get_complexity():_}")
			print("Adding explicit links...")

		# Add template explicit links.
		for node1, node2 in self._template.all_links():
			node1_index = self._get_node_index(*node1)
			node2_index = self._get_node_index(*node2)
			self._add_road(node1_index, node2_index, length=1)

		if LOG:
			print("Explicit links added")
			self.show()
			print(f"Total defined: {self.count_defined()}")
			print("Depth 1 done")
			print()
			print("Analyzing recursively...")

		# Take into consideration implicit 'recursive' links.
		# Will go for maximum of `self._template.doors - 2` iterations, I hope.
		# Complexity: DOORS - 2
		# Inner complexity: DOORS * (DOORS - 1) / 2 * ROOMS * NODES * NODES * NODES
		# Total complexity: (DOORS - 2) * DOORS * (DOORS - 1) / 2 * ROOMS * NODES * NODES * NODES
		# NODES = (ROOMS + 1) * NODES
		depth = 1
		while self._update():
			depth += 1
			if LOG:
				print(f'Depth {depth} done')
				print()

	def _add_road(self, node1_index: int, node2_index: int, length: int, recursion_depth: int = 0) -> bool:
		"""Update labyrinth with new road. Update distances if needed.
		Return value indicates if new road made a difference.
		"""
		cur_dist = self._get(node1_index, node2_index)
		if cur_dist is not None and cur_dist <= length:
			self._counter += 1
			return False

		if LOG:
			node1, node2 = self._reverse_get_node_index(node1_index), self._reverse_get_node_index(node2_index)
			pad = '\t' * recursion_depth
			# dist((0, 0), (1, 1)) = 5 <- None
			if node1 == (0, 0) and node2 == (1, 1) and cur_dist is None and length == 5:
				t = 2
			print(f'{pad}dist({node1}, {node2}) = {length} <- {cur_dist}')

		self._set(node1_index, node2_index, length)
		self._propagate(node1_index, node2_index, length, recursion_depth)

		return True

	def _propagate(self, node1_index: int, node2_index: int, length: int, recursion_depth: int = 0):
		"""Propagate changes in `self._data` after calling
		self._set(node1_index, node2_index, length).

		Imagine two sets of nodes (possibly intersecting):
		A: node1 and all nodes connected to it except node2.
		B: node2 and all nodes connected to it except node1.
		This method updates distances for each pair of nodes:
		(node_i from A, node_j from B)
		Except for (node1, node2), obviously, because it should have been
		updated before call of this method.
		"""
		# Iterate through A:
		# Complexity: NODES * NODES * NODES
		for node_i_index in range(self._total_nodes):
			if node_i_index == node2_index:
				self._counter += 1
				continue
			if (left_dist := self._get(node_i_index, node1_index)) is None:
				# No connection
				self._counter += 1
				continue

			# Iterate through B:
			# NOTE: we can't exclude symmetric cases by starting `node_j_index`
			# from `node_i_index + 1`, because nested loop is not symmetrical
			# by its nature. Suppose node1 is only connected to node with
			# index 10, while node2 only to node with index 1.
			for node_j_index in range(self._total_nodes):
				if (
					node_j_index == node1_index
					# Exclude (node1, node2) pair.
					or node_i_index == node1_index and node_j_index == node2_index
				):
					self._counter += 1
					continue
				if (right_dist := self._get(node2_index, node_j_index)) is None:
					# No connection
					self._counter += 1
					continue
				# We can go node_i <-> node1 <-> node2 <-> node_j.
				self._add_road(
					node_i_index,
					node_j_index,
					left_dist + length + right_dist,
					recursion_depth + 1
				)

	def _update(self) -> bool:
		"""Update `self._data` using recursive knowledge.

		If there is path (0, i) <-> (0, j), then there are paths
		(room, i) <-> (room, j) for every inner room.
		"""
		# Go through distances for each unordered pair of nodes from outer room.
		# Using them generate new 'roads' for each inner room.
		# Complexity: DOORS * (DOORS - 1) / 2 * ROOMS
		# Inner complexity: NODES * NODES * NODES
		# Total complexity: DOORS * (DOORS - 1) / 2 * ROOMS * NODES * NODES * NODES
		updated = False
		for door1 in range(self._template.doors - 1):
			node1_index = self._get_node_index(room=0, door=door1)
			for door2 in range(door1 + 1, self._template.doors):
				node2_index = self._get_node_index(room=0, door=door2)
				if (dist := self._get(node1_index, node2_index)) is None:
					self._counter += 1
					continue

				if LOG:
					node1 = self._reverse_get_node_index(node1_index)
					node2 = self._reverse_get_node_index(node2_index)
					print(f"Processing {node1} <-> {node2}")

				for room in range(1, self._template.rooms + 1):
					was_updated = self._add_road(
						self._get_node_index(room, door1),
						self._get_node_index(room, door2),
						dist
					)
					updated |= was_updated
					if LOG:
						if was_updated:
							print(f"Total defined: {self.count_defined()}")

		return updated


def main():
	...
	import time
	import draw

	print("Input:")
	template, start, finish = test.get_hard_test(rooms=2, doors=4)
	print()

	time0 = time.perf_counter()
	dist_matrix = DistMatrix(template)
	time1 = time.perf_counter()
	print()
	print(f"Real complexity: {dist_matrix.counter:_}")
	print()

	shortest_path_len = dist_matrix.get(NodeIndex(0, start), NodeIndex(0, finish))
	print("Shortest path length:", shortest_path_len)
	print(f"Found in {time1 - time0:.3f} seconds")

	draw.show(draw.draw_template, template, depth=1, marker=(start, finish))


if __name__ == "__main__":
	main()
