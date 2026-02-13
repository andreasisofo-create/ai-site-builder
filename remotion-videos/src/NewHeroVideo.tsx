import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
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
/*  SCENE 1: Typing animation in input field (frames 0-90, 0-3s)       */
/* ------------------------------------------------------------------ */

const TYPING_TEXT =
  "Ristorante Da Marco, cucina tradizionale romana, zona Trastevere";

const HeroScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Input field fade-in
  const fieldEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Typing: one character per frame, starting at frame 10
  const charsVisible = Math.min(
    TYPING_TEXT.length,
    Math.max(0, frame - 10)
  );
  const displayedText = TYPING_TEXT.slice(0, charsVisible);

  // Blinking cursor
  const cursorVisible = Math.sin(frame * 0.2) > 0;

  // Label fade-in
  const labelOpacity = interpolate(frame, [0, 15], [0, 1], {
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
      }}
    >
      {/* Label */}
      <div
        style={{
          opacity: labelOpacity,
          fontSize: 28,
          fontWeight: 600,
          color: COLORS.muted,
          marginBottom: 24,
          letterSpacing: 1,
        }}
      >
        Descrivi la tua attivita
      </div>

      {/* Input field */}
      <div
        style={{
          opacity: interpolate(fieldEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(fieldEnter, [0, 1], [20, 0])}px)`,
          width: 900,
          minHeight: 72,
          padding: "20px 28px",
          borderRadius: 16,
          border: `2px solid ${COLORS.accent}`,
          background: COLORS.bg,
          boxShadow: `0 0 0 4px ${COLORS.accent}20, 0 4px 20px rgba(0,0,0,0.06)`,
          display: "flex",
          alignItems: "center",
        }}
      >
        <span
          style={{
            fontSize: 26,
            color: COLORS.text,
            fontWeight: 500,
            lineHeight: 1.4,
          }}
        >
          {displayedText}
          {cursorVisible && (
            <span
              style={{
                display: "inline-block",
                width: 2,
                height: 28,
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
/*  SCENE 2: Progress bar (frames 90-180, 3-6s)                        */
/* ------------------------------------------------------------------ */

const HeroScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Text fade-in
  const textEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Progress: 0% to 100% over 90 frames
  const progress = interpolate(frame, [10, 85], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });
  const percentage = Math.round(progress);

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 40,
      }}
    >
      {/* Text */}
      <div
        style={{
          opacity: interpolate(textEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(textEnter, [0, 1], [20, 0])}px)`,
          fontSize: 42,
          fontWeight: 700,
          color: COLORS.text,
          textAlign: "center",
        }}
      >
        L'AI sta creando il tuo sito...
      </div>

      {/* Progress bar container */}
      <div
        style={{
          width: 700,
          display: "flex",
          flexDirection: "column",
          gap: 16,
          alignItems: "center",
        }}
      >
        {/* Bar */}
        <div
          style={{
            width: "100%",
            height: 16,
            borderRadius: 8,
            background: "#F1F5F9",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${progress}%`,
              height: "100%",
              borderRadius: 8,
              background: `linear-gradient(90deg, ${COLORS.accent}, ${COLORS.violet})`,
            }}
          />
        </div>

        {/* Percentage */}
        <div
          style={{
            fontSize: 28,
            fontWeight: 700,
            color: COLORS.accent,
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {percentage}%
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 3: Browser mockup (frames 180-360, 6-12s)                    */
/* ------------------------------------------------------------------ */

const HeroScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Browser slide up
  const browserEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 80 },
  });

  // Staggered content blocks
  const nav = spring({ frame: frame - 15, fps, config: { damping: 14 } });
  const hero = spring({ frame: frame - 25, fps, config: { damping: 14 } });
  const cards = spring({ frame: frame - 40, fps, config: { damping: 14 } });

  // Badge appear (after 2 seconds = 60 frames)
  const badgeEnter = spring({
    frame: frame - 70,
    fps,
    config: { damping: 10, stiffness: 100 },
  });

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Browser chrome mockup */}
      <div
        style={{
          opacity: interpolate(browserEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(browserEnter, [0, 1], [60, 0])}px)`,
          width: 1000,
          borderRadius: 16,
          overflow: "hidden",
          border: `1px solid ${COLORS.border}`,
          boxShadow: "0 25px 80px rgba(0,0,0,0.1), 0 4px 20px rgba(0,0,0,0.05)",
        }}
      >
        {/* Toolbar */}
        <div
          style={{
            height: 48,
            background: "#F8FAFC",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            gap: 10,
            borderBottom: `1px solid ${COLORS.border}`,
          }}
        >
          {/* Traffic lights */}
          <div style={{ display: "flex", gap: 7 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F57" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FFBD2E" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28C840" }} />
          </div>
          {/* URL bar */}
          <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
            <div
              style={{
                padding: "6px 24px",
                borderRadius: 8,
                background: "#FFFFFF",
                border: `1px solid ${COLORS.border}`,
                color: COLORS.muted,
                fontSize: 14,
                fontFamily: "monospace",
              }}
            >
              damarco-ristorante.e-quipe.app
            </div>
          </div>
        </div>

        {/* Website content */}
        <div style={{ background: "#FFFFFF", padding: 24 }}>
          {/* Nav */}
          <div
            style={{
              opacity: interpolate(nav, [0, 1], [0, 1]),
              height: 44,
              borderRadius: 10,
              background: COLORS.lightBg,
              marginBottom: 16,
              display: "flex",
              alignItems: "center",
              padding: "0 16px",
              justifyContent: "space-between",
            }}
          >
            <div style={{ width: 100, height: 14, borderRadius: 4, background: COLORS.accent }} />
            <div style={{ display: "flex", gap: 12 }}>
              {[60, 50, 70, 55].map((w, i) => (
                <div key={i} style={{ width: w, height: 10, borderRadius: 3, background: "#CBD5E1" }} />
              ))}
            </div>
          </div>

          {/* Hero block */}
          <div
            style={{
              opacity: interpolate(hero, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(hero, [0, 1], [20, 0])}px)`,
              height: 200,
              borderRadius: 12,
              background: `linear-gradient(135deg, #FEF3C7, #FBBF24)`,
              marginBottom: 16,
              padding: 32,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              gap: 12,
            }}
          >
            <div style={{ width: 320, height: 24, borderRadius: 6, background: "rgba(30,41,59,0.3)" }} />
            <div style={{ width: 220, height: 14, borderRadius: 4, background: "rgba(30,41,59,0.15)" }} />
            <div
              style={{
                width: 140,
                height: 38,
                borderRadius: 8,
                background: COLORS.text,
                marginTop: 8,
              }}
            />
          </div>

          {/* Cards row */}
          <div
            style={{
              opacity: interpolate(cards, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(cards, [0, 1], [20, 0])}px)`,
              display: "flex",
              gap: 12,
            }}
          >
            {[1, 2, 3].map((_, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  height: 90,
                  borderRadius: 10,
                  background: COLORS.lightBg,
                  border: `1px solid ${COLORS.border}`,
                  padding: 14,
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                }}
              >
                <div style={{ width: "60%", height: 12, borderRadius: 3, background: COLORS.accent + "60" }} />
                <div style={{ width: "80%", height: 8, borderRadius: 2, background: "#CBD5E1" }} />
                <div style={{ width: "50%", height: 8, borderRadius: 2, background: "#E2E8F0" }} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Success badge */}
      <div
        style={{
          position: "absolute",
          bottom: 120,
          right: 280,
          opacity: interpolate(badgeEnter, [0, 1], [0, 1]),
          transform: `scale(${interpolate(badgeEnter, [0, 1], [0.5, 1])})`,
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "14px 28px",
          borderRadius: 50,
          background: "#ECFDF5",
          border: `2px solid ${COLORS.success}`,
          boxShadow: "0 8px 30px rgba(16,185,129,0.2)",
        }}
      >
        {/* Green circle + check */}
        <svg width={28} height={28} viewBox="0 0 28 28">
          <circle cx={14} cy={14} r={14} fill={COLORS.success} />
          <path
            d="M 8 14 L 12 18 L 20 10"
            fill="none"
            stroke="#FFFFFF"
            strokeWidth={3}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span
          style={{
            fontSize: 22,
            fontWeight: 700,
            color: COLORS.success,
          }}
        >
          Online in 45 secondi
        </span>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  COMPOSITION: 15 seconds, 450 frames at 30fps, LOOPABLE             */
/* ------------------------------------------------------------------ */

export const NewHeroVideoComposition = () => {
  const frame = useCurrentFrame();

  // Scene boundaries: 0-90 (3s), 90-180 (3s), 180-360 (6s), 360-450 (3s fade)
  const scene =
    frame < 90 ? 1 : frame < 180 ? 2 : frame < 360 ? 3 : 4;

  // Scene 1 fade out
  const fadeOut1 = interpolate(frame, [80, 90], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // Scene 2 fade in/out
  const fadeIn2 = interpolate(frame, [90, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut2 = interpolate(frame, [170, 180], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // Scene 3 fade in/out (slide-up handled inside)
  const fadeIn3 = interpolate(frame, [180, 190], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut3 = interpolate(frame, [350, 360], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // Scene 4 (loop fade): gentle fade to white
  const fadeToWhite = interpolate(frame, [360, 450], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      {scene === 1 && (
        <AbsoluteFill style={{ opacity: fadeOut1 }}>
          <HeroScene1 />
        </AbsoluteFill>
      )}
      {scene === 2 && (
        <AbsoluteFill style={{ opacity: Math.min(fadeIn2, fadeOut2) }}>
          <HeroScene2 />
        </AbsoluteFill>
      )}
      {scene === 3 && (
        <AbsoluteFill style={{ opacity: Math.min(fadeIn3, fadeOut3) }}>
          <HeroScene3 />
        </AbsoluteFill>
      )}
      {scene === 4 && (
        <AbsoluteFill
          style={{
            background: COLORS.bg,
            opacity: fadeToWhite,
          }}
        />
      )}
    </AbsoluteFill>
  );
};

export const NEW_HERO_VIDEO_CONFIG = {
  id: "NewHeroVideo",
  fps: 30,
  durationInFrames: 450, // 15 seconds
  width: 1920,
  height: 1080,
};
