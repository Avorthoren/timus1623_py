"""
https://acm.timus.ru/problem.aspx?space=1&num=1623

'Compiled' version for timus: all in one file.

UPDATE: still too slow, only c++ solution worked.
"""
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

	@classmethod
	def from_str(cls, s: str):
		room, door = map(int, s.split('.'))
		return cls(room, door)


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

	@staticmethod
	def links_from_input(total_links: int):
		for _ in range(total_links):
			s1, s2 = input().split(' - ')
			yield NodeIndex.from_str(s1), NodeIndex.from_str(s2)

	@classmethod
	def from_input(cls):
		doors, rooms = map(int, input().split())
		links = int(input())
		return cls(rooms, doors, cls.links_from_input(links))


type _Data_T = list[list[int | None]]
type _UpdatedLinks_T = set[tuple[int, int]]


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
		self._total_nodes = (template.rooms + 1) * template.doors

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
		"""Fill `self._data` with proper values."""
		updated_outer_links: _UpdatedLinks_T = set()
		# Add template explicit links.
		for node1, node2 in self._template.all_links():
			node1_index = self._get_node_index(*node1)
			node2_index = self._get_node_index(*node2)
			self._set(node1_index, node2_index, dist=1)
			if self._is_outer_node(node1_index) and self._is_outer_node(node2_index):
				updated_outer_links.add((node1_index, node2_index))

		# Eventually `self._data` will 'converge' to final value.
		self._update(updated_outer_links)
		while updated_outer_links:
			self._update(updated_outer_links)

	def _update(self, updated_outer_links: _UpdatedLinks_T):
		"""Update `self._data` using recursive knowledge.

		If there is path (0, a) <-> (0, b), then there are paths
		(room, a) <-> (room, b) for every inner room.
		This method pops one link from `updated_outer_links` and uses it to
		update mentioned inner links.
		"""
		for node1_index, node2_index in updated_outer_links:
			dist = self._get(node1_index, node2_index)
			door1, door2 = self._get_outer_node_door(node1_index), self._get_outer_node_door(node2_index)
			for room in range(1, self._template.rooms + 1):
				inner_node1_index = self._get_node_index(room, door1)
				inner_node2_index = self._get_node_index(room, door2)
				self._set(inner_node1_index, inner_node2_index, dist)

		updated_outer_links.clear()
		self._floyd_warshall(updated_outer_links)

	def _floyd_warshall(self, updated_outer_links: _UpdatedLinks_T):
		"""Recalculate `self._data` using Floyd-Warshall algorithm."""
		for bridge_index in range(self._total_nodes):
			for node_i_index in range(self._total_nodes - 1):
				if node_i_index == bridge_index:
					continue
				if (left_dist := self._get(node_i_index, bridge_index)) is None:
					continue

				i_is_outer = self._is_outer_node(node_i_index)
				for node_j_index in range(node_i_index + 1, self._total_nodes):
					if node_j_index == bridge_index:
						continue
					if (right_dist := self._get(bridge_index, node_j_index)) is None:
						continue

					# We can go node_i <-> bridge <-> node_j.
					dist = left_dist + right_dist
					cur_dist = self._get(node_i_index, node_j_index)
					if cur_dist is not None and cur_dist <= dist:
						continue

					self._set(node_i_index, node_j_index, dist)
					if i_is_outer and self._is_outer_node(node_j_index):
						updated_outer_links.add((node_i_index, node_j_index))


def main():
	template = Template.from_input()
	# Should comply with DistMatrix._get_node_index
	start, finish = map(int, input().split())
	start, finish = NodeIndex(0, start), NodeIndex(0, finish)

	dist_matrix = DistMatrix(template)

	if (dist := dist_matrix.get(start, finish)) is None:
		print('no solution')
	else:
		print(dist)


if __name__ == "__main__":
	main()
