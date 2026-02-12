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
import {
  StatsVideoComposition,
  STATS_VIDEO_CONFIG,
} from "./StatsVideo";
import {
  TestimonialsVideoComposition,
  TESTIMONIALS_VIDEO_CONFIG,
} from "./TestimonialsVideo";
import {
  PricingVideoComposition,
  PRICING_VIDEO_CONFIG,
} from "./PricingVideo";
import {
  TimelineVideoComposition,
  TIMELINE_VIDEO_CONFIG,
} from "./TimelineVideo";

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
      <Composition
        id="StatsVideo"
        component={StatsVideoComposition}
        durationInFrames={STATS_VIDEO_CONFIG.durationInFrames}
        fps={STATS_VIDEO_CONFIG.fps}
        width={STATS_VIDEO_CONFIG.width}
        height={STATS_VIDEO_CONFIG.height}
      />
      <Composition
        id="TestimonialsVideo"
        component={TestimonialsVideoComposition}
        durationInFrames={TESTIMONIALS_VIDEO_CONFIG.durationInFrames}
        fps={TESTIMONIALS_VIDEO_CONFIG.fps}
        width={TESTIMONIALS_VIDEO_CONFIG.width}
        height={TESTIMONIALS_VIDEO_CONFIG.height}
      />
      <Composition
        id="PricingVideo"
        component={PricingVideoComposition}
        durationInFrames={PRICING_VIDEO_CONFIG.durationInFrames}
        fps={PRICING_VIDEO_CONFIG.fps}
        width={PRICING_VIDEO_CONFIG.width}
        height={PRICING_VIDEO_CONFIG.height}
      />
      <Composition
        id="TimelineVideo"
        component={TimelineVideoComposition}
        durationInFrames={TIMELINE_VIDEO_CONFIG.durationInFrames}
        fps={TIMELINE_VIDEO_CONFIG.fps}
        width={TIMELINE_VIDEO_CONFIG.width}
        height={TIMELINE_VIDEO_CONFIG.height}
      />
    </>
  );
};
