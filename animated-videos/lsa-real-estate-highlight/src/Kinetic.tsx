import React from 'react';
import {useCurrentFrame, useVideoConfig, spring, interpolate} from 'remotion';
import {evolvePath} from '@remotion/paths';
import {C, POPPINS} from './theme';

/**
 * Kinetic headline: each word flies up, un-blurs and overshoots in scale,
 * staggered. Words wrapped in {curly} render in `accent` color.
 */
export const KineticHeadline: React.FC<{
  text: string;
  size: number;
  delay?: number;
  stagger?: number;
  accent?: string;
  color?: string;
}> = ({text, size, delay = 0, stagger = 4, accent = C.blue, color = C.white}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const words = text.split(' ');
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '0 18px',
        fontFamily: POPPINS,
        fontWeight: 900,
        fontSize: size,
        lineHeight: 1.04,
        letterSpacing: -1,
      }}
    >
      {words.map((w, i) => {
        const isAccent = /[{}]/.test(w);
        const clean = w.replace(/[{}]/g, '');
        const s = spring({
          frame: frame - delay - i * stagger,
          fps,
          config: {damping: 14, mass: 0.7},
        });
        const blur = interpolate(s, [0, 1], [14, 0]);
        const y = interpolate(s, [0, 1], [60, 0]);
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              transform: `translateY(${y}px) scale(${s})`,
              filter: `blur(${blur}px)`,
              opacity: interpolate(s, [0, 0.4], [0, 1], {extrapolateRight: 'clamp'}),
              color: isAccent ? accent : color,
            }}
          >
            {clean}
          </span>
        );
      })}
    </div>
  );
};

/** Hand-drawn-style underline that strokes on. */
export const DrawUnderline: React.FC<{
  delay: number;
  width: number;
  color: string;
}> = ({delay, width, color}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const d = `M 4 14 Q ${width / 2} -6 ${width - 4} 12`;
  const len = width * 1.15;
  const prog = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: 22});
  const {strokeDasharray, strokeDashoffset} = evolvePath(prog, d);
  return (
    <svg width={width} height={26} style={{overflow: 'visible'}}>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={7}
        strokeLinecap="round"
        strokeDasharray={strokeDasharray || len}
        strokeDashoffset={strokeDashoffset || 0}
      />
    </svg>
  );
};

/** Count-up number with a settle. */
export const CountUp: React.FC<{
  to: number;
  delay?: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
}> = ({to, delay = 0, duration = 36, prefix = '', suffix = ''}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 200}, durationInFrames: duration});
  const v = Math.round(interpolate(s, [0, 1], [0, to]));
  return (
    <span>
      {prefix}
      {v}
      {suffix}
    </span>
  );
};

/** Glowing check badge that pops + draws its tick. */
export const CheckBadge: React.FC<{delay: number; size?: number; color?: string}> = ({
  delay,
  size = 56,
  color = C.green,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: frame - delay, fps, config: {damping: 11, mass: 0.6}});
  const tick = `M ${size * 0.28} ${size * 0.52} L ${size * 0.44} ${size * 0.68} L ${size * 0.74} ${size * 0.34}`;
  const draw = spring({frame: frame - delay - 4, fps, config: {damping: 200}, durationInFrames: 14});
  const {strokeDasharray, strokeDashoffset} = evolvePath(draw, tick);
  return (
    <div
      style={{
        width: size,
        height: size,
        minWidth: size,
        borderRadius: '50%',
        background: color,
        transform: `scale(${pop})`,
        boxShadow: `0 0 ${size / 2}px ${color}99`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <svg width={size} height={size}>
        <path
          d={tick}
          fill="none"
          stroke={C.white}
          strokeWidth={size * 0.1}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
        />
      </svg>
    </div>
  );
};
