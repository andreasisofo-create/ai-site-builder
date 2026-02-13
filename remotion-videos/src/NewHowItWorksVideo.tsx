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

const COLORS = {
  bg: "#FFFFFF",
  text: "#1E293B",
  accent: "#4F46E5",
  violet: "#7C3AED",
  success: "#10B981",
  muted: "#64748B",
  border: "#E2E8F0",
  lightBg: "#F8FAFC",
};

/* ------------------------------------------------------------------ */
/*  SVG ICONS                                                          */
/* ------------------------------------------------------------------ */

const MessageSquareIcon = ({ size = 80, color = COLORS.accent }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const SparklesIcon = ({ size = 80, color = COLORS.violet }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3z" />
    <path d="M18 14l.7 2.3L21 17l-2.3.7L18 20l-.7-2.3L15 17l2.3-.7L18 14z" />
  </svg>
);

const RocketIcon = ({ size = 80, color = COLORS.success }: { size?: number; color?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
    <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
  </svg>
);

/* ------------------------------------------------------------------ */
/*  SCENE 1: DESCRIVI (frames 0-210, 0-7s)                             */
/* ------------------------------------------------------------------ */

const CHAT_TEXT = "Sono un parrucchiere a Milano, specializzato in colorazioni naturali";

const DescriviScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Icon + title fade in
  const iconEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 90 },
  });
  const titleEnter = spring({
    frame: frame - 15,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Chat bubble appears at frame 50
  const bubbleEnter = spring({
    frame: frame - 50,
    fps,
    config: { damping: 14, stiffness: 80 },
  });

  // Typing inside bubble starts at frame 60
  const charsVisible = Math.min(
    CHAT_TEXT.length,
    Math.max(0, frame - 60)
  );
  const displayedText = CHAT_TEXT.slice(0, charsVisible);
  const cursorVisible = frame >= 60 && charsVisible < CHAT_TEXT.length && Math.sin(frame * 0.2) > 0;

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 32,
      }}
    >
      {/* Icon */}
      <div
        style={{
          opacity: interpolate(iconEnter, [0, 1], [0, 1]),
          transform: `scale(${interpolate(iconEnter, [0, 1], [0.5, 1])})`,
        }}
      >
        <div
          style={{
            width: 100,
            height: 100,
            borderRadius: 24,
            background: `${COLORS.accent}12`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <MessageSquareIcon size={52} />
        </div>
      </div>

      {/* Title */}
      <div
        style={{
          opacity: interpolate(titleEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
          fontSize: 52,
          fontWeight: 800,
          color: COLORS.text,
          textAlign: "center",
        }}
      >
        Descrivi il tuo business
      </div>

      {/* Chat bubble */}
      <div
        style={{
          opacity: interpolate(bubbleEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(bubbleEnter, [0, 1], [30, 0])}px)`,
          maxWidth: 800,
          padding: "24px 32px",
          borderRadius: 20,
          borderBottomLeftRadius: 6,
          background: COLORS.lightBg,
          border: `1px solid ${COLORS.border}`,
          boxShadow: "0 4px 20px rgba(0,0,0,0.04)",
        }}
      >
        <span
          style={{
            fontSize: 26,
            color: COLORS.text,
            fontWeight: 500,
            lineHeight: 1.5,
          }}
        >
          {displayedText}
          {cursorVisible && (
            <span
              style={{
                display: "inline-block",
                width: 2,
                height: 26,
                background: COLORS.accent,
                marginLeft: 2,
                verticalAlign: "middle",
              }}
            />
          )}
        </span>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 2: GENERA (frames 210-450, 7-15s)                            */
/* ------------------------------------------------------------------ */

const GeneraScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Icon + title
  const iconEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 90 },
  });
  const titleEnter = spring({
    frame: frame - 15,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Wireframe fill progress
  const fillProgress = interpolate(frame, [30, 200], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Timer: 00:00 to 00:45
  const timerSeconds = Math.min(45, Math.round(fillProgress * 45));
  const timerText = `00:${timerSeconds.toString().padStart(2, "0")}`;

  // Wireframe rows
  const rows = [
    { y: 0, h: 40, label: "nav" },
    { y: 50, h: 140, label: "hero" },
    { y: 200, h: 30, label: "section-title" },
    { y: 240, h: 80, label: "cards" },
    { y: 330, h: 30, label: "footer" },
  ];
  const totalHeight = 360;

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 32,
      }}
    >
      {/* Icon */}
      <div
        style={{
          opacity: interpolate(iconEnter, [0, 1], [0, 1]),
          transform: `scale(${interpolate(iconEnter, [0, 1], [0.5, 1])})`,
        }}
      >
        <div
          style={{
            width: 100,
            height: 100,
            borderRadius: 24,
            background: `${COLORS.violet}12`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <SparklesIcon size={52} />
        </div>
      </div>

      {/* Title */}
      <div
        style={{
          opacity: interpolate(titleEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
          fontSize: 52,
          fontWeight: 800,
          color: COLORS.text,
          textAlign: "center",
        }}
      >
        L'AI crea il tuo sito
      </div>

      {/* Wireframe + timer */}
      <div style={{ display: "flex", alignItems: "flex-start", gap: 48 }}>
        {/* Wireframe container */}
        <div
          style={{
            width: 500,
            height: totalHeight,
            position: "relative",
            borderRadius: 12,
            border: `1px solid ${COLORS.border}`,
            overflow: "hidden",
            background: COLORS.lightBg,
          }}
        >
          {/* Color fill overlay */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: `${fillProgress * 100}%`,
              background: `linear-gradient(180deg, ${COLORS.accent}15, ${COLORS.violet}10)`,
            }}
          />

          {/* Wireframe blocks */}
          {rows.map((row, i) => {
            const rowFilled = fillProgress > (row.y + row.h / 2) / totalHeight;
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  top: row.y + 10,
                  left: 16,
                  right: 16,
                  height: row.h,
                  borderRadius: 8,
                  border: `2px ${rowFilled ? "solid" : "dashed"} ${rowFilled ? COLORS.accent + "60" : COLORS.border}`,
                  background: rowFilled ? COLORS.accent + "10" : "transparent",
                  transition: "all 0.3s",
                }}
              />
            );
          })}
        </div>

        {/* Timer */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 8,
            marginTop: 20,
          }}
        >
          <div
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: COLORS.accent,
              fontVariantNumeric: "tabular-nums",
              fontFamily: "monospace",
            }}
          >
            {timerText}
          </div>
          <div
            style={{
              fontSize: 18,
              color: COLORS.muted,
              fontWeight: 600,
            }}
          >
            secondi
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 3: PUBBLICA (frames 450-660, 15-22s)                         */
/* ------------------------------------------------------------------ */

function seededRandom(seed: number): number {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

const PubblicaScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Icon + title
  const iconEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 90 },
  });
  const titleEnter = spring({
    frame: frame - 15,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Phone mockup
  const phoneEnter = spring({
    frame: frame - 25,
    fps,
    config: { damping: 12, stiffness: 80 },
  });

  // Confetti (small colored circles falling)
  const confettiColors = [COLORS.accent, COLORS.violet, COLORS.success, "#F59E0B"];
  const confettiPieces = Array.from({ length: 12 }, (_, i) => ({
    x: 300 + seededRandom(i * 3 + 1) * 400,
    startY: -40 - seededRandom(i * 3 + 2) * 80,
    delay: 50 + Math.floor(seededRandom(i * 3 + 3) * 30),
    color: confettiColors[i % confettiColors.length],
    size: 8 + seededRandom(i * 3 + 4) * 10,
  }));

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 32,
        overflow: "hidden",
      }}
    >
      {/* Icon */}
      <div
        style={{
          opacity: interpolate(iconEnter, [0, 1], [0, 1]),
          transform: `scale(${interpolate(iconEnter, [0, 1], [0.5, 1])})`,
        }}
      >
        <div
          style={{
            width: 100,
            height: 100,
            borderRadius: 24,
            background: `${COLORS.success}12`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <RocketIcon size={52} />
        </div>
      </div>

      {/* Title */}
      <div
        style={{
          opacity: interpolate(titleEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
          fontSize: 52,
          fontWeight: 800,
          color: COLORS.text,
          textAlign: "center",
        }}
      >
        Sei online
      </div>

      {/* Phone mockup */}
      <div
        style={{
          opacity: interpolate(phoneEnter, [0, 1], [0, 1]),
          transform: `scale(${interpolate(phoneEnter, [0, 1], [0.8, 1])})`,
          width: 260,
          height: 460,
          borderRadius: 32,
          border: `3px solid ${COLORS.border}`,
          background: COLORS.bg,
          boxShadow: "0 20px 60px rgba(0,0,0,0.1)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Phone status bar */}
        <div
          style={{
            height: 32,
            background: COLORS.lightBg,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div style={{ width: 60, height: 4, borderRadius: 2, background: COLORS.border }} />
        </div>

        {/* Phone content - colored sections */}
        <div style={{ flex: 1, padding: 10, display: "flex", flexDirection: "column", gap: 8 }}>
          {/* Nav */}
          <div style={{ height: 24, borderRadius: 6, background: COLORS.lightBg }} />
          {/* Hero */}
          <div
            style={{
              height: 120,
              borderRadius: 10,
              background: `linear-gradient(135deg, ${COLORS.accent}30, ${COLORS.violet}20)`,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              padding: 12,
              gap: 6,
            }}
          >
            <div style={{ width: "70%", height: 10, borderRadius: 3, background: COLORS.accent + "50" }} />
            <div style={{ width: "50%", height: 8, borderRadius: 3, background: COLORS.accent + "30" }} />
            <div style={{ width: 60, height: 20, borderRadius: 5, background: COLORS.accent, marginTop: 4 }} />
          </div>
          {/* Cards */}
          <div style={{ display: "flex", gap: 6 }}>
            {[1, 2].map((_, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  height: 70,
                  borderRadius: 8,
                  background: COLORS.lightBg,
                  border: `1px solid ${COLORS.border}`,
                  padding: 8,
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                }}
              >
                <div style={{ width: "60%", height: 6, borderRadius: 2, background: COLORS.accent + "40" }} />
                <div style={{ width: "80%", height: 5, borderRadius: 2, background: "#CBD5E1" }} />
              </div>
            ))}
          </div>
          {/* Contact */}
          <div style={{ height: 50, borderRadius: 8, background: COLORS.lightBg }} />
        </div>
      </div>

      {/* Confetti */}
      {confettiPieces.map((piece, i) => {
        const fallProgress = interpolate(
          frame,
          [piece.delay, piece.delay + 80],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );
        const y = piece.startY + fallProgress * 700;
        const opacity = interpolate(fallProgress, [0.7, 1], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: piece.x,
              top: y,
              width: piece.size,
              height: piece.size,
              borderRadius: "50%",
              background: piece.color,
              opacity: fallProgress > 0 ? opacity : 0,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  CLOSE SCENE (frames 660-750, 22-25s)                               */
/* ------------------------------------------------------------------ */

const CloseScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const textEnter = spring({
    frame: frame - 10,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Fade out at the end
  const fadeOut = interpolate(frame, [70, 90], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 16,
        opacity: fadeOut,
      }}
    >
      <div
        style={{
          opacity: interpolate(textEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(textEnter, [0, 1], [20, 0])}px)`,
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontSize: 48,
            fontWeight: 800,
            color: COLORS.text,
          }}
        >
          Crea il tuo sito gratis
        </div>
        <div
          style={{
            marginTop: 16,
            fontSize: 36,
            fontWeight: 700,
            color: COLORS.accent,
          }}
        >
          e-quipe.app
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  COMPOSITION: 25 seconds, 750 frames at 30fps                       */
/* ------------------------------------------------------------------ */

export const NewHowItWorksVideoComposition = () => {
  const frame = useCurrentFrame();

  // Transition overlays
  const slide1to2 = interpolate(frame, [200, 210], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const slide2to3 = interpolate(frame, [440, 450], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fade3to4 = interpolate(frame, [650, 660], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      {/* Scene 1: DESCRIVI (0-210) */}
      <Sequence from={0} durationInFrames={210}>
        <AbsoluteFill
          style={{
            transform: `translateX(${interpolate(slide1to2, [0, 1], [0, -100])}%)`,
          }}
        >
          <DescriviScene />
        </AbsoluteFill>
      </Sequence>

      {/* Scene 2: GENERA (210-450) */}
      <Sequence from={210} durationInFrames={240}>
        <AbsoluteFill
          style={{
            transform: `translateX(${interpolate(
              frame < 210 ? 0 : interpolate(frame, [210, 220], [100, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              [0, 100],
              [0, 100]
            )}%) translateX(${frame >= 440 ? interpolate(slide2to3, [0, 1], [0, -100]) : 0}%)`,
          }}
        >
          <GeneraScene />
        </AbsoluteFill>
      </Sequence>

      {/* Scene 3: PUBBLICA (450-660) */}
      <Sequence from={450} durationInFrames={210}>
        <AbsoluteFill style={{ opacity: fade3to4 }}>
          <PubblicaScene />
        </AbsoluteFill>
      </Sequence>

      {/* Close (660-750) */}
      <Sequence from={660} durationInFrames={90}>
        <CloseScene />
      </Sequence>
    </AbsoluteFill>
  );
};

export const NEW_HOW_IT_WORKS_VIDEO_CONFIG = {
  id: "NewHowItWorksVideo",
  fps: 30,
  durationInFrames: 750, // 25 seconds
  width: 1920,
  height: 1080,
};
