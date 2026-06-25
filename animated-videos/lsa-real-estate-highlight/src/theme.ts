import {loadFont as loadPoppins} from '@remotion/google-fonts/Poppins';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';

// Real display + body typography (the single biggest upgrade over Arial).
export const {fontFamily: POPPINS} = loadPoppins('normal', {
  weights: ['600', '700', '800', '900'],
});
export const {fontFamily: INTER} = loadInter('normal', {
  weights: ['400', '500', '600', '700'],
});

export const C = {
  blue: '#4285F4',
  blueLite: '#8AB4F8',
  red: '#EA4335',
  yellow: '#FBBC05',
  green: '#34A853',
  greenLite: '#5BD98A',
  ink: '#05080F',
  ink2: '#0A1020',
  white: '#FFFFFF',
  mute: 'rgba(255,255,255,0.60)',
  line: 'rgba(255,255,255,0.10)',
};

export const FPS = 30;

// Fake frosted-glass card style — reads as glass without a live
// backdrop-filter (which is brutally slow to software-render).
export const glass = (accent: string): React.CSSProperties => ({
  background:
    'linear-gradient(160deg, rgba(255,255,255,0.10), rgba(255,255,255,0.03))',
  border: `1px solid ${accent}44`,
  borderRadius: 34,
  boxShadow: `0 30px 80px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.14)`,
});
