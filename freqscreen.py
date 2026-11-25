import pygame
import math


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Standard English letter frequencies (percent, from general text corpora)
ENGLISH_FREQ = {
    "A": 8.17, "B": 1.49, "C": 2.78, "D": 4.25, "E": 12.70, "F": 2.23,
    "G": 2.02, "H": 6.09, "I": 6.97, "J": 0.15, "K": 0.77, "L": 4.03,
    "M": 2.41, "N": 6.75, "O": 7.51, "P": 1.93, "Q": 0.10, "R": 5.99,
    "S": 6.33, "T": 9.06, "U": 2.76, "V": 0.98, "W": 2.36, "X": 0.15,
    "Y": 1.97, "Z": 0.07,
}


class FreqScreen:
    def __init__(self, crypt_screen, font_small, font_large):
        self.crypt_screen = crypt_screen  # we read ciphertext from here
        self.font_small = font_small
        self.font_large = font_large
        self.go_back = False
        self.back_rect = None

    def layout(self, screen_w, screen_h):
        self.back_rect = pygame.Rect(screen_w - 220, 60, 160, 40)

    def handle_click(self, pos):
        if self.back_rect.collidepoint(pos):
            self.go_back = True

    def handle_key(self, event):
        pass  # read-only screen

    def _count_frequencies(self):
        text = self.crypt_screen.ciphertext.upper().replace(" ", "")
        text = "".join(c for c in text if c.isalpha())
        total = len(text)
        if total == 0:
            return {L: 0.0 for L in LETTERS}, 0

        counts = {L: 0 for L in LETTERS}
        for ch in text:
            if ch in counts:
                counts[ch] += 1
        return {L: 100.0 * counts[L] / total for L in LETTERS}, total

    def draw(self, screen):
        screen.fill("#1a1a1a")

        title = self.font_large.render("Frequency Analysis", True, "white")
        screen.blit(title, (60, 60))

        # Back button
        pygame.draw.rect(screen, "#4a5a6a", self.back_rect, border_radius=6)
        pygame.draw.rect(screen, "white", self.back_rect, width=1, border_radius=6)
        back_txt = self.font_small.render("Back to Machine", True, "white")
        screen.blit(back_txt, back_txt.get_rect(center=self.back_rect.center))

        # Compute frequencies
        observed, total = self._count_frequencies()

        # Subtitle
        subtitle = f"Ciphertext letters analyzed: {total}"
        screen.blit(self.font_small.render(subtitle, True, "#88aaff"), (60, 100))

        if total == 0:
            hint = self.font_small.render(
                "Type a ciphertext on the Crypt screen first (Tab to go there).",
                True, "grey",
            )
            screen.blit(hint, (60, 160))
            self._draw_legend(screen)
            return

        # Chart area
        chart_x = 60
        chart_y = 200
        chart_w = 1180
        chart_h = 380
        bar_slot = chart_w / 26
        bar_w = bar_slot * 0.7
        max_pct = max(max(observed.values()), max(ENGLISH_FREQ.values()))
        scale = chart_h / max_pct

        # Baseline
        base_y = chart_y + chart_h
        pygame.draw.line(screen, "#555555",
                         (chart_x, base_y), (chart_x + chart_w, base_y), 2)

        for i, letter in enumerate(LETTERS):
            slot_x = chart_x + i * bar_slot

            # Reference bar (faint, English)
            ref_h = ENGLISH_FREQ[letter] * scale
            ref_rect = pygame.Rect(
                slot_x + bar_slot * 0.15, base_y - ref_h,
                bar_w, ref_h,
            )
            pygame.draw.rect(screen, "#2a3a4a", ref_rect)

            # Observed bar (bright)
            obs_h = observed[letter] * scale
            obs_rect = pygame.Rect(
                slot_x + bar_slot * 0.15, base_y - obs_h,
                bar_w, obs_h,
            )
            pygame.draw.rect(screen, "#43aa8b", obs_rect)

            # Letter label
            lbl = self.font_small.render(letter, True, "white")
            screen.blit(lbl, lbl.get_rect(center=(slot_x + bar_slot / 2, base_y + 15)))

        # Y-axis labels (0, 5, 10, 15 percent)
        for pct in [0, 5, 10, 15]:
            y = base_y - pct * scale
            if y < chart_y - 5:
                continue
            screen.blit(self.font_small.render(f"{pct}%", True, "#888888"),
                        (chart_x - 45, y - 8))
            pygame.draw.line(screen, "#333333",
                             (chart_x, y), (chart_x + chart_w, y), 1)

        self._draw_legend(screen)

    def _draw_legend(self, screen):
        # Legend at the bottom
        legend_y = 640
        pygame.draw.rect(screen, "#2a3a4a", pygame.Rect(60, legend_y, 18, 18))
        screen.blit(self.font_small.render("English reference", True, "grey"),
                    (85, legend_y))
        pygame.draw.rect(screen, "#43aa8b", pygame.Rect(260, legend_y, 18, 18))
        screen.blit(self.font_small.render("Observed ciphertext", True, "grey"),
                    (285, legend_y))

        # Explanatory note
        note_y = 680
        note = ("Enigma flattens letter frequencies into a near-uniform distribution — "
                "that's why frequency analysis alone cannot break it.")
        screen.blit(self.font_small.render(note, True, "#666666"), (60, note_y))