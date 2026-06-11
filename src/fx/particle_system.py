"""Particle system with object pool."""
from __future__ import annotations
import pygame
import random
import math
import settings


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


class Particle:
    __slots__ = ["pos", "vel", "lifetime", "max_lifetime",
                 "color_start", "color_end", "size_start", "size_end", "active"]

    def __init__(self):
        self.active = False
        self.pos = [0.0, 0.0]
        self.vel = [0.0, 0.0]
        self.lifetime = 0.0
        self.max_lifetime = 1.0
        self.color_start = (255, 255, 255)
        self.color_end = (0, 0, 0)
        self.size_start = 4.0
        self.size_end = 0.0

    def reset(self, x, y, vx, vy, lifetime, cs, ce, ss, se):
        self.active = True
        self.pos[:] = [x, y]
        self.vel[:] = [vx, vy]
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color_start = cs
        self.color_end = ce
        self.size_start = ss
        self.size_end = se

    def update(self, dt):
        if not self.active:
            return
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
        self.vel[1] += 200 * dt  # gravity pull

    def draw(self, surface, camera):
        t = 1.0 - (self.lifetime / self.max_lifetime)
        color = _lerp_color(self.color_start, self.color_end, t)
        size = max(1, int(self.size_start + (self.size_end - self.size_start) * t))
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        x, y = int(self.pos[0]), int(self.pos[1])
        if camera:
            x, y = camera.apply_point((x, y))
        s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (size, size), size)
        surface.blit(s, (x - size, y - size))


class ParticleSystem:
    def __init__(self, max_particles=settings.MAX_PARTICLES):
        self._pool = [Particle() for _ in range(max_particles)]
        self._active: list[Particle] = []

    def _acquire(self):
        for p in self._pool:
            if not p.active:
                return p
        return None  # pool exhausted

    def burst(self, x, y, count=12,
              color_start=(255, 200, 0), color_end=(255, 60, 0),
              speed=150.0, lifetime=0.6, size_start=5, size_end=0):
        for _ in range(count):
            p = self._acquire()
            if not p:
                break
            angle = random.uniform(0, math.tau)
            spd = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd - speed * 0.3
            lt = random.uniform(lifetime * 0.7, lifetime)
            p.reset(x, y, vx, vy, lt, color_start, color_end, size_start, size_end)
            self._active.append(p)

    def trail(self, x, y, vx=0, vy=0,
              color_start=(0, 220, 255), color_end=(0, 80, 140),
              lifetime=0.3, size_start=3):
        p = self._acquire()
        if p:
            p.reset(x, y, vx + random.uniform(-20, 20), vy + random.uniform(-20, 20),
                    random.uniform(lifetime * 0.5, lifetime),
                    color_start, color_end, size_start, 0)
            self._active.append(p)

    def update(self, dt):
        for p in self._active:
            p.update(dt)
        self._active = [p for p in self._active if p.active]

    def draw(self, surface, camera=None):
        for p in self._active:
            p.draw(surface, camera)
