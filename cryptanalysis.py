from rotor import Rotor
from reflector import Reflector
from plugboard import Plugboard
from keyboard import Keyboard
from enigma import Enigma
from config import ROTOR_WIRINGS, REFLECTOR_WIRINGS


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def make_enigma(rotor_names, reflector_name, rings, plugboard_pairs):
    """Build a fresh Enigma from config values."""
    rotors = [Rotor(*ROTOR_WIRINGS[name]) for name in rotor_names]
    reflector = Reflector(REFLECTOR_WIRINGS[reflector_name])
    enigma = Enigma(reflector, rotors[0], rotors[1], rotors[2],
                    Plugboard(plugboard_pairs), Keyboard())
    enigma.set_ring(rings)
    return enigma


def crib_impossible_alignments(ciphertext, crib):
    """Return offsets where the crib would have to encrypt a letter to itself."""
    ciphertext = ciphertext.upper().replace(" ", "")
    crib = crib.upper().replace(" ", "")
    impossible = set()
    for offset in range(len(ciphertext) - len(crib) + 1):
        for i, c in enumerate(crib):
            if ciphertext[offset + i] == c:
                impossible.add(offset)
                break
    return impossible


# --- Fast attack machinery -------------------------------------------------

_TABLE_CACHE = {}


def _build_letter_table(rotor_names, reflector_name, rings, plugboard_pairs):
    """
    Precompute cipher of every (a, b, c, letter) — 26^3 * 26 = 456,976 entries.
    a, b, c are the rotor positions (0-25). This table is the single source
    of truth for 'what does letter X encrypt to when the rotors are at (a,b,c)?'
    """
    table = {}
    for a in range(26):
        for b in range(26):
            for c in range(26):
                enigma = make_enigma(rotor_names, reflector_name, rings, plugboard_pairs)
                enigma.set_key(LETTERS[a] + LETTERS[b] + LETTERS[c])
                for ch in LETTERS:
                    _, out = enigma.encipher(ch)
                    table[(a, b, c, ch)] = out
    return table


def _get_table(rotor_names, reflector_name, rings, plugboard_pairs):
    """Return a cached letter table, building it only if needed."""
    key = (tuple(rotor_names), reflector_name, tuple(rings), tuple(plugboard_pairs))
    if key not in _TABLE_CACHE:
        _TABLE_CACHE[key] = _build_letter_table(
            rotor_names, reflector_name, rings, plugboard_pairs
        )
    return _TABLE_CACHE[key]


def _notch_positions(rotor_names, rings):
    def adjusted(rotor_name, ring):
        original_notch = ROTOR_WIRINGS[rotor_name][1]
        n_notch = LETTERS.find(original_notch)
        return (n_notch - ring) % 26
    return [
        adjusted(rotor_names[1], rings[1]),  # middle
        adjusted(rotor_names[2], rings[2]),  # right
    ]


def _step(a, b, c, mid_notch, right_notch):
    """Advance the rotor state by one keypress (correct Enigma stepping)."""
    if b == mid_notch:
        a = (a + 1) % 26
        b = (b + 1) % 26
    elif c == right_notch:
        b = (b + 1) % 26
    c = (c + 1) % 26
    return a, b, c


def crib_drag(ciphertext, crib, rotor_names, reflector_name, rings,
              plugboard_pairs, max_results=20):
    """Crib-drag attack — the correct, simple version."""
    ciphertext = ciphertext.upper().replace(" ", "")
    crib = crib.upper().replace(" ", "")
    impossible = crib_impossible_alignments(ciphertext, crib)

    results = []
    for offset in range(len(ciphertext) - len(crib) + 1):
        if offset in impossible:
            continue

        crib_segment = ciphertext[offset:offset + len(crib)]
        target_first = crib[0]

        for a in range(26):
            for b in range(26):
                for c in range(26):
                    enigma = make_enigma(rotor_names, reflector_name, rings, plugboard_pairs)
                    enigma.set_key(LETTERS[a] + LETTERS[b] + LETTERS[c])

                    for _ in range(offset):
                        enigma.encipher("A")

                    _, out_first = enigma.encipher(crib_segment[0])
                    if out_first != target_first:
                        continue

                    recovered = out_first
                    for ch in crib_segment[1:]:
                        _, out = enigma.encipher(ch)
                        recovered += out

                    if recovered == crib:
                        key = LETTERS[a] + LETTERS[b] + LETTERS[c]
                        results.append({
                            "offset": offset,
                            "key": key,
                            "plaintext": recovered,
                            "ciphertext_segment": crib_segment,
                        })
                        if len(results) >= max_results:
                            return results
    return results