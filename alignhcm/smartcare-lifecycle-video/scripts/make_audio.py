#!/usr/bin/env python3
"""Audio bed + voiceover for the SmartCare sizzle.

- Synthesizes a warm, confident cinematic bed (pad + sub pulse + shimmer +
  transition risers) whose chord changes land on the scene boundaries.
- Renders the 7 VO lines with edge-tts, places them on the scene clock,
  and ducks the bed ~6 dB under the voice.
- Writes 48k stereo WAVs: full mix (music+VO), plus music-only and VO-only.

Requires: numpy, edge-tts, imageio-ffmpeg.  No external network beyond edge-tts.
"""
from __future__ import annotations
import os, subprocess, tempfile, math, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg

os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"; OUT.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
DUR = 59.8          # matches video.html DURATION
N = int(SR * DUR)
T = np.arange(N) / SR
rng = np.random.default_rng(814)

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-6%"
# (start_time, text)
VO = [
    (0.55,  "Go-live is only the beginning. SmartCare keeps your H C M moving, every day after."),
    (6.7,   "Stabilize. Optimize. Thrive. One support model for the work that never really stops."),
    (16.8,  "Optimize the system you already own. Sharper workflows, cleaner reporting, less friction."),
    (26.1,  "As configuration gets dialed in, system health climbs toward optimal."),
    (34.3,  "Then thrive beyond support. Continuous improvement, stronger decisions, room to grow."),
    (43.3,  "Insights compound, performance rises, and your platform keeps paying you back."),
    (51.5,  "SmartCare, from Align. Stabilize, optimize, and thrive. Align H C M dot com."),
]
BOUNDS = [6.0, 16.15, 25.15, 33.65, 42.65, 50.85]  # scene starts (for risers/chord changes)

# ----------------------------------------------------------------- helpers
def adsr(n, a, d, s, r, sus=0.7):
    env = np.zeros(n); a=int(a*SR); d=int(d*SR); r=int(r*SR)
    a=max(a,1); d=max(d,1); r=max(r,1)
    ai=min(a,n); env[:ai]=np.linspace(0,1,ai)
    di=min(a+d,n); env[a:di]=np.linspace(1,sus,di-a)
    env[di:max(di,n-r)]=sus
    if r<n: env[n-r:]=np.linspace(env[n-r-1] if n-r-1>=0 else sus,0,r)
    return env

def sine(f,ph=0.0): return np.sin(2*np.pi*f*T+ph)
def softclip(x,drive=1.0): return np.tanh(x*drive)/np.tanh(drive) if drive>0 else x

def early_reflections(x, mix=0.24):
    """Vectorized multi-tap 'space' (early reflections + short diffuse tail)."""
    out=np.zeros((N,2))
    tapsL=[(0.011,0.55),(0.023,0.40),(0.037,0.30),(0.053,0.22),(0.071,0.16),(0.097,0.11),(0.131,0.07)]
    tapsR=[(0.013,0.55),(0.027,0.40),(0.041,0.30),(0.059,0.22),(0.079,0.16),(0.101,0.11),(0.139,0.07)]
    for taps,ch in ((tapsL,0),(tapsR,1)):
        for d,g in taps:
            s=int(d*SR)
            out[s:,ch]+=g*x[:N-s]
    return out*mix

def norm_rms(x, target_db=-20.0):
    rms=np.sqrt(np.mean(x**2))+1e-9
    return x * (10**(target_db/20)/rms)

def db(x): return 10**(x/20)

# ----------------------------------------------------------------- chords
# A major family; roots build a hopeful I-V-vi-IV-I-V-I arc across the scenes
CHORDS = {
 'A':  [220.00,277.18,329.63,440.00],
 'E':  [164.81,207.65,246.94,329.63],
 'F#m':[185.00,220.00,277.18,369.99],
 'D':  [146.83,185.00,220.00,293.66],
 'Csm':[138.59,164.81,207.65,277.18],
}
# (start, chord) — changes near scene boundaries
PROG = [(0.0,'A'),(6.0,'E'),(16.15,'F#m'),(25.15,'D'),(33.65,'A'),(42.65,'E'),(50.85,'A')]

def chord_weight(start, end):
    w=np.zeros(N); s=int(start*SR); e=int(min(end,DUR)*SR)
    xf=int(0.9*SR)
    if e<=s: return w
    w[s:e]=1.0
    a=min(xf,e-s); w[s:s+a]*=np.linspace(0,1,a)
    b=min(xf,e-s); w[e-b:e]*=np.linspace(1,0,b)
    return w

def build_pad():
    pad=np.zeros((N,2))
    for i,(st,ch) in enumerate(PROG):
        end = PROG[i+1][0] if i+1<len(PROG) else DUR
        w=chord_weight(st, end+0.9)
        for j,f in enumerate(CHORDS[ch]):
            det=1+0.004*(j-1.5)                       # slight per-voice detune
            # warm tone: sine + soft triangle partial + gentle vibrato
            vib=1+0.0016*np.sin(2*np.pi*4.6*T + j)
            voice = 0.6*np.sin(2*np.pi*f*det*vib*T) + 0.16*np.sin(2*np.pi*2*f*det*T) \
                    + 0.10*np.sin(2*np.pi*3*f*det*T)
            amp = (0.14 if j<3 else 0.08)
            panL=0.5+0.28*np.sin(0.2*T+j); panR=1-panL
            pad[:,0]+= amp*w*voice*panL
            pad[:,1]+= amp*w*voice*panR
    # slow swell over whole piece
    swell = 0.7+0.3*np.sin(2*np.pi*T/DUR - np.pi/2)
    pad*=swell[:,None]
    return pad

def build_sub():
    sub=np.zeros(N)
    for i,(st,ch) in enumerate(PROG):
        end = PROG[i+1][0] if i+1<len(PROG) else DUR
        root=CHORDS[ch][0]/2
        w=chord_weight(st,end+0.9)
        sub += w*0.5*np.sin(2*np.pi*root*T)
    # gentle 1.5s heartbeat pulse
    puls=np.zeros(N)
    beat=1.5
    for k in range(int(DUR/beat)+1):
        c=int(k*beat*SR); ln=int(0.5*SR)
        if c<N:
            seg=np.arange(min(ln,N-c))
            env=np.exp(-seg/ (0.16*SR))
            puls[c:c+len(seg)] += env
    return sub*(0.5+0.5*puls)*0.6

def build_shimmer():
    sh=np.zeros((N,2))
    notes=[880.0,1108.7,1318.5,1760.0]  # A5 C#6 E6 A6
    times=np.arange(2.0, DUR-2, 1.9)
    for k,tt in enumerate(times):
        f=notes[k%len(notes)]*(1 if k%3 else 2)
        c=int(tt*SR); ln=int(2.2*SR); seg=np.arange(min(ln,N-c))
        if len(seg)==0: continue
        env=np.exp(-seg/(0.7*SR))*np.sin(np.pi*np.linspace(0,1,len(seg)))**0.5
        tone=0.5*np.sin(2*np.pi*f*(seg/SR))+0.2*np.sin(2*np.pi*2*f*(seg/SR))
        pan=0.5+0.4*math.sin(k)
        sh[c:c+len(seg),0]+=0.05*env*tone*pan
        sh[c:c+len(seg),1]+=0.05*env*tone*(1-pan)
    return sh

def build_risers():
    r=np.zeros((N,2))
    noise=rng.standard_normal(N)
    # cheap lowpass via cumulative smoothing
    for b in BOUNDS:
        c=int(b*SR); pre=int(1.1*SR)
        s=max(0,c-pre); seg=np.arange(c-s)
        if len(seg)==0: continue
        env=(seg/len(seg))**2.2
        # bandpassed noise sweep
        nz=noise[s:c]*env
        r[s:c,0]+=0.16*nz; r[s:c,1]+=0.16*np.roll(nz,50)
        # soft impact at boundary
        il=int(0.7*SR); iseg=np.arange(min(il,N-c))
        if len(iseg):
            ie=np.exp(-iseg/(0.18*SR))
            boom=np.sin(2*np.pi*np.linspace(60,42,len(iseg))*(iseg/SR))
            r[c:c+len(iseg),0]+=0.22*ie*boom; r[c:c+len(iseg),1]+=0.22*ie*boom
    # smooth the noise a touch (moving average)
    k=np.ones(24)/24
    r[:,0]=np.convolve(r[:,0],k,'same'); r[:,1]=np.convolve(r[:,1],k,'same')
    return r

# ----------------------------------------------------------------- VO
def synth_vo():
    vo=np.zeros((N,2)); ok=False
    with tempfile.TemporaryDirectory() as td:
        for i,(st,text) in enumerate(VO):
            mp3=os.path.join(td,f"vo{i}.mp3")
            try:
                subprocess.run(["edge-tts","--voice",VOICE,f"--rate={RATE}","--text",text,
                                "--write-media",mp3], check=True,
                               capture_output=True, timeout=60)
                raw=subprocess.run([FF,"-hide_banner","-loglevel","error","-i",mp3,
                                    "-ac","1","-ar",str(SR),"-f","f32le","-"],
                                   check=True, capture_output=True).stdout
                mono=np.frombuffer(raw,dtype=np.float32).copy()
            except Exception as e:
                print("VO fail line",i,e, file=sys.stderr); continue
            ok=True
            # light de-ess-free warmth: normalize each line
            mono = norm_rms(mono, -14.5)
            c=int(st*SR); ln=min(len(mono),N-c)
            if ln<=0: continue
            # small fades
            fa=int(0.02*SR)
            mono[:fa]*=np.linspace(0,1,fa); mono[-fa:]*=np.linspace(1,0,fa)
            vo[c:c+ln,0]+=mono[:ln]; vo[c:c+ln,1]+=mono[:ln]
    return vo, ok

def duck_env(vo):
    """Vectorized ducking envelope: smoothed |VO| with slight look-ahead."""
    mono=np.abs(vo).mean(1)
    slow=np.convolve(mono, np.ones(int(0.13*SR))/int(0.13*SR),'same')
    fast=np.convolve(mono, np.ones(int(0.02*SR))/int(0.02*SR),'same')
    env=np.maximum(slow, 0.9*fast)
    env/=(env.max()+1e-9)
    env=np.roll(env, -int(0.05*SR))            # duck opens a hair before the word
    # gate tiny values so silent gaps fully un-duck
    env=np.clip((env-0.06)/0.94,0,1)
    return env

# ----------------------------------------------------------------- master
def limit(x, ceil_db=-1.2):
    peak=np.max(np.abs(x))+1e-9
    x=x/peak*db(-0.5)
    x=softclip(x,1.6)*db(-2.0)
    peak=np.max(np.abs(x))+1e-9
    return x*(db(ceil_db)/peak)

def write_wav(path, x):
    x=np.clip(x,-1,1); pcm=(x*32767).astype('<i2').tobytes()
    p=subprocess.Popen([FF,"-y","-hide_banner","-loglevel","error","-f","s16le",
                        "-ar",str(SR),"-ac","2","-i","pipe:0", str(path)], stdin=subprocess.PIPE)
    p.communicate(pcm)

def main():
    print("building bed…")
    music = build_pad()
    music[:,0]+=build_sub(); music[:,1]+=build_sub()
    music += build_shimmer()
    music += build_risers()
    # space
    wet = early_reflections(music.mean(1)*0.5)
    music = music*0.9 + wet
    music = norm_rms(music, -19.5)

    print("rendering voiceover…")
    vo, ok = synth_vo()
    if ok:
        d = duck_env(vo)
        music *= (1 - 0.72*d)[:,None]          # duck bed ~11 dB under VO for clarity
        vo = norm_rms(vo, -12.6)
        mix = music + vo
    else:
        print("!! no VO — music only")
        mix = music
    mix = limit(mix, -1.2)

    # master fades
    fi=int(0.4*SR); fo=int(0.8*SR)
    mix[:fi]*=np.linspace(0,1,fi)[:,None]; mix[-fo:]*=np.linspace(1,0,fo)[:,None]

    write_wav(OUT/"mix.wav", mix)
    write_wav(OUT/"music.wav", limit(music,-1.5))
    if ok: write_wav(OUT/"vo.wav", np.clip(vo,-1,1))
    print("wrote", OUT/"mix.wav")

if __name__=="__main__":
    main()
