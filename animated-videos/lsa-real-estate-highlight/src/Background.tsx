import React from 'react';
import {AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {noise2D, noise3D} from '@remotion/noise';
import {C} from './theme';

/**
 * Animated mesh-gradient background: several color blobs drift along
 * Perlin-noise paths, so the motion is organic instead of looping.
 */
export const MeshBg: React.FC<{tint?: string}> = ({tint = C.blue}) => {
  const frame = useCurrentFrame();
  const t = frame / 90;

  // Soft radial-gradient "blobs" stacked in a single paint. Radial
  // gradients are essentially free, unlike a blur() filter, so we get
  // the same diffuse mesh look at a fraction of the render cost.
  const blobs = [
    {seed: 1, color: tint, r: 46, op: 0.5},
    {seed: 7, color: C.green, r: 40, op: 0.34},
    {seed: 13, color: C.blue, r: 38, op: 0.3},
    {seed: 21, color: C.yellow, r: 30, op: 0.18},
  ];

  const layers = blobs
    .map((b) => {
      const x = interpolate(noise2D(b.seed, t, 0), [-1, 1], [-10, 110]);
      const y = interpolate(noise2D(b.seed + 99, 0, t), [-1, 1], [-5, 105]);
      const hex = Math.round(b.op * 255).toString(16).padStart(2, '0');
      return `radial-gradient(${b.r}% ${b.r}% at ${x}% ${y}%, ${b.color}${hex}, transparent 70%)`;
    })
    .join(', ');

  return (
    <AbsoluteFill style={{background: C.ink}}>
      <AbsoluteFill style={{background: layers}} />
      <AbsoluteFill
        style={{background: `radial-gradient(120% 90% at 50% -10%, ${C.ink2}99, transparent 60%)`}}
      />
      <Vignette />
    </AbsoluteFill>
  );
};

const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        'radial-gradient(75% 75% at 50% 45%, transparent 55%, rgba(0,0,0,0.55) 100%)',
    }}
  />
);

/** Floating decorative dots that drift on a noise field. */
export const FloatingDots: React.FC<{count?: number}> = ({count = 16}) => {
  const frame = useCurrentFrame();
  const palette = [C.blueLite, C.green, C.yellow, C.red];
  return (
    <AbsoluteFill style={{opacity: 0.5}}>
      {Array.from({length: count}).map((_, i) => {
        const baseX = (i * 137.5) % 100;
        const baseY = (i * 263.1) % 100;
        const dx = noise3D(i, frame / 120, 0, 0) * 6;
        const dy = noise3D(i + 50, 0, frame / 120, 0) * 6;
        const tw = interpolate(
          noise2D(i + 5, frame / 40, 0),
          [-1, 1],
          [0.25, 1]
        );
        const size = 6 + (i % 4) * 4;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${baseX + dx}%`,
              top: `${baseY + dy}%`,
              width: size,
              height: size,
              borderRadius: '50%',
              background: palette[i % palette.length],
              opacity: tw,
              boxShadow: `0 0 ${size * 2}px ${palette[i % palette.length]}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
