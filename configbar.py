import pygame


class ConfigBar:
    def __init__(self, config, font):
        self.config = config
        self.font = font
        self.buttons = []

    def layout(self, screen_width, top_y):
        self.buttons = []
        row1_y = top_y
        x = 60
        for i in range(3):
            x = self._triplet(x, row1_y, f"R{i+1}", self.config.rotors[i],
                              f"rotor{i}_-", f"rotor{i}_cycle", f"rotor{i}_+")
            x += 30
        x += 20
        self._triplet(x, row1_y, "Refl", self.config.reflector,
                      "refl_-", "refl_cycle", "refl_+")

        row2_y = top_y + 45
        x = 60
        for i in range(3):
            x = self._stepper(x, row2_y, f"Ring {i+1}", self.config.rings[i],
                              f"ring{i}_-", f"ring{i}_+")
            x += 30
        self._add(x, row2_y, 160, 32, "key_cycle", f"Key: {self.config.key}")

    def _add(self, x, y, w, h, action, label):
        self.buttons.append((pygame.Rect(x, y, w, h), action, label))
        return x + w

    def _triplet(self, x, y, prefix, value, a_minus, a_cycle, a_plus):
        x = self._add(x, y, 28, 32, a_minus, "-") + 4
        x = self._add(x, y, 90, 32, a_cycle, f"{prefix}: {value}") + 4
        x = self._add(x, y, 28, 32, a_plus, "+") + 4
        return x

    def _stepper(self, x, y, label, value, a_minus, a_plus):
        x = self._add(x, y, 80, 32, "noop", label) + 4
        x = self._add(x, y, 28, 32, a_minus, "-") + 4
        x = self._add(x, y, 40, 32, "noop", str(value)) + 4
        x = self._add(x, y, 28, 32, a_plus, "+") + 4
        return x

    def draw(self, screen):
        for rect, action, label in self.buttons:
            color = "#333333" if action == "noop" else "#4a5a6a"
            border = "#555555" if action == "noop" else "white"
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, border, rect, width=1, border_radius=6)
            text = self.font.render(label, True, "white")
            screen.blit(text, text.get_rect(center=rect.center))

    def handle_click(self, pos):
        for rect, action, _ in self.buttons:
            if rect.collidepoint(pos) and action != "noop":
                return action
        return None

    def apply_action(self, action):
        changed = False
        if action.startswith("rotor"):
            slot = int(action[5])
            kind = action.split("_", 1)[1]
            if kind in ("-", "cycle", "+"):
                self.config.cycle_rotor(slot, -1 if kind == "-" else +1)
                changed = True
        elif action.startswith("refl"):
            kind = action.split("_", 1)[1]
            if kind in ("-", "+", "cycle"):
                self.config.cycle_reflector(-1 if kind == "-" else +1)
                changed = True
        elif action.startswith("ring"):
            slot = int(action[4])
            kind = action.split("_", 1)[1]
            self.config.bump_ring(slot, -1 if kind == "-" else +1)
            changed = True
        elif action == "key_cycle":
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            idx = letters.find(self.config.key[0])
            self.config.key = letters[(idx + 1) % 26] + self.config.key[1:]
            changed = True
        return changed