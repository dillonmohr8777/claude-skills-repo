import React, {useMemo, useState, useEffect} from 'react';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {useCurrentFrame, delayRender, continueRender, staticFile} from 'remotion';
import {noise2D, noise3D} from '@remotion/noise';
import {C} from '../theme';

/* -------------------------------------------------------------------------- */
/* Lighting rig — warm key + cool rim + soft fill                              */
/* -------------------------------------------------------------------------- */
export const Rig: React.FC<{tint?: string}> = ({tint = C.blue}) => (
  <>
    <ambientLight intensity={0.55} />
    <pointLight position={[6, 8, 8]} intensity={420} color="#ffffff" />
    <pointLight position={[-8, -4, 4]} intensity={260} color={tint} />
    <pointLight position={[0, 6, -6]} intensity={300} color={C.green} />
    <directionalLight position={[0, 10, 5]} intensity={1.1} />
  </>
);

/* -------------------------------------------------------------------------- */
/* Camera rig — gentle dolly + parallax driven by Remotion frame               */
/* -------------------------------------------------------------------------- */
export const CameraRig: React.FC<{z?: number; sway?: number}> = ({z = 7, sway = 0.6}) => {
  const frame = useCurrentFrame();
  const {camera} = useThree();
  const x = noise2D(11, frame / 120, 0) * sway;
  const y = noise2D(22, 0, frame / 120) * sway * 0.6;
  camera.position.set(x, y, z);
  camera.lookAt(0, 0, 0);
  return null;
};

/* -------------------------------------------------------------------------- */
/* Deterministic particle field (no Math.random → no cross-tab flicker)        */
/* -------------------------------------------------------------------------- */
export const Particles: React.FC<{count?: number; color?: string}> = ({
  count = 220,
  color = C.blueLite,
}) => {
  const frame = useCurrentFrame();
  const {positions, base} = useMemo(() => {
    const arr = new Float32Array(count * 3);
    const b: number[][] = [];
    const golden = Math.PI * (3 - Math.sqrt(5));
    for (let i = 0; i < count; i++) {
      const t = i / count;
      const radius = 6 + (i % 7) * 1.4;
      const a = i * golden;
      const x = Math.cos(a) * radius * (0.3 + t);
      const y = (t - 0.5) * 18;
      const z = Math.sin(a) * radius * (0.3 + t) - 4;
      b.push([x, y, z]);
      arr[i * 3] = x;
      arr[i * 3 + 1] = y;
      arr[i * 3 + 2] = z;
    }
    return {positions: arr, base: b};
  }, [count]);

  // drift
  const geo = useMemo(() => new THREE.BufferGeometry(), []);
  useMemo(() => {
    const p = positions.slice();
    for (let i = 0; i < base.length; i++) {
      p[i * 3] = base[i][0] + noise3D(i, frame / 90, 0, 0) * 0.8;
      p[i * 3 + 1] = base[i][1] + noise3D(i + 7, 0, frame / 90, 0) * 0.8;
      p[i * 3 + 2] = base[i][2];
    }
    geo.setAttribute('position', new THREE.BufferAttribute(p, 3));
  }, [frame, base, positions, geo]);

  return (
    <points geometry={geo}>
      <pointsMaterial size={0.08} color={color} transparent opacity={0.8} sizeAttenuation />
    </points>
  );
};

/* -------------------------------------------------------------------------- */
/* Floating wireframe shapes for depth                                         */
/* -------------------------------------------------------------------------- */
export const FloatingShapes: React.FC<{tint?: string}> = ({tint = C.blue}) => {
  const frame = useCurrentFrame();
  const shapes = [
    {pos: [-4.5, 2.6, -3], type: 'ico', s: 0.9, c: tint},
    {pos: [4.6, -2.2, -2], type: 'torus', s: 0.8, c: C.green},
    {pos: [3.4, 3.2, -4], type: 'octa', s: 0.7, c: C.yellow},
    {pos: [-3.8, -3.0, -3], type: 'torus', s: 0.5, c: C.blueLite},
  ] as const;
  return (
    <>
      {shapes.map((s, i) => (
        <mesh
          key={i}
          position={s.pos as [number, number, number]}
          rotation={[frame / 70 + i, frame / 90 + i, 0]}
          scale={s.s}
        >
          {s.type === 'ico' && <icosahedronGeometry args={[1, 0]} />}
          {s.type === 'octa' && <octahedronGeometry args={[1, 0]} />}
          {s.type === 'torus' && <torusGeometry args={[0.8, 0.26, 16, 40]} />}
          <meshStandardMaterial
            color={s.c}
            wireframe
            emissive={s.c}
            emissiveIntensity={0.5}
            transparent
            opacity={0.45}
          />
        </mesh>
      ))}
    </>
  );
};

/* -------------------------------------------------------------------------- */
/* Logo texture loader — blocks the frame until the PNG is decoded             */
/* -------------------------------------------------------------------------- */
export const useLogoTexture = (): THREE.Texture | null => {
  const [tex, setTex] = useState<THREE.Texture | null>(null);
  const [handle] = useState(() => delayRender('load-logo'));
  useEffect(() => {
    new THREE.TextureLoader().load(
      staticFile('logo.png'),
      (t) => {
        t.colorSpace = THREE.SRGBColorSpace;
        t.anisotropy = 8;
        setTex(t);
        continueRender(handle);
      },
      undefined,
      () => continueRender(handle)
    );
  }, [handle]);
  return tex;
};

/* -------------------------------------------------------------------------- */
/* CanvasTexture label — draws crisp text onto a 3D surface                    */
/* -------------------------------------------------------------------------- */
export const makeLabelTexture = (
  lines: {text: string; color: string; font: string}[],
  w = 900,
  h = 256,
  bg = 'rgba(255,255,255,0.96)',
  align: CanvasTextAlign = 'left'
): THREE.CanvasTexture => {
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  // rounded card bg
  const r = 36;
  ctx.fillStyle = bg;
  ctx.beginPath();
  ctx.moveTo(r, 0);
  ctx.arcTo(w, 0, w, h, r);
  ctx.arcTo(w, h, 0, h, r);
  ctx.arcTo(0, h, 0, 0, r);
  ctx.arcTo(0, 0, w, 0, r);
  ctx.closePath();
  ctx.fill();
  ctx.textBaseline = 'middle';
  ctx.textAlign = align;
  const x = align === 'left' ? 48 : w / 2;
  const startY = h / 2 - ((lines.length - 1) * 56) / 2;
  lines.forEach((ln, i) => {
    ctx.font = ln.font;
    ctx.fillStyle = ln.color;
    ctx.fillText(ln.text, x, startY + i * 64);
  });
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
};
