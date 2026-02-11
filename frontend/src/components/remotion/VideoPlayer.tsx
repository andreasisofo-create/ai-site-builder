"use client";

import { Player } from "@remotion/player";
import {
  HeroVideoComposition,
  AdsVideoComposition,
  HERO_VIDEO_CONFIG,
  ADS_VIDEO_CONFIG,
} from "./DemoVideo";

interface VideoPlayerProps {
  className?: string;
  autoPlay?: boolean;
  loop?: boolean;
}

/**
 * Remotion Player for the Hero video composition.
 * Shows the AI site builder workflow: describe -> generate -> result -> publish.
 */
export default function VideoPlayer({
  className = "",
  autoPlay = true,
  loop = true,
}: VideoPlayerProps) {
  return (
    <div className={`rounded-2xl overflow-hidden border border-white/10 shadow-2xl ${className}`}>
      <Player
        component={HeroVideoComposition}
        compositionWidth={HERO_VIDEO_CONFIG.width}
        compositionHeight={HERO_VIDEO_CONFIG.height}
        durationInFrames={HERO_VIDEO_CONFIG.durationInFrames}
        fps={HERO_VIDEO_CONFIG.fps}
        autoPlay={autoPlay}
        loop={loop}
        style={{ width: "100%", height: "auto" }}
        controls={false}
      />
    </div>
  );
}

/**
 * Remotion Player for the Ads video composition.
 * Shows the ads management dashboard with metrics and ROI.
 */
export function AdsVideoPlayer({
  className = "",
  autoPlay = true,
  loop = true,
}: VideoPlayerProps) {
  return (
    <div className={`rounded-2xl overflow-hidden border border-white/10 shadow-2xl ${className}`}>
      <Player
        component={AdsVideoComposition}
        compositionWidth={ADS_VIDEO_CONFIG.width}
        compositionHeight={ADS_VIDEO_CONFIG.height}
        durationInFrames={ADS_VIDEO_CONFIG.durationInFrames}
        fps={ADS_VIDEO_CONFIG.fps}
        autoPlay={autoPlay}
        loop={loop}
        style={{ width: "100%", height: "auto" }}
        controls={false}
      />
    </div>
  );
}
