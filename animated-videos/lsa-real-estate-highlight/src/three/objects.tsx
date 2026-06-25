import React, {useMemo} from 'react';
import * as THREE from 'three';
import {useCurrentFrame, useVideoConfig, spring, interpolate} from 'remotion';
import {noise2D} from '@remotion/noise';
import {C, POPPINS} from '../theme';
import {useLogoTexture, makeLabelTexture} from './world';

const ease = (frame: number, fps: number, delay: number, dur = 30, damping = 14) =>
  spring({frame: frame - delay, fps, config: {damping, mass: 0.8}, durationInFrames: dur});

/* --------------------------- Logo medallion ------------------------------- */
export const Medallion: React.FC<{delay?: number; scale?: number}> = ({delay = 0, scale = 1}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const logo = useLogoTexture();

  const intro = ease(frame, fps, delay, 40, 11);
  const pop = interpolate(intro, [0, 1], [0, 1]);
  // flip in: 2.5 turns settling to face camera, then gentle wobble
  const flip = interpolate(intro, [0, 1], [Math.PI * 2.5, 0]);
  const wobble = noise2D(3, (frame - delay) / 80, 0) * 0.18 * intro;

  return (
    <group scale={pop * scale} rotation={[wobble * 0.5, flip + wobble, 0]}>
      {/* coin body */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[2, 2, 0.32, 72]} />
        <meshStandardMaterial color={C.ink2} metalness={0.95} roughness={0.28} />
      </mesh>
      {/* polished rim */}
      <mesh position={[0, 0, 0]}>
        <torusGeometry args={[2, 0.1, 24, 80]} />
        <meshStandardMaterial color={C.blueLite} metalness={1} roughness={0.18} emissive={C.blue} emissiveIntensity={0.5} />
      </mesh>
      {/* glow ring */}
      <mesh position={[0, 0, -0.05]}>
        <torusGeometry args={[2.18, 0.04, 16, 80]} />
        <meshBasicMaterial color={C.blueLite} transparent opacity={0.6 * intro} />
      </mesh>
      {/* logo art on front face — circle crops the square's white corners */}
      {logo && (
        <mesh position={[0, 0, 0.17]}>
          <circleGeometry args={[1.92, 64]} />
          <meshStandardMaterial map={logo} metalness={0.15} roughness={0.55} />
        </mesh>
      )}
      {/* logo art on back face */}
      {logo && (
        <mesh position={[0, 0, -0.17]} rotation={[0, Math.PI, 0]}>
          <circleGeometry args={[1.92, 64]} />
          <meshStandardMaterial map={logo} metalness={0.15} roughness={0.55} />
        </mesh>
      )}
    </group>
  );
};

/* --------------------------- 3D bar chart --------------------------------- */
export const Bars3D: React.FC<{delay?: number}> = ({delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const bars = [
    {h: 3.4, x: -2.6, c: C.green},
    {h: 2.8, x: 0, c: C.blueLite},
    {h: 3.8, x: 2.6, c: C.yellow},
  ];
  return (
    <group position={[0, -2, 0]} scale={0.72} rotation={[0.12, -0.45 + noise2D(9, frame / 140, 0) * 0.12, 0]}>
      {/* floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
        <planeGeometry args={[14, 14]} />
        <meshStandardMaterial color={C.ink} metalness={0.6} roughness={0.4} />
      </mesh>
      {bars.map((b, i) => {
        const g = ease(frame, fps, delay + i * 8, 40, 200);
        const h = b.h * g;
        return (
          <group key={i} position={[b.x, 0, 0]}>
            <mesh position={[0, h / 2, 0]} scale={[1, h <= 0 ? 0.001 : 1, 1]}>
              <boxGeometry args={[1.5, h <= 0 ? 0.001 : b.h, 1.5]} />
              <meshStandardMaterial
                color={b.c}
                metalness={0.55}
                roughness={0.25}
                emissive={b.c}
                emissiveIntensity={0.35}
              />
            </mesh>
            {/* glowing cap */}
            <mesh position={[0, h + 0.04, 0]}>
              <boxGeometry args={[1.6, 0.08, 1.6]} />
              <meshBasicMaterial color={b.c} transparent opacity={g} />
            </mesh>
          </group>
        );
      })}
    </group>
  );
};

/* ------------------- Stacked SERP cards (text on 3D faces) ---------------- */
const CardFace: React.FC<{
  y: number;
  delay: number;
  highlight?: boolean;
  lines: {text: string; color: string; font: string}[];
}> = ({y, delay, highlight, lines}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const g = ease(frame, fps, delay, 26, 16);
  const x = interpolate(g, [0, 1], [-9, 0]);
  const tex = useMemo(
    () => makeLabelTexture(lines, 960, highlight ? 300 : 220, highlight ? '#ffffff' : 'rgba(20,28,46,0.92)'),
    [lines, highlight]
  );
  const depth = highlight ? 0.42 : 0.26;
  const w = 4.7;
  const h = highlight ? 1.5 : 1.12;
  return (
    <group position={[x, y, highlight ? 0.5 : 0]} rotation={[0, interpolate(g, [0, 1], [-0.6, 0]), 0]}>
      <mesh>
        <boxGeometry args={[w, h, depth]} />
        <meshStandardMaterial
          color={highlight ? '#ffffff' : C.ink2}
          metalness={0.5}
          roughness={highlight ? 0.25 : 0.4}
          emissive={highlight ? C.green : '#000000'}
          emissiveIntensity={highlight ? 0.25 : 0}
        />
      </mesh>
      <mesh position={[0, 0, depth / 2 + 0.01]}>
        <planeGeometry args={[w * 0.97, h * 0.86]} />
        <meshBasicMaterial map={tex} transparent />
      </mesh>
    </group>
  );
};

export const SerpStack3D: React.FC<{delay?: number}> = ({delay = 0}) => {
  const frame = useCurrentFrame();
  return (
    <group rotation={[0.16, 0.3 + noise2D(4, frame / 160, 0) * 0.1, -0.04]} position={[0, -1.0, 0]} scale={0.92}>
      <CardFace
        y={1.6}
        delay={delay}
        highlight
        lines={[
          {text: 'Your Local Service Ad', color: '#0B1220', font: `800 60px ${POPPINS}`},
          {text: 'Google Guaranteed · Top spot', color: C.green, font: `700 38px ${POPPINS}`},
        ]}
      />
      <CardFace y={-0.1} delay={delay + 12} lines={[{text: 'Standard Google Ad', color: '#cdd6e6', font: `600 48px ${POPPINS}`}]} />
      <CardFace y={-1.5} delay={delay + 20} lines={[{text: 'Organic SEO result', color: '#cdd6e6', font: `600 48px ${POPPINS}`}]} />
      <CardFace y={-2.9} delay={delay + 28} lines={[{text: 'Organic SEO result', color: '#cdd6e6', font: `600 48px ${POPPINS}`}]} />
    </group>
  );
};

/* ----------------------------- Trust badge -------------------------------- */
export const Badge3D: React.FC<{delay?: number}> = ({delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const intro = ease(frame, fps, delay, 36, 11);
  const spinY = interpolate(intro, [0, 1], [Math.PI * 2, 0]) + noise2D(8, (frame - delay) / 90, 0) * 0.25;
  const tex = useMemo(
    () => makeLabelTexture([{text: '✓', color: '#ffffff', font: `900 200px ${POPPINS}`}], 320, 320, 'rgba(0,0,0,0)', 'center'),
    []
  );
  return (
    <group scale={intro} rotation={[0, spinY, 0]}>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[2, 2, 0.36, 72]} />
        <meshStandardMaterial color={C.green} metalness={0.85} roughness={0.25} emissive={C.green} emissiveIntensity={0.25} />
      </mesh>
      <mesh>
        <torusGeometry args={[2, 0.12, 24, 80]} />
        <meshStandardMaterial color={C.greenLite} metalness={1} roughness={0.15} emissive={C.green} emissiveIntensity={0.6} />
      </mesh>
      <mesh position={[0, 0, 0.19]}>
        <planeGeometry args={[2.6, 2.6]} />
        <meshBasicMaterial map={tex} transparent />
      </mesh>
    </group>
  );
};
