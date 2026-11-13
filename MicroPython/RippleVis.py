from random import randrange, seed

from fastcircle import bresenhams_circle
from hsv import hsv_to_rgb_255


class Ripple:
    def __init__(self, x: int, y: int, bg_color_hsv: list[int]):
        self.x: int = x
        self.y: int = y
        self.bg_color_hsv: list[int] = bg_color_hsv

        self.speed: float = 12.0
        self.radius: float = 0.0
        self.max_radius: float = 32.0
        self.trail_offset: float = 4.0

    def update(self, delta: float) -> bool:
        self.radius += delta * self.speed
        return self.radius - self.trail_offset < self.max_radius

    def draw(self, display) -> None:
        base_h, base_s, base_v = self.bg_color_hsv

        # Primary ring
        if self.radius < self.max_radius:
            progress: float = min(1.0, self.radius / self.max_radius)
            fade: float = 1.0 - progress

            s: int = int(base_s * progress)
            v: int = int(base_v + (45 * fade))
            display.set_pen(display.create_pen(*hsv_to_rgb_255(base_h, s, v)))
            bresenhams_circle(display, self.x, self.y, int(self.radius))

        # Secondary ring
        trail_radius: float = self.radius - self.trail_offset
        if 0 < trail_radius < self.max_radius:
            trail_progress: float = min(1.0, trail_radius / self.max_radius)
            trail_fade: float = 1.0 - trail_progress

            s_trail: int = int(base_s * (0.4 + 0.6 * trail_progress))
            v_trail: int = int(base_v + (22 * trail_fade))
            display.set_pen(display.create_pen(*hsv_to_rgb_255(base_h, s_trail, v_trail)))
            bresenhams_circle(display, self.x, self.y, int(trail_radius))


class RippleVis:
    def __init__(self, width: int, height: int):
        self.vis_width: int = width
        self.vis_height: int = height
        self.vis_start_x: int = width // 8
        self.vis_end_x: int = self.vis_start_x * 7
        self.vis_start_y: int = height // 8
        self.vis_end_y: int = self.vis_start_y * 7

        self.bg_color_hsv: list[int] = [220, 60, 5]
        self.bg_color_rgb: tuple[int, int, int] = hsv_to_rgb_255(*self.bg_color_hsv)

        self.max_ripples: int = 5
        self.ripple_count: int = 0
        self.ripples: list[Ripple] = []
        self.ms_since_last_ripple: float = 0.0
        self.next_ripple_after: int = 0

    def _add_ripple(self) -> None:
        self.ripple_count += 1
        self.ms_since_last_ripple = 0.0
        self.next_ripple_after = randrange(100, 750)
        x: int = randrange(self.vis_start_x, self.vis_end_x)
        y: int = randrange(self.vis_start_y, self.vis_end_y)
        self.ripples.append(Ripple(x, y, self.bg_color_hsv))

    def reset(self) -> None:
        self._add_ripple()

    def update(self, delta: float, display, accel) -> None:
        # Fill background
        display.set_pen(display.create_pen(*self.bg_color_rgb))
        display.rectangle(0, 0, self.vis_width, self.vis_height)

        # Update (and remove) ripples
        for i in range(len(self.ripples) - 1, -1, -1):
            r: Ripple = self.ripples[i]
            if delta < 1 and not r.update(delta):
                self.ripples.pop(i)
                self.ripple_count -= 1
            else:
                r.draw(display)

        # Add new ripple
        self.ms_since_last_ripple += delta * 1000
        if self.ripple_count < self.max_ripples and self.ms_since_last_ripple > self.next_ripple_after:
            self._add_ripple()
