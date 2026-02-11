"use client";

import { Player } from "@remotion/player";
import { DemoVideoComposition, DEMO_VIDEO_CONFIG } from "./DemoVideo";

interface VideoPlayerProps {
  className?: string;
  autoPlay?: boolean;
  loop?: boolean;
}

/**
 * Remotion Player wrapper for the E-quipe demo video.
 * Renders the animated composition inline on the landing page.
 */
export default function VideoPlayer({
  className = "",
  autoPlay = true,
  loop = true,
}: VideoPlayerProps) {
  return (
    <div className={`rounded-2xl overflow-hidden border border-white/10 shadow-2xl ${className}`}>
      <Player
        component={DemoVideoComposition}
        compositionWidth={DEMO_VIDEO_CONFIG.width}
        compositionHeight={DEMO_VIDEO_CONFIG.height}
        durationInFrames={DEMO_VIDEO_CONFIG.durationInFrames}
        fps={DEMO_VIDEO_CONFIG.fps}
        autoPlay={autoPlay}
        loop={loop}
        style={{ width: "100%", height: "auto" }}
        controls={false}
      />
    </div>
  );
}
