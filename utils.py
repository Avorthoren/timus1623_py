from typing import NamedTuple


class Pos(NamedTuple):
	x: float = 0
	y: float = 0


def main():
	t = Pos(42, 73)
	print(isinstance(t, tuple))


if __name__ == "__main__":
	main()
