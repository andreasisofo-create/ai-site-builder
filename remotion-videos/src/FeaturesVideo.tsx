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
const MONO = `"Courier New", Consolas, monospace`;

const BG = "#0d1117";
const GREEN = "#00ff41";
const CYAN = "#00d4ff";

/* ------------------------------------------------------------------ */
/*  Scanline overlay - subtle horizontal lines                         */
/* ------------------------------------------------------------------ */

const Scanlines = () => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background:
        "repeating-linear-gradient(0deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 3px)",
      pointerEvents: "none",
      zIndex: 100,
    }}
  />
);

/* ------------------------------------------------------------------ */
/*  Blinking cursor component                                          */
/* ------------------------------------------------------------------ */

const Cursor = ({ color = GREEN }: { color?: string }) => {
  const frame = useCurrentFrame();
  const visible = Math.sin(frame * 0.25) > 0;
  return (
    <span
      style={{
        display: "inline-block",
        width: 14,
        height: "1.1em",
        background: visible ? color : "transparent",
        marginLeft: 2,
        verticalAlign: "middle",
      }}
    />
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 1: 19 TEMPLATE                                               */
/* ------------------------------------------------------------------ */

const TerminalScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Prompt typing
  const promptText = "> list --templates --all";
  const promptProgress = interpolate(frame, [5, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const promptChars = Math.floor(promptProgress * promptText.length);

  // Big number entrance
  const numberSpring = spring({
    frame: frame - 25,
    fps,
    config: { damping: 12, stiffness: 80 },
  });

  // Subtitle
  const subtitleOpacity = interpolate(frame, [35, 45], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Template grid - 6 colored rectangles
  const templateColors = ["#dc2626", "#3b82f6", "#7c3aed", "#22c55e", "#f59e0b", "#ec4899"];

  // Glow pulse on the number
  const glowPulse = interpolate(
    Math.sin(frame * 0.08),
    [-1, 1],
    [10, 30]
  );

  return (
    <AbsoluteFill
      style={{
        background: BG,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Scanlines />

      {/* Terminal prompt line */}
      <div
        style={{
          position: "absolute",
          top: 80,
          left: 120,
          fontFamily: MONO,
          fontSize: 28,
          color: GREEN,
          zIndex: 2,
        }}
      >
        <span style={{ color: "#586069" }}>user@sitebuilder:~$ </span>
        <span>{promptText.slice(0, promptChars)}</span>
        {promptChars < promptText.length && <Cursor />}
      </div>

      {/* Big "19" */}
      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 16,
          transform: `scale(${interpolate(numberSpring, [0, 1], [0.3, 1])})`,
          opacity: interpolate(numberSpring, [0, 1], [0, 1]),
        }}
      >
        <div
          style={{
            fontSize: 220,
            fontWeight: 900,
            fontFamily: MONO,
            color: GREEN,
            lineHeight: 1,
            textShadow: `0 0 ${glowPulse}px ${GREEN}, 0 0 ${glowPulse * 2}px rgba(0,255,65,0.3)`,
          }}
        >
          19
        </div>

        {/* Subtitle */}
        <div
          style={{
            fontSize: 48,
            fontWeight: 700,
            color: "#e6edf3",
            letterSpacing: 8,
            opacity: subtitleOpacity,
            transform: `translateY(${interpolate(subtitleOpacity, [0, 1], [10, 0])}px)`,
          }}
        >
          TEMPLATE PROFESSIONALI
        </div>
      </div>

      {/* Grid of 6 template thumbnails */}
      <div
        style={{
          position: "absolute",
          bottom: 100,
          display: "flex",
          gap: 24,
          zIndex: 2,
        }}
      >
        {templateColors.map((color, i) => {
          const cardDelay = 40 + i * 5;
          const cardOpacity = interpolate(frame, [cardDelay, cardDelay + 10], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const cardY = interpolate(frame, [cardDelay, cardDelay + 10], [20, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });

          return (
            <div
              key={i}
              style={{
                width: 140,
                height: 90,
                borderRadius: 8,
                background: `linear-gradient(135deg, ${color}33, ${color}11)`,
                border: `1px solid ${color}66`,
                opacity: cardOpacity,
                transform: `translateY(${cardY}px)`,
                display: "flex",
                flexDirection: "column",
                padding: 10,
                gap: 6,
              }}
            >
              <div style={{ width: "60%", height: 4, borderRadius: 2, background: `${color}88` }} />
              <div style={{ width: "40%", height: 3, borderRadius: 2, background: `${color}44` }} />
              <div style={{ flex: 1 }} />
              <div style={{ width: 30, height: 10, borderRadius: 3, background: `${color}66` }} />
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 2: AI POWERED                                                */
/* ------------------------------------------------------------------ */

const TerminalScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title
  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 80 },
  });

  // Typing command
  const cmdText = "> generate --style modern --ai kimi-k2.5";
  const cmdProgress = interpolate(frame, [10, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cmdChars = Math.floor(cmdProgress * cmdText.length);

  // Loading bar
  const barProgress = interpolate(frame, [42, 65], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Status lines after loading
  const statusLines = [
    { text: "[OK] Analisi business completata", delay: 50 },
    { text: "[OK] Theme generato: colori + font", delay: 55 },
    { text: "[OK] Contenuti AI creati", delay: 60 },
    { text: "[OK] Componenti assemblati", delay: 65 },
    { text: "[OK] GSAP animazioni iniettate", delay: 68 },
  ];

  // Glow pulse on title
  const cyanGlow = interpolate(Math.sin(frame * 0.1), [-1, 1], [10, 25]);

  return (
    <AbsoluteFill
      style={{
        background: BG,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Scanlines />

      {/* Title: AI POWERED */}
      <div
        style={{
          position: "absolute",
          top: 100,
          fontSize: 72,
          fontWeight: 900,
          color: CYAN,
          letterSpacing: 6,
          textShadow: `0 0 ${cyanGlow}px ${CYAN}, 0 0 ${cyanGlow * 2}px rgba(0,212,255,0.3)`,
          opacity: interpolate(titleSpring, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(titleSpring, [0, 1], [20, 0])}px)`,
          zIndex: 2,
        }}
      >
        AI POWERED
      </div>

      {/* Terminal window */}
      <div
        style={{
          width: 1100,
          minHeight: 400,
          borderRadius: 12,
          background: "#161b22",
          border: `1px solid #30363d`,
          padding: 0,
          overflow: "hidden",
          position: "relative",
          zIndex: 1,
          marginTop: 60,
        }}
      >
        {/* Terminal title bar */}
        <div
          style={{
            height: 40,
            background: "#21262d",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            gap: 8,
            borderBottom: "1px solid #30363d",
          }}
        >
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ff5f57" }} />
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ffbd2e" }} />
          <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28c840" }} />
          <span style={{ marginLeft: 16, fontFamily: MONO, fontSize: 14, color: "#8b949e" }}>
            site-builder-cli
          </span>
        </div>

        {/* Terminal content */}
        <div style={{ padding: "24px 28px", fontFamily: MONO, fontSize: 24, lineHeight: 1.8 }}>
          {/* Command line */}
          <div style={{ color: GREEN }}>
            <span style={{ color: "#8b949e" }}>$ </span>
            {cmdText.slice(0, cmdChars)}
            {cmdChars < cmdText.length && <Cursor />}
          </div>

          {/* Loading bar */}
          {frame >= 42 && (
            <div style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 16 }}>
              <span style={{ color: CYAN, fontSize: 20 }}>Generazione</span>
              <div
                style={{
                  flex: 1,
                  height: 16,
                  borderRadius: 4,
                  background: "#21262d",
                  border: "1px solid #30363d",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${barProgress * 100}%`,
                    height: "100%",
                    background: `linear-gradient(90deg, ${GREEN}, ${CYAN})`,
                    borderRadius: 3,
                    boxShadow: `0 0 10px ${GREEN}66`,
                  }}
                />
              </div>
              <span style={{ color: GREEN, fontSize: 20 }}>
                {Math.floor(barProgress * 100)}%
              </span>
            </div>
          )}

          {/* Status lines */}
          {statusLines.map((line, i) => {
            const lineOpacity = interpolate(frame, [line.delay, line.delay + 3], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <div
                key={i}
                style={{
                  marginTop: i === 0 ? 16 : 4,
                  opacity: lineOpacity,
                  color: GREEN,
                  fontSize: 20,
                }}
              >
                {line.text}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 3: 29 ANIMAZIONI                                             */
/* ------------------------------------------------------------------ */

const TerminalScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Big number
  const numberSpring = spring({
    frame: frame - 5,
    fps,
    config: { damping: 12, stiffness: 80 },
  });

  const cyanGlow = interpolate(Math.sin(frame * 0.08), [-1, 1], [10, 30]);

  // Subtitle
  const subtitleOpacity = interpolate(frame, [20, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 4 animated squares
  const squareSize = 100;

  // Square 1: fade-in
  const fadeInProgress = interpolate(frame, [25, 45], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Square 2: scale-up
  const scaleUpProgress = interpolate(frame, [30, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Square 3: slide-right
  const slideRightProgress = interpolate(frame, [35, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Square 4: rotate
  const rotateProgress = interpolate(frame, [40, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const squares = [
    {
      label: "fade-in",
      color: GREEN,
      style: {
        opacity: fadeInProgress,
      },
    },
    {
      label: "scale-up",
      color: CYAN,
      style: {
        transform: `scale(${interpolate(scaleUpProgress, [0, 1], [0, 1])})`,
        opacity: scaleUpProgress > 0 ? 1 : 0,
      },
    },
    {
      label: "slide-right",
      color: GREEN,
      style: {
        transform: `translateX(${interpolate(slideRightProgress, [0, 1], [-80, 0])}px)`,
        opacity: slideRightProgress,
      },
    },
    {
      label: "rotate",
      color: CYAN,
      style: {
        transform: `rotate(${interpolate(rotateProgress, [0, 1], [-180, 0])}deg)`,
        opacity: rotateProgress,
      },
    },
  ];

  return (
    <AbsoluteFill
      style={{
        background: BG,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Scanlines />

      {/* Big "29" + subtitle */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 12,
          marginBottom: 60,
          zIndex: 2,
          transform: `scale(${interpolate(numberSpring, [0, 1], [0.3, 1])})`,
          opacity: interpolate(numberSpring, [0, 1], [0, 1]),
        }}
      >
        <div
          style={{
            fontSize: 200,
            fontWeight: 900,
            fontFamily: MONO,
            color: CYAN,
            lineHeight: 1,
            textShadow: `0 0 ${cyanGlow}px ${CYAN}, 0 0 ${cyanGlow * 2}px rgba(0,212,255,0.3)`,
          }}
        >
          29
        </div>
        <div
          style={{
            fontSize: 48,
            fontWeight: 700,
            color: "#e6edf3",
            letterSpacing: 8,
            opacity: subtitleOpacity,
          }}
        >
          EFFETTI GSAP
        </div>
      </div>

      {/* 4 animated squares */}
      <div
        style={{
          display: "flex",
          gap: 60,
          zIndex: 2,
        }}
      >
        {squares.map((sq, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 16,
            }}
          >
            <div
              style={{
                width: squareSize,
                height: squareSize,
                borderRadius: 12,
                border: `2px solid ${sq.color}`,
                background: `${sq.color}15`,
                boxShadow: `0 0 15px ${sq.color}33`,
                ...sq.style,
              }}
            />
            <span
              style={{
                fontFamily: MONO,
                fontSize: 20,
                color: sq.color,
                opacity: interpolate(frame, [50, 60], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              {sq.label}
            </span>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 4: 1 CLICK DEPLOY                                           */
/* ------------------------------------------------------------------ */

const TerminalScene4 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Checkmark entrance
  const checkSpring = spring({
    frame: frame - 5,
    fps,
    config: { damping: 10, stiffness: 100 },
  });

  // "PUBBLICA" text
  const publishOpacity = interpolate(frame, [20, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Globe icon entrance
  const globeOpacity = interpolate(frame, [30, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Globe rotation
  const globeRotation = frame * 0.8;

  // URL typing
  const urlText = "tuosito.e-quipe.app";
  const urlProgress = interpolate(frame, [40, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const urlChars = Math.floor(urlProgress * urlText.length);

  // Green glow on checkmark
  const greenGlow = interpolate(Math.sin(frame * 0.1), [-1, 1], [15, 35]);

  return (
    <AbsoluteFill
      style={{
        background: BG,
        fontFamily: FONT,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 40,
      }}
    >
      <Scanlines />

      {/* Large green checkmark */}
      <div
        style={{
          position: "relative",
          zIndex: 2,
          transform: `scale(${interpolate(checkSpring, [0, 1], [0, 1])})`,
          opacity: interpolate(checkSpring, [0, 1], [0, 1]),
        }}
      >
        <svg width={180} height={180} viewBox="0 0 180 180">
          <circle
            cx={90}
            cy={90}
            r={80}
            fill="none"
            stroke={GREEN}
            strokeWidth={4}
            opacity={0.3}
            filter={`drop-shadow(0 0 ${greenGlow}px ${GREEN})`}
          />
          <path
            d="M55 90 L80 115 L125 65"
            fill="none"
            stroke={GREEN}
            strokeWidth={8}
            strokeLinecap="round"
            strokeLinejoin="round"
            filter={`drop-shadow(0 0 ${greenGlow}px ${GREEN})`}
          />
        </svg>
      </div>

      {/* "PUBBLICA" text */}
      <div
        style={{
          fontSize: 72,
          fontWeight: 900,
          color: GREEN,
          letterSpacing: 10,
          textShadow: `0 0 ${greenGlow}px ${GREEN}, 0 0 ${greenGlow * 2}px rgba(0,255,65,0.3)`,
          opacity: publishOpacity,
          transform: `translateY(${interpolate(publishOpacity, [0, 1], [15, 0])}px)`,
          zIndex: 2,
        }}
      >
        PUBBLICA
      </div>

      {/* Globe icon */}
      <div
        style={{
          opacity: globeOpacity,
          zIndex: 2,
        }}
      >
        <svg width={120} height={120} viewBox="-60 -60 120 120">
          {/* Outer circle */}
          <circle
            cx={0}
            cy={0}
            r={50}
            fill="none"
            stroke={CYAN}
            strokeWidth={2}
            opacity={0.6}
          />
          {/* Vertical meridian */}
          <ellipse
            cx={0}
            cy={0}
            rx={25}
            ry={50}
            fill="none"
            stroke={CYAN}
            strokeWidth={1.5}
            opacity={0.4}
          />
          {/* Horizontal equator */}
          <ellipse
            cx={0}
            cy={0}
            rx={50}
            ry={18}
            fill="none"
            stroke={CYAN}
            strokeWidth={1.5}
            opacity={0.4}
          />
          {/* Rotating meridian */}
          <ellipse
            cx={0}
            cy={0}
            rx={15}
            ry={50}
            fill="none"
            stroke={CYAN}
            strokeWidth={1}
            opacity={0.3}
            transform={`rotate(${globeRotation * 0.5})`}
          />
          {/* Center dot */}
          <circle cx={0} cy={0} r={4} fill={CYAN} opacity={0.8} />
        </svg>
      </div>

      {/* URL bar */}
      <div
        style={{
          padding: "16px 36px",
          borderRadius: 10,
          background: "#161b22",
          border: `1px solid #30363d`,
          display: "flex",
          alignItems: "center",
          gap: 14,
          zIndex: 2,
          opacity: interpolate(frame, [38, 42], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        <div
          style={{
            width: 10,
            height: 10,
            borderRadius: "50%",
            background: GREEN,
            boxShadow: `0 0 8px ${GREEN}88`,
          }}
        />
        <span style={{ fontFamily: MONO, fontSize: 32, color: "#e6edf3", fontWeight: 500 }}>
          https://
          <span style={{ color: CYAN }}>
            {urlText.slice(0, urlChars)}
          </span>
          {urlChars < urlText.length && <Cursor color={CYAN} />}
        </span>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  COMPOSITION                                                        */
/* ------------------------------------------------------------------ */

export const FeaturesVideoComposition = () => {
  return (
    <AbsoluteFill style={{ background: BG }}>
      <Sequence from={0} durationInFrames={75}>
        <TerminalScene1 />
      </Sequence>
      <Sequence from={75} durationInFrames={75}>
        <TerminalScene2 />
      </Sequence>
      <Sequence from={150} durationInFrames={75}>
        <TerminalScene3 />
      </Sequence>
      <Sequence from={225} durationInFrames={75}>
        <TerminalScene4 />
      </Sequence>
    </AbsoluteFill>
  );
};

export const FEATURES_VIDEO_CONFIG = {
  id: "FeaturesVideo",
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
};
