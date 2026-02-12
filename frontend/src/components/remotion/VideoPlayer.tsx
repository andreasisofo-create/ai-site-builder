"use client";

import { Player } from "@remotion/player";
import {
  HeroVideoComposition,
  AdsVideoComposition,
  HERO_VIDEO_CONFIG,
  ADS_VIDEO_CONFIG,
} from "./DemoVideo";
import {
  FeaturesVideoComposition,
  FEATURES_VIDEO_CONFIG,
} from "./FeaturesVideo";
import {
  ProcessVideoComposition,
  PROCESS_VIDEO_CONFIG,
} from "./ProcessVideo";

interface VideoPlayerProps {
  className?: string;
  autoPlay?: boolean;
  loop?: boolean;
}

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

export function FeaturesVideoPlayer({
  className = "",
  autoPlay = true,
  loop = true,
}: VideoPlayerProps) {
  return (
    <div className={`rounded-2xl overflow-hidden border border-white/10 shadow-2xl ${className}`}>
      <Player
        component={FeaturesVideoComposition}
        compositionWidth={FEATURES_VIDEO_CONFIG.width}
        compositionHeight={FEATURES_VIDEO_CONFIG.height}
        durationInFrames={FEATURES_VIDEO_CONFIG.durationInFrames}
        fps={FEATURES_VIDEO_CONFIG.fps}
        autoPlay={autoPlay}
        loop={loop}
        style={{ width: "100%", height: "auto" }}
        controls={false}
      />
    </div>
  );
}

export function ProcessVideoPlayer({
  className = "",
  autoPlay = true,
  loop = true,
}: VideoPlayerProps) {
  return (
    <div className={`rounded-2xl overflow-hidden border border-white/10 shadow-2xl ${className}`}>
      <Player
        component={ProcessVideoComposition}
        compositionWidth={PROCESS_VIDEO_CONFIG.width}
        compositionHeight={PROCESS_VIDEO_CONFIG.height}
        durationInFrames={PROCESS_VIDEO_CONFIG.durationInFrames}
        fps={PROCESS_VIDEO_CONFIG.fps}
        autoPlay={autoPlay}
        loop={loop}
        style={{ width: "100%", height: "auto" }}
        controls={false}
      />
    </div>
  );
}
