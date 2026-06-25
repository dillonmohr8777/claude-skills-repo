import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, Easing} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {fade} from '@remotion/transitions/fade';
import {clockWipe} from '@remotion/transitions/clock-wipe';
import {MeshBg} from './Background';
import {KineticHeadline, CountUp} from './Kinetic';
import {C, POPPINS, INTER} from './theme';
import {Rig, CameraRig, Particles, FloatingShapes} from './three/world';
import {Medallion, Bars3D, SerpStack3D, Badge3D} from './three/objects';

const W = 1080;
const H = 1920;

/* layered text-shadow → faux-extruded 3D type for the DOM overlays */
const extrude = (c: string): React.CSSProperties => ({
  textShadow: `0 1px 0 ${c}, 0 2px 0 ${c}, 0 3px 0 ${c}, 0 4px 0 ${c}, 0 6px 14px rgba(0,0,0,0.55)`,
});

const useReveal = (delay = 0, settle = 18) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: settle});
  return {opacity: s, transform: `translateY(${interpolate(s, [0, 1], [34, 0])}px)`};
};

const Kicker: React.FC<{children: React.ReactNode; color: string; delay?: number}> = ({children, color, delay = 0}) => {
  const r = useReveal(delay);
  return (
    <div
      style={{
        ...r,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 12,
        color,
        fontFamily: INTER,
        fontWeight: 700,
        letterSpacing: 6,
        fontSize: 26,
        textTransform: 'uppercase',
        padding: '12px 24px',
        borderRadius: 100,
        border: `1px solid ${color}55`,
        background: `${color}1f`,
      }}
    >
      <span style={{width: 10, height: 10, borderRadius: '50%', background: color, boxShadow: `0 0 14px ${color}`}} />
      {children}
    </div>
  );
};

/** Transparent 3D layer over the gradient backdrop. */
const Stage: React.FC<{tint: string; camZ?: number; children: React.ReactNode; particles?: number; shapes?: boolean}> = ({
  tint,
  camZ = 7,
  children,
  particles = 200,
  shapes = true,
}) => (
  <ThreeCanvas
    width={W}
    height={H}
    camera={{fov: 45, position: [0, 0, camZ], near: 0.1, far: 100}}
    gl={{alpha: true, antialias: true}}
    style={{position: 'absolute', inset: 0}}
  >
    <CameraRig z={camZ} />
    <Rig tint={tint} />
    {shapes && <FloatingShapes tint={tint} />}
    <Particles count={particles} color={tint} />
    {children}
  </ThreeCanvas>
);

const Overlay: React.FC<{children: React.ReactNode; justify?: string}> = ({children, justify = 'flex-end'}) => (
  <AbsoluteFill
    style={{
      justifyContent: justify,
      alignItems: 'center',
      padding: 80,
      paddingBottom: 150,
      textAlign: 'center',
      fontFamily: INTER,
    }}
  >
    {children}
  </AbsoluteFill>
);

/* ------------------------------- Scenes ---------------------------------- */

const SceneHero: React.FC = () => {
  const sub = useReveal(70);
  const title = 96;
  return (
    <AbsoluteFill>
      <MeshBg tint={C.blue} />
      <Stage tint={C.blue} camZ={11} particles={240}>
        <group position={[0, 1.6, 0]}>
          <Medallion delay={6} scale={1.0} />
        </group>
      </Stage>
      <Overlay>
        <div style={{...useReveal(40)}}>
          <div style={{...extrude(C.ink2), color: C.white, fontSize: title, fontWeight: 900, fontFamily: POPPINS, lineHeight: 1.02}}>
            Local Service Ads
          </div>
          <div style={{...extrude(C.ink2), color: C.blue, fontSize: title, fontWeight: 900, fontFamily: POPPINS, lineHeight: 1.02}}>
            + SEO for Realtors
          </div>
        </div>
        <div style={{...sub, color: C.mute, fontSize: 34, marginTop: 30, fontWeight: 500}}>
          Momentum Digital · how top agents get found
        </div>
      </Overlay>
    </AbsoluteFill>
  );
};

const SceneHook: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const barIn = spring({frame: frame - 24, fps, config: {damping: 13}});
  const caret = Math.floor(frame / 8) % 2;
  const sub = useReveal(64);
  return (
    <AbsoluteFill>
      <MeshBg tint={C.red} />
      <Stage tint={C.red} camZ={7} particles={160} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 80, textAlign: 'center'}}>
        <div style={{marginBottom: 38}}>
          <Kicker color={C.red}>High-intent search</Kicker>
        </div>
        <KineticHeadline text="“Realtor {near} {me}”" size={72} delay={6} accent={C.red} />
        <div
          style={{
            marginTop: 54,
            width: 800,
            height: 104,
            borderRadius: 52,
            background: C.white,
            display: 'flex',
            alignItems: 'center',
            padding: '0 40px',
            gap: 20,
            transform: `perspective(900px) rotateX(${interpolate(barIn, [0, 1], [22, 0])}deg) scale(${interpolate(barIn, [0, 1], [0.8, 1])})`,
            opacity: barIn,
            boxShadow: '0 40px 80px rgba(0,0,0,0.55)',
          }}
        >
          <span style={{fontSize: 42}}>🔍</span>
          <span style={{color: C.ink, fontSize: 38, fontWeight: 600, fontFamily: INTER}}>
            realtor near me<span style={{opacity: caret, color: C.blue}}>|</span>
          </span>
        </div>
        <div style={{...sub, color: C.mute, fontSize: 36, marginTop: 50, fontWeight: 500, lineHeight: 1.35}}>
          Buyers ready to act.{' '}
          <span style={{color: C.white, fontWeight: 800, fontFamily: POPPINS}}>Are you the one they see?</span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const SceneSerp: React.FC = () => (
  <AbsoluteFill>
    <MeshBg tint={C.green} />
    <Stage tint={C.green} camZ={12} particles={140} shapes={false}>
      <SerpStack3D delay={14} />
    </Stage>
    <AbsoluteFill style={{alignItems: 'center', paddingTop: 150, textAlign: 'center'}}>
      <div style={{marginBottom: 24}}>
        <Kicker color={C.green}>Why LSAs win</Kicker>
      </div>
      <div style={{...extrude(C.ink2)}}>
        <KineticHeadline text="They sit {above} it all" size={60} delay={6} accent={C.green} />
      </div>
    </AbsoluteFill>
  </AbsoluteFill>
);

const SceneTrust: React.FC = () => {
  const items = ['Verified & Google Guaranteed', 'Pay per lead, not per click', 'Calls from ready-to-act buyers'];
  return (
    <AbsoluteFill>
      <MeshBg tint={C.yellow} />
      <Stage tint={C.yellow} camZ={11} particles={170}>
        <group position={[0, 0.9, 0]}>
          <Badge3D delay={10} />
        </group>
      </Stage>
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 150, textAlign: 'center'}}>
        <div style={{marginBottom: 24}}>
          <Kicker color={C.yellow}>Built for trust</Kicker>
        </div>
        <div style={{...extrude(C.ink2)}}>
          <KineticHeadline text="Pay per {lead}" size={70} delay={6} accent={C.yellow} />
        </div>
      </AbsoluteFill>
      <Overlay justify="flex-end">
        <div style={{display: 'flex', flexDirection: 'column', gap: 22}}>
          {items.map((t, i) => {
            const r = useReveal(40 + i * 14);
            return (
              <div key={i} style={{...r, display: 'flex', alignItems: 'center', gap: 18, color: C.white, fontSize: 36, fontWeight: 600}}>
                <span style={{color: C.green, fontSize: 40, fontFamily: POPPINS, fontWeight: 900}}>✓</span>
                {t}
              </div>
            );
          })}
        </div>
      </Overlay>
    </AbsoluteFill>
  );
};

const SceneNumbers: React.FC = () => {
  const rows = [
    {label: 'Local Service Ads — fast top spot', pct: 92, c: C.green},
    {label: 'SEO — durable organic traffic', pct: 78, c: C.blueLite},
    {label: 'Both together — local dominance', pct: 100, c: C.yellow},
  ];
  return (
    <AbsoluteFill>
      <MeshBg tint={C.blue} />
      <Stage tint={C.blue} camZ={13} particles={150} shapes={false}>
        <Bars3D delay={16} />
      </Stage>
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 150, textAlign: 'center'}}>
        <div style={{marginBottom: 24}}>
          <Kicker color={C.blueLite}>The long game</Kicker>
        </div>
        <div style={{...extrude(C.ink2)}}>
          <KineticHeadline text="LSAs win {today}. SEO {compounds}." size={52} delay={6} accent={C.blueLite} />
        </div>
      </AbsoluteFill>
      <Overlay>
        <div style={{display: 'flex', flexDirection: 'column', gap: 18, width: 880}}>
          {rows.map((r, i) => {
            const rv = useReveal(40 + i * 12);
            return (
              <div key={i} style={{...rv, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline'}}>
                <span style={{color: C.white, fontSize: 30, fontWeight: 600, fontFamily: INTER}}>{r.label}</span>
                <span style={{color: r.c, fontSize: 46, fontWeight: 900, fontFamily: POPPINS, ...extrude(C.ink)}}>
                  <CountUp to={r.pct} delay={40 + i * 12} duration={40} suffix="%" />
                </span>
              </div>
            );
          })}
        </div>
      </Overlay>
    </AbsoluteFill>
  );
};

const ScenePlaybook: React.FC = () => {
  const steps = ['Claim & verify your Google Guaranteed profile', 'Run LSAs to capture high-intent calls now', 'Invest in local SEO for lasting reach'];
  return (
    <AbsoluteFill>
      <MeshBg tint={C.green} />
      <Stage tint={C.green} camZ={7} particles={170} />
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 160, textAlign: 'center'}}>
        <div style={{marginBottom: 24}}>
          <Kicker color={C.green}>Your playbook</Kicker>
        </div>
        <div style={{...extrude(C.ink2)}}>
          <KineticHeadline text="3 moves to {win}" size={68} delay={6} accent={C.green} />
        </div>
      </AbsoluteFill>
      <Overlay>
        <div style={{display: 'flex', flexDirection: 'column', gap: 30, perspective: 1000}}>
          {steps.map((t, i) => {
            const r = useReveal(34 + i * 16, 16);
            return (
              <div
                key={i}
                style={{
                  opacity: r.opacity,
                  transform: `${r.transform} rotateX(8deg)`,
                  transformStyle: 'preserve-3d',
                  width: 860,
                  padding: '26px 32px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 24,
                  textAlign: 'left',
                  borderRadius: 26,
                  background: 'linear-gradient(160deg, rgba(255,255,255,0.12), rgba(255,255,255,0.03))',
                  border: `1px solid ${C.green}55`,
                  boxShadow: `0 30px 60px rgba(0,0,0,0.5)`,
                }}
              >
                <div
                  style={{
                    width: 70,
                    height: 70,
                    minWidth: 70,
                    borderRadius: 18,
                    background: `linear-gradient(135deg, ${C.green}, ${C.blue})`,
                    color: C.white,
                    fontSize: 38,
                    fontWeight: 900,
                    fontFamily: POPPINS,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: `0 0 26px ${C.green}88`,
                  }}
                >
                  {i + 1}
                </div>
                <div style={{color: C.white, fontSize: 34, fontWeight: 600, lineHeight: 1.25}}>{t}</div>
              </div>
            );
          })}
        </div>
      </Overlay>
    </AbsoluteFill>
  );
};

const SceneOutro: React.FC = () => {
  const tag = useReveal(46);
  return (
    <AbsoluteFill>
      <MeshBg tint={C.blue} />
      <Stage tint={C.blue} camZ={10} particles={260}>
        <group position={[0, 2.0, 0]} scale={0.62}>
          <Medallion delay={4} />
        </group>
      </Stage>
      <Overlay>
        <div style={{...extrude(C.ink2)}}>
          <KineticHeadline text="Get found {locally.}" size={92} delay={6} accent={C.green} stagger={6} />
        </div>
        <div style={{...useReveal(34), color: C.mute, fontSize: 34, marginTop: 30, fontWeight: 500}}>
          Local Service Ads + SEO, working together.
        </div>
        <div
          style={{
            ...tag,
            marginTop: 50,
            padding: '20px 44px',
            borderRadius: 100,
            background: 'linear-gradient(160deg, rgba(255,255,255,0.12), rgba(255,255,255,0.03))',
            border: `1px solid ${C.blue}66`,
            color: C.white,
            fontSize: 32,
            fontWeight: 700,
            fontFamily: POPPINS,
          }}
        >
          Momentum Digital · Mac Frederick
        </div>
      </Overlay>
    </AbsoluteFill>
  );
};

/* ------------------------------- Timeline -------------------------------- */
const t = (d = 25) => linearTiming({durationInFrames: d, easing: Easing.inOut(Easing.ease)});

export const Highlight3D: React.FC = () => (
  <AbsoluteFill style={{background: C.ink}}>
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={290}>
        <SceneHero />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={260}>
        <SceneHook />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={slide({direction: 'from-right'})} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={320}>
        <SceneSerp />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={clockWipe({width: W, height: H})} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={300}>
        <SceneTrust />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={slide({direction: 'from-bottom'})} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={300}>
        <SceneNumbers />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={wipe({direction: 'from-left'})} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={260}>
        <ScenePlaybook />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={t()} />
      <TransitionSeries.Sequence durationInFrames={220}>
        <SceneOutro />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  </AbsoluteFill>
);
