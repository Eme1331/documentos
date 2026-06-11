"""Final boss: NEXUS PRIME — 3 phases."""
from src.bosses.base_boss import BaseBoss
from src.bosses.phase_controller import BossPhase, AttackPattern


class NexusPrime(BaseBoss):
    def __init__(self, x, y, stats, event_bus=None):
        merged = {"name": "NEXUS PRIME", "hp": 1200, "width": 96, "height": 128,
                  "color": [60, 0, 180], **stats}
        super().__init__(x, y, merged, event_bus)

    def _setup_phases(self):
        self.phases = [
            BossPhase(1, 1.0, [
                AttackPattern("melee_combo", 1.0, 1.8),
                AttackPattern("plasma_barrage", 0.8, 3.5),
                AttackPattern("shield_bash", 0.5, 5.0),
            ], movement_behavior="aggressive"),
            BossPhase(2, 0.65, [
                AttackPattern("screen_missiles", 1.0, 2.0),
                AttackPattern("quantum_slash", 1.0, 2.5),
                AttackPattern("emp_blast", 0.6, 6.0),
            ], speed_multiplier=1.4, damage_multiplier=1.3,
               movement_behavior="aerial"),
            BossPhase(3, 0.3, [
                AttackPattern("pillar_sync_1", 1.0, 1.5),
                AttackPattern("pillar_sync_2", 1.0, 1.5),
                AttackPattern("pillar_sync_3", 1.0, 1.5),
                AttackPattern("singularity_collapse", 0.3, 10.0),
            ], speed_multiplier=1.6, damage_multiplier=1.5,
               movement_behavior="phase"),
        ]
