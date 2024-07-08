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

type _Data_T = list[list[int | None]]
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

		self._data: _Data_T = self._get_empty_matrix()

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
		if node1_index < node2_index:
			return self._data[node1_index][node2_index]
		else:
			return self._data[node2_index][node1_index]

	def _set(self, node1_index: int, node2_index: int, dist: int):
		if node1_index < node2_index:
			self._data[node1_index][node2_index] = dist
		else:
			self._data[node2_index][node1_index] = dist

	def _get_empty_matrix(self) -> _Data_T:
		n = self._total_nodes
		data: _Data_T = [[None] * n for _ in range(n)]
		for i in range(n):
			data[i][i] = 0

		return data

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

		Всего TOTAL_NODES = (ROOMS + 1) * DOORS нод.
		Я храню квадратную матрицу "расстояний", но использую только половину:
		W[i, j] для i <= j.
		Инициирую её "бесконечными" значениями, а главную диагональ - нулями.

		Также я храню множество U пар дверей внешней комнаты, "расстояние"
		между которыми было обновлено. Изначально оно пусто.

		ВЕСЬ_АЛГОРИТМ:
			Для всёх ребёр (a, b) из входящих данных:
				ДОБАВИТЬ_ДОРОГУ(a, b, 1)  # длина 1

			Пока U не пусто:
				ОБНОВИТЬ()

		=============================================
		ОБНОВИТЬ():
			Изъять любой элемент (a, b) из U
			Для каждой внутренней комнаты (всего их ROOMS):
				Взять соответствующую пару дверей (i, j)
				ДОБАВИТЬ_ДОРОГУ(i, j, W[a, b])

		=============================================
		ДОБАВИТЬ_ДОРОГУ(a, b, dist):
			Если W[a, b] <= dist:
				Выйти

			W[a, b] = dist
			Если (a, b) пара внешних дверей:
				Добавить (a, b) в U

			РАСПРОСТРАНИТЬ(a, b, dist)

		=============================================
		РАСПРОСТРАНИТЬ(a, b, dist):
			Для всех нод i кроме b:
				Если W[i, a] "бесконечна":
					Перейти к следующей i
				Для всех нод j кроме a:
					Если (i, j) == (a, b):
						Перейти к следующей j
					Если W[b, j] "бесконечна":
						Перейти к следующей j

					ij_dist = W[i, a] + dist + W[b, j]
					Если W[i, j] <= ij_dist:
						Перейти к следующей j

					W[i, j] = ij_dist
					Если (i, j) пара внешних дверей:
						Добавить (i, j) в U
		"""
		updated_outer_links: _UpdatedLinks_T = set()
		# Add template explicit links.
		for node1, node2 in self._template.all_links():
			node1_index = self._get_node_index(*node1)
			node2_index = self._get_node_index(*node2)
			self._add_road(node1_index, node2_index, updated_outer_links)

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
			return

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
				continue
			if (left_dist := self._get(node_i_index, node1_index)) is None:
				# No (i, a) connection
				continue

			i_is_outer = self._is_outer_node(node_i_index)
			# Iterate through B:
			for node_j_index in range(self._total_nodes):
				if (
					node_j_index == node1_index
					# Exclude (a, b) pair.
					or node_i_index == node1_index and node_j_index == node2_index
				):
					continue
				if (right_dist := self._get(node2_index, node_j_index)) is None:
					# No (j, b) connection
					continue

				# We can go node_i <-> node1 <-> node2 <-> node_j.
				dist = left_dist + length + right_dist
				cur_dist = self._get(node_i_index, node_j_index)
				if cur_dist is not None and cur_dist <= dist:
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
