import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {fade} from '@remotion/transitions/fade';
import {clockWipe} from '@remotion/transitions/clock-wipe';
import {Star, Triangle} from '@remotion/shapes';
import {MeshBg, FloatingDots} from './Background';
import {KineticHeadline, DrawUnderline, CountUp, CheckBadge} from './Kinetic';
import {C, POPPINS, INTER, glass} from './theme';

const W = 1080;
const H = 1920;

const useReveal = (delay = 0, settle = 18) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: settle});
  return {opacity: s, transform: `translateY(${interpolate(s, [0, 1], [36, 0])}px)`};
};

const Kicker: React.FC<{children: React.ReactNode; color: string; delay?: number}> = ({
  children,
  color,
  delay = 0,
}) => {
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
        background: `${color}14`,
      }}
    >
      <span style={{width: 10, height: 10, borderRadius: '50%', background: color, boxShadow: `0 0 14px ${color}`}} />
      {children}
    </div>
  );
};

const Frame: React.FC<{children: React.ReactNode}> = ({children}) => (
  <AbsoluteFill
    style={{
      justifyContent: 'center',
      alignItems: 'center',
      padding: 80,
      textAlign: 'center',
      fontFamily: INTER,
    }}
  >
    {children}
  </AbsoluteFill>
);

const SlowSpin: React.FC<{children: React.ReactNode; speed?: number}> = ({children, speed = 1}) => {
  const frame = useCurrentFrame();
  return <div style={{transform: `rotate(${frame * speed}deg)`}}>{children}</div>;
};

/* ----------------------------- Scene 1: Intro ----------------------------- */
const SceneIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame, fps, config: {damping: 10, mass: 0.8}});
  const sub = useReveal(46);
  return (
    <AbsoluteFill>
      <MeshBg tint={C.blue} />
      <FloatingDots />
      <Frame>
        <div style={{position: 'absolute', top: 360, opacity: 0.5}}>
          <SlowSpin speed={0.2}>
            <Star points={5} innerRadius={120} outerRadius={250} fill="none" stroke={C.blue} strokeWidth={2} />
          </SlowSpin>
        </div>
        <div
          style={{
            transform: `scale(${pop}) rotate(${interpolate(pop, [0, 1], [-12, 0])}deg)`,
            width: 170,
            height: 170,
            borderRadius: 44,
            background: `linear-gradient(135deg, ${C.blue}, ${C.green})`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 30px 90px ${C.blue}66`,
            marginBottom: 54,
          }}
        >
          <span style={{fontSize: 92}}>📍</span>
        </div>
        <KineticHeadline text="Local Service Ads" size={84} delay={14} accent={C.blue} />
        <div style={{height: 8}} />
        <KineticHeadline text="{+} SEO for {Realtors}" size={84} delay={26} accent={C.blue} />
        <div style={{...sub, color: C.mute, fontSize: 34, marginTop: 40, fontWeight: 500}}>
          How top agents get found on Google
        </div>
      </Frame>
    </AbsoluteFill>
  );
};

/* ----------------------------- Scene 2: Hook ------------------------------ */
const SceneHook: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const barIn = spring({frame: frame - 36, fps, config: {damping: 13}});
  const caret = Math.floor(frame / 8) % 2;
  const sub = useReveal(78);
  return (
    <AbsoluteFill>
      <MeshBg tint={C.red} />
      <Frame>
        <div style={{marginBottom: 40}}>
          <Kicker color={C.red}>High-intent search</Kicker>
        </div>
        <KineticHeadline text="“Realtor {near me}”" size={70} delay={8} accent={C.red} />
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
            transform: `scale(${interpolate(barIn, [0, 1], [0.8, 1])})`,
            opacity: barIn,
            boxShadow: '0 30px 70px rgba(0,0,0,0.5)',
          }}
        >
          <span style={{fontSize: 42}}>🔍</span>
          <span style={{color: C.ink, fontSize: 38, fontWeight: 600, fontFamily: INTER}}>
            realtor near me
            <span style={{opacity: caret, color: C.blue}}>|</span>
          </span>
        </div>
        <div style={{...sub, color: C.mute, fontSize: 36, marginTop: 56, fontWeight: 500, lineHeight: 1.35}}>
          Buyers ready to act.{' '}
          <span style={{color: C.white, fontWeight: 800, fontFamily: POPPINS}}>
            Are you the one they see?
          </span>
        </div>
      </Frame>
    </AbsoluteFill>
  );
};

/* -------------------------- Scene 3: Why LSAs win ------------------------- */
const SerpRow: React.FC<{top: number; delay: number; label: string; highlight?: boolean}> = ({
  top,
  delay,
  label,
  highlight,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 16}, durationInFrames: 20});
  const glow = highlight ? interpolate(Math.sin(frame / 12), [-1, 1], [0.4, 0.8]) : 0;
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: '50%',
        transform: `translateX(-50%) translateY(${interpolate(s, [0, 1], [40, 0])}px)`,
        opacity: s,
        width: 840,
        height: highlight ? 156 : 104,
        borderRadius: 28,
        ...(highlight
          ? {background: C.white, boxShadow: `0 24px 70px ${C.green}${Math.round(glow * 99).toString(16)}`}
          : glass(C.white)),
        display: 'flex',
        alignItems: 'center',
        padding: '0 36px',
        gap: 22,
      }}
    >
      {highlight && <CheckBadge delay={delay + 6} size={70} color={C.green} />}
      <div style={{textAlign: 'left'}}>
        <div
          style={{
            color: highlight ? C.ink : C.mute,
            fontSize: highlight ? 38 : 30,
            fontWeight: highlight ? 800 : 600,
            fontFamily: highlight ? POPPINS : INTER,
          }}
        >
          {label}
        </div>
        {highlight && (
          <div style={{color: C.green, fontSize: 25, fontWeight: 700, marginTop: 4, fontFamily: INTER}}>
            Google Guaranteed · Top of page
          </div>
        )}
      </div>
    </div>
  );
};

const SceneSerp: React.FC = () => (
  <AbsoluteFill>
    <MeshBg tint={C.green} />
    <Frame>
      <div style={{position: 'absolute', top: 170, width: '100%'}}>
        <div style={{marginBottom: 28}}>
          <Kicker color={C.green}>Why LSAs win</Kicker>
        </div>
        <KineticHeadline text="They sit {above} everything" size={60} delay={6} accent={C.green} />
        <div style={{display: 'flex', justifyContent: 'center', marginTop: 10}}>
          <DrawUnderline delay={34} width={360} color={C.green} />
        </div>
      </div>
      <div style={{position: 'absolute', top: 600, width: '100%', height: 760}}>
        <SerpRow top={0} delay={28} highlight label="Your Local Service Ad" />
        <SerpRow top={210} delay={52} label="Standard Google Ad" />
        <SerpRow top={340} delay={66} label="Organic SEO result" />
        <SerpRow top={460} delay={80} label="Organic SEO result" />
      </div>
    </Frame>
  </AbsoluteFill>
);

/* --------------------------- Scene 4: Trust pills ------------------------- */
const Pill: React.FC<{delay: number; icon: string; title: string; body: string; accent: string}> = ({
  delay,
  icon,
  title,
  body,
  accent,
}) => {
  const r = useReveal(delay, 16);
  return (
    <div
      style={{
        ...r,
        ...glass(accent),
        width: 860,
        padding: '32px 36px',
        display: 'flex',
        gap: 26,
        alignItems: 'center',
        textAlign: 'left',
      }}
    >
      <div
        style={{
          width: 96,
          height: 96,
          minWidth: 96,
          borderRadius: 26,
          background: `${accent}26`,
          border: `1px solid ${accent}55`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 50,
        }}
      >
        {icon}
      </div>
      <div>
        <div style={{color: C.white, fontSize: 40, fontWeight: 800, fontFamily: POPPINS}}>{title}</div>
        <div style={{color: C.mute, fontSize: 29, fontWeight: 500, marginTop: 6, lineHeight: 1.3}}>
          {body}
        </div>
      </div>
    </div>
  );
};

const SceneValue: React.FC = () => (
  <AbsoluteFill>
    <MeshBg tint={C.yellow} />
    <Frame>
      <div style={{position: 'absolute', top: 180}}>
        <div style={{marginBottom: 26}}>
          <Kicker color={C.yellow}>Built for trust</Kicker>
        </div>
        <KineticHeadline text="Pay per {lead}, not click" size={58} delay={6} accent={C.yellow} />
      </div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 30, marginTop: 200}}>
        <Pill delay={26} icon="✅" title="Google Guaranteed" body="Verified & licensed — instant credibility up top." accent={C.green} />
        <Pill delay={42} icon="💸" title="Only pay for real leads" body="Charged per call, not per click on your ad." accent={C.yellow} />
        <Pill delay={58} icon="📞" title="Calls from ready buyers" body="High commercial intent — people acting now." accent={C.blue} />
      </div>
    </Frame>
  </AbsoluteFill>
);

/* --------------------------- Scene 5: The numbers ------------------------- */
const Bar: React.FC<{delay: number; label: string; pct: number; color: string}> = ({
  delay,
  label,
  pct,
  color,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const g = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: 44});
  return (
    <div style={{width: 860, marginBottom: 44, textAlign: 'left'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14}}>
        <span style={{color: C.white, fontSize: 30, fontWeight: 700, fontFamily: INTER}}>{label}</span>
        <span style={{color, fontSize: 40, fontWeight: 900, fontFamily: POPPINS}}>
          <CountUp to={pct} delay={delay} duration={44} suffix="%" />
        </span>
      </div>
      <div style={{height: 28, borderRadius: 14, background: 'rgba(255,255,255,0.08)', overflow: 'hidden'}}>
        <div
          style={{
            height: '100%',
            width: `${interpolate(g, [0, 1], [0, pct])}%`,
            borderRadius: 14,
            background: `linear-gradient(90deg, ${color}, ${color}99)`,
            boxShadow: `0 0 24px ${color}88`,
          }}
        />
      </div>
    </div>
  );
};

const SceneNumbers: React.FC = () => (
  <AbsoluteFill>
    <MeshBg tint={C.blue} />
    <Frame>
      <div style={{position: 'absolute', top: 210}}>
        <div style={{marginBottom: 26}}>
          <Kicker color={C.blueLite}>The long game</Kicker>
        </div>
        <KineticHeadline text="LSAs win {today}. SEO {compounds}." size={56} delay={6} accent={C.blueLite} />
      </div>
      <div style={{marginTop: 320}}>
        <Bar delay={34} label="Local Service Ads — fast top spot" pct={92} color={C.green} />
        <Bar delay={54} label="SEO — durable organic traffic" pct={78} color={C.blueLite} />
        <Bar delay={74} label="Both together — local dominance" pct={100} color={C.yellow} />
      </div>
    </Frame>
  </AbsoluteFill>
);

/* --------------------------- Scene 6: Playbook ---------------------------- */
const Step: React.FC<{delay: number; n: number; text: string}> = ({delay, n, text}) => {
  const r = useReveal(delay, 16);
  return (
    <div style={{...r, ...glass(C.green), width: 860, padding: '28px 34px', display: 'flex', alignItems: 'center', gap: 26, textAlign: 'left'}}>
      <div
        style={{
          width: 72,
          height: 72,
          minWidth: 72,
          borderRadius: 20,
          background: `linear-gradient(135deg, ${C.green}, ${C.blue})`,
          color: C.white,
          fontSize: 40,
          fontWeight: 900,
          fontFamily: POPPINS,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: `0 0 30px ${C.green}66`,
        }}
      >
        {n}
      </div>
      <div style={{color: C.white, fontSize: 36, fontWeight: 600, lineHeight: 1.25}}>{text}</div>
    </div>
  );
};

const ScenePlaybook: React.FC = () => (
  <AbsoluteFill>
    <MeshBg tint={C.green} />
    <Frame>
      <div style={{position: 'absolute', top: 210}}>
        <div style={{marginBottom: 26}}>
          <Kicker color={C.green}>Your playbook</Kicker>
        </div>
        <KineticHeadline text="3 moves to {win}" size={66} delay={6} accent={C.green} />
      </div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 34, marginTop: 200}}>
        <Step delay={28} n={1} text="Claim & verify your Google Guaranteed profile" />
        <Step delay={46} n={2} text="Run LSAs to capture high-intent calls now" />
        <Step delay={64} n={3} text="Invest in local SEO for lasting reach" />
      </div>
    </Frame>
  </AbsoluteFill>
);

/* ----------------------------- Scene 7: Outro ----------------------------- */
const SceneOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tag = useReveal(46);
  return (
    <AbsoluteFill>
      <MeshBg tint={C.blue} />
      <FloatingDots count={20} />
      <div style={{position: 'absolute', top: 520, left: '50%', transform: 'translateX(-50%)', opacity: 0.35}}>
        <div style={{transform: `rotate(${-frame * 0.3}deg)`}}>
          <Triangle length={320} direction="up" fill="none" stroke={C.green} strokeWidth={2} />
        </div>
      </div>
      <Frame>
        <KineticHeadline text="Get found {locally.}" size={92} delay={6} accent={C.green} stagger={6} />
        <div style={{color: C.mute, fontSize: 34, marginTop: 36, fontWeight: 500, ...useReveal(34)}}>
          Local Service Ads + SEO, working together.
        </div>
        <div
          style={{
            ...tag,
            marginTop: 60,
            padding: '22px 46px',
            borderRadius: 100,
            ...glass(C.blue),
            color: C.white,
            fontSize: 34,
            fontWeight: 700,
            fontFamily: POPPINS,
          }}
        >
          Momentum Digital · Mac Frederick
        </div>
      </Frame>
    </AbsoluteFill>
  );
};

/* ------------------------------- Timeline --------------------------------- */
const ease = linearTiming({durationInFrames: 25, easing: Easing.inOut(Easing.ease)});

export const Highlight: React.FC = () => {
  return (
    <AbsoluteFill style={{background: C.ink}}>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={230}>
          <SceneIntro />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({direction: 'from-bottom'})} timing={ease} />
        <TransitionSeries.Sequence durationInFrames={290}>
          <SceneHook />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={wipe({direction: 'from-left'})} timing={ease} />
        <TransitionSeries.Sequence durationInFrames={320}>
          <SceneSerp />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({direction: 'from-right'})} timing={ease} />
        <TransitionSeries.Sequence durationInFrames={320}>
          <SceneValue />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={clockWipe({width: W, height: H})} timing={ease} />
        <TransitionSeries.Sequence durationInFrames={300}>
          <SceneNumbers />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({direction: 'from-bottom'})} timing={ease} />
        <TransitionSeries.Sequence durationInFrames={300}>
          <ScenePlaybook />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={ease} />
        <TransitionSeries.Sequence durationInFrames={190}>
          <SceneOutro />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
