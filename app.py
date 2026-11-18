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

        pygame.display.flip()

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