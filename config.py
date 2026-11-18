from dataclasses import dataclass, field


ROTOR_WIRINGS = {
    "I":   ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
    "II":  ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
    "IV":  ("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J"),
    "V":   ("VZBRGITYUPSDNHLXAWMJQOFECK", "Z"),
}

REFLECTOR_WIRINGS = {
    "A": "EJMZALYXVBWFCRQUONTSPIKHGD",
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}

ROTOR_ORDER = ["I", "II", "III", "IV", "V"]
REFLECTOR_ORDER = ["A", "B", "C"]


@dataclass
class Config:
    rotors: list = field(default_factory=lambda: ["I", "II", "III"])
    reflector: str = "B"
    rings: tuple = (1, 1, 1)
    key: str = "AAA"
    plugboard: list = field(default_factory=lambda: ["AB", "CD", "EF"])

    def cycle_rotor(self, slot, direction=1):
        idx = ROTOR_ORDER.index(self.rotors[slot])
        self.rotors[slot] = ROTOR_ORDER[(idx + direction) % len(ROTOR_ORDER)]

    def cycle_reflector(self, direction=1):
        idx = REFLECTOR_ORDER.index(self.reflector)
        self.reflector = REFLECTOR_ORDER[(idx + direction) % len(REFLECTOR_ORDER)]

    def bump_ring(self, slot, delta):
        rings = list(self.rings)
        rings[slot] = ((rings[slot] - 1 + delta) % 26) + 1
        self.rings = tuple(rings)