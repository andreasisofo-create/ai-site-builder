import "./index.css";
import { Composition } from "remotion";
import {
  HeroVideoComposition,
  AdsVideoComposition,
  HERO_VIDEO_CONFIG,
  ADS_VIDEO_CONFIG,
} from "./DemoVideo";
import {
  ProcessVideoComposition,
  PROCESS_VIDEO_CONFIG,
} from "./ProcessVideo";
import {
  FeaturesVideoComposition,
  FEATURES_VIDEO_CONFIG,
} from "./FeaturesVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HeroVideo"
        component={HeroVideoComposition}
        durationInFrames={HERO_VIDEO_CONFIG.durationInFrames}
        fps={HERO_VIDEO_CONFIG.fps}
        width={HERO_VIDEO_CONFIG.width}
        height={HERO_VIDEO_CONFIG.height}
      />
      <Composition
        id="AdsVideo"
        component={AdsVideoComposition}
        durationInFrames={ADS_VIDEO_CONFIG.durationInFrames}
        fps={ADS_VIDEO_CONFIG.fps}
        width={ADS_VIDEO_CONFIG.width}
        height={ADS_VIDEO_CONFIG.height}
      />
      <Composition
        id="ProcessVideo"
        component={ProcessVideoComposition}
        durationInFrames={PROCESS_VIDEO_CONFIG.durationInFrames}
        fps={PROCESS_VIDEO_CONFIG.fps}
        width={PROCESS_VIDEO_CONFIG.width}
        height={PROCESS_VIDEO_CONFIG.height}
      />
      <Composition
        id="FeaturesVideo"
        component={FeaturesVideoComposition}
        durationInFrames={FEATURES_VIDEO_CONFIG.durationInFrames}
        fps={FEATURES_VIDEO_CONFIG.fps}
        width={FEATURES_VIDEO_CONFIG.width}
        height={FEATURES_VIDEO_CONFIG.height}
      />
    </>
  );
};
