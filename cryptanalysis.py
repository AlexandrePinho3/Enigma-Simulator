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


def crib_drag(ciphertext, crib, rotor_names, reflector_name, rings,
              plugboard_pairs, max_results=20):
    """
    Full crib-drag attack:
    1. Rule out impossible alignments (self-encryption).
    2. For each remaining alignment, try all 17,576 rotor start positions.
    3. Return a list of (offset, rotor_key, plaintext_fragment) hits.
    """
    ciphertext = ciphertext.upper().replace(" ", "")
    crib = crib.upper().replace(" ", "")
    impossible = crib_impossible_alignments(ciphertext, crib)

    results = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for offset in range(len(ciphertext) - len(crib) + 1):
        if offset in impossible:
            continue

        crib_segment = ciphertext[offset:offset + len(crib)]

        # Try every rotor key
        for a in letters:
            for b in letters:
                for c in letters:
                    key = a + b + c
                    enigma = make_enigma(rotor_names, reflector_name, rings, plugboard_pairs)
                    enigma.set_key(key)

                    # Advance the machine offset times (to skip earlier letters)
                    for _ in range(offset):
                        enigma.encipher("A")

                    # Now encrypt the crib segment; see if it matches the crib
                    recovered = ""
                    for ch in crib_segment:
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