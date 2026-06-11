"""Patrol behavior: back and forth."""
class PatrolBehavior:
    def __init__(self, origin_x: float, dist: float = 120.0, speed: float = 70.0) -> None:
        self.origin_x = origin_x
        self.dist = dist
        self.speed = speed
        self.direction = 1

    def update(self, transform, dt: float) -> None:
        transform.velocity.x = self.speed * self.direction
        dx = transform.position.x - self.origin_x
        if abs(dx) > self.dist:
            self.direction *= -1
            transform.facing = self.direction
