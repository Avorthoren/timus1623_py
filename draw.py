import tkinter
from typing import Callable, Optional

from template import NodeIndex, Template
from draw_template import RectTemplate, RoadTemplate, DrawTemplate
from utils import Pos
import test


# Window size.
MAX_W, MAX_H = 1850, 1100

type Drawer_T = Callable  # first argument is tkinter.canvas, then any number of arguments, including zero.
type Coord_T = tuple[float, float]


def _draw_room(canvas: tkinter.Canvas, outer_room: RectTemplate, room: RectTemplate) -> RectTemplate:
	"""Draw room by its template and return its pixel representation."""
	room = DrawTemplate.get_rect_from_abstract(room, outer_room)
	canvas.create_oval(*room, outline='lightgrey', dash=(10, 10))

	return room


def _draw_door(canvas: tkinter.Canvas, outer_room: RectTemplate, door: RectTemplate, fill: str = 'lightgrey'):
	door = DrawTemplate.get_rect_from_abstract(door, outer_room, ensure_min=True)
	canvas.create_oval(*door, outline="black", fill=fill)


def _draw_road(canvas: tkinter.Canvas, outer_room: RectTemplate, road: RoadTemplate):
	road = DrawTemplate.get_road_from_abstract(road, outer_room)
	# noinspection PyTypeChecker
	canvas.create_line(road.p1, road.p2, width=road.width, fill="black")


def _draw_level(
	canvas: tkinter.Canvas,
	# Part of the canvas we want to draw in.
	outer_room: RectTemplate,
	template: DrawTemplate,
	depth_left: int
):
	if not depth_left:
		return

	for room_template in template.inner_rooms:
		room = _draw_room(canvas, outer_room, room_template)
		_draw_level(canvas, room, template, depth_left - 1)

	for door_template in template.inner_doors:
		_draw_door(canvas, outer_room, door_template)

	for road_template in template.roads:
		_draw_road(canvas, outer_room, road_template)


def draw_template(
	canvas: tkinter.Canvas,
	logic_template: Template,
	depth: int = 1,  # last level to draw
	marker: Optional[tuple[int, int]] = None  # start and end nodes index
):
	# For some reason it gives values 1 higher from each side (so height and
	# width are both 2 pixels larger) than you request upon creating the canvas,
	# even if you set border width to zero... Apparently I'm missing something.
	top_left = Pos(0, 0)
	bottom_right = Pos(canvas.winfo_reqwidth(), canvas.winfo_reqheight())
	whole_canvas = RectTemplate(top_left, bottom_right)

	# Create drawing template using canvas width and height.
	template = DrawTemplate(
		logic_template,
		bottom_right.x - top_left.x,
		bottom_right.y - top_left.y
	)

	# Draw level-0 room border.
	outer_room = _draw_room(canvas, whole_canvas, template.outer_room)
	# Draw level-0 doors.
	for i, door in enumerate(template.outer_doors):
		_args = [canvas, outer_room, door]
		if marker is not None:
			if i == marker[0]:
				_args.append('blue')
			elif i == marker[1]:
				_args.append('red')
		_draw_door(*_args)

	# Draw everything else recursively.
	_draw_level(canvas, whole_canvas, template, depth_left=depth)


def show(drawer: Drawer_T, *args, **kwargs) -> None:
	main_window = tkinter.Tk()
	canvas = tkinter.Canvas(main_window, bg="white", height=MAX_H, width=MAX_W, borderwidth=0)
	main_window.update()
	canvas.pack()
	main_window.update()

	drawer(canvas, *args, **kwargs)

	main_window.mainloop()


def test_draw(canvas: tkinter.Canvas, x1: float, y1: float, x2: float, y2: float, fill: str) -> None:
	rect = RectTemplate(Pos(x1, y1), Pos(x2, y2))
	canvas.create_line(*rect, fill=fill)


def main():
	logic_template = Template(rooms=3, doors=6, plain_links=(
		(NodeIndex(0, 0), NodeIndex(0, 1)),
		(NodeIndex(0, 0), NodeIndex(1, 0)),
		(NodeIndex(0, 2), NodeIndex(2, 5)),
		(NodeIndex(3, 3), NodeIndex(0, 0)),
		(NodeIndex(1, 4), NodeIndex(1, 5))
	))

	logic_template = Template(rooms=1, doors=12, plain_links=(
		(NodeIndex(0, 0), NodeIndex(1, 1)),
		(NodeIndex(0, 1), NodeIndex(0, 2)),
		(NodeIndex(1, 2), NodeIndex(1, 3)),
		(NodeIndex(0, 3), NodeIndex(0, 4)),
		(NodeIndex(1, 4), NodeIndex(1, 5)),
		(NodeIndex(0, 5), NodeIndex(0, 6)),
		(NodeIndex(1, 6), NodeIndex(1, 7)),
		(NodeIndex(0, 7), NodeIndex(0, 8)),
		(NodeIndex(1, 8), NodeIndex(1, 9)),
		(NodeIndex(0, 9), NodeIndex(0, 10)),
		(NodeIndex(1, 10), NodeIndex(0, 11)),
	))

	logic_template = Template(rooms=0, doors=8, plain_links=(
		(NodeIndex(0, 0), NodeIndex(0, 2)),
		(NodeIndex(0, 1), NodeIndex(0, 3)),
		(NodeIndex(0, 2), NodeIndex(0, 4)),
		(NodeIndex(0, 3), NodeIndex(0, 5)),
		(NodeIndex(0, 4), NodeIndex(0, 6)),
		(NodeIndex(0, 5), NodeIndex(0, 7)),
		(NodeIndex(0, 6), NodeIndex(0, 0)),
		(NodeIndex(0, 7), NodeIndex(0, 1)),
	))

	# Interesting
	logic_template = Template(rooms=2, doors=4, plain_links=(
		(NodeIndex(0, 0), NodeIndex(1, 0)),
		(NodeIndex(0, 1), NodeIndex(1, 0)),
		(NodeIndex(1, 1), NodeIndex(1, 2)),
		(NodeIndex(1, 2), NodeIndex(0, 3)),
		(NodeIndex(2, 3), NodeIndex(0, 3)),
		(NodeIndex(2, 2), NodeIndex(0, 2)),
		(NodeIndex(2, 0), NodeIndex(0, 2)),
	))

	# Interesting
	logic_template = Template(rooms=2, doors=4, plain_links=(
		(NodeIndex(0, 0), NodeIndex(1, 0)),
		(NodeIndex(0, 1), NodeIndex(1, 0)),
		(NodeIndex(1, 1), NodeIndex(1, 3)),
		(NodeIndex(1, 3), NodeIndex(0, 2)),
		(NodeIndex(1, 2), NodeIndex(2, 3)),
		(NodeIndex(2, 1), NodeIndex(2, 3)),
		(NodeIndex(2, 2), NodeIndex(0, 3)),
	))

	# Interesting. Simple-hard test.
	logic_template = Template(rooms=2, doors=4, plain_links=(
		(NodeIndex(0, 0), NodeIndex(1, 0)),
		(NodeIndex(1, 0), NodeIndex(0, 1)),
		(NodeIndex(1, 1), NodeIndex(0, 2)),
		(NodeIndex(1, 2), NodeIndex(0, 3)),
		(NodeIndex(0, 2), NodeIndex(2, 0)),
		# (NodeIndex(0, 2), NodeIndex(3, 0)),
		# (NodeIndex(0, 2), NodeIndex(4, 0)),
	))
	start, finish = 0, 3

	# # Interesting. Simple-hard unsolvable test.
	# logic_template = Template(rooms=2, doors=5, plain_links=(
	# 	(NodeIndex(0, 0), NodeIndex(0, 1)),
	# 	(NodeIndex(0, 1), NodeIndex(0, 2)),
	# 	(NodeIndex(0, 2), NodeIndex(0, 3)),
	# 	(NodeIndex(0, 1), NodeIndex(1, 2)),
	# 	(NodeIndex(0, 3), NodeIndex(2, 2)),
	# 	(NodeIndex(1, 3), NodeIndex(1, 4)),
	# 	(NodeIndex(2, 3), NodeIndex(2, 4)),
	# 	# (NodeIndex(0, 2), NodeIndex(3, 0)),
	# 	# (NodeIndex(0, 2), NodeIndex(4, 0)),
	# ))
	#
	# logic_template, start, finish = test.get_hard_unsolvable_test(2, 5)

	show(draw_template, logic_template, depth=4, marker=(start, finish))


if __name__ == "__main__":
	main()
