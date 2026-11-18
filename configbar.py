import pygame


class PlugboardEditor:
    """A focusable text field for editing plugboard pairs."""

    MAX_LEN = 40

    def __init__(self, config):
        self.config = config
        self.text = " ".join(config.plugboard)
        self.focused = False
        self.changed = False
        self.rect = None  # set by ConfigBar.layout

    def handle_key(self, event):
        """Returns True if the event was consumed (so App won't process it)."""
        if not self.focused:
            return False

        if event.key == pygame.K_RETURN:
            self._commit()
            self.focused = False
            return True
        if event.key == pygame.K_ESCAPE:
            self.text = " ".join(self.config.plugboard)  # revert
            self.focused = False
            return True
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return True

        key = event.unicode.upper()
        if len(key) == 1 and (key.isalpha() or key == " ") and len(self.text) < self.MAX_LEN:
            self.text += key
            return True
        return False

    def _commit(self):
        """Parse and validate; if valid, update config.plugboard. Otherwise revert."""
        pairs = self.text.replace(" ", "").upper()
        if not self._valid(pairs):
            self.text = " ".join(self.config.plugboard)
            return
        self.config.plugboard = [pairs[i:i+2] for i in range(0, len(pairs), 2)]
        self.text = " ".join(self.config.plugboard)
        self.changed = True

    def _valid(self, pairs_str):
        if len(pairs_str) % 2 != 0:
            return False
        if len(set(pairs_str)) != len(pairs_str):
            return False
        return all(c.isalpha() for c in pairs_str)

    def draw(self, screen, font):
        color = "#22aa77" if self.focused else "#4a5a6a"
        pygame.draw.rect(screen, "#222222", self.rect, border_radius=6)
        pygame.draw.rect(screen, color, self.rect, width=2, border_radius=6)
        label = f"Plugboard: {self.text}" + ("|" if self.focused else "")
        text = font.render(label, True, "white")
        # Clip text if it overflows the field
        screen.blit(text, (self.rect.x + 10, self.rect.centery - text.get_height() // 2))


class ConfigBar:
    def __init__(self, config, font):
        self.config = config
        self.font = font
        self.buttons = []
        self.plugboard_editor = PlugboardEditor(config)

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

        # Third row: plugboard editor
        row3_y = top_y + 90
        self.plugboard_editor.rect = pygame.Rect(60, row3_y, 500, 32)

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
        self.plugboard_editor.draw(screen, self.font)

    def handle_click(self, pos):
        # Plugboard editor focus takes priority
        if self.plugboard_editor.rect.collidepoint(pos):
            self.plugboard_editor.focused = True
            return None

        if self.plugboard_editor.focused:
            self.plugboard_editor.text = " ".join(self.config.plugboard)
            self.plugboard_editor.focused = False
            self.plugboard_editor.changed = False

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