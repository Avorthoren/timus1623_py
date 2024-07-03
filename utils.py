import dataclasses


@dataclasses.dataclass(slots=True)
class Pos:
	x: float
	y: float
