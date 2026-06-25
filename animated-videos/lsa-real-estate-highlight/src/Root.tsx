import {Composition} from 'remotion';
import {Highlight} from './Highlight';

const FPS = 30;
const DURATION_IN_FRAMES = 1800; // 60 seconds

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Highlight"
      component={Highlight}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={1080}
      height={1920}
    />
  );
};
