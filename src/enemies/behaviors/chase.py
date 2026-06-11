"""Chase behavior."""
class ChaseBehavior:
    def __init__(self, speed: float = 100.0) -> None:
        self.speed = speed

    def update(self, transform, target_transform, dt: float) -> None:
        if not target_transform:
            return
        dx = target_transform.position.x - transform.position.x
        transform.velocity.x = self.speed * (1 if dx > 0 else -1)
        transform.facing = 1 if dx > 0 else -1
