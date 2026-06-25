import React from 'react';
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

/* ------------------------------------------------------------------ */
/* Palette + shared helpers                                            */
/* ------------------------------------------------------------------ */

const COLORS = {
  blue: '#4285F4',
  red: '#EA4335',
  yellow: '#FBBC05',
  green: '#34A853',
  ink: '#0B1220',
  ink2: '#111c30',
  white: '#FFFFFF',
  mute: 'rgba(255,255,255,0.62)',
};

const FONT = 'Inter, Helvetica, Arial, sans-serif';

/** Eased fade + upward slide that settles by `settle` frames in. */
const useReveal = (delay = 0, settle = 18) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: settle});
  return {
    opacity: interpolate(s, [0, 1], [0, 1]),
    transform: `translateY(${interpolate(s, [0, 1], [40, 0])}px)`,
  };
};

const Bg: React.FC<{tint?: string}> = ({tint = COLORS.blue}) => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 300], [0, 30], {extrapolateRight: 'extend'});
  return (
    <AbsoluteFill style={{background: COLORS.ink}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(900px 900px at ${50 + Math.sin(drift / 18) * 12}% ${
            22 + Math.cos(drift / 22) * 8
          }%, ${tint}33, transparent 60%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(700px 700px at ${30 + Math.cos(drift / 16) * 14}% 85%, ${COLORS.green}22, transparent 60%)`,
        }}
      />
    </AbsoluteFill>
  );
};

const Dots: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{opacity: 0.18}}>
      {Array.from({length: 14}).map((_, i) => {
        const x = (i * 137) % 1080;
        const y = (i * 311) % 1920;
        const float = Math.sin((frame + i * 40) / 30) * 14;
        const c = [COLORS.blue, COLORS.red, COLORS.yellow, COLORS.green][i % 4];
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y + float,
              width: 10 + (i % 3) * 6,
              height: 10 + (i % 3) * 6,
              borderRadius: '50%',
              background: c,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const Center: React.FC<{children: React.ReactNode; pad?: number}> = ({children, pad = 90}) => (
  <AbsoluteFill
    style={{
      justifyContent: 'center',
      alignItems: 'center',
      padding: pad,
      textAlign: 'center',
      fontFamily: FONT,
    }}
  >
    {children}
  </AbsoluteFill>
);

const Kicker: React.FC<{children: React.ReactNode; color?: string; delay?: number}> = ({
  children,
  color = COLORS.yellow,
  delay = 0,
}) => {
  const r = useReveal(delay);
  return (
    <div
      style={{
        ...r,
        color,
        fontWeight: 800,
        letterSpacing: 4,
        fontSize: 30,
        textTransform: 'uppercase',
        marginBottom: 28,
      }}
    >
      {children}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 1 — Intro                                                     */
/* ------------------------------------------------------------------ */

const SceneIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame, fps, config: {damping: 12, mass: 0.8}});
  const t1 = useReveal(20);
  const t2 = useReveal(34);
  const by = useReveal(54);
  return (
    <AbsoluteFill>
      <Bg tint={COLORS.blue} />
      <Dots />
      <Center>
        <div
          style={{
            transform: `scale(${pop})`,
            width: 150,
            height: 150,
            borderRadius: 40,
            background: `linear-gradient(135deg, ${COLORS.blue}, ${COLORS.green})`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 30px 80px rgba(66,133,244,0.45)',
            marginBottom: 50,
          }}
        >
          <span style={{fontSize: 84}}>📍</span>
        </div>
        <div style={{...t1, color: COLORS.white, fontSize: 78, fontWeight: 900, lineHeight: 1.05}}>
          Local Service Ads
        </div>
        <div style={{...t2, color: COLORS.blue, fontSize: 78, fontWeight: 900, lineHeight: 1.05}}>
          + SEO for Realtors
        </div>
        <div style={{...by, color: COLORS.mute, fontSize: 34, marginTop: 40, fontWeight: 600}}>
          How top agents get found on Google
        </div>
      </Center>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 2 — The hook / problem                                        */
/* ------------------------------------------------------------------ */

const SceneHook: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const barW = spring({frame: frame - 30, fps, config: {damping: 200}, durationInFrames: 30});
  const k = useReveal(0);
  const q = useReveal(14);
  const sub = useReveal(70);
  return (
    <AbsoluteFill>
      <Bg tint={COLORS.red} />
      <Center>
        <Kicker color={COLORS.red}>High-intent searches</Kicker>
        <div style={{...q, color: COLORS.white, fontSize: 64, fontWeight: 900, lineHeight: 1.1}}>
          “Realtor near me”
        </div>
        {/* search bar */}
        <div
          style={{
            marginTop: 46,
            width: 760,
            height: 96,
            borderRadius: 48,
            background: COLORS.white,
            display: 'flex',
            alignItems: 'center',
            padding: '0 36px',
            gap: 18,
            boxShadow: '0 24px 60px rgba(0,0,0,0.4)',
          }}
        >
          <span style={{fontSize: 40}}>🔍</span>
          <div style={{height: 36, overflow: 'hidden', flex: 1, textAlign: 'left'}}>
            <span style={{color: COLORS.ink, fontSize: 36, fontWeight: 600}}>
              realtor near me
            </span>
          </div>
          <div
            style={{
              width: `${interpolate(barW, [0, 1], [0, 100])}%`,
              maxWidth: 4,
              height: 44,
              background: COLORS.blue,
            }}
          />
        </div>
        <div style={{...sub, color: COLORS.mute, fontSize: 36, marginTop: 50, fontWeight: 600}}>
          Buyers ready to act. The question is —<br />
          <span style={{color: COLORS.white, fontWeight: 800}}>are you the one they see?</span>
        </div>
      </Center>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 3 — LSA sits at the very top                                  */
/* ------------------------------------------------------------------ */

const SerpRow: React.FC<{
  top: number;
  delay: number;
  label: string;
  highlight?: boolean;
}> = ({top, delay, label, highlight}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: 18});
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: '50%',
        transform: `translateX(-50%) translateY(${interpolate(s, [0, 1], [30, 0])}px)`,
        opacity: s,
        width: 820,
        height: highlight ? 150 : 110,
        borderRadius: 24,
        background: highlight ? COLORS.white : 'rgba(255,255,255,0.08)',
        border: highlight ? `none` : '1px solid rgba(255,255,255,0.12)',
        boxShadow: highlight ? '0 24px 70px rgba(52,168,83,0.5)' : 'none',
        display: 'flex',
        alignItems: 'center',
        padding: '0 34px',
        gap: 22,
      }}
    >
      {highlight && (
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: '50%',
            background: COLORS.green,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: COLORS.white,
            fontSize: 40,
            fontWeight: 900,
          }}
        >
          ✓
        </div>
      )}
      <div style={{textAlign: 'left'}}>
        <div
          style={{
            color: highlight ? COLORS.ink : COLORS.mute,
            fontSize: highlight ? 36 : 30,
            fontWeight: highlight ? 900 : 600,
          }}
        >
          {label}
        </div>
        {highlight && (
          <div style={{color: COLORS.green, fontSize: 26, fontWeight: 800, marginTop: 4}}>
            Google Guaranteed · Top of page
          </div>
        )}
      </div>
    </div>
  );
};

const SceneSerp: React.FC = () => {
  return (
    <AbsoluteFill>
      <Bg tint={COLORS.green} />
      <Center pad={60}>
        <div style={{position: 'absolute', top: 150, width: '100%'}}>
          <Kicker color={COLORS.green}>Why LSAs win</Kicker>
          <div style={{color: COLORS.white, fontSize: 58, fontWeight: 900, lineHeight: 1.1}}>
            They show up <span style={{color: COLORS.green}}>above</span><br /> everything else
          </div>
        </div>
        <div style={{position: 'absolute', top: 560, width: '100%', height: 700}}>
          <SerpRow top={0} delay={26} highlight label="Your Local Service Ad" />
          <SerpRow top={200} delay={48} label="Standard Google Ad" />
          <SerpRow top={330} delay={62} label="Organic SEO result" />
          <SerpRow top={460} delay={76} label="Organic SEO result" />
        </div>
      </Center>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 4 — Pay per lead + Google Guaranteed                          */
/* ------------------------------------------------------------------ */

const Pill: React.FC<{
  delay: number;
  icon: string;
  title: string;
  body: string;
  accent: string;
}> = ({delay, icon, title, body, accent}) => {
  const r = useReveal(delay);
  return (
    <div
      style={{
        ...r,
        width: 840,
        background: 'rgba(255,255,255,0.06)',
        border: `1px solid ${accent}55`,
        borderRadius: 30,
        padding: '34px 38px',
        display: 'flex',
        gap: 28,
        alignItems: 'center',
        textAlign: 'left',
      }}
    >
      <div
        style={{
          width: 96,
          height: 96,
          minWidth: 96,
          borderRadius: 24,
          background: `${accent}26`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 50,
        }}
      >
        {icon}
      </div>
      <div>
        <div style={{color: COLORS.white, fontSize: 40, fontWeight: 900}}>{title}</div>
        <div style={{color: COLORS.mute, fontSize: 30, fontWeight: 600, marginTop: 6, lineHeight: 1.3}}>
          {body}
        </div>
      </div>
    </div>
  );
};

const SceneValue: React.FC = () => {
  return (
    <AbsoluteFill>
      <Bg tint={COLORS.yellow} />
      <Center>
        <div style={{position: 'absolute', top: 170}}>
          <Kicker color={COLORS.yellow}>Built for trust</Kicker>
          <div style={{color: COLORS.white, fontSize: 60, fontWeight: 900, lineHeight: 1.1}}>
            Pay per <span style={{color: COLORS.yellow}}>lead</span>,<br />not per click
          </div>
        </div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 34, marginTop: 220}}>
          <Pill
            delay={24}
            icon="✅"
            title="Google Guaranteed badge"
            body="Verified & licensed — instant credibility at the top."
            accent={COLORS.green}
          />
          <Pill
            delay={42}
            icon="💸"
            title="Only pay for real leads"
            body="Charged per call, not per click on your ad."
            accent={COLORS.yellow}
          />
          <Pill
            delay={60}
            icon="📞"
            title="Calls from ready buyers"
            body="High commercial intent — people looking to act now."
            accent={COLORS.blue}
          />
        </div>
      </Center>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 5 — SEO long game                                             */
/* ------------------------------------------------------------------ */

const Bar: React.FC<{delay: number; label: string; pct: number; color: string}> = ({
  delay,
  label,
  pct,
  color,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const g = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: 40});
  return (
    <div style={{width: 820, marginBottom: 40, textAlign: 'left'}}>
      <div style={{color: COLORS.white, fontSize: 32, fontWeight: 800, marginBottom: 12}}>{label}</div>
      <div style={{height: 46, borderRadius: 23, background: 'rgba(255,255,255,0.08)', overflow: 'hidden'}}>
        <div
          style={{
            height: '100%',
            width: `${interpolate(g, [0, 1], [0, pct])}%`,
            borderRadius: 23,
            background: `linear-gradient(90deg, ${color}, ${color}AA)`,
          }}
        />
      </div>
    </div>
  );
};

const SceneSeo: React.FC = () => {
  return (
    <AbsoluteFill>
      <Bg tint={COLORS.blue} />
      <Center>
        <div style={{position: 'absolute', top: 200}}>
          <Kicker color={COLORS.blue}>The long game</Kicker>
          <div style={{color: COLORS.white, fontSize: 58, fontWeight: 900, lineHeight: 1.1}}>
            LSAs win today.<br />
            <span style={{color: COLORS.blue}}>SEO</span> compounds forever.
          </div>
        </div>
        <div style={{marginTop: 300}}>
          <Bar delay={30} label="Local Service Ads — fast top placement" pct={92} color={COLORS.green} />
          <Bar delay={48} label="SEO — durable, free organic traffic" pct={78} color={COLORS.blue} />
          <Bar delay={66} label="Both together — total local dominance" pct={100} color={COLORS.yellow} />
        </div>
      </Center>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 6 — Takeaways                                                 */
/* ------------------------------------------------------------------ */

const Check: React.FC<{delay: number; text: string}> = ({delay, text}) => {
  const r = useReveal(delay);
  return (
    <div style={{...r, display: 'flex', alignItems: 'center', gap: 24, textAlign: 'left', width: 840}}>
      <div
        style={{
          width: 56,
          height: 56,
          minWidth: 56,
          borderRadius: '50%',
          background: COLORS.green,
          color: COLORS.white,
          fontSize: 34,
          fontWeight: 900,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        ✓
      </div>
      <div style={{color: COLORS.white, fontSize: 38, fontWeight: 700, lineHeight: 1.25}}>{text}</div>
    </div>
  );
};

const SceneTakeaways: React.FC = () => {
  return (
    <AbsoluteFill>
      <Bg tint={COLORS.green} />
      <Center>
        <div style={{position: 'absolute', top: 200}}>
          <Kicker color={COLORS.green}>Your playbook</Kicker>
          <div style={{color: COLORS.white, fontSize: 62, fontWeight: 900}}>3 moves to win</div>
        </div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 46, marginTop: 180}}>
          <Check delay={26} text="Claim & verify your Google Guaranteed profile" />
          <Check delay={46} text="Run LSAs to capture high-intent calls now" />
          <Check delay={66} text="Invest in local SEO for lasting organic reach" />
        </div>
      </Center>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* Scene 7 — CTA outro                                                 */
/* ------------------------------------------------------------------ */

const SceneOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame, fps, config: {damping: 12}});
  const t = useReveal(18);
  const b = useReveal(34);
  const tag = useReveal(50);
  return (
    <AbsoluteFill>
      <Bg tint={COLORS.blue} />
      <Dots />
      <Center>
        <div
          style={{
            transform: `scale(${pop})`,
            color: COLORS.white,
            fontSize: 92,
            fontWeight: 900,
            lineHeight: 1.05,
          }}
        >
          Get found
        </div>
        <div style={{...t, color: COLORS.green, fontSize: 92, fontWeight: 900, lineHeight: 1.05}}>
          locally.
        </div>
        <div style={{...b, color: COLORS.mute, fontSize: 34, marginTop: 40, fontWeight: 600}}>
          Local Service Ads + SEO, working together.
        </div>
        <div
          style={{
            ...tag,
            marginTop: 64,
            padding: '20px 44px',
            borderRadius: 40,
            border: `2px solid ${COLORS.blue}`,
            color: COLORS.white,
            fontSize: 34,
            fontWeight: 800,
          }}
        >
          Momentum Digital · Mac Frederick
        </div>
      </Center>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* Master timeline                                                     */
/* ------------------------------------------------------------------ */

export const Highlight: React.FC = () => {
  return (
    <AbsoluteFill style={{background: COLORS.ink}}>
      <Sequence durationInFrames={165}>
        <SceneIntro />
      </Sequence>
      <Sequence from={165} durationInFrames={255}>
        <SceneHook />
      </Sequence>
      <Sequence from={420} durationInFrames={300}>
        <SceneSerp />
      </Sequence>
      <Sequence from={720} durationInFrames={300}>
        <SceneValue />
      </Sequence>
      <Sequence from={1020} durationInFrames={300}>
        <SceneSeo />
      </Sequence>
      <Sequence from={1320} durationInFrames={300}>
        <SceneTakeaways />
      </Sequence>
      <Sequence from={1620} durationInFrames={180}>
        <SceneOutro />
      </Sequence>
    </AbsoluteFill>
  );
};
