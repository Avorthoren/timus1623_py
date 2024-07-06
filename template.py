"""
Module for template of fractal labyrinth described in:
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
from typing import Iterable, NamedTuple


# Node index in current context. Example:
# In context of level 0 (outer level of the labyrinth) all outer doors
# will have room index 0, and all doors of k-th inner room will have
# room index k.
class NodeIndex(NamedTuple):
	room: int
	door: int

	def __str__(self):
		return f'({self.room}, {self.door})'


# Describes input values.
type Link_T = tuple[NodeIndex, NodeIndex]


@dataclasses.dataclass(slots=True, frozen=True)
class Template:
	"""Full logic description of the labyrinth."""
	# Total number of INNER rooms. 0 means this is a simple one-room labyrinth.
	rooms: int
	# Total number of OUTER doors.
	doors: int
	# List of connected nodes for each node.
	# If there is link between ni1 and ni2 then:
	# ni2 in links[ni1]
	# ni1 in links[ni2]
	links: dict[NodeIndex, list[NodeIndex]] = dataclasses.field(init=False, default_factory=dict)
	plain_links: dataclasses.InitVar[Iterable[Link_T]]

	def __post_init__(self, plain_links: Iterable[Link_T]):
		for node1, node2 in plain_links:
			self.links.setdefault(node1, []).append(node2)
			self.links.setdefault(node2, []).append(node1)

	def all_links(self) -> Iterable[Link_T]:
		for node1, connected_nodes in self.links.items():
			for node2 in connected_nodes:
				# So that we don't yield same link twice.
				if node2 < node1:
					continue
				yield node1, node2

	def outer_links(self) -> Iterable[Link_T]:
		"""Links between outer doors."""
		for node1, node2 in self.all_links():
			if node1.room or node2.room:
				continue
			yield node1, node2

	def inner_links(self) -> Iterable[Link_T]:
		"""All links except outer links."""
		for node1, node2 in self.all_links():
			if not (node1.room or node2.room):
				continue
			yield node1, node2

	@staticmethod
	def timus_link_repr(plain_link: Link_T) -> str:
		node1, node2 = plain_link
		return f'{node1.room}.{node1.door} - {node2.room}.{node2.door}'

	def timus_repr_gen(self) -> Iterable[str]:
		yield f'{self.doors} {self.rooms}'
		all_links = tuple(self.all_links())

		yield str(len(all_links))
		for link in all_links:
			yield self.timus_link_repr(link)

	def timus_repr(self) -> str:
		return '\n'.join(self.timus_repr_gen())


def main():
	...


if __name__ == "__main__":
	main()
