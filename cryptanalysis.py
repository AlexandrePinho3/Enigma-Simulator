from rotor import Rotor
from reflector import Reflector
from plugboard import Plugboard
from keyboard import Keyboard
from enigma import Enigma
from config import ROTOR_WIRINGS, REFLECTOR_WIRINGS


def make_enigma(rotor_names, reflector_name, rings, plugboard_pairs):
    """Build a fresh Enigma from config values."""
    rotors = [Rotor(*ROTOR_WIRINGS[name]) for name in rotor_names]
    reflector = Reflector(REFLECTOR_WIRINGS[reflector_name])
    enigma = Enigma(reflector, rotors[0], rotors[1], rotors[2],
                    Plugboard(plugboard_pairs), Keyboard())
    enigma.set_ring(rings)
    return enigma


def crib_impossible_alignments(ciphertext, crib):
    """
    Find alignments where the crib would have to encrypt a letter to itself.
    Returns a set of offsets that are IMPOSSIBLE (ruled out).
    """
    ciphertext = ciphertext.upper().replace(" ", "")
    crib = crib.upper().replace(" ", "")
    impossible = set()

    for offset in range(len(ciphertext) - len(crib) + 1):
        for i, c in enumerate(crib):
            if ciphertext[offset + i] == c:
                impossible.add(offset)
                break

    return impossible


def crib_drag(ciphertext, crib, rotor_names, reflector_name, rings, plugboard_pairs, max_results=20):
    ciphertext = ciphertext.upper().replace(" ", "")
    crib = crib.upper().replace(" ", "")
    impossible = crib_impossible_alignments(ciphertext, crib)

    results = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for offset in range(len(ciphertext) - len(crib) + 1):
        if offset in impossible:
            continue

        crib_segment = ciphertext[offset:offset + len(crib)]

        # Optimization: Extract just the first letter we need to test
        target_first_letter = crib[0]

        for a in letters:
            for b in letters:
                for c in letters:
                    key = a + b + c

                    # Build a fresh machine
                    enigma = make_enigma(rotor_names, reflector_name, rings, plugboard_pairs)
                    enigma.set_key(key)

                    # Fast-forward to the offset (skip the "A" encryption loop)
                    # For small offsets, enciphering "A" is fine, but we can also just
                    # rotate the rotors directly if we want. Let's keep the encipher loop
                    # for now but break early if the FIRST letter fails.
                    for _ in range(offset):
                        enigma.encipher("A")

                    # Check the FIRST letter of the crib first
                    _, out_first = enigma.encipher(crib_segment[0])

                    if out_first != target_first_letter:
                        continue  # Fast fail! Move to next key

                    # If it passed the first letter, do the rest
                    recovered = out_first
                    for ch in crib_segment[1:]:
                        _, out = enigma.encipher(ch)
                        recovered += out

                    if recovered == crib:
                        results.append({
                            "offset": offset,
                            "key": key,
                            "plaintext": recovered,
                            "ciphertext_segment": crib_segment,
                        })
                        if len(results) >= max_results:
                            return results

    return results