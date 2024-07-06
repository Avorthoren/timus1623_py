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

# from __future__ import annotations
import dataclasses
from typing import Iterable, Self

from template import Template, NodeIndex, Link_T


type _Data_T = list[int | None]
type _Locations_T = [list[list[int]]]


class DistMatrix:
	__slots__ = '_template', '_total_nodes', '_data',  # '_LOCATION'

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
		self._fill()

	def get(self, node1: NodeIndex, node2: NodeIndex) -> int | None:
		"""Get the shortest path length between two nodes."""
		return self._get(self._get_node_index(*node1), self._get_node_index(*node2))

	def _get_node_index(self, room: int, door: int) -> int:
		return room * self._template.doors + door

	def _get(self, node1_index: int, node2_index: int) -> int | None:
		"""Get the shortest path length between two nodes."""
		if node1_index == node2_index:
			return 0
		return self._data[self._get_location(node1_index, node2_index)]

	def _set(self, node1_index: int, node2_index: int, dist: int):
		self._data[self._get_location(node1_index, node2_index)] = dist

	def _prepare_locations(self) -> _Locations_T:
		"""Prepare indices of `self._data` elements for each pair of
		DISTINCT node indices.

		NOTE: Turns out, it doesn't make a difference in speed,
		but only uses more memory.
		"""
		return [[
			self._get_location(node1_index, node2_index)
			for node2_index in range(self._total_nodes)
		] for node1_index in range(self._total_nodes)]

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

	def _fill(self):
		"""Fill `self._data` with proper values."""
		# Add template explicit links.
		for node1, node2 in self._template.all_links():
			node1_index = self._get_node_index(*node1)
			node2_index = self._get_node_index(*node2)
			self._add_road(node1_index, node2_index, length=1)

		# Take into consideration implicit 'recursive' links.
		# Will go for maximum of `self._template.doors - 2` iterations, I hope.
		# Complexity: DOORS - 2
		# Inner complexity: DOORS * (DOORS - 1) / 2 * ROOMS * NODES * NODES * NODES
		# Total complexity: (DOORS - 2) * DOORS * (DOORS - 1) / 2 * ROOMS * NODES * NODES * NODES
		# NODES = (ROOMS + 1) * NODES
		while self._update():
			pass

	def _add_road(self, node1_index: int, node2_index: int, length: int) -> bool:
		"""Update labyrinth with new road. Update distances if needed.
		Return value indicates if new road made a difference.
		"""
		cur_dist = self._get(node1_index, node2_index)
		if cur_dist is not None and cur_dist <= length:
			return False

		self._set(node1_index, node2_index, length)
		self._propagate(node1_index, node2_index, length)

		return True

	def _propagate(self, node1_index: int, node2_index: int, length: int):
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
				continue
			if (left_dist := self._get(node_i_index, node1_index)) is None:
				# No connection
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
					continue
				if (right_dist := self._get(node2_index, node_j_index)) is None:
					# No connection
					continue
				# We can go node_i <-> node1 <-> node2 <-> node_j.
				self._add_road(node_i_index, node_j_index, left_dist + length + right_dist)

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
					continue

				for room in range(1, self._template.rooms + 1):
					updated |= self._add_road(
						self._get_node_index(room, door1),
						self._get_node_index(room, door2),
						dist
					)

		return updated


def main():
	...



if __name__ == "__main__":
	main()
