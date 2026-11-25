from rotor import Rotor
from reflector import Reflector
from plugboard import Plugboard
from keyboard import Keyboard
from enigma import Enigma


def make_default_enigma():
    I = Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q")
    II = Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E")
    III = Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V")
    B = Reflector("YRUHQSLDPXNGOKMIEBFZCWVJAT")
    return Enigma(B, I, II, III, Plugboard([]), Keyboard())


def test_recriprocal():
    """Enciphering then deciphering must return the original."""
    e = make_default_enigma()
    e.set_ring((1, 1, 1))
    e.set_key("AAA")

    plaintext = "HELLOWORLD"
    ciphertext = "".join(e.encipher(c)[1] for c in plaintext)

    # Reset machine to same starting state
    e2 = make_default_enigma()
    e2.set_ring((1, 1, 1))
    e2.set_key("AAA")
    recovered = "".join(e2.encipher(c)[1] for c in ciphertext)

    assert recovered == plaintext


def test_known_vector():
    """Classic test: with default settings, 'AAAAA' -> 'BDZGO'."""
    e = make_default_enigma()
    e.set_ring((1, 1, 1))
    e.set_key("AAA")
    out = "".join(e.encipher("A")[1] for _ in range(5))
    assert out == "BDZGO", f"got {out}"


def test_ring_setting_affects_output():
    """Changing ring settings must change the ciphertext."""
    e1 = make_default_enigma()
    e1.set_ring((1, 1, 1))
    e1.set_key("AAA")
    out1 = "".join(e1.encipher("A")[1] for _ in range(5))

    e2 = make_default_enigma()
    e2.set_ring((2, 1, 1))
    e2.set_key("AAA")
    out2 = "".join(e2.encipher("A")[1] for _ in range(5))

    assert out1 != out2, "Ring setting had no effect on output"


def test_ring_setting_reference_vector():
    """Known vector: rings (2,2,2), key AAA, 'AAAAA' -> 'EWTYX'."""
    e = make_default_enigma()
    e.set_ring((2, 2, 2))
    e.set_key("AAA")
    out = "".join(e.encipher("A")[1] for _ in range(5))
    assert out == "EWTYX", f"got {out}"


def test_fast_crib_drag_matches_with_nondefault_rings():
    """Fast crib_drag must agree with the slow one under arbitrary ring settings."""
    from cryptanalysis import crib_drag, make_enigma

    rotor_names = ["I", "II", "III"]
    reflector = "B"
    rings = (5, 7, 3)  # deliberately non-default
    plugboard = ["AB", "CD"]

    # Encrypt a known plaintext
    e = make_enigma(rotor_names, reflector, rings, plugboard)
    e.set_key("XFV")
    plaintext = "HELLOWETTERBERICHT"
    ciphertext = "".join(e.encipher(c)[1] for c in plaintext)

    # Attack it with the same settings
    results = crib_drag(ciphertext, "WETTER", rotor_names, reflector, rings, plugboard)

    assert len(results) >= 1, "Attack failed with non-default rings"
    assert results[0]["key"] == "XFV"
    assert results[0]["offset"] == 5