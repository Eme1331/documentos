"""Flying (sinusoidal float) behavior."""
import math

class FlyingBehavior:
    def __init__(self, amplitude: float = 30.0, frequency: float = 1.0) -> None:
        self.amplitude = amplitude
        self.frequency = frequency
        self._t = 0.0
        self._base_y: float | None = None

    def update(self, transform, dt: float) -> None:
        if self._base_y is None:
            self._base_y = transform.position.y
        self._t += dt
        transform.position.y = self._base_y + math.sin(self._t * self.frequency * 2 * math.pi) * self.amplitude
        transform.velocity.y = 0
