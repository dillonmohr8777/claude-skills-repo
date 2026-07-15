#!/usr/bin/env python3
"""Music + sound design for the Hope Wellness 60s reel (music-and-text cut).

Per the brief: no licensed voice was available in this environment, so this
is the polished music-and-text version rather than an artificial placeholder
voiceover. 72 BPM, airy piano, warm pads, very light organic percussion,
breath swells at scene changes, low airy transition whooshes, restrained
foley (journal pencil, soft footsteps, volleyball taps), clean warm resolve
with a natural tail inside the final 60.00 s.

Writes: out/reel-audio.wav  (48 kHz stereo, exactly 60.00 s)
"""

import math
import os
import wave

import numpy as np

SR = 48000
DUR = 60.0
N = int(SR * DUR)
BPM = 72.0
BEAT = 60.0 / BPM            # 0.8333 s
BAR = BEAT * 4               # 3.3333 s

rng = np.random.default_rng(2026)
mix = np.zeros((N, 2), np.float64)
T = np.arange(N) / SR


def add(sig, t0, gain=1.0, pan=0.0):
    """Mix a mono signal into the master at time t0 with constant-power pan."""
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    seg = sig[: N - i0]
    gl = math.cos((pan + 1) * math.pi / 4) * gain
    gr = math.sin((pan + 1) * math.pi / 4) * gain
    mix[i0:i0 + len(seg), 0] += seg * gl
    mix[i0:i0 + len(seg), 1] += seg * gr


def env(n, a, d, sus_level=0.0, s=0.0, r=0.0):
    """Simple ADSR-ish envelope in samples."""
    e = np.zeros(n)
    ia, id_, is_, ir = int(a * SR), int(d * SR), int(s * SR), int(r * SR)
    idx = 0
    if ia:
        e[:ia] = np.linspace(0, 1, ia)
        idx += ia
    if id_ and idx < n:
        seg = min(id_, n - idx)
        e[idx:idx + seg] = np.linspace(1, sus_level, seg)
        idx += seg
    if is_ and idx < n:
        seg = min(is_, n - idx)
        e[idx:idx + seg] = sus_level
        idx += seg
    if ir and idx < n:
        seg = min(ir, n - idx)
        e[idx:idx + seg] = np.linspace(sus_level, 0, seg)
        idx += seg
    return e


def piano(freq, dur, vel=1.0):
    """Soft additive felt-piano pluck."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for h, amp in ((1, 1.0), (2, 0.42), (3, 0.22), (4, 0.10), (5, 0.055), (6, 0.03)):
        decay = np.exp(-t * (2.1 + 0.85 * h))
        sig += amp * decay * np.sin(2 * math.pi * freq * h * t)
    onset = np.minimum(t / 0.010, 1.0)
    tail = np.minimum((dur - t) / 0.05, 1.0)
    return sig * onset * np.clip(tail, 0, 1) * vel * 0.16


def pad_chord(freqs, dur, vel=1.0):
    """Warm detuned pad."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f0 in freqs:
        for det in (-2.5, 0.0, 2.7):
            f = f0 * (2 ** (det / 1200))
            ph = rng.random() * 6.283
            sig += np.sin(2 * math.pi * f * t + ph)
            sig += 0.28 * np.sin(2 * math.pi * f * 2 * t + ph * 1.7)
    sig /= (len(freqs) * 3 * 1.28)
    e = env(n, a=1.3, d=0.5, sus_level=0.82, s=max(dur - 3.6, 0), r=1.8)
    breathe = 1.0 + 0.06 * np.sin(2 * math.pi * t / 4.0)
    return sig * e * breathe * vel * 0.11


def noise_swell(dur, f_lo, f_hi, vel=1.0, shape=0.5):
    """Band-limited airy noise swell (breath / whoosh)."""
    n = int(dur * SR)
    w = rng.standard_normal(n)
    spec = np.fft.rfft(w)
    fr = np.fft.rfftfreq(n, 1 / SR)
    band = np.exp(-0.5 * ((fr - (f_lo + f_hi) / 2) / ((f_hi - f_lo) / 2.2)) ** 2)
    w = np.fft.irfft(spec * band, n)
    w /= (np.abs(w).max() + 1e-9)
    t = np.arange(n) / n
    e = np.sin(np.pi * t) ** (1.0 / max(shape, 0.05))
    return w * e * vel


def thump(freq, dur, vel=1.0, click=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * math.pi * freq * t * (1 - 0.3 * t / dur)) * np.exp(-t * 26)
    sig = body
    if click:
        c = rng.standard_normal(n) * np.exp(-t * 240)
        sig = sig + click * c * 0.4
    return sig * vel


# ------------------------------------------------------------ harmony ------
F3, A3, Bb3, C4, D4, E4, F4, G4, A4, Bb4, C5, E5 = (
    174.61, 220.0, 233.08, 261.63, 293.66, 329.63, 349.23,
    392.0, 440.0, 466.16, 523.25, 659.26)

FMAJ9 = [F3, A3, C4, E4, G4]
AM7 = [A3, C4, E4, G4]
BBMAJ9 = [Bb3, D4, F4, A4]
CADD9 = [C4, E4, G4, D4 * 2]

# 18 bars: 2 intro, 3 x 4-bar cycle, Bb -> Csus turn, final F resolve
PROG = ([("F", FMAJ9), ("F", FMAJ9)] +
        [("F", FMAJ9), ("Am", AM7), ("Bb", BBMAJ9), ("C", CADD9)] * 3 +
        [("Bb", BBMAJ9), ("C", CADD9)] +
        [("F", FMAJ9), ("F", FMAJ9)])

for bar, (name, chord) in enumerate(PROG):
    t0 = bar * BAR
    if t0 >= DUR:
        break
    vel = 0.75 if bar < 2 else 1.0
    if bar >= 16:
        vel = 1.05  # warm final resolve
    add(pad_chord(chord, BAR + 2.4, vel), t0, gain=1.0, pan=0.0)

# piano: gentle rising broken chords, sparser in the intro and outro
ARP_BARS = range(2, 17)
for bar in ARP_BARS:
    name, chord = PROG[bar]
    tones = sorted(chord)[-4:]
    order = [0, 1, 2, 3] if bar % 2 == 0 else [0, 2, 1, 3]
    for b, oi in enumerate(order):
        if bar in (2, 15) and b == 3:
            continue  # leave air
        t0 = bar * BAR + b * BEAT + rng.uniform(-0.008, 0.010)
        f = tones[oi] * (2 if (bar % 4 == 3 and b == 0) else 1)
        v = 0.55 + 0.25 * math.sin(b * 1.3 + bar) * 0.5 + (0.18 if b == 0 else 0)
        add(piano(f, 2.6, v), t0, gain=1.0, pan=(-0.25 + 0.5 * (b / 3)))

# final resolving piano note-cluster at bar 17 beat 1 (56.67 s)
add(piano(F4, 3.2, 0.9), 16 * BAR, gain=1.0, pan=0.05)
add(piano(A4, 3.2, 0.65), 16 * BAR + 0.04, gain=1.0, pan=-0.12)
add(piano(C5, 3.0, 0.5), 16 * BAR + 0.09, gain=1.0, pan=0.14)
add(piano(F3, 3.4, 0.75), 16 * BAR + 0.02, gain=1.0, pan=0.0)

# ------------------------------------------------- breath and transitions --
SCENE_TIMES = [3.0, 8.0, 13.0, 18.0, 23.0, 28.0, 33.0, 38.0, 43.0, 48.0, 53.0, 56.0]
for st in SCENE_TIMES:
    add(noise_swell(2.4, 250, 900, vel=0.028, shape=0.7), st - 1.3, gain=1.0,
        pan=rng.uniform(-0.2, 0.2))          # breath swell into the cut
    add(noise_swell(0.9, 500, 1600, vel=0.020, shape=1.2), st - 0.25, gain=1.0,
        pan=rng.uniform(-0.15, 0.15))        # low airy whoosh, never sharp

# opening breath (logo assembly) and a closing exhale
add(noise_swell(2.8, 200, 700, vel=0.030, shape=0.6), 0.15)
add(noise_swell(3.2, 180, 600, vel=0.024, shape=0.5), 56.4)

# ------------------------------------------------------------------ foley --
# quiet journal pencil (reflection scene, ~14 s)
for k in range(5):
    add(noise_swell(0.34, 1800, 5200, vel=0.012, shape=1.4),
        14.0 + k * 0.42 + rng.uniform(0, 0.05), pan=0.25)
# soft fabric / mat movement (stretch and rest scenes)
add(noise_swell(0.8, 400, 1400, vel=0.012, shape=1.0), 19.2, pan=-0.2)
add(noise_swell(0.9, 350, 1200, vel=0.012, shape=1.0), 29.3, pan=0.15)
# soft footsteps under the jog / walk scenes (33-42 s), alternating pan
for k in range(11):
    t0 = 33.4 + k * BEAT
    if t0 > 42.4:
        break
    add(thump(85, 0.16, vel=0.028, click=0.15), t0, pan=-0.3 if k % 2 else 0.3)
# restrained volleyball taps on the match cuts
add(thump(130, 0.14, vel=0.05, click=0.5), 48.0, pan=0.1)
add(thump(126, 0.14, vel=0.045, click=0.5), 53.0, pan=-0.1)

# very light organic shaker, only under the movement chapter (33-53 s)
for k in range(48):
    t0 = 33.0 + k * BEAT / 2
    if t0 >= 52.6:
        break
    v = 0.010 if k % 2 == 0 else 0.006
    add(noise_swell(0.09, 3000, 9000, vel=v, shape=1.6), t0, pan=0.22)

# ------------------------------------------------------------- mastering --
# gentle warmth shelf: blend in a lowpassed copy
def warm(x):
    k = np.exp(-np.arange(0, 400) / 90.0)
    k /= k.sum()
    low = np.vstack([np.convolve(x[:, c], k, mode="same") for c in (0, 1)]).T
    return 0.86 * x + 0.20 * low


mix = warm(mix)

# clean warm resolve: master fade begins 58.6 s, ~10 frames of natural tail
fade = np.ones(N)
i0 = int(58.6 * SR)
fade[i0:] = np.linspace(1, 0, N - i0) ** 1.4
mix *= fade[:, None]

# normalize to -1.5 dBFS true peak-ish
peak = np.abs(mix).max()
mix = mix / (peak + 1e-9) * (10 ** (-1.5 / 20))

# soft-knee safety (no clipping)
mix = np.tanh(mix * 1.1) / math.tanh(1.1)
assert np.abs(mix).max() <= 0.985

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "reel-audio.wav")
os.makedirs(os.path.dirname(out), exist_ok=True)
pcm = (mix * 32767).astype(np.int16)
with wave.open(out, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm.tobytes())
print("audio written:", out, f"{len(pcm)/SR:.3f}s peak={np.abs(mix).max():.3f}")
