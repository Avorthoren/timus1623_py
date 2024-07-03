import functools
import math
import random
import tkinter
from typing import Callable, Protocol, Optional

from template import Template


# Window size.
MAX_W, MAX_H = 1800-2, 600-2
# Precalculated vector for cluster's hitbox diagonal.
# HALF_DIAG = vector.Vector2D(core.RADIUS, core.RADIUS)
# # Precalculated vector for drawing small circle at pos of first object of the
# # cluster.
# INST_HALF_DIAG = vector.Vector2D(3, 3)
# # Color of this small circle.
# CLUSTER_ORIGIN_COLOR = "black"  # `None` for same as color of the cluster.
# # For clusters colors.
# CIRCLE_COLORS = "red", "green", "blue", "orange", "magenta", "cyan", "yellow"
# # For drawing grid.
# GRID_STEP = 50  # px
#
#
# def draw_one(
# 	pos: core.Pos_T,
# 	canvas: tkinter.Canvas,
# 	color: str,
# 	half_diag: core.Pos_T
# ) -> None:
# 	top_left = pos - half_diag
# 	bottom_right = pos + half_diag
# 	canvas.create_oval(
# 		top_left.x,
# 		top_left.y,
# 		bottom_right.x,
# 		bottom_right.y,
# 		outline=color
# 	)
#
#
# def draw_object(
# 	obj: core.Obj_T,
# 	canvas: tkinter.Canvas,
# 	color: str,
# 	pointers: bool,
# 	cardinality: bool,
# 	half_diag: core.Pos_T
# ) -> None:
# 	is_atomic = obj.n == 1
# 	cluster_origin_color = color if CLUSTER_ORIGIN_COLOR is None else CLUSTER_ORIGIN_COLOR
#
# 	draw_one(obj.pos, canvas, color, half_diag)
#
# 	if cardinality:
# 		canvas.create_text(
# 			round(obj.pos.x),
# 			round(obj.pos.y),
# 			fill=color,
# 			font=f"cutive {round(4 * core.RADIUS / 5)}",
# 			text=str(obj.n)
# 		)
#
# 	if is_atomic:
# 		origin = obj
# 	else:
# 		origin = next(iter(obj))
# 		if pointers:
# 			for sub_obj in obj:
# 				canvas.create_line(
# 					obj.pos.x,
# 					obj.pos.y,
# 					sub_obj.pos.x,
# 					sub_obj.pos.y,
# 					fill=color
# 				)
#
# 	draw_one(origin.pos, canvas, cluster_origin_color, INST_HALF_DIAG)
#
#
# def _draw(
# 	objects: core.Objs_T,
# 	canvas: tkinter.Canvas,
# 	random_colors: bool,
# 	pointers: bool,
# 	cardinality: bool
# ) -> None:
# 	_objects = objects.values() if isinstance(objects, dict) else objects
# 	half_diag = vector.Vector2D(core.RADIUS, core.RADIUS)
# 	for obj in _objects:
# 		color = random.choice(CIRCLE_COLORS) if random_colors else CIRCLE_COLORS[obj.i - 1]
# 		draw_object(obj, canvas, color, pointers, cardinality, half_diag)
#
#
# def draw_grid(canvas: tkinter.Canvas, step: core.Coord_T = GRID_STEP, color: str = "black"):
# 	for x in range(0, MAX_W, step):
# 		canvas.create_line(x, 0, x, MAX_H, fill=color)
#
# 	for y in range(0, MAX_H, step):
# 		canvas.create_line(0, y, MAX_W, y, fill=color)


Drawer_T = Callable  # first argument is tkinter.canvas, then any number of arguments, including zero.
Coord_T = tuple[float, float]


def show(drawer: Drawer_T, *args, **kwargs) -> None:
	main_window = tkinter.Tk()
	canvas = tkinter.Canvas(main_window, bg="white", height=MAX_H, width=MAX_W, borderwidth=0)
	main_window.update()
	canvas.pack()
	main_window.update()

	drawer(canvas, *args, **kwargs)

	# print(canvas.winfo_y(), canvas.winfo_x())
	# print(canvas.winfo_height(), canvas.winfo_width())
	# print(canvas.winfo_reqheight(), canvas.winfo_reqwidth())

	main_window.mainloop()


def test_draw(canvas: tkinter.Canvas, x1: float, y1: float, x2: float, y2: float, fill: str) -> None:
	canvas.create_line(x1, y1, x2, y2, fill=fill)


def _get_rooms_matrix_size(canvas_width: float, canvas_height: float, rooms: int) -> tuple[int, int]:
	"""Get rectangular arrangement of rooms that is the closest to canvas ration.

	For example, if canvas is 1800x700, and we have 22 rooms, we will arrange
	them in 8x3 grid. First two rows will have 8 rooms, last row - 6 rooms.
	Actually, this function only gives grid dimensions, we may decide to align
	rooms in the last row to the center.
	"""
	if not rooms:
		return 0, 0

	def _ratio_defect(_ratio: float, _cols: int, _rows: int):
		_real_ratio = _cols / _rows
		if _ratio > _real_ratio:
			return _ratio / _real_ratio - 1
		else:
			return _real_ratio / _ratio - 1

	# Search for `cols` and `rows` such that:
	# rows * cols >= rooms
	# _ratio_defect -> min
	# Simplified explanation: we add 'approximate' equation:
	# ratio = cols / rows
	# From which (and the first one) we get:
	# rows * ratio >= rooms / rows
	# rows ~ sqrt(rooms / ratio)
	if canvas_width < canvas_height:
		canvas_ratio = canvas_height / canvas_width
		flipped = True
	else:
		canvas_ratio = canvas_width / canvas_height
		flipped = False

	rows_base = round(math.sqrt(rooms / canvas_ratio))
	cols, rows = 1, 1
	# Search for optimal number of rows around `rows_base`: +- 1.
	for rows_cur in range(max(rows_base - 1, 1), rows_base + 2):
		cols_cur = (rooms - 1) // rows_cur + 1
		if _ratio_defect(canvas_ratio, cols_cur, rows_cur) < _ratio_defect(canvas_ratio, cols, rows):
			cols, rows = cols_cur, rows_cur

	return (rows, cols) if flipped else (cols, rows)


def _draw_level(
	canvas: tkinter.Canvas,
	template: Template,
	depth_left: int,
	zoom: float,
	top_left: Coord_T,
	bottom_right: Coord_T,
	outer_doors: Optional[list[Coord_T]] = None
) -> list[...]:
	# Doors of different inner rooms can be connected!
	...


def draw_template(
	canvas: tkinter.Canvas,
	template: Template,
	depth: int = 1,    # last level to draw
	zoom: float = 0.5  # size of boundary rectangular for all inner rooms grid compared to outer room
):
	# For some reason it gives values 1 higher from each side (so height and
	# width are both 2 pixels larger) than you request upon creating the canvas,
	# even if you set border width to zero...
	x_max, y_max = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
	cols, rows = _get_rooms_matrix_size(x_max, y_max, template.rooms)


def main():
	show(test_draw, 10.5, 10, MAX_W-100, MAX_H-10, fill="black")
	# W, H = 1800, 700
	# print(W / H)
	# for rooms in range(0, 60):
	# 	print(rooms, _get_rooms_matrix_size(W, H, rooms))


if __name__ == "__main__":
	main()
