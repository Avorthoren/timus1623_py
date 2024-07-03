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

from __future__ import annotations
import dataclasses
from typing import Iterable, Self

from template import Template, Link_T


class Node:
	__slots__ = '_from'

	def __init__(self):
		...


class Labyrinth:
	__slots__ = '_template',  '_nodes'

	def __init__(self, rooms: int, doors: int, links: Iterable[Link_T]):
		self._template = Template.create(rooms, doors, links)
		self._nodes = {}

	def solve(self, start: int, finish: int) -> list[Node] | None:
		...


def main():
	...


if __name__ == "__main__":
	main()
