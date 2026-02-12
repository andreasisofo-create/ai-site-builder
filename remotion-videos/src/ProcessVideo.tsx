import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();
const FONT = `${fontFamily}, -apple-system, BlinkMacSystemFont, sans-serif`;

/* ------------------------------------------------------------------ */
/*  COLORS                                                             */
/* ------------------------------------------------------------------ */

const SCENE_COLORS = {
  scene1: "#1a1aff",
  scene2: "#7c00ff",
  scene3: "#00c853",
  scene4: "#ff6d00",
};

/* ------------------------------------------------------------------ */
/*  COLOR WIPE TRANSITION                                              */
/* ------------------------------------------------------------------ */

const ColorWipe = ({
  color,
  progress,
  direction,
}: {
  color: string;
  progress: number;
  direction: "left" | "right";
}) => {
  const xPercent =
    direction === "right"
      ? interpolate(progress, [0, 1], [-100, 0], { extrapolateRight: "clamp" })
      : interpolate(progress, [0, 1], [100, 0], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        background: color,
        transform: `translateX(${xPercent}%)`,
        zIndex: 100,
      }}
    />
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 1: SCEGLI IL TEMPLATE                                        */
/* ------------------------------------------------------------------ */

const Scene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Watermark "01"
  const watermarkOpacity = interpolate(frame, [0, 15], [0, 0.1], {
    extrapolateRight: "clamp",
  });

  // Title animation
  const titleSpring = spring({ frame: frame - 5, fps, config: { damping: 14, stiffness: 80 } });
  const titleY = interpolate(titleSpring, [0, 1], [80, 0]);
  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);

  // Three template cards sliding in from right
  const cards = [
    { color: "#ff4081", delay: 15 },
    { color: "#00e5ff", delay: 22 },
    { color: "#ffea00", delay: 29 },
  ];

  // Floating geometric shapes
  const circleY = interpolate(frame, [0, 90], [0, -30], { extrapolateRight: "clamp" });
  const squareRotation = interpolate(frame, [0, 90], [0, 45], { extrapolateRight: "clamp" });

  // Exit wipe
  const wipeProgress = interpolate(frame, [78, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: SCENE_COLORS.scene1, fontFamily: FONT, overflow: "hidden" }}>
      {/* Watermark */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          fontSize: 300,
          fontWeight: 900,
          color: "#ffffff",
          opacity: watermarkOpacity,
          lineHeight: 1,
          userSelect: "none",
        }}
      >
        01
      </div>

      {/* Floating circle */}
      <div
        style={{
          position: "absolute",
          top: 150 + circleY,
          right: 120,
          width: 80,
          height: 80,
          borderRadius: "50%",
          border: "4px solid rgba(255,255,255,0.2)",
        }}
      />

      {/* Floating square */}
      <div
        style={{
          position: "absolute",
          bottom: 180,
          left: 100,
          width: 60,
          height: 60,
          border: "4px solid rgba(255,255,255,0.15)",
          transform: `rotate(${squareRotation}deg)`,
        }}
      />

      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 200,
          left: 140,
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 600,
            color: "rgba(255,255,255,0.6)",
            letterSpacing: 6,
            marginBottom: 16,
          }}
        >
          STEP 01
        </div>
        <h1
          style={{
            fontSize: 86,
            fontWeight: 900,
            color: "#ffffff",
            lineHeight: 1.05,
            margin: 0,
          }}
        >
          SCEGLI IL
          <br />
          TEMPLATE
        </h1>
      </div>

      {/* Template cards */}
      <div
        style={{
          position: "absolute",
          bottom: 160,
          right: 120,
          display: "flex",
          gap: 24,
        }}
      >
        {cards.map((card, i) => {
          const cardSpring = spring({
            frame: frame - card.delay,
            fps,
            config: { damping: 13, stiffness: 90 },
          });
          const cardX = interpolate(cardSpring, [0, 1], [300, 0]);
          const cardOpacity = interpolate(cardSpring, [0, 1], [0, 1]);

          return (
            <div
              key={i}
              style={{
                width: 180,
                height: 240,
                borderRadius: 16,
                background: card.color,
                opacity: cardOpacity,
                transform: `translateX(${cardX}px)`,
                boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
                display: "flex",
                flexDirection: "column",
                padding: 16,
                justifyContent: "flex-end",
              }}
            >
              <div
                style={{
                  width: "80%",
                  height: 10,
                  borderRadius: 5,
                  background: "rgba(255,255,255,0.5)",
                  marginBottom: 8,
                }}
              />
              <div
                style={{
                  width: "55%",
                  height: 8,
                  borderRadius: 4,
                  background: "rgba(255,255,255,0.3)",
                }}
              />
            </div>
          );
        })}
      </div>

      {/* Exit color wipe to scene 2 */}
      {wipeProgress > 0 && (
        <ColorWipe color={SCENE_COLORS.scene2} progress={wipeProgress} direction="right" />
      )}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 2: DESCRIVI IL BUSINESS                                      */
/* ------------------------------------------------------------------ */

const Scene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Watermark "02"
  const watermarkOpacity = interpolate(frame, [0, 15], [0, 0.1], {
    extrapolateRight: "clamp",
  });

  // Title
  const titleSpring = spring({ frame: frame - 5, fps, config: { damping: 14, stiffness: 80 } });
  const titleY = interpolate(titleSpring, [0, 1], [80, 0]);
  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);

  // Form field rectangles
  const fields = [
    { width: 600, delay: 15 },
    { width: 500, delay: 22 },
    { width: 550, delay: 29 },
  ];

  // Geometric decorations
  const triangleRotation = interpolate(frame, [0, 90], [0, 60], { extrapolateRight: "clamp" });
  const circleScale = interpolate(frame, [0, 90], [0.8, 1.2], { extrapolateRight: "clamp" });

  // Exit wipe
  const wipeProgress = interpolate(frame, [78, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: SCENE_COLORS.scene2, fontFamily: FONT, overflow: "hidden" }}>
      {/* Watermark */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          fontSize: 300,
          fontWeight: 900,
          color: "#ffffff",
          opacity: watermarkOpacity,
          lineHeight: 1,
        }}
      >
        02
      </div>

      {/* Triangle decoration */}
      <div
        style={{
          position: "absolute",
          top: 120,
          right: 180,
          width: 0,
          height: 0,
          borderLeft: "40px solid transparent",
          borderRight: "40px solid transparent",
          borderBottom: "70px solid rgba(255,255,255,0.15)",
          transform: `rotate(${triangleRotation}deg)`,
        }}
      />

      {/* Circle decoration */}
      <div
        style={{
          position: "absolute",
          bottom: 140,
          left: 160,
          width: 70,
          height: 70,
          borderRadius: "50%",
          background: "rgba(255,255,255,0.1)",
          transform: `scale(${circleScale})`,
        }}
      />

      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 180,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 600,
            color: "rgba(255,255,255,0.6)",
            letterSpacing: 6,
            marginBottom: 16,
          }}
        >
          STEP 02
        </div>
        <h1
          style={{
            fontSize: 82,
            fontWeight: 900,
            color: "#ffffff",
            lineHeight: 1.05,
            margin: 0,
          }}
        >
          DESCRIVI IL
          <br />
          BUSINESS
        </h1>
      </div>

      {/* Form fields (simple white rectangles) */}
      <div
        style={{
          position: "absolute",
          bottom: 200,
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          flexDirection: "column",
          gap: 20,
          alignItems: "center",
        }}
      >
        {fields.map((field, i) => {
          const fieldSpring = spring({
            frame: frame - field.delay,
            fps,
            config: { damping: 13, stiffness: 90 },
          });
          const fieldX = interpolate(fieldSpring, [0, 1], [-200, 0]);
          const fieldOpacity = interpolate(fieldSpring, [0, 1], [0, 1]);

          return (
            <div
              key={i}
              style={{
                width: field.width,
                height: 56,
                borderRadius: 12,
                background: "rgba(255,255,255,0.15)",
                border: "2px solid rgba(255,255,255,0.3)",
                opacity: fieldOpacity,
                transform: `translateX(${fieldX}px)`,
              }}
            >
              {/* Simulated text inside field */}
              <div
                style={{
                  margin: "18px 20px",
                  width: `${40 + i * 10}%`,
                  height: 12,
                  borderRadius: 6,
                  background: "rgba(255,255,255,0.4)",
                }}
              />
            </div>
          );
        })}
      </div>

      {/* Exit color wipe to scene 3 */}
      {wipeProgress > 0 && (
        <ColorWipe color={SCENE_COLORS.scene3} progress={wipeProgress} direction="left" />
      )}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 3: L'AI GENERA                                               */
/* ------------------------------------------------------------------ */

const Scene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Watermark "03"
  const watermarkOpacity = interpolate(frame, [0, 15], [0, 0.1], {
    extrapolateRight: "clamp",
  });

  // Title
  const titleSpring = spring({ frame: frame - 5, fps, config: { damping: 14, stiffness: 80 } });
  const titleY = interpolate(titleSpring, [0, 1], [80, 0]);
  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);

  // Spinning circle / loading
  const spinAngle = interpolate(frame, [0, 90], [0, 720], { extrapolateRight: "clamp" });

  // Percentage counter 0 -> 100%
  const percentage = Math.min(
    100,
    Math.round(
      interpolate(frame, [10, 80], [0, 100], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    )
  );

  // Pulsing effect for the ring
  const pulseScale = interpolate(
    Math.sin(frame * 0.15),
    [-1, 1],
    [0.95, 1.05]
  );

  // Floating square decoration
  const squareY = interpolate(frame, [0, 90], [0, -25], { extrapolateRight: "clamp" });
  const squareRot = interpolate(frame, [0, 90], [0, 90], { extrapolateRight: "clamp" });

  // Exit wipe
  const wipeProgress = interpolate(frame, [78, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: SCENE_COLORS.scene3, fontFamily: FONT, overflow: "hidden" }}>
      {/* Watermark */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          fontSize: 300,
          fontWeight: 900,
          color: "#ffffff",
          opacity: watermarkOpacity,
          lineHeight: 1,
        }}
      >
        03
      </div>

      {/* Floating square */}
      <div
        style={{
          position: "absolute",
          top: 130 + squareY,
          left: 180,
          width: 50,
          height: 50,
          border: "4px solid rgba(255,255,255,0.2)",
          transform: `rotate(${squareRot}deg)`,
        }}
      />

      {/* Small circle decoration */}
      <div
        style={{
          position: "absolute",
          bottom: 160,
          right: 200,
          width: 40,
          height: 40,
          borderRadius: "50%",
          background: "rgba(255,255,255,0.1)",
        }}
      />

      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 160,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 600,
            color: "rgba(255,255,255,0.6)",
            letterSpacing: 6,
            marginBottom: 16,
          }}
        >
          STEP 03
        </div>
        <h1
          style={{
            fontSize: 82,
            fontWeight: 900,
            color: "#ffffff",
            lineHeight: 1.05,
            margin: 0,
          }}
        >
          L'AI GENERA
        </h1>
      </div>

      {/* Spinning circle + percentage */}
      <div
        style={{
          position: "absolute",
          bottom: 180,
          left: "50%",
          transform: `translateX(-50%) scale(${pulseScale})`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 24,
        }}
      >
        {/* Spinning ring */}
        <div
          style={{
            width: 200,
            height: 200,
            position: "relative",
          }}
        >
          {/* Outer ring */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: "50%",
              border: "6px solid rgba(255,255,255,0.15)",
            }}
          />
          {/* Spinning arc */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: "50%",
              border: "6px solid transparent",
              borderTopColor: "#ffffff",
              borderRightColor: "#ffffff",
              transform: `rotate(${spinAngle}deg)`,
            }}
          />
          {/* Percentage text */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 64,
              fontWeight: 900,
              color: "#ffffff",
            }}
          >
            {percentage}%
          </div>
        </div>
      </div>

      {/* Exit color wipe to scene 4 */}
      {wipeProgress > 0 && (
        <ColorWipe color={SCENE_COLORS.scene4} progress={wipeProgress} direction="right" />
      )}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 4: SITO PRONTO!                                              */
/* ------------------------------------------------------------------ */

const Scene4 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Watermark "04"
  const watermarkOpacity = interpolate(frame, [0, 15], [0, 0.1], {
    extrapolateRight: "clamp",
  });

  // Title
  const titleSpring = spring({ frame: frame - 5, fps, config: { damping: 14, stiffness: 80 } });
  const titleY = interpolate(titleSpring, [0, 1], [80, 0]);
  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);

  // Checkmark animation
  const checkSpring = spring({
    frame: frame - 20,
    fps,
    config: { damping: 10, stiffness: 100 },
  });
  const checkScale = interpolate(checkSpring, [0, 1], [0, 1]);
  const checkOpacity = interpolate(checkSpring, [0, 1], [0, 1]);

  // Checkmark path drawing
  const checkPathLength = interpolate(frame, [25, 45], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // URL text
  const urlSpring = spring({
    frame: frame - 45,
    fps,
    config: { damping: 12, stiffness: 80 },
  });
  const urlY = interpolate(urlSpring, [0, 1], [40, 0]);
  const urlOpacity = interpolate(urlSpring, [0, 1], [0, 1]);

  // Decorations
  const circleFloat = interpolate(frame, [0, 90], [0, -20], { extrapolateRight: "clamp" });
  const squareRot = interpolate(frame, [0, 90], [0, 30], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: SCENE_COLORS.scene4, fontFamily: FONT, overflow: "hidden" }}>
      {/* Watermark */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          fontSize: 300,
          fontWeight: 900,
          color: "#ffffff",
          opacity: watermarkOpacity,
          lineHeight: 1,
        }}
      >
        04
      </div>

      {/* Circle decoration */}
      <div
        style={{
          position: "absolute",
          top: 140 + circleFloat,
          right: 160,
          width: 90,
          height: 90,
          borderRadius: "50%",
          border: "4px solid rgba(255,255,255,0.2)",
        }}
      />

      {/* Square decoration */}
      <div
        style={{
          position: "absolute",
          bottom: 160,
          left: 140,
          width: 55,
          height: 55,
          border: "4px solid rgba(255,255,255,0.15)",
          transform: `rotate(${squareRot}deg)`,
        }}
      />

      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 140,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <div
          style={{
            fontSize: 28,
            fontWeight: 600,
            color: "rgba(255,255,255,0.6)",
            letterSpacing: 6,
            marginBottom: 16,
          }}
        >
          STEP 04
        </div>
        <h1
          style={{
            fontSize: 86,
            fontWeight: 900,
            color: "#ffffff",
            lineHeight: 1.05,
            margin: 0,
          }}
        >
          SITO PRONTO!
        </h1>
      </div>

      {/* Large checkmark */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: `translate(-50%, -10%) scale(${checkScale})`,
          opacity: checkOpacity,
        }}
      >
        <svg width={220} height={220} viewBox="0 0 220 220">
          {/* Circle background */}
          <circle
            cx={110}
            cy={110}
            r={100}
            fill="rgba(255,255,255,0.15)"
            stroke="#ffffff"
            strokeWidth={6}
          />
          {/* Checkmark path */}
          <path
            d="M 60 110 L 95 150 L 160 75"
            fill="none"
            stroke="#ffffff"
            strokeWidth={12}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={200}
            strokeDashoffset={200 * (1 - checkPathLength)}
          />
        </svg>
      </div>

      {/* URL text */}
      <div
        style={{
          position: "absolute",
          bottom: 180,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: urlOpacity,
          transform: `translateY(${urlY}px)`,
        }}
      >
        <div
          style={{
            display: "inline-block",
            padding: "16px 48px",
            borderRadius: 16,
            background: "rgba(255,255,255,0.15)",
            border: "2px solid rgba(255,255,255,0.3)",
          }}
        >
          <span
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: "#ffffff",
              letterSpacing: 2,
            }}
          >
            tuosito.it
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  COMPOSITION                                                        */
/* ------------------------------------------------------------------ */

export const ProcessVideoComposition = () => {
  return (
    <AbsoluteFill>
      <Sequence from={0} durationInFrames={90}>
        <Scene1 />
      </Sequence>
      <Sequence from={90} durationInFrames={90}>
        <Scene2 />
      </Sequence>
      <Sequence from={180} durationInFrames={90}>
        <Scene3 />
      </Sequence>
      <Sequence from={270} durationInFrames={90}>
        <Scene4 />
      </Sequence>
    </AbsoluteFill>
  );
};

export const PROCESS_VIDEO_CONFIG = {
  id: "ProcessVideo",
  fps: 30,
  durationInFrames: 360,
  width: 1920,
  height: 1080,
};
