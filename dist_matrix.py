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
	__slots__ = '_template', '_total_nodes', '_data', '_LOCATION'

	def __init__(self, template: Template):
		self._template = template
		# Get index of the last node.
		self._total_nodes = self._get_node_index(template.rooms + 1, template.doors)
		# Flat version of one 'half' of square matrix of `_total_nodes` size,
		# except for main diagonal.
		self._data: _Data_T = [None] * (self._total_nodes * (self._total_nodes - 1) >> 1)

		self._LOCATION: _Locations_T = self._prepare_locations()
		# Calculate all distances:
		self._fill()

	def get(self, node1: NodeIndex, node2: NodeIndex) -> int | None:
		"""Get the shortest path length between two nodes."""
		return self._get(self._get_node_index(*node1), self._get_node_index(*node2))

	def _get_node_index(self, room: int, door: int) -> int:
		return room * self._template.doors + door

	def _get(self, node1_index: int, node2_index: int) -> int | None:
		"""Get the shortest path length between two nodes."""
		# TODO: use self._LOCATION
		return self._data[self._get_location(node1_index, node2_index)]

	def _set(self, node1_index: int, node2_index: int, dist: int):
		# TODO: use self._LOCATION
		self._data[self._get_location(node1_index, node2_index)] = dist

	def _prepare_locations(self) -> _Locations_T:
		"""Prepare indices of `self._data` elements for each pair of node indices.
		WARNING: a pair of equal indices should never be used.
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
		# Add template links.
		for node1, node2 in self._template.all_links():
			node1_index = self._get_node_index(*node1)
			node2_index = self._get_node_index(*node2)
			self._add_road(node1_index, node2_index)

		# Take into consideration implicit 'recursive' links.
		# Will go for maximum of `self._template.doors - 2` iterations, I hope.
		while self._update():
			pass

	def _add_road(self, node1_index: int, node2_index: int, length: int = 1):
		"""Update labyrinth with new road. Update distances if needed."""
		cur_dist = self._get(node1_index, node2_index)
		if cur_dist is not None and cur_dist <= length:
			return

		self._set(node1_index, node2_index, length)
		self._propagate(node1_index, node2_index)
		self._propagate(node2_index, node1_index)

	def _propagate(self, from_node_index: int, to_node_index: int):
		...

	def _update(self) -> bool:
		...

		return True


def main():
	...


if __name__ == "__main__":
	main()
