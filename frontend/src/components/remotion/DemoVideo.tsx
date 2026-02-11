"use client";

import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";
import {
  TransitionSeries,
  linearTiming,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { evolvePath } from "@remotion/paths";
import { loadFont } from "@remotion/google-fonts/Inter";

// Load Inter font
const { fontFamily } = loadFont();

/* ------------------------------------------------------------------ */
/*  SHARED HELPERS                                                     */
/* ------------------------------------------------------------------ */

const FONT = `${fontFamily}, -apple-system, BlinkMacSystemFont, sans-serif`;

const GradientOrb = ({
  color,
  size,
  x,
  y,
  phaseOffset,
}: {
  color: string;
  size: number;
  x: string;
  y: string;
  phaseOffset: number;
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const breathe = interpolate(
    frame,
    [0, durationInFrames / 2, durationInFrames],
    [1, 1.3, 1],
    { extrapolateRight: "clamp" }
  );
  const drift = Math.sin((frame + phaseOffset) * 0.02) * 15;

  return (
    <div
      style={{
        position: "absolute",
        width: size,
        height: size,
        borderRadius: "50%",
        background: color,
        filter: `blur(${size * 0.4}px)`,
        left: x,
        top: y,
        transform: `scale(${breathe}) translate(${drift}px, ${drift * 0.6}px)`,
      }}
    />
  );
};

/** Seeded pseudo-random for deterministic rendering */
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

/* ------------------------------------------------------------------ */
/*  HERO VIDEO COMPOSITION — 12 seconds, 360 frames                   */
/* ------------------------------------------------------------------ */

/** Scene 1: "Descrivi il tuo business" — typewriter + form fields */
const HeroScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Typewriter for "Ristorante Da Mario"
  const typeText = "Ristorante Da Mario";
  const typeProgress = interpolate(frame, [15, 15 + typeText.length * 2], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const visibleChars = Math.floor(typeProgress * typeText.length);

  // Cursor blink
  const cursorOpacity =
    visibleChars < typeText.length ? (Math.sin(frame * 0.3) > 0 ? 1 : 0) : 0;

  // Form fields appear with spring stagger
  const fields = [
    { label: "NOME ATTIVITA", delay: 5 },
    { label: "TIPO", delay: 20 },
    { label: "STILE", delay: 35 },
  ];

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Animated gradient orbs */}
      <GradientOrb color="rgba(139,92,246,0.15)" size={500} x="10%" y="15%" phaseOffset={0} />
      <GradientOrb color="rgba(59,130,246,0.12)" size={400} x="60%" y="55%" phaseOffset={60} />
      <GradientOrb color="rgba(168,85,247,0.10)" size={350} x="75%" y="10%" phaseOffset={120} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 48,
        }}
      >
        {/* Title */}
        <div
          style={{
            opacity: interpolate(
              spring({ frame, fps, config: { damping: 15, stiffness: 80 } }),
              [0, 1],
              [0, 1]
            ),
            transform: `translateY(${interpolate(
              spring({ frame, fps, config: { damping: 15 } }),
              [0, 1],
              [40, 0]
            )}px)`,
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 20px",
              borderRadius: 24,
              background: "rgba(99,102,241,0.12)",
              border: "1px solid rgba(99,102,241,0.25)",
              marginBottom: 20,
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "#22c55e",
                boxShadow: "0 0 8px rgba(34,197,94,0.5)",
              }}
            />
            <span style={{ fontSize: 14, color: "#a5b4fc", letterSpacing: 1.5, fontWeight: 600 }}>
              STEP 1
            </span>
          </div>
          <h1
            style={{
              fontSize: 56,
              fontWeight: 800,
              color: "white",
              textAlign: "center",
              lineHeight: 1.15,
            }}
          >
            Descrivi il tuo{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #60a5fa, #a78bfa)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              business
            </span>
          </h1>
        </div>

        {/* Form fields */}
        <div style={{ width: 650, display: "flex", flexDirection: "column", gap: 20 }}>
          {fields.map((field, i) => {
            const fieldEnter = spring({
              frame: frame - field.delay,
              fps,
              config: { damping: 14, stiffness: 100 },
            });
            const fieldOpacity = interpolate(fieldEnter, [0, 1], [0, 1]);
            const fieldY = interpolate(fieldEnter, [0, 1], [30, 0]);

            return (
              <div
                key={field.label}
                style={{
                  opacity: fieldOpacity,
                  transform: `translateY(${fieldY}px)`,
                }}
              >
                <div
                  style={{
                    fontSize: 12,
                    color: "#64748b",
                    marginBottom: 8,
                    fontWeight: 600,
                    letterSpacing: 1,
                  }}
                >
                  {field.label}
                </div>
                <div
                  style={{
                    padding: "14px 18px",
                    borderRadius: 12,
                    background: "rgba(255,255,255,0.04)",
                    border:
                      i === 0
                        ? "1px solid rgba(99,102,241,0.4)"
                        : "1px solid rgba(255,255,255,0.08)",
                    fontSize: 18,
                    color: "white",
                    minHeight: 50,
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  {i === 0 && (
                    <span>
                      {typeText.slice(0, visibleChars)}
                      <span
                        style={{
                          opacity: cursorOpacity,
                          borderRight: "2px solid #818cf8",
                          marginLeft: 1,
                          display: "inline-block",
                          height: 20,
                        }}
                      />
                    </span>
                  )}
                  {i === 1 && frame > 50 && (
                    <span style={{ color: "#94a3b8" }}>Ristorante</span>
                  )}
                  {i === 2 && frame > 65 && (
                    <span style={{ color: "#94a3b8" }}>Elegante</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 2: "L'AI genera il tuo sito" — progress ring + particles */
const HeroScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Progress ring: 0% to 100% over the scene
  const progress = interpolate(frame, [10, 85], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });

  const percentage = Math.round(progress * 100);

  // Ring SVG
  const ringSize = 200;
  const strokeWidth = 6;
  const r = (ringSize - strokeWidth) / 2;
  const circumference = 2 * Math.PI * r;
  const dashOffset = circumference * (1 - progress);

  // Flash when reaching 100%
  const flashOpacity =
    percentage >= 100
      ? interpolate(frame, [85, 95], [0.6, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 0;

  // Pulsing text opacity
  const pulseOpacity = interpolate(
    Math.sin(frame * 0.12),
    [-1, 1],
    [0.5, 1]
  );

  // Floating particles (deterministic positions)
  const particles = Array.from({ length: 20 }, (_, i) => ({
    x: seededRandom(i * 3 + 1) * 1920,
    y: seededRandom(i * 3 + 2) * 1080,
    size: 3 + seededRandom(i * 3 + 3) * 5,
    speed: 0.5 + seededRandom(i * 7) * 1.5,
    phase: seededRandom(i * 11) * Math.PI * 2,
  }));

  // Title entrance
  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <GradientOrb color="rgba(99,102,241,0.15)" size={600} x="20%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(168,85,247,0.12)" size={500} x="60%" y="50%" phaseOffset={40} />

      {/* Floating particles */}
      {particles.map((p, i) => {
        const px = p.x + Math.sin(frame * 0.03 * p.speed + p.phase) * 40;
        const py = p.y + Math.cos(frame * 0.025 * p.speed + p.phase) * 30;
        const pOpacity = interpolate(
          Math.sin(frame * 0.05 + p.phase),
          [-1, 1],
          [0.1, 0.5]
        );
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: px,
              top: py,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              background:
                i % 3 === 0
                  ? "rgba(99,102,241,0.8)"
                  : i % 3 === 1
                    ? "rgba(168,85,247,0.8)"
                    : "rgba(59,130,246,0.8)",
              opacity: pOpacity,
              filter: `blur(${p.size * 0.3}px)`,
            }}
          />
        );
      })}

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
        }}
      >
        {/* Title */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 20px",
              borderRadius: 24,
              background: "rgba(99,102,241,0.12)",
              border: "1px solid rgba(99,102,241,0.25)",
              marginBottom: 20,
            }}
          >
            <span style={{ fontSize: 14, color: "#a5b4fc", letterSpacing: 1.5, fontWeight: 600 }}>
              STEP 2
            </span>
          </div>
          <h1
            style={{
              fontSize: 56,
              fontWeight: 800,
              color: "white",
              textAlign: "center",
              lineHeight: 1.15,
            }}
          >
            {"L'AI genera il tuo "}

            <span
              style={{
                background: "linear-gradient(135deg, #60a5fa, #a78bfa)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              sito
            </span>
          </h1>
        </div>

        {/* Progress ring */}
        <div style={{ position: "relative" }}>
          <svg
            width={ringSize}
            height={ringSize}
            style={{ transform: "rotate(-90deg)" }}
          >
            <circle
              cx={ringSize / 2}
              cy={ringSize / 2}
              r={r}
              fill="none"
              stroke="rgba(255,255,255,0.06)"
              strokeWidth={strokeWidth}
            />
            <circle
              cx={ringSize / 2}
              cy={ringSize / 2}
              r={r}
              fill="none"
              stroke="url(#progressGrad)"
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
            />
            <defs>
              <linearGradient id="progressGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
          {/* Percentage text centered on ring */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: ringSize,
              height: ringSize,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span
              style={{
                fontSize: 48,
                fontWeight: 800,
                color: "white",
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {percentage}%
            </span>
          </div>
        </div>

        {/* Status text */}
        <div
          style={{
            fontSize: 22,
            color: "#a5b4fc",
            fontWeight: 500,
            opacity: percentage < 100 ? pulseOpacity : 1,
          }}
        >
          {percentage < 100 ? "Generazione in corso..." : "Completato!"}
        </div>
      </div>

      {/* Flash overlay when done */}
      <AbsoluteFill
        style={{
          background: "rgba(99,102,241,0.3)",
          opacity: flashOpacity,
        }}
      />
    </AbsoluteFill>
  );
};

/** Scene 3: "Il risultato" — mock browser with generated site */
const HeroScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const browserEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 16, stiffness: 80 },
  });
  const browserScale = interpolate(browserEnter, [0, 1], [0.88, 1]);
  const browserOpacity = interpolate(browserEnter, [0, 1], [0, 1]);

  // Sections appear with stagger
  const navEnter = spring({ frame: frame - 15, fps, config: { damping: 14 } });
  const heroEnter = spring({ frame: frame - 25, fps, config: { damping: 14 } });
  const btnEnter = spring({ frame: frame - 40, fps, config: { damping: 12 } });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <GradientOrb color="rgba(59,130,246,0.10)" size={600} x="5%" y="10%" phaseOffset={0} />
      <GradientOrb color="rgba(139,92,246,0.08)" size={450} x="70%" y="60%" phaseOffset={50} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 32,
          width: "100%",
          maxWidth: 1100,
        }}
      >
        {/* Title */}
        <div
          style={{
            opacity: interpolate(
              spring({ frame, fps, config: { damping: 15 } }),
              [0, 1],
              [0, 1]
            ),
            transform: `translateY(${interpolate(
              spring({ frame, fps }),
              [0, 1],
              [20, 0]
            )}px)`,
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 20px",
              borderRadius: 24,
              background: "rgba(34,197,94,0.12)",
              border: "1px solid rgba(34,197,94,0.25)",
              marginBottom: 16,
            }}
          >
            <span style={{ fontSize: 14, color: "#86efac", letterSpacing: 1.5, fontWeight: 600 }}>
              STEP 3
            </span>
          </div>
          <h1
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: "white",
              textAlign: "center",
            }}
          >
            Il risultato
          </h1>
        </div>

        {/* Mock browser */}
        <div
          style={{
            transform: `scale(${browserScale})`,
            opacity: browserOpacity,
            borderRadius: 16,
            overflow: "hidden",
            border: "1px solid rgba(255,255,255,0.08)",
            boxShadow:
              "0 25px 80px rgba(0,0,0,0.6), 0 0 60px rgba(99,102,241,0.15)",
            width: "100%",
          }}
        >
          {/* Chrome bar */}
          <div
            style={{
              height: 44,
              background: "#161616",
              display: "flex",
              alignItems: "center",
              padding: "0 16px",
              gap: 8,
            }}
          >
            <div style={{ display: "flex", gap: 6 }}>
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  background: "#ff5f57",
                }}
              />
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  background: "#ffbd2e",
                }}
              />
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  background: "#28c840",
                }}
              />
            </div>
            <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
              <div
                style={{
                  padding: "4px 24px",
                  borderRadius: 8,
                  background: "rgba(255,255,255,0.05)",
                  color: "#94a3b8",
                  fontSize: 13,
                  fontFamily: "monospace",
                }}
              >
                ristorante-da-mario.e-quipe.app
              </div>
            </div>
          </div>

          {/* Site content */}
          <div style={{ background: "#0a0a0a", position: "relative" }}>
            {/* Nav */}
            <div
              style={{
                opacity: interpolate(navEnter, [0, 1], [0, 1]),
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "16px 32px",
                borderBottom: "1px solid rgba(255,255,255,0.06)",
              }}
            >
              <span
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: "white",
                }}
              >
                Da Mario
              </span>
              <div style={{ display: "flex", gap: 24, fontSize: 14, color: "rgba(255,255,255,0.6)" }}>
                <span>Menu</span>
                <span>Chi Siamo</span>
                <span>Galleria</span>
                <span>Contatti</span>
              </div>
            </div>

            {/* Hero section */}
            <div
              style={{
                opacity: interpolate(heroEnter, [0, 1], [0, 1]),
                transform: `translateY(${interpolate(heroEnter, [0, 1], [15, 0])}px)`,
                height: 340,
                background: "linear-gradient(135deg, #1a0a0a, #2a1515, #1a0f0a)",
                padding: "48px 48px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                position: "relative",
                overflow: "hidden",
              }}
            >
              {/* Decorative overlay */}
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  right: 0,
                  width: "40%",
                  height: "100%",
                  background:
                    "radial-gradient(circle at 70% 50%, rgba(220,38,38,0.08), transparent 60%)",
                }}
              />
              <h2
                style={{
                  fontSize: 44,
                  fontWeight: 800,
                  color: "white",
                  marginBottom: 12,
                  lineHeight: 1.2,
                }}
              >
                Il vero gusto
                <br />
                della tradizione
              </h2>
              <p
                style={{
                  fontSize: 18,
                  color: "rgba(255,255,255,0.6)",
                  marginBottom: 24,
                  maxWidth: 400,
                }}
              >
                Cucina romana autentica dal 1985
              </p>
              <div
                style={{
                  opacity: interpolate(btnEnter, [0, 1], [0, 1]),
                  transform: `scale(${interpolate(btnEnter, [0, 1], [0.8, 1])})`,
                  display: "inline-flex",
                  padding: "14px 32px",
                  borderRadius: 10,
                  background: "#dc2626",
                  color: "white",
                  fontSize: 16,
                  fontWeight: 700,
                  width: "fit-content",
                  boxShadow: "0 8px 30px rgba(220,38,38,0.3)",
                }}
              >
                Prenota un Tavolo
              </div>
            </div>

            {/* Section tabs */}
            <div
              style={{
                display: "flex",
                gap: 1,
                background: "rgba(255,255,255,0.02)",
              }}
            >
              {["Chi Siamo", "Il Menu", "Galleria", "Recensioni", "Contatti"].map(
                (s, i) => {
                  const secEnter = spring({
                    frame: frame - (50 + i * 5),
                    fps,
                    config: { damping: 14 },
                  });
                  return (
                    <div
                      key={s}
                      style={{
                        flex: 1,
                        padding: "14px 8px",
                        textAlign: "center",
                        fontSize: 13,
                        color: "#64748b",
                        borderRight: "1px solid rgba(255,255,255,0.04)",
                        opacity: interpolate(secEnter, [0, 1], [0, 1]),
                      }}
                    >
                      {s}
                    </div>
                  );
                }
              )}
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 4: "Pubblica con 1 click" — checkmark, URL, confetti */
const HeroScene4 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Browser shrink to left
  const browserScale = interpolate(frame, [0, 25], [1, 0.55], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });
  const browserX = interpolate(frame, [0, 25], [0, -320], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });

  // Right side elements
  const checkEnter = spring({
    frame: frame - 20,
    fps,
    config: { damping: 10, stiffness: 120 },
  });
  const textEnter = spring({
    frame: frame - 30,
    fps,
    config: { damping: 14 },
  });
  const urlEnter = spring({
    frame: frame - 40,
    fps,
    config: { damping: 14 },
  });
  const badgeEnter = spring({
    frame: frame - 60,
    fps,
    config: { damping: 14 },
  });

  // Confetti particles
  const confettiColors = [
    "#3b82f6",
    "#8b5cf6",
    "#22c55e",
    "#f59e0b",
    "#ec4899",
    "#06b6d4",
  ];
  const confetti = Array.from({ length: 40 }, (_, i) => ({
    x: seededRandom(i * 5 + 1) * 1920,
    startY: -20 - seededRandom(i * 5 + 2) * 200,
    speed: 2 + seededRandom(i * 5 + 3) * 4,
    size: 4 + seededRandom(i * 5 + 4) * 8,
    color: confettiColors[Math.floor(seededRandom(i * 5 + 5) * confettiColors.length)],
    wobble: seededRandom(i * 5 + 6) * Math.PI * 2,
    rotation: seededRandom(i * 5 + 7) * 360,
  }));

  const confettiProgress = interpolate(frame, [25, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
        fontFamily: FONT,
        overflow: "hidden",
      }}
    >
      <GradientOrb color="rgba(34,197,94,0.12)" size={500} x="50%" y="30%" phaseOffset={0} />
      <GradientOrb color="rgba(59,130,246,0.08)" size={400} x="20%" y="60%" phaseOffset={70} />

      {/* Confetti */}
      {confettiProgress > 0 &&
        confetti.map((c, i) => {
          const y =
            c.startY + confettiProgress * (1080 + 400) * (c.speed / 6);
          const wobbleX = Math.sin(confettiProgress * 10 + c.wobble) * 30;
          const rot = c.rotation + confettiProgress * 720;
          const opacity = interpolate(y, [800, 1100], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: c.x + wobbleX,
                top: y,
                width: c.size,
                height: c.size * 0.6,
                borderRadius: 2,
                background: c.color,
                transform: `rotate(${rot}deg)`,
                opacity: opacity * 0.8,
              }}
            />
          );
        })}

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          width: "100%",
          height: "100%",
          padding: 60,
          gap: 60,
        }}
      >
        {/* Left: mini browser */}
        <div
          style={{
            transform: `scale(${browserScale}) translateX(${browserX}px)`,
            borderRadius: 14,
            overflow: "hidden",
            border: "1px solid rgba(255,255,255,0.08)",
            boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
            width: 700,
            flexShrink: 0,
          }}
        >
          <div
            style={{
              height: 36,
              background: "#161616",
              display: "flex",
              alignItems: "center",
              padding: "0 12px",
              gap: 6,
            }}
          >
            <div style={{ display: "flex", gap: 5 }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ff5f57" }} />
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ffbd2e" }} />
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#28c840" }} />
            </div>
            <div style={{ flex: 1, textAlign: "center", fontSize: 11, color: "#64748b", fontFamily: "monospace" }}>
              ristorante-da-mario.e-quipe.app
            </div>
          </div>
          <div
            style={{
              height: 320,
              background: "linear-gradient(135deg, #1a0a0a, #2a1515)",
              padding: 24,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <h3 style={{ fontSize: 22, fontWeight: 800, color: "white", marginBottom: 8 }}>
              Il vero gusto della tradizione
            </h3>
            <p style={{ fontSize: 12, color: "rgba(255,255,255,0.6)", marginBottom: 16 }}>
              Cucina romana autentica dal 1985
            </p>
            <div
              style={{
                padding: "8px 18px",
                borderRadius: 8,
                background: "#dc2626",
                color: "white",
                fontSize: 12,
                fontWeight: 600,
                width: "fit-content",
              }}
            >
              Prenota un Tavolo
            </div>
          </div>
        </div>

        {/* Right: publish confirmation */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 24,
          }}
        >
          {/* Green checkmark */}
          <div
            style={{
              opacity: interpolate(checkEnter, [0, 1], [0, 1]),
              transform: `scale(${interpolate(checkEnter, [0, 1], [0.3, 1])})`,
            }}
          >
            <div
              style={{
                width: 120,
                height: 120,
                borderRadius: "50%",
                background: "linear-gradient(135deg, #22c55e, #16a34a)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 15px 50px rgba(34,197,94,0.3)",
              }}
            >
              <svg width={60} height={60} viewBox="0 0 60 60">
                <path
                  d="M15 30 L25 42 L45 18"
                  fill="none"
                  stroke="white"
                  strokeWidth={5}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray={60}
                  strokeDashoffset={interpolate(checkEnter, [0, 1], [60, 0])}
                />
              </svg>
            </div>
          </div>

          {/* Published text */}
          <div
            style={{
              opacity: interpolate(textEnter, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(textEnter, [0, 1], [20, 0])}px)`,
            }}
          >
            <h2
              style={{
                fontSize: 44,
                fontWeight: 800,
                color: "white",
                textAlign: "center",
              }}
            >
              Sito Pubblicato!
            </h2>
          </div>

          {/* URL */}
          <div
            style={{
              opacity: interpolate(urlEnter, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(urlEnter, [0, 1], [15, 0])}px)`,
              padding: "12px 28px",
              borderRadius: 12,
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <span
              style={{
                fontSize: 18,
                color: "#94a3b8",
                fontFamily: "monospace",
              }}
            >
              https://ristorante-da-mario.e-quipe.app
            </span>
          </div>

          {/* Powered by badge */}
          <div
            style={{
              opacity: interpolate(badgeEnter, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(badgeEnter, [0, 1], [10, 0])}px)`,
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "10px 20px",
              borderRadius: 20,
              background: "rgba(99,102,241,0.08)",
              border: "1px solid rgba(99,102,241,0.2)",
            }}
          >
            <span style={{ fontSize: 14, color: "#a5b4fc", fontWeight: 600 }}>
              Powered by E-quipe AI
            </span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const HeroVideoComposition = () => {
  return (
    <TransitionSeries>
      {/* Scene 1: Describe your business (frames 0-90) */}
      <TransitionSeries.Sequence durationInFrames={90}>
        <HeroScene1 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      {/* Scene 2: AI generates (frames ~75-180) */}
      <TransitionSeries.Sequence durationInFrames={105}>
        <HeroScene2 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      {/* Scene 3: The result (frames ~165-270) */}
      <TransitionSeries.Sequence durationInFrames={105}>
        <HeroScene3 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={wipe({ direction: "from-left" })}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      {/* Scene 4: Publish (frames ~255-360) */}
      <TransitionSeries.Sequence durationInFrames={105}>
        <HeroScene4 />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};

export const HERO_VIDEO_CONFIG = {
  id: "HeroVideo",
  fps: 30,
  durationInFrames: 360, // 12 seconds
  width: 1920,
  height: 1080,
};

/* ------------------------------------------------------------------ */
/*  ADS VIDEO COMPOSITION — 10 seconds, 300 frames                    */
/* ------------------------------------------------------------------ */

/** Scene 1: Dashboard overview with animated bar chart */
const AdsScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  // Bar chart data
  const barData = [
    { label: "Lun", value: 65 },
    { label: "Mar", value: 82 },
    { label: "Mer", value: 55 },
    { label: "Gio", value: 95 },
    { label: "Ven", value: 120 },
  ];
  const maxValue = 130;

  // Y-axis labels
  const yLabels = [0, 30, 60, 90, 120];

  return (
    <AbsoluteFill
      style={{
        background: "#0a0a0a",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Subtle grid pattern */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <GradientOrb color="rgba(59,130,246,0.10)" size={500} x="10%" y="15%" phaseOffset={0} />
      <GradientOrb color="rgba(139,92,246,0.08)" size={400} x="70%" y="55%" phaseOffset={50} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
          width: "100%",
          maxWidth: 1000,
        }}
      >
        {/* Title */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [30, 0])}px)`,
            textAlign: "center",
          }}
        >
          <div
            style={{
              display: "inline-flex",
              padding: "6px 16px",
              borderRadius: 20,
              background: "rgba(34,197,94,0.1)",
              border: "1px solid rgba(34,197,94,0.2)",
              color: "#86efac",
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: 1.5,
              marginBottom: 16,
            }}
          >
            DASHBOARD
          </div>
          <h2
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: "white",
              lineHeight: 1.2,
            }}
          >
            Conversioni Mensili
          </h2>
        </div>

        {/* Chart area */}
        <div
          style={{
            width: "100%",
            height: 380,
            borderRadius: 16,
            background: "rgba(255,255,255,0.02)",
            border: "1px solid rgba(255,255,255,0.06)",
            padding: "32px 48px 48px",
            display: "flex",
            position: "relative",
          }}
        >
          {/* Y-axis labels */}
          <div
            style={{
              width: 40,
              display: "flex",
              flexDirection: "column-reverse",
              justifyContent: "space-between",
              paddingBottom: 32,
              marginRight: 16,
            }}
          >
            {yLabels.map((label) => (
              <span
                key={label}
                style={{
                  fontSize: 12,
                  color: "#475569",
                  textAlign: "right",
                }}
              >
                {label}
              </span>
            ))}
          </div>

          {/* Bars */}
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "flex-end",
              gap: 32,
              paddingBottom: 32,
              borderBottom: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            {barData.map((bar, i) => {
              const barEnter = spring({
                frame: frame - (20 + i * 5),
                fps,
                config: { damping: 12, stiffness: 80 },
              });
              const barHeight = (bar.value / maxValue) * 260;

              return (
                <div
                  key={bar.label}
                  style={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 12,
                  }}
                >
                  {/* Value label above bar */}
                  <span
                    style={{
                      fontSize: 14,
                      fontWeight: 700,
                      color: "white",
                      opacity: interpolate(barEnter, [0, 1], [0, 1]),
                    }}
                  >
                    {bar.value}
                  </span>
                  {/* Bar */}
                  <div
                    style={{
                      width: "100%",
                      maxWidth: 80,
                      height: barHeight * interpolate(barEnter, [0, 1], [0, 1]),
                      borderRadius: "10px 10px 4px 4px",
                      background: `linear-gradient(180deg, #3b82f6, #6366f1)`,
                      boxShadow: "0 4px 20px rgba(59,130,246,0.2)",
                    }}
                  />
                  {/* X label */}
                  <span
                    style={{
                      fontSize: 14,
                      color: "#64748b",
                      fontWeight: 500,
                    }}
                  >
                    {bar.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 2: Campaign metrics with counters and line chart */
const AdsScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Metrics with counter animation
  const metrics = [
    { label: "Impressioni", target: 45230, color: "#3b82f6", delay: 10 },
    { label: "Click", target: 2847, color: "#8b5cf6", delay: 20 },
    { label: "Conversioni", target: 312, color: "#22c55e", delay: 30 },
  ];

  // SVG line chart path
  const chartPath =
    "M 0 120 C 40 110, 80 95, 120 85 C 160 75, 200 60, 240 70 C 280 80, 320 45, 360 35 C 400 25, 440 40, 480 20 C 520 10, 560 15, 600 5";
  const chartProgress = interpolate(frame, [50, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });

  // evolvePath returns { strokeDasharray, strokeDashoffset } for progressive reveal
  const evolvedStyle = evolvePath(chartProgress, chartPath);

  return (
    <AbsoluteFill
      style={{
        background: "#0a0a0a",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Grid pattern */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <GradientOrb color="rgba(139,92,246,0.10)" size={500} x="15%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(59,130,246,0.08)" size={400} x="65%" y="50%" phaseOffset={40} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          gap: 40,
          width: "100%",
          maxWidth: 1000,
        }}
      >
        {/* Metric cards */}
        <div style={{ display: "flex", gap: 24 }}>
          {metrics.map((m, i) => {
            const cardEnter = spring({
              frame: frame - m.delay,
              fps,
              config: { damping: 14, stiffness: 100 },
            });
            const counterProgress = interpolate(
              frame,
              [m.delay + 5, m.delay + 50],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            const currentValue = Math.round(counterProgress * m.target);

            // Format number with dots for thousands
            const formatted = currentValue.toLocaleString("it-IT");

            return (
              <div
                key={m.label}
                style={{
                  flex: 1,
                  padding: "28px 24px",
                  borderRadius: 16,
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  opacity: interpolate(cardEnter, [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(cardEnter, [0, 1], [30, 0])}px) scale(${interpolate(cardEnter, [0, 1], [0.95, 1])})`,
                }}
              >
                {/* Color indicator circle */}
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 12,
                    background: `${m.color}15`,
                    border: `1px solid ${m.color}30`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: 16,
                  }}
                >
                  <div
                    style={{
                      width: 12,
                      height: 12,
                      borderRadius: "50%",
                      background: m.color,
                      boxShadow: `0 0 10px ${m.color}50`,
                    }}
                  />
                </div>
                <div
                  style={{
                    fontSize: 14,
                    color: "#64748b",
                    marginBottom: 8,
                    fontWeight: 500,
                  }}
                >
                  {m.label}
                </div>
                <div
                  style={{
                    fontSize: 36,
                    fontWeight: 800,
                    color: "white",
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {formatted}
                </div>
              </div>
            );
          })}
        </div>

        {/* Line chart */}
        <div
          style={{
            width: "100%",
            height: 180,
            borderRadius: 16,
            background: "rgba(255,255,255,0.02)",
            border: "1px solid rgba(255,255,255,0.06)",
            padding: "24px 32px",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              fontSize: 14,
              color: "#64748b",
              fontWeight: 600,
              marginBottom: 12,
            }}
          >
            Andamento Conversioni
          </div>
          <svg
            viewBox="0 0 600 130"
            style={{
              width: "100%",
              height: 110,
            }}
          >
            {/* Grid lines */}
            {[30, 60, 90, 120].map((y) => (
              <line
                key={y}
                x1={0}
                y1={y}
                x2={600}
                y2={y}
                stroke="rgba(255,255,255,0.04)"
                strokeWidth={1}
              />
            ))}
            {/* Gradient fill under curve */}
            <defs>
              <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.2" />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
              </linearGradient>
            </defs>
            {/* The animated line */}
            <path
              d={chartPath}
              fill="none"
              stroke="#8b5cf6"
              strokeWidth={3}
              strokeLinecap="round"
              strokeDasharray={evolvedStyle.strokeDasharray}
              strokeDashoffset={evolvedStyle.strokeDashoffset}
            />
          </svg>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Scene 3: ROI + CTA with badges */
const AdsScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ROI number entrance
  const roiEnter = spring({
    frame: frame - 5,
    fps,
    config: { damping: 10, stiffness: 100 },
  });

  // Counter for ROI percentage
  const roiProgress = interpolate(frame, [5, 50], [0, 340], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });
  const roiValue = Math.round(roiProgress);

  const subtitleEnter = spring({
    frame: frame - 25,
    fps,
    config: { damping: 14 },
  });

  const badges = [
    { label: "Meta Ads", color: "#1877f2" },
    { label: "Google Ads", color: "#4285f4" },
    { label: "Contenuti AI", color: "#8b5cf6" },
  ];

  const brandEnter = spring({
    frame: frame - 70,
    fps,
    config: { damping: 14 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "#0a0a0a",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Grid pattern */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <GradientOrb color="rgba(34,197,94,0.12)" size={500} x="40%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(99,102,241,0.10)" size={400} x="20%" y="60%" phaseOffset={60} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 32,
        }}
      >
        {/* Big ROI number */}
        <div
          style={{
            opacity: interpolate(roiEnter, [0, 1], [0, 1]),
            transform: `scale(${interpolate(roiEnter, [0, 1], [0.6, 1])})`,
            textAlign: "center",
          }}
        >
          <span
            style={{
              fontSize: 120,
              fontWeight: 900,
              background: "linear-gradient(135deg, #22c55e, #3b82f6, #8b5cf6)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              lineHeight: 1,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            +{roiValue}%
          </span>
          <div
            style={{
              fontSize: 32,
              fontWeight: 700,
              color: "white",
              marginTop: 8,
            }}
          >
            ROI
          </div>
        </div>

        {/* Subtitle */}
        <div
          style={{
            opacity: interpolate(subtitleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(subtitleEnter, [0, 1], [20, 0])}px)`,
            fontSize: 24,
            color: "#94a3b8",
            textAlign: "center",
            maxWidth: 600,
            lineHeight: 1.5,
          }}
        >
          Gestito dagli esperti di{" "}
          <span style={{ color: "white", fontWeight: 700 }}>E-quipe</span>
        </div>

        {/* Badges */}
        <div style={{ display: "flex", gap: 20, marginTop: 16 }}>
          {badges.map((badge, i) => {
            const badgeEnter = spring({
              frame: frame - (40 + i * 10),
              fps,
              config: { damping: 14 },
            });
            return (
              <div
                key={badge.label}
                style={{
                  opacity: interpolate(badgeEnter, [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(badgeEnter, [0, 1], [20, 0])}px)`,
                  padding: "12px 28px",
                  borderRadius: 12,
                  background: `${badge.color}15`,
                  border: `1px solid ${badge.color}30`,
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                }}
              >
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    background: badge.color,
                    boxShadow: `0 0 8px ${badge.color}50`,
                  }}
                />
                <span
                  style={{
                    fontSize: 16,
                    fontWeight: 600,
                    color: "white",
                  }}
                >
                  {badge.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Brand with glow */}
        <div
          style={{
            opacity: interpolate(brandEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(brandEnter, [0, 1], [15, 0])}px)`,
            marginTop: 32,
            display: "flex",
            alignItems: "center",
            gap: 12,
            padding: "14px 32px",
            borderRadius: 20,
            background: "rgba(99,102,241,0.08)",
            border: "1px solid rgba(99,102,241,0.2)",
            boxShadow: `0 0 ${interpolate(
              Math.sin(frame * 0.08),
              [-1, 1],
              [20, 40]
            )}px rgba(99,102,241,0.15)`,
          }}
        >
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 16,
              fontWeight: 800,
              color: "white",
            }}
          >
            E
          </div>
          <span
            style={{
              fontSize: 20,
              fontWeight: 700,
              background: "linear-gradient(135deg, #60a5fa, #a78bfa)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            E-quipe
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const AdsVideoComposition = () => {
  return (
    <TransitionSeries>
      {/* Scene 1: Dashboard overview with bar chart */}
      <TransitionSeries.Sequence durationInFrames={100}>
        <AdsScene1 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      {/* Scene 2: Campaign metrics with counters */}
      <TransitionSeries.Sequence durationInFrames={115}>
        <AdsScene2 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-bottom" })}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      {/* Scene 3: ROI + CTA */}
      <TransitionSeries.Sequence durationInFrames={115}>
        <AdsScene3 />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};

export const ADS_VIDEO_CONFIG = {
  id: "AdsVideo",
  fps: 30,
  durationInFrames: 300, // 10 seconds
  width: 1920,
  height: 1080,
};

/* ------------------------------------------------------------------ */
/*  EXPORTS (backward compatible)                                      */
/* ------------------------------------------------------------------ */

export const DemoVideoComposition = HeroVideoComposition;
export const DEMO_VIDEO_CONFIG = HERO_VIDEO_CONFIG;
