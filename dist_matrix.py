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
type _UpdatedLinks_T = set[tuple[int, int]]


LOG = bool(int(os.environ.get('LOG', '0')))


class DistMatrix:
	__slots__ = (
		# : Template
		# Input description of the labyrinth.
		'_template',
		# : int
		# Convenience const for total number of outer and inner template doors.
		'_total_nodes',
		# : _Data_T
		# Flat version of one 'half' of square matrix of `_total_nodes` size,
		# except for main diagonal.
		'_data',
		# : int
		# For debugging: calculates 'real complexity'
		'_counter'
	)

	def __init__(self, template: Template):
		self._template = template
		self._total_nodes = total_nodes = (template.rooms + 1) * template.doors

		self._data: _Data_T = [None] * (total_nodes * (total_nodes - 1) >> 1)

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
		"""Enumerates all doors from 0 to `self._total_nodes - 1`."""
		return room * self._template.doors + door

	def _reverse_get_node_index(self, node_index: int) -> NodeIndex:
		# WARNING: Has to comply with `_get_node_index`
		room, door = divmod(node_index, self._template.doors)
		return NodeIndex(room, door)

	def _is_outer_node(self, node_index: int) -> bool:
		# Has to comply with `_get_node_index`
		return node_index < self._template.doors

	@staticmethod
	def _get_outer_node_door(node_index: int) -> int:
		"""Get door-index of the node considering it's outer node."""
		# WARNING: Has to comply with `_get_node_index`
		return node_index

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
		return (doors - 2) * doors * (doors - 1) // 2 * rooms * nodes ** 2

	def _fill(self):
		"""Fill `self._data` with proper values.

		For all explicit links:
		1. set new W
		2. add link to set
		3. recalculate all W, adding needed links to set
		While set:
		1. Pop link
		2. Create inner links from it
		3. For each created inner link:
		3.1. set new W
		3.2. recalculate all W, adding needed links to set
		"""
		if LOG:
			print("ANALYZING...")
			print(f"Estimated complexity: {self.get_complexity():_}")
			print("Adding explicit links...")

		updated_outer_links: _UpdatedLinks_T = set()
		# Add template explicit links.
		for node1, node2 in self._template.all_links():
			node1_index = self._get_node_index(*node1)
			node2_index = self._get_node_index(*node2)
			self._add_road(node1_index, node2_index, updated_outer_links)

		if LOG:
			print("Explicit links added")
			self.show()
			print(f"Total defined: {self.count_defined()}")
			print("Depth 1 done")
			print()
			print("Analyzing recursively...")

		# Eventually `self._data` will 'converge' to final value.
		while updated_outer_links:
			self._update(updated_outer_links)

	def _update(self, updated_outer_links: _UpdatedLinks_T):
		"""Update `self._data` using recursive knowledge.

		If there is path (0, a) <-> (0, b), then there are paths
		(room, a) <-> (room, b) for every inner room.
		This method pops one link from `updated_outer_links` and uses it to
		update mentioned inner links.
		"""
		node1_index, node2_index = updated_outer_links.pop()
		dist = self._get(node1_index, node2_index)
		door1, door2 = self._get_outer_node_door(node1_index), self._get_outer_node_door(node2_index)
		for room in range(1, self._template.rooms + 1):
			inner_node1_index = self._get_node_index(room, door1)
			inner_node2_index = self._get_node_index(room, door2)
			self._add_road(inner_node1_index, inner_node2_index, updated_outer_links, dist)

	def _add_road(
		self,
		node1_index: int,
		node2_index: int,
		updated_outer_links: _UpdatedLinks_T,
		length: int = 1
	):
		"""Update labyrinth with new road. Update distances if needed.
		Return value indicates if new road made a difference.
		"""
		cur_dist = self._get(node1_index, node2_index)
		if cur_dist is not None and cur_dist <= length:
			self._counter += 1
			return

		if LOG:
			node1, node2 = self._reverse_get_node_index(node1_index), self._reverse_get_node_index(node2_index)
			print(f'dist({node1}, {node2}) = {length} <- {cur_dist}')

		self._set(node1_index, node2_index, length)
		if self._is_outer_node(node1_index) and self._is_outer_node(node2_index):
			updated_outer_links.add((node1_index, node2_index))

		self._propagate(node1_index, node2_index, updated_outer_links, length)

	def _propagate(self, node1_index: int, node2_index: int, updated_outer_links: _UpdatedLinks_T, length: int):
		"""Propagate changes in `self._data` after calling
		self._set(node1_index, node2_index, length).

		Let's denote:
		a, b = node1_index, node2_index
		W[i, j] = self._get(i, j)
		Then general algorithm goes like this:
		for each node pair (i, j):
		    W[i, j] = min(
		        W[i, j],
		        W[i, a] + W[a, b] + W[b, j],
		        W[i, b] + W[b, a] + W[a, j]
		    )
		Obviously, W[a, b] == W[b, a] == length.
		We will check two new possible paths from i to j in two separate steps.

		Imagine two sets of nodes (possibly intersecting):
		A: node a and all nodes connected to it except b.
		B: node b and all nodes connected to it except a.
		We will iterate through each pair of nodes:
		(i from A, j from B)
		Except for (a, b), obviously, because it should have been
		updated before call of this method.
		On each such iteration we will check new possible path from i to j:
		i -> a -> b -> j
		If i is also connected to b and j is connected to a, then at some point
		we will also check:
		j -> a -> b -> i
		which is just reversed:
		i -> b -> a -> j
		thus, completing above algorithm.
		Keep in mind, we will also hit, for example, pair (a, j), checking path:
		a -> a -> b -> j
		Since `self._get(a, a) == 0` we're OK.
		"""
		# Iterate through A:
		for node_i_index in range(self._total_nodes):
			if node_i_index == node2_index:
				self._counter += 1
				continue
			if (left_dist := self._get(node_i_index, node1_index)) is None:
				# No (i, a) connection
				self._counter += 1
				continue

			i_is_outer = self._is_outer_node(node_i_index)
			# Iterate through B:
			for node_j_index in range(self._total_nodes):
				if (
					node_j_index == node1_index
					# Exclude (a, b) pair.
					or node_i_index == node1_index and node_j_index == node2_index
				):
					self._counter += 1
					continue
				if (right_dist := self._get(node2_index, node_j_index)) is None:
					# No (j, b) connection
					self._counter += 1
					continue

				# We can go node_i <-> node1 <-> node2 <-> node_j.
				dist = left_dist + length + right_dist
				cur_dist = self._get(node_i_index, node_j_index)
				if cur_dist is not None and cur_dist <= dist:
					self._counter += 1
					continue

				self._set(node_i_index, node_j_index, dist)
				if i_is_outer and self._is_outer_node(node_j_index):
					updated_outer_links.add((node_i_index, node_j_index))


def main():
	...
	import time
	import draw

	print("Input:")
	template, start, finish = test.get_hard_test(rooms=5, doors=20)
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

	# draw.show(draw.draw_template, template, depth=1, marker=(start, finish))


if __name__ == "__main__":
	main()
