"""Ranged attack behavior."""
class RangedAttackBehavior:
    def __init__(self, cooldown: float = 2.0, speed: float = 300.0, damage: int = 10) -> None:
        self.cooldown = cooldown
        self.projectile_speed = speed
        self.damage = damage
        self._timer = 0.0

    def update(self, transform, target_transform, entity_manager, dt: float) -> None:
        self._timer -= dt
        if self._timer <= 0 and target_transform:
            self._timer = self.cooldown
            self._fire(transform, target_transform, entity_manager)

    def _fire(self, tr, target_tr, em) -> None:
        from src.combat.projectile import Projectile
        dx = target_tr.position.x - tr.position.x
        dy = target_tr.position.y - tr.position.y
        length = max((dx*dx + dy*dy) ** 0.5, 1)
        vx = dx / length * self.projectile_speed
        vy = dy / length * self.projectile_speed
        proj = Projectile(tr.position.x, tr.position.y, vx, vy,
                          self.damage, owner_tag="enemy",
                          color=(220, 60, 60))
        if em:
            em.add(proj, "projectiles")
