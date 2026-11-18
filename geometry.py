# geometry.py


def compute_component_width(width, margins, gap):
    """Width of one Enigma component (reflector, rotor, plugboard, etc.)."""
    return (width - margins["left"] - margins["right"] - 5 * gap) / 6


def compute_component_height(height, margins):
    """Height of one Enigma component."""
    return height - margins["top"] - margins["bottom"]


def compute_signal_points(path, width, height, margins, gap):
    """
    Return the list of (x, y) screen coordinates for the signal path.
    `path` is a list of signal indices (0-25) returned by Enigma.encipher().
    """
    w = compute_component_width(width, margins, gap)
    h = compute_component_height(height, margins)

    y = [margins["top"] + (signal + 1) * h / 27 for signal in path]
    x = [width - margins["right"] - w / 2]  # Keyboard

    for i in [4, 3, 2, 1, 0]:  # Forward pass
        x.append(margins["left"] + i * (w + gap) + w * 3 / 4)
        x.append(margins["left"] + i * (w + gap) + w * 1 / 4)
    x.append(margins["left"] + w * 3 / 4)  # Reflector

    for i in [1, 2, 3, 4]:  # Backward pass
        x.append(margins["left"] + i * (w + gap) + w * 1 / 4)
        x.append(margins["left"] + i * (w + gap) + w * 3 / 4)
    x.append(width - margins["right"] - w / 2)  # Lampboard

    return list(zip(x, y))