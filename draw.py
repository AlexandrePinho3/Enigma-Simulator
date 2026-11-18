# draw.py
import pygame
from geometry import compute_component_width, compute_component_height, compute_signal_points


def draw(enigma, path, screen, width, height, margins, gap, font):

    w = compute_component_width(width, margins, gap)
    h = compute_component_height(height, margins)

    # Draw the signal path
    if len(path) > 0:
        points = compute_signal_points(path, width, height, margins, gap)
        for i in range(1, 21):
            if i < 10:
                color = "#43aa8b"
            elif i < 12:
                color = "#f9c74f"
            else:
                color = "#e63946"
            pygame.draw.line(screen, color, points[i - 1], points[i], width=5)

    # Draw components left to right
    x = margins["left"]
    for component in [enigma.re, enigma.r1, enigma.r2, enigma.r3, enigma.pb, enigma.kb]:
        component.draw(screen, x, margins["top"], w, h, font)
        x += w + gap

    # Draw titles above each component
    names = ["Reflector", "1ºRotor", "2ºRotor", "3ºRotor", "Plugboard", "Key/Lampboard"]
    title_y = margins["top"] * 0.8
    for i in range(6):
        cx = margins["left"] + w / 2 + i * (w + gap)
        title = font.render(names[i], True, "white")
        screen.blit(title, title.get_rect(center=(cx, title_y)))