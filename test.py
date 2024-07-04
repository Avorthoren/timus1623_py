from collections import namedtuple
from typing import Type, NamedTuple


class Test(NamedTuple):
	x: float
	y: float

	def hello(self):
		print(self.x, self.y)


def main():
	t = Test(4, 6)
	t.hello()


if __name__ == "__main__":
	main()
