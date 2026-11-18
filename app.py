import pygame
from keyboard import Keyboard
from plugboard import Plugboard
from rotor import Rotor
from reflector import Reflector
from enigma import Enigma
from draw import draw


class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Enigma Machine Simulator")

        self.WIDTH, self.HEIGHT = 1300, 750
        self.SCREEN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.MARGINS = {"top": 200, "bottom": 100, "left": 100, "right": 100}
        self.GAP = 100

        self.MONO = pygame.font.SysFont("FreeMono", 25)
        self.BOLD = pygame.font.SysFont("FreeMono", 25, bold=True)

        self.input_text = ""
        self.output_text = ""
        self.path = []

        # Animation state
        self.anim = None
        self.ANIM_SPEED = 0.04
        self.PAUSE_TICKS = 400

        self.enigma = self._build_enigma()

    def _build_enigma(self):
        I = Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q")
        II = Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E")
        III = Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V")
        B = Reflector("YRUHQSLDPXNGOKMIEBFZCWVJAT")
        enigma = Enigma(B, I, II, III, Plugboard(["AB", "CD", "EF"]), Keyboard())
        enigma.set_ring((1, 1, 1))
        enigma.set_key("CAT")
        return enigma

    def reset_message(self):
        self.input_text = ""
        self.output_text = ""
        self.path = []
        self.enigma = self._build_enigma()

    def render(self):
        self.SCREEN.fill("#333333")

        text = self.BOLD.render(self.input_text, True, "grey")
        box = text.get_rect(center=(self.WIDTH / 2, self.MARGINS["top"] / 3))
        self.SCREEN.blit(text, box)

        text = self.MONO.render(self.output_text, True, "grey")
        box = text.get_rect(center=(self.WIDTH / 2, self.MARGINS["top"] / 3 + 30))
        self.SCREEN.blit(text, box)

        draw(self.enigma, self.path, self.SCREEN,
             self.WIDTH, self.HEIGHT, self.MARGINS, self.GAP, self.BOLD)

        self._draw_animation()

        pygame.display.flip()

    def _start_animation(self, path):
        if not path:
            self.anim = None
            return
        self.anim = {
            "path": list(path),
            "start": pygame.time.get_ticks(),
        }

    def _point_positions(self, path):
        w = (self.WIDTH - self.MARGINS["left"] - self.MARGINS["right"] - 5 * self.GAP) / 6
        h = self.HEIGHT - self.MARGINS["top"] - self.MARGINS["bottom"]

        y = [self.MARGINS["top"] + (s + 1) * h / 27 for s in path]
        x = [self.WIDTH - self.MARGINS["right"] - w / 2]
        for i in [4, 3, 2, 1, 0]:
            x.append(self.MARGINS["left"] + i * (w + self.GAP) + w * 3/4)
            x.append(self.MARGINS["left"] + i * (w + self.GAP) + w * 1/4)
        x.append(self.MARGINS["left"] + w * 3/4)
        for i in [1, 2, 3, 4]:
            x.append(self.MARGINS["left"] + i * (w + self.GAP) + w * 1/4)
            x.append(self.MARGINS["left"] + i * (w + self.GAP) + w * 3/4)
        x.append(self.WIDTH - self.MARGINS["right"] - w / 2)
        return list(zip(x, y))

    def _draw_animation(self):
        if self.anim is None:
            return

        points = self._point_positions(self.anim["path"])
        elapsed = pygame.time.get_ticks() - self.anim["start"]
        seg_ms = self.ANIM_SPEED * 1000
        total_ms = seg_ms * (len(points) - 1)
        hold_ms = total_ms + self.PAUSE_TICKS

        if elapsed > hold_ms:
            self.anim = None
            return

        if elapsed >= total_ms:
            idx = len(points) - 1
            frac = 0.0
        else:
            idx = int(elapsed // seg_ms)
            frac = (elapsed % seg_ms) / seg_ms

        x0, y0 = points[idx]
        x1, y1 = points[min(idx + 1, len(points) - 1)]
        dot_x = x0 + (x1 - x0) * frac
        dot_y = y0 + (y1 - y0) * frac

        pygame.draw.circle(self.SCREEN, "#f9c74f", (int(dot_x), int(dot_y)), 14)
        pygame.draw.circle(self.SCREEN, "#ffffff", (int(dot_x), int(dot_y)), 7)
        pygame.draw.circle(self.SCREEN, "#43aa8b", (int(dot_x), int(dot_y)), 3)

    def handle_key(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            self.output_text = self.output_text[:-1]
            self.path = []
        elif event.key == pygame.K_r:
            self.reset_message()
        elif event.key == pygame.K_DOWN:
            self.enigma.r3.rotate()
        elif event.key == pygame.K_SPACE:
            self.input_text += " "
            self.output_text += " "
        else:
            key = event.unicode.lower()
            if key in "abcdefghijklmnopqrstuvwxyz":
                letter = key.upper()
                self.input_text += letter
                self.path, cipher = self.enigma.encipher(letter)
                self.output_text += cipher
                self._start_animation(self.path)

    def run(self):
        running = True
        while running:
            self.render()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)
        pygame.quit()