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
from typing import Iterable, Self, NamedTuple

from utils import Pos


# Node index in current context. Example:
# In context of level 0 (outer level of the labyrinth) all outer doors
# will have room index 0, and all doors of k-th inner room will have
# room index k.
class NodeIndex(NamedTuple):
	room: int
	door: int


# Describes input values.
Link_T = tuple[NodeIndex, NodeIndex]


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


# # # # # # # # # # # # # # # # # # # # # #
# Visual representation of the labyrinth  #
# # # # # # # # # # # # # # # # # # # # # #


class DoorTemplate(NamedTuple):
	# Top left boundary rectangular corner.
	tl: Pos
	# Bottom right boundary rectangular corner.
	br: Pos

	def center(self) -> Pos:
		return Pos(
			(self.tl.x + self.br.x) / 2,
			(self.tl.y + self.br.y) / 2,
		)


RoomTemplate = DoorTemplate


class RoadTemplate(NamedTuple):
	# Endpoints of the road
	p1: Pos
	p2: Pos
	# Road width relative to canvas width
	x_relative_width: float


"""How we expect labyrinth to be drawn?
0. Draw outer room border.
1. Draw outer room doors.
2. If `depth`:
	2.1. For each inner room:
		2.1.1. Draw border.
		2.1.2. Draw doors.
		2.1.3. Go recursively to 2 with `depth = depth - 1`.
	2.2. Draw all roads between inner and outer doors.

Therefore we need templates for:
1. Inner rooms.
2. Outer doors.
3. Inner doors.
4. Roads.
"""


class DrawTemplate:
	# Size of boundary rectangular for all inner rooms grid compared to outer room.
	_ZOOM_FACTOR = 0.5
	# Door size compared to smaller canvas edge.
	_DOOR_MAX_RELATIVE_DIAMETER = 0.02
	# Min door size in pixels.
	_DOOR_MIN_DIAMETER = 2
	# Road width compared to smaller door diameter.
	_ROAD_MAX_RELATIVE_WIDTH = 0.25
	# Min road width in pixels.
	_ROAD_MIN_WIDTH = 1
	# Distance between inner rooms compared to their size.
	_ROOMS_MIN_RELATIVE_DISTANCE = 0.2

	@classmethod
	def get_zoom_factor(cls) -> float:
		return cls._ZOOM_FACTOR

	__slots__ = (
		# INPUT VALUES.
		# : Template
		'_logic_template',
		# : float
		# Canvas width and height.
		'_width', '_height',

		# CALCULATED VALUES.
		# : int
		# Total number of columns and rows for inner rooms.
		'_cols', '_rows',

		# : RoomTemplate
		# All rooms in a list in order they are numbered. I.e. first element
		# would be outer room.
		'_rooms',

		# : DoorTemplate
		# All doors in a list in order they are numbered. I.e. if there are
		# N outer doors in template then first N elements will be outer doors,
		# next N elements - doors of the 1st inner room, and so on.
		'_doors',

		# : RoadTemplate
		# All roads between outer and inner doors.
		'_roads',
	)

	@property
	def logic_template(self) -> Template:
		return self._logic_template

	@property
	def width(self) -> float:
		return self._width

	@property
	def height(self) -> float:
		return self._height

	@property
	def cols(self) -> int:
		return self._cols

	@property
	def rows(self) -> int:
		return self._rows

	@property
	def rooms(self) -> tuple[RoomTemplate, ...]:
		return self._rooms

	@property
	def doors(self) -> tuple[DoorTemplate, ...]:
		return self._doors

	@property
	def roads(self) -> tuple[RoadTemplate, ...]:
		return self._roads

	def __init__(self, logic_template: Template, width: float, height: float):
		# Save 'building-values'.
		self._logic_template = logic_template
		self._width = width
		self._height = height

		# Calculate other values. Order matters, because next thing
		# might depend on the previous.
		self._cols, self._rows = self._get_rooms_matrix_size()
		self._rooms = tuple(self._prepare_rooms())
		self._doors = tuple(self._prepare_doors())
		self._roads = tuple(self._prepare_roads())

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
		"""Check how `cols/rows` differs from desired `ratio`."""
		real_ratio = cols / rows
		if ratio > real_ratio:
			return ratio / real_ratio - 1
		else:
			return real_ratio / ratio - 1

	def _prepare_rooms(self) -> Iterable[RoomTemplate]:
		"""Yield outer and all inner rooms shapes."""
		# OUTER ROOM.
		# Simplest way: fill all the space.
		yield RoomTemplate(Pos(0, 0), Pos(1, 1))

		if not self._logic_template.rooms:
			return

		# INNER ROOMS.
		# We create all inner rooms of the same size.
		# Actual ratio (cols/rows) will not usually perfectly match canvas
		# ratio (width/height), therefore if cols/rows < width/height
		# we calculate dimensions according to y-size of rooms.
		if self._cols * self._height < self._rows * self._width:
			count, other_count = self._rows, self._cols
			flipped = True
		else:
			count, other_count = self._cols, self._rows
			flipped = False
		# We have to fit `count` rooms and `count - 1` gaps into `self._ZOOM_FACTOR`.
		room_relative_size = self._ZOOM_FACTOR / (count + self._ROOMS_MIN_RELATIVE_DISTANCE * (count - 1))

		# Gap in orthogonal direction will be bigger.
		if other_count > 1:
			other_gap = (self._ZOOM_FACTOR / room_relative_size - other_count) / (other_count - 1)
		else:
			other_gap = 0

		if flipped:
			x_gap, y_gap = other_gap, self._ROOMS_MIN_RELATIVE_DISTANCE
		else:
			x_gap, y_gap = self._ROOMS_MIN_RELATIVE_DISTANCE, other_gap

		# Distance from the edge of the canvas to the closest room.
		PADDING = (1 - self._ZOOM_FACTOR) / 2
		for room in range(self._logic_template.rooms):
			# TODO: 'flip' is self._width < self._height ..?
			row, col = divmod(room, self._cols)
			top_left = Pos(
				PADDING + (room_relative_size + x_gap) * col,
				PADDING + (room_relative_size + y_gap) * row
			)
			bottom_right = Pos(
				top_left.x + room_relative_size,
				top_left.y + room_relative_size
			)
			yield RoomTemplate(top_left, bottom_right)

	def _prepare_doors(self) -> Iterable[DoorTemplate]:
		"""Yield all doors templates.

		Imagine origin in top left corner, Ox pointer to the right and
		Oy pointed to the left.
		Imagine ellipse inscribed into boundary rectangle.
		Then doors will be evenly distributed on upper half of the ellipse
		from left to right (or on the left half from top to bottom if
		rectangular width < height). Angle between horizontal and first door
		will be half of the angle between consecutive doors.
		"""
		total_doors = self._logic_template.doors
		if not total_doors:
			return

		# Make ratio <= 1.
		if self._width < self._height:
			flipped = True
			ratio = self._width / self._width
			door_x_relative_radius = self._DOOR_MAX_RELATIVE_DIAMETER / 2
			door_y_relative_radius = door_x_relative_radius * ratio
		else:
			# Regular case: usually canvas width is greater.
			flipped = False
			ratio = self._height / self._width
			door_y_relative_radius = self._DOOR_MAX_RELATIVE_DIAMETER / 2
			door_x_relative_radius = door_y_relative_radius * ratio

		# Square of inscribed ellipse eccentricity.
		e2 = 1 - ratio ** 2

		# Prepare abstract templates for doors.
		doors = []
		# Half angle between consecutive doors.
		half_alpha = math.pi / total_doors / 2
		for i in range(total_doors):
			theta = half_alpha * (2 * i + 1)
			center_relative_pos = self._get_door_center_relative_pos(theta, e2, ratio, flipped)
			doors.append(DoorTemplate(
				Pos(center_relative_pos.x - door_x_relative_radius, center_relative_pos.y - door_y_relative_radius),
				Pos(center_relative_pos.x + door_x_relative_radius, center_relative_pos.y + door_y_relative_radius),
			))

		# Finally yield template for doors with respect to rooms templates.
		for room in self._rooms:
			room_relative_width = room.br.x - room.tl.x
			room_relative_height = room.br.y - room.tl.y
			for door in doors:
				top_left = Pos(
					room.tl.x + room_relative_width * door.tl.x,
					room.tl.y + room_relative_height * door.tl.y
				)
				bottom_right = Pos(
					room.tl.x + room_relative_width * door.br.x,
					room.tl.y + room_relative_height * door.br.y
				)
				yield DoorTemplate(top_left, bottom_right)

	@staticmethod
	def _get_door_center_relative_pos(
		theta: float,  # angle to horizontal
		e2: float,     # square of ellipse eccentricity
		ratio: float,  # ellipse short to long semi axis ratio
		flipped: bool  # should we flip x and y in the end (canvas width < height)
	) -> Pos:
		"""Uses ellipse equation in polar coords relative to center.

		Distance from ellipse's center to the point on ellipse:
		r = height/2 / sqrt(1 - e2 * (cos(theta))**2)
		Since ellipse center is in (width/2, height/2) pos:
		x = width/2 - r * cos(t)
		y = height/2 - r * sin(t)
		But we want those coordinates relative to ellipse size:
		(x/width, y/height)
		Hence, the result.

		`e2`, `ratio` and `flipped` are precalculated outside to avoid
		unnecessary calculations.
		e2 = 1 - ratio ** 2
		"""
		sqrt_help = math.sqrt(1 - e2 * math.cos(theta) ** 2)
		x_relative = (1 - math.cos(theta) * ratio / sqrt_help) / 2
		y_relative = (1 - math.sin(theta) / sqrt_help) / 2
		if flipped:
			return Pos(y_relative, x_relative)
		else:
			return Pos(x_relative, y_relative)

	def get_door(self, node_index: NodeIndex) -> DoorTemplate:
		"""Depends on the fact that `_prepare_doors` stores them in exactly this order."""
		return self._doors[node_index.door + node_index.room * self._logic_template.doors]

	def _prepare_roads(self) -> Iterable[RoadTemplate]:
		for node1, node2 in self._logic_template.all_links():
			door1, door2 = self.get_door(node1), self.get_door(node2)
			# Here we assume that door template built in such a way that when
			# it will be calculated in pixels it will have equal width and
			# height. Therefore, it doesn't matter what relative size to choose.
			# But we want go from the smallest door in pair.
			min_door_x_relative_diameter = min(door1.br.x - door1.tl.x, door2.br.x - door2.tl.x)
			road_x_relative_width = min_door_x_relative_diameter * self._ROAD_MAX_RELATIVE_WIDTH

			yield RoadTemplate(door1.center(), door2.center(), road_x_relative_width)


def main():
	template = Template(rooms=3, doors=6, plain_links=(
		(NodeIndex(0, 0), NodeIndex(1, 0)),
		(NodeIndex(0, 2), NodeIndex(2, 5)),
		(NodeIndex(3, 3), NodeIndex(0, 0)),
	))

	draw_t = DrawTemplate(template, 1800, 900)
	print(draw_t.cols)


if __name__ == "__main__":
	main()
