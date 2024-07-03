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
import math
from typing import Iterable, Self

from utils import Pos

# Node index in current context. First number is index of the room while
# second is index of the door. Example:
# In context of level 0 (outer level of the labyrinth) all outer doors
# will have the first index 0, and all doors of k-th inner room will have
# the first index k.
NodeIndex_T = tuple[int, int]

# Describes input values.
Link_T = tuple[NodeIndex_T, NodeIndex_T]


@dataclasses.dataclass(slots=True, frozen=True)
class Template:
	"""Full description of the labyrinth."""
	# Total number of INNER rooms. 0 means this is a simple one-room labyrinth.
	rooms: int
	doors: int
	# List of connected nodes for each node.
	# If there is link between ni1 and ni2 then:
	# ni2 in links[ni1]
	# ni1 in links[ni2]
	links: dict[NodeIndex_T, list[NodeIndex_T]] = dataclasses.field(init=False, default_factory=dict)
	plain_links: dataclasses.InitVar[Iterable[Link_T]]

	def __post_init__(self, plain_links: Iterable[Link_T]):
		for node1_index, node2_index in plain_links:
			self.links.setdefault(node1_index, []).append(node2_index)
			self.links.setdefault(node2_index, []).append(node1_index)

	def all_links(self) -> Iterable[Link_T]:
		for node1, connected_nodes in self.links.items():
			for node2 in connected_nodes:
				if node2 >= node1:
					yield node1, node2


@dataclasses.dataclass(slots=True, frozen=True)
class DoorTemplate:
	# Top left boundary rectangular corner.
	tl: Pos
	# Bottom right boundary rectangular corner.
	br: Pos


InnerRoomTemplate = DoorTemplate


class DrawTemplate:
	# Size of boundary rectangular for all inner rooms grid compared to outer room.
	_ZOOM_FACTOR = 0.5
	# Door size compared to smaller canvas edge.
	_DOOR_MAX_RELATIVE_DIAMETER = 0.01
	# Min door size in pixels.
	_DOOR_MIN_DIAMETER = 2
	# Road width compared to smaller door diameter.
	_ROAD_MAX_RELATIVE_WIDTH = 0.25
	# Min road width in pixels.
	_ROAD_MIN_WIDTH = 1

	@classmethod
	def get_zoom_factor(cls) -> float:
		return cls._ZOOM_FACTOR

	__slots__ = (
		'_logic_template', '_width', '_height',
		# Calculated:
		'_cols', '_rows',
		'_'
	)

	def __init__(self, logic_template: Template, width: float, height: float):
		self._logic_template = logic_template
		self._width = width
		self._height = height

		self._cols, self._rows = self._get_rooms_matrix_size()



	def _get_rooms_matrix_size(self) -> tuple[int, int]:
		"""Get rectangular arrangement of rooms that is the closest to
		canvas ratio: number of columns and number of rows.

		For example, if canvas is 1800x700, and we have 22 rooms, we will arrange
		them in 8x3 grid. First two rows will have 8 rooms, last row - 6 rooms.
		Actually, this function only gives grid dimensions, we may decide to align
		rooms in the last row to the center.
		"""
		rooms = self._logic_template.rooms
		if not rooms:
			return 0, 0

		# Search for `cols` and `rows` such that:
		# rows * cols >= rooms
		# _ratio_defect -> min
		# Simplified explanation: we add 'approximate' equation:
		# ratio = cols / rows
		# From which (and the first one) we get:
		# rows * ratio >= rooms / rows
		# rows ~ sqrt(rooms / ratio)
		if self._width < self._height:
			canvas_ratio = self._height / self._width
			flipped = True
		else:
			canvas_ratio = self._width / self._height
			flipped = False

		rows_base = round(math.sqrt(rooms / canvas_ratio))
		cols, rows = 1, 1
		# Search for optimal number of rows around `rows_base`: +- 1.
		for rows_cur in range(max(rows_base - 1, 1), rows_base + 2):
			cols_cur = (rooms - 1) // rows_cur + 1
			if self._ratio_defect(canvas_ratio, cols_cur, rows_cur) < self._ratio_defect(canvas_ratio, cols, rows):
				cols, rows = cols_cur, rows_cur

		return (rows, cols) if flipped else (cols, rows)

	@staticmethod
	def _ratio_defect(ratio: float, cols: int, rows: int):
		_real_ratio = cols / rows
		if ratio > _real_ratio:
			return ratio / _real_ratio - 1
		else:
			return _real_ratio / ratio - 1



def main():
	template = Template(rooms=3, doors=6, plain_links=(
		((0, 0), (1, 0)),
		((0, 2), (2, 5)),
		((3, 3), (0, 0)),
	))

	draw_t = DrawTemplate(template, 100, 200)
	print(draw_t.cols)


if __name__ == "__main__":
	main()
