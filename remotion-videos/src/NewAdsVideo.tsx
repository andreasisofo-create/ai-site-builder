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
/*  SCENE 1: "Il tuo sito e online." + "Ma chi lo vede?" (0-150, 5s)   */
/* ------------------------------------------------------------------ */

const AdsScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Main text fade in
  const mainEnter = spring({
    frame: frame - 10,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // "Ma chi lo vede?" appears after 1s (30 frames)
  const subEnter = spring({
    frame: frame - 45,
    fps,
    config: { damping: 14, stiffness: 90 },
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
        gap: 24,
      }}
    >
      {/* Main text */}
      <div
        style={{
          opacity: interpolate(mainEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(mainEnter, [0, 1], [20, 0])}px)`,
          fontSize: 72,
          fontWeight: 800,
          color: COLORS.text,
          textAlign: "center",
        }}
      >
        Il tuo sito e online.
      </div>

      {/* Sub text */}
      <div
        style={{
          opacity: interpolate(subEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(subEnter, [0, 1], [15, 0])}px)`,
          fontSize: 48,
          fontWeight: 600,
          color: COLORS.muted,
          textAlign: "center",
        }}
      >
        Ma chi lo vede?
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 2: 3 Cards slide up + "Ci pensiamo noi" (150-300, 5s)        */
/* ------------------------------------------------------------------ */

/** Simple Instagram icon (camera shape) */
const InstagramIcon = () => (
  <svg width={36} height={36} viewBox="0 0 24 24" fill="none" stroke={COLORS.accent} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <rect x={2} y={2} width={20} height={20} rx={5} ry={5} />
    <circle cx={12} cy={12} r={5} />
    <circle cx={17.5} cy={6.5} r={1} fill={COLORS.accent} stroke="none" />
  </svg>
);

/** Simple Google 'G' */
const GoogleIcon = () => (
  <svg width={36} height={36} viewBox="0 0 24 24">
    <text x={4} y={20} fontSize={22} fontWeight={900} fill="#4285F4" fontFamily="Arial, sans-serif">
      G
    </text>
  </svg>
);

/** Bar chart icon */
const BarChartIcon = () => (
  <svg width={36} height={36} viewBox="0 0 24 24" fill="none" stroke={COLORS.success} strokeWidth={2} strokeLinecap="round">
    <rect x={3} y={12} width={4} height={10} rx={1} fill={COLORS.success + "40"} />
    <rect x={10} y={6} width={4} height={16} rx={1} fill={COLORS.success + "60"} />
    <rect x={17} y={2} width={4} height={20} rx={1} fill={COLORS.success + "80"} />
  </svg>
);

const AdsScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // "Ci pensiamo noi" title
  const titleEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  const cards = [
    { icon: <InstagramIcon />, label: "Meta Ads", color: COLORS.accent, delay: 20 },
    { icon: <GoogleIcon />, label: "Google Ads", color: "#4285F4", delay: 29 },
    { icon: <BarChartIcon />, label: "Report mensile", color: COLORS.success, delay: 38 },
  ];

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 48,
      }}
    >
      {/* Title */}
      <div
        style={{
          opacity: interpolate(titleEnter, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
          fontSize: 56,
          fontWeight: 800,
          color: COLORS.text,
          textAlign: "center",
        }}
      >
        Ci pensiamo noi
      </div>

      {/* Cards */}
      <div style={{ display: "flex", gap: 32 }}>
        {cards.map((card, i) => {
          const cardEnter = spring({
            frame: frame - card.delay,
            fps,
            config: { damping: 12, stiffness: 80 },
          });

          return (
            <div
              key={i}
              style={{
                opacity: interpolate(cardEnter, [0, 1], [0, 1]),
                transform: `translateY(${interpolate(cardEnter, [0, 1], [60, 0])}px)`,
                width: 280,
                padding: "40px 32px",
                borderRadius: 20,
                background: COLORS.bg,
                border: `1px solid ${COLORS.border}`,
                boxShadow: "0 8px 30px rgba(0,0,0,0.06)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 20,
              }}
            >
              {/* Icon container */}
              <div
                style={{
                  width: 72,
                  height: 72,
                  borderRadius: 18,
                  background: card.color + "12",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {card.icon}
              </div>
              {/* Label */}
              <div
                style={{
                  fontSize: 26,
                  fontWeight: 700,
                  color: COLORS.text,
                }}
              >
                {card.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 3: Phone + notifications (300-450, 5s)                        */
/* ------------------------------------------------------------------ */

const AdsScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phone mockup
  const phoneEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 14, stiffness: 80 },
  });

  // Notification banners
  const notifications = [
    { text: "Nuovo cliente da Instagram", delay: 30 },
    { text: "Prenotazione dal sito", delay: 50 },
    { text: "Richiesta preventivo", delay: 70 },
  ];

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      {/* Phone mockup */}
      <div
        style={{
          opacity: interpolate(phoneEnter, [0, 1], [0, 1]),
          transform: `scale(${interpolate(phoneEnter, [0, 1], [0.85, 1])})`,
          width: 320,
          height: 580,
          borderRadius: 40,
          border: `3px solid ${COLORS.border}`,
          background: COLORS.bg,
          boxShadow: "0 25px 80px rgba(0,0,0,0.1)",
          overflow: "hidden",
          position: "relative",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Status bar */}
        <div
          style={{
            height: 36,
            background: COLORS.lightBg,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div style={{ width: 70, height: 5, borderRadius: 3, background: COLORS.border }} />
        </div>

        {/* Content area */}
        <div style={{ flex: 1, padding: 12, display: "flex", flexDirection: "column", gap: 10 }}>
          {/* Dashboard header */}
          <div style={{ height: 28, borderRadius: 6, background: COLORS.lightBg, marginBottom: 4 }} />
          {/* Mini chart placeholder */}
          <div
            style={{
              height: 100,
              borderRadius: 12,
              background: `linear-gradient(135deg, ${COLORS.accent}15, ${COLORS.violet}10)`,
              display: "flex",
              alignItems: "flex-end",
              padding: "0 12px 12px",
              gap: 8,
            }}
          >
            {[40, 60, 45, 75, 55, 80, 65].map((h, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  height: `${h}%`,
                  borderRadius: 4,
                  background: COLORS.accent + "50",
                }}
              />
            ))}
          </div>
          {/* Stats row */}
          <div style={{ display: "flex", gap: 8 }}>
            {[1, 2].map((_, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  height: 60,
                  borderRadius: 10,
                  background: COLORS.lightBg,
                  border: `1px solid ${COLORS.border}`,
                }}
              />
            ))}
          </div>
          {/* More content */}
          <div style={{ height: 80, borderRadius: 10, background: COLORS.lightBg }} />
        </div>

        {/* Notification banners sliding down */}
        {notifications.map((notif, i) => {
          const notifEnter = spring({
            frame: frame - notif.delay,
            fps,
            config: { damping: 14, stiffness: 90 },
          });
          const yPos = interpolate(notifEnter, [0, 1], [-80, 48 + i * 80]);
          const opacity = interpolate(notifEnter, [0, 1], [0, 1]);

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                top: yPos,
                left: 12,
                right: 12,
                padding: "14px 16px",
                borderRadius: 14,
                background: COLORS.bg,
                border: `1px solid ${COLORS.border}`,
                boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
                opacity,
                display: "flex",
                alignItems: "center",
                gap: 10,
                zIndex: 10,
              }}
            >
              {/* Mail icon placeholder */}
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 7,
                  background: COLORS.accent + "20",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 14,
                  flexShrink: 0,
                }}
              >
                <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke={COLORS.accent} strokeWidth={2}>
                  <rect x={2} y={4} width={20} height={16} rx={2} />
                  <path d="M22 4L12 13L2 4" />
                </svg>
              </div>
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: COLORS.text,
                  whiteSpace: "nowrap",
                }}
              >
                {notif.text}
              </span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  CLOSE SCENE (450-540, 3s)                                          */
/* ------------------------------------------------------------------ */

const AdsClose = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const textEnter = spring({
    frame: frame - 10,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Fade out at end
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
        gap: 8,
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
            fontSize: 64,
            fontWeight: 800,
            color: COLORS.text,
            lineHeight: 1.2,
          }}
        >
          Sito + Clienti.
        </div>
        <div
          style={{
            fontSize: 48,
            fontWeight: 700,
            color: COLORS.accent,
            marginTop: 8,
          }}
        >
          Tutto incluso.
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  COMPOSITION: 18 seconds, 540 frames at 30fps                       */
/* ------------------------------------------------------------------ */

export const NewAdsVideoComposition = () => {
  const frame = useCurrentFrame();

  // Fade transitions between scenes
  const fade1to2 = interpolate(frame, [140, 150], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fade2to3 = interpolate(frame, [290, 300], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fade3to4 = interpolate(frame, [440, 450], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      {/* Scene 1: Problem statement (0-150) */}
      <Sequence from={0} durationInFrames={150}>
        <AbsoluteFill style={{ opacity: fade1to2 }}>
          <AdsScene1 />
        </AbsoluteFill>
      </Sequence>

      {/* Scene 2: Cards (150-300) */}
      <Sequence from={150} durationInFrames={150}>
        <AbsoluteFill style={{ opacity: fade2to3 }}>
          <AdsScene2 />
        </AbsoluteFill>
      </Sequence>

      {/* Scene 3: Phone + notifications (300-450) */}
      <Sequence from={300} durationInFrames={150}>
        <AbsoluteFill style={{ opacity: fade3to4 }}>
          <AdsScene3 />
        </AbsoluteFill>
      </Sequence>

      {/* Close (450-540) */}
      <Sequence from={450} durationInFrames={90}>
        <AdsClose />
      </Sequence>
    </AbsoluteFill>
  );
};

export const NEW_ADS_VIDEO_CONFIG = {
  id: "NewAdsVideo",
  fps: 30,
  durationInFrames: 540, // 18 seconds
  width: 1920,
  height: 1080,
};
