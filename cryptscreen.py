import pygame
from cryptanalysis import crib_drag


class CryptScreen:
    def __init__(self, config, font_small, font_large):
        self.config = config
        self.font_small = font_small
        self.font_large = font_large

        self.ciphertext = ""
        self.crib = ""
        self.focused_field = None  # "ciphertext", "crib", or None
        self.results = []
        self.status = "Type ciphertext, press Enter, then type crib, press Enter."
        self.running_attack = False

        # Layout rects (set on first render)
        self.cipher_rect = None
        self.crib_rect = None
        self.attack_rect = None
        self.results_y_start = 400

    def layout(self, screen_w, screen_h):
        self.cipher_rect = pygame.Rect(60, 150, 800, 40)
        self.crib_rect = pygame.Rect(60, 220, 400, 40)
        self.attack_rect = pygame.Rect(60, 290, 200, 40)

    def handle_click(self, pos):
        if self.cipher_rect.collidepoint(pos):
            self.focused_field = "ciphertext"
        elif self.crib_rect.collidepoint(pos):
            self.focused_field = "crib"
        elif self.attack_rect.collidepoint(pos):
            self.focused_field = None
            self._run_attack()
        else:
            self.focused_field = None

    def handle_key(self, event):
        if self.focused_field == "ciphertext":
            if event.key == pygame.K_BACKSPACE:
                self.ciphertext = self.ciphertext[:-1]
            elif event.key == pygame.K_RETURN:
                self.focused_field = "crib"
            else:
                ch = event.unicode.upper()
                if len(ch) == 1 and ch.isalpha():
                    self.ciphertext += ch
        elif self.focused_field == "crib":
            if event.key == pygame.K_BACKSPACE:
                self.crib = self.crib[:-1]
            elif event.key == pygame.K_RETURN:
                self.focused_field = None
            else:
                ch = event.unicode.upper()
                if len(ch) == 1 and ch.isalpha():
                    self.crib += ch

    def _run_attack(self):
        if not self.ciphertext or not self.crib:
            self.status = "Need both ciphertext and crib."
            return
        if len(self.crib) > len(self.ciphertext):
            self.status = "Crib longer than ciphertext."
            return
        self.status = "Running... (this may take 30-60s)"
        self.running_attack = True
        # Draw the "running" message before blocking
        # (we'll draw again after; in a real app use threading)
        pygame.display.flip()

        self.results = crib_drag(
            self.ciphertext, self.crib,
            self.config.rotors, self.config.reflector,
            self.config.rings, self.config.plugboard,
        )
        self.running_attack = False
        if self.results:
            self.status = f"Found {len(self.results)} candidate rotor keys."
        else:
            self.status = "No candidates found. (Try a different crib, or rotor/ring settings don't match.)"

    def draw(self, screen):
        screen.fill("#1a1a1a")
        title = self.font_large.render("Crib Dragging — Turing's Method", True, "white")
        screen.blit(title, (60, 60))

        # Ciphertext field
        label = self.font_small.render("Ciphertext:", True, "white")
        screen.blit(label, (60, 120))
        color = "#22aa77" if self.focused_field == "ciphertext" else "#4a5a6a"
        pygame.draw.rect(screen, "#222222", self.cipher_rect, border_radius=6)
        pygame.draw.rect(screen, color, self.cipher_rect, width=2, border_radius=6)
        txt = self.font_small.render(self.ciphertext + ("|" if self.focused_field == "ciphertext" else ""), True, "white")
        screen.blit(txt, (self.cipher_rect.x + 8, self.cipher_rect.y + 10))

        # Crib field
        label = self.font_small.render("Crib (guessed plaintext):", True, "white")
        screen.blit(label, (60, 190))
        color = "#22aa77" if self.focused_field == "crib" else "#4a5a6a"
        pygame.draw.rect(screen, "#222222", self.crib_rect, border_radius=6)
        pygame.draw.rect(screen, color, self.crib_rect, width=2, border_radius=6)
        txt = self.font_small.render(self.crib + ("|" if self.focused_field == "crib" else ""), True, "white")
        screen.blit(txt, (self.crib_rect.x + 8, self.crib_rect.y + 10))

        # Attack button
        pygame.draw.rect(screen, "#4a5a6a", self.attack_rect, border_radius=6)
        pygame.draw.rect(screen, "white", self.attack_rect, width=1, border_radius=6)
        btn_txt = self.font_small.render("Attack", True, "white")
        screen.blit(btn_txt, btn_txt.get_rect(center=self.attack_rect.center))

        # Status
        status_txt = self.font_small.render(self.status, True, "grey")
        screen.blit(status_txt, (280, 305))

        # Results
        y = self.results_y_start
        header = self.font_small.render("Candidates (offset, rotor key, decrypted segment):", True, "white")
        screen.blit(header, (60, y - 20))
        for r in self.results:
            line = f"  offset {r['offset']:>3}  |  key {r['key']}  |  segment {r['ciphertext_segment']} -> {r['plaintext']}"
            screen.blit(self.font_small.render(line, True, "white"), (60, y))
            y += 24