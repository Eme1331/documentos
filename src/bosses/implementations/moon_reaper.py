"""moon_reaper boss."""
from src.bosses.base_boss import BaseBoss
from src.bosses.phase_controller import BossPhase, AttackPattern

_NAMES = {
    "scorpion_mecha": ("Scorpion Mecha Prime", [80,40,20], 450),
    "cryo_sentinel": ("Cryo Sentinel", [60,160,220], 420),
    "mutant_bio_core": ("Mutant Bio-Core", [80,200,80], 480),
    "storm_valkyrie": ("Storm Valkyrie", [200,180,255], 460),
    "magma_colossus": ("Magma Colossus", [255,100,20], 550),
    "neuro_beast": ("Neuro Beast", [180,60,220], 500),
    "moon_reaper": ("Moon Reaper", [200,200,220], 480),
    "void_harbinger": ("Void Harbinger", [80,0,140], 520),
}

class MoonReaper(BaseBoss):
    def __init__(self, x, y, stats, event_bus=None):
        _id = "moon_reaper"
        n, col, hp = _NAMES.get(_id, ("Boss", [200,80,80], 400))
        merged = {"name": n, "hp": hp, "width": 64, "height": 96, "color": col, **stats}
        super().__init__(x, y, merged, event_bus)

    def _setup_phases(self):
        self.phases = [
            BossPhase(1, 1.0, [AttackPattern("attack_1", 1.0, 2.0),
                                AttackPattern("attack_2", 0.7, 4.0)]),
            BossPhase(2, 0.5, [AttackPattern("attack_1", 1.0, 1.5),
                                AttackPattern("attack_2", 1.0, 2.5),
                                AttackPattern("rage_attack", 0.5, 5.0)],
                      speed_multiplier=1.3, damage_multiplier=1.25),
        ]
