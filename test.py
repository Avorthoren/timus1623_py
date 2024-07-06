from collections import namedtuple
from typing import Type, NamedTuple, Iterable

from template import Template, Link_T, NodeIndex


class Test(NamedTuple):
	x: float
	y: float

	def hello(self):
		print(self.x, self.y)


def hard_test_links_gen(rooms: int, doors: int) -> Iterable[Link_T]:
	yield NodeIndex(0, 0), NodeIndex(1, 0)
	for d in range(doors - 1):
		yield NodeIndex(1, d), NodeIndex(0, d + 1)
	for r in range(2, rooms + 1):
		yield NodeIndex(0, doors - 2), NodeIndex(r, 0)


def get_hard_test(rooms: int = 5, doors: int = 20, echo: bool = True) -> tuple[Template, int, int]:
	template = Template(rooms, doors, hard_test_links_gen(rooms, doors))
	start, finish = 0, doors - 1

	if echo:
		print(template.timus_repr())
		print(start, finish)

	return template, start, finish


def hard_unsolvable_test_links_gen(rooms: int, doors: int) -> Iterable[Link_T]:
	# Connect all outer doors except the last one.
	for d in range(doors - 2):
		yield NodeIndex(0, d), NodeIndex(0, d + 1)
	# Line above made all doors in each of inner rooms also connected, except
	# the last door for each one of them. We can fix that still leaving last
	# door of outer room isolated.
	for r in range(1, rooms + 1):
		yield NodeIndex(r, doors - 2), NodeIndex(r, doors - 1)
	# Connect outer room to each inner room, thus, making all doors accessible,
	# except the last door of outer room.
	bridge_outer_door = (doors - 1) >> 1  # any except `doors - 1`
	bridge_inner_door = (doors - 1) >> 1  # any
	for r in range(1, rooms + 1):
		yield NodeIndex(0, bridge_outer_door), NodeIndex(r, bridge_inner_door)


def get_hard_unsolvable_test(rooms: int = 5, doors: int = 20, echo: bool = True) -> tuple[Template, int, int]:
	template = Template(rooms, doors, hard_unsolvable_test_links_gen(rooms, doors))
	start, finish = 0, doors - 1

	if echo:
		print(template.timus_repr())
		print(start, finish)

	return template, start, finish


def main():
	# get_hard_test(5, 20)
	get_hard_unsolvable_test(5, 20)


if __name__ == "__main__":
	main()
