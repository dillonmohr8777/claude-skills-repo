import {Composition} from 'remotion';
import {Highlight3D} from './Highlight3D';
import {Highlight} from './Highlight';

const FPS = 30;
const DURATION = 1800; // 60 seconds

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Main deliverable — fully 3D (WebGL) version */}
      <Composition
        id="Highlight"
        component={Highlight3D}
        durationInFrames={DURATION}
        fps={FPS}
        width={1080}
        height={1920}
      />
      {/* Previous flat/motion-graphics version, kept for reference */}
      <Composition
        id="Highlight2D"
        component={Highlight}
        durationInFrames={DURATION}
        fps={FPS}
        width={1080}
        height={1920}
      />
    </>
  );
};
