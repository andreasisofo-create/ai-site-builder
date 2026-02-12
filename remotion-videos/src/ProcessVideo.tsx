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

const { fontFamily } = loadFont();
const FONT = `${fontFamily}, -apple-system, BlinkMacSystemFont, sans-serif`;

function seededRandom(seed: number): number {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

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

/* ------------------------------------------------------------------ */
/*  SCENE 1: Scegli un Template — Card carousel with perspective tilt  */
/* ------------------------------------------------------------------ */

const ProcessScene1 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });

  const cards = [
    { name: "Restaurant Elegant", color: "#dc2626", category: "Ristorante" },
    { name: "SaaS Gradient", color: "#3b82f6", category: "SaaS" },
    { name: "Portfolio Gallery", color: "#8b5cf6", category: "Portfolio" },
    { name: "Business Corporate", color: "#0ea5e9", category: "Business" },
  ];

  // Carousel sliding effect
  const carouselShift = interpolate(frame, [20, 70], [0, -600], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });

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
      <GradientOrb color="rgba(139,92,246,0.12)" size={500} x="10%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(59,130,246,0.10)" size={400} x="70%" y="50%" phaseOffset={50} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 48,
          width: "100%",
          maxWidth: 1200,
        }}
      >
        {/* Step badge + Title */}
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
              alignItems: "center",
              gap: 8,
              padding: "8px 20px",
              borderRadius: 24,
              background: "rgba(99,102,241,0.12)",
              border: "1px solid rgba(99,102,241,0.25)",
              marginBottom: 20,
            }}
          >
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#3b82f6", boxShadow: "0 0 8px rgba(59,130,246,0.5)" }} />
            <span style={{ fontSize: 14, color: "#a5b4fc", letterSpacing: 1.5, fontWeight: 600 }}>STEP 1</span>
          </div>
          <h2 style={{ fontSize: 52, fontWeight: 800, color: "white", lineHeight: 1.15 }}>
            Scegli il tuo{" "}
            <span style={{ background: "linear-gradient(135deg, #60a5fa, #a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              template
            </span>
          </h2>
        </div>

        {/* Carousel */}
        <div style={{ width: "100%", overflow: "hidden", position: "relative" }}>
          <div
            style={{
              display: "flex",
              gap: 24,
              transform: `translateX(${200 + carouselShift}px)`,
              perspective: 1000,
            }}
          >
            {cards.map((card, i) => {
              const cardEnter = spring({
                frame: frame - (8 + i * 6),
                fps,
                config: { damping: 14, stiffness: 90 },
              });
              // Perspective tilt based on position
              const tiltDeg = interpolate(
                Math.sin(frame * 0.04 + i * 1.5),
                [-1, 1],
                [-4, 4]
              );

              return (
                <div
                  key={card.name}
                  style={{
                    minWidth: 280,
                    opacity: interpolate(cardEnter, [0, 1], [0, 1]),
                    transform: `translateY(${interpolate(cardEnter, [0, 1], [50, 0])}px) perspective(800px) rotateY(${tiltDeg}deg)`,
                    borderRadius: 16,
                    overflow: "hidden",
                    border: "1px solid rgba(255,255,255,0.08)",
                    background: "rgba(255,255,255,0.03)",
                    boxShadow: "0 20px 50px rgba(0,0,0,0.3)",
                  }}
                >
                  {/* Preview area */}
                  <div
                    style={{
                      height: 200,
                      background: `linear-gradient(135deg, ${card.color}20, ${card.color}08)`,
                      padding: 20,
                      display: "flex",
                      flexDirection: "column",
                      gap: 8,
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <div style={{ width: 50, height: 8, borderRadius: 4, background: card.color, opacity: 0.5 }} />
                      <div style={{ display: "flex", gap: 6 }}>
                        {[1, 2, 3].map((n) => (
                          <div key={n} style={{ width: 20, height: 5, borderRadius: 3, background: "rgba(255,255,255,0.12)" }} />
                        ))}
                      </div>
                    </div>
                    <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", gap: 6 }}>
                      <div style={{ width: "80%", height: 12, borderRadius: 6, background: "rgba(255,255,255,0.18)" }} />
                      <div style={{ width: "55%", height: 8, borderRadius: 4, background: "rgba(255,255,255,0.1)" }} />
                      <div style={{ width: 60, height: 16, borderRadius: 5, background: card.color, opacity: 0.7, marginTop: 8 }} />
                    </div>
                  </div>
                  {/* Footer */}
                  <div style={{ padding: "14px 16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div>
                      <p style={{ fontSize: 13, fontWeight: 600, color: "white", marginBottom: 2 }}>{card.name}</p>
                      <p style={{ fontSize: 11, color: "#64748b" }}>{card.category}</p>
                    </div>
                    <div style={{ width: 10, height: 10, borderRadius: "50%", background: card.color }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 2: Descrivi il Business — Form with typewriter               */
/* ------------------------------------------------------------------ */

const ProcessScene2 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  // Form fields with typewriter
  const fields = [
    { label: "NOME ATTIVITA", value: "Trattoria Bella Vista", delay: 10, typeStart: 15, typeEnd: 50 },
    { label: "SETTORE", value: "Ristorante Italiano", delay: 25, typeStart: 35, typeEnd: 55 },
    { label: "STILE DESIDERATO", value: "Elegante e Moderno", delay: 40, typeStart: 50, typeEnd: 70 },
    { label: "DESCRIZIONE", value: "Cucina tradizionale con un tocco contemporaneo", delay: 55, typeStart: 60, typeEnd: 85 },
  ];

  // Progress dots
  const progressSteps = 3;
  const currentStep = interpolate(frame, [0, 90], [0, progressSteps], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

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
      <GradientOrb color="rgba(99,102,241,0.12)" size={500} x="20%" y="15%" phaseOffset={0} />
      <GradientOrb color="rgba(168,85,247,0.10)" size={400} x="65%" y="55%" phaseOffset={40} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 36,
          width: "100%",
          maxWidth: 700,
        }}
      >
        {/* Step badge + Title */}
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
              alignItems: "center",
              gap: 8,
              padding: "8px 20px",
              borderRadius: 24,
              background: "rgba(99,102,241,0.12)",
              border: "1px solid rgba(99,102,241,0.25)",
              marginBottom: 20,
            }}
          >
            <span style={{ fontSize: 14, color: "#a5b4fc", letterSpacing: 1.5, fontWeight: 600 }}>STEP 2</span>
          </div>
          <h2 style={{ fontSize: 48, fontWeight: 800, color: "white", lineHeight: 1.15 }}>
            Descrivi il tuo{" "}
            <span style={{ background: "linear-gradient(135deg, #60a5fa, #a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              business
            </span>
          </h2>
        </div>

        {/* Progress dots */}
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          {Array.from({ length: progressSteps }, (_, i) => {
            const active = currentStep >= i + 1;
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div
                  style={{
                    width: 12,
                    height: 12,
                    borderRadius: "50%",
                    background: active ? "linear-gradient(135deg, #3b82f6, #8b5cf6)" : "rgba(255,255,255,0.1)",
                    border: active ? "none" : "1px solid rgba(255,255,255,0.15)",
                    transition: "background 0.3s",
                    boxShadow: active ? "0 0 10px rgba(99,102,241,0.4)" : "none",
                  }}
                />
                {i < progressSteps - 1 && (
                  <div
                    style={{
                      width: 40,
                      height: 2,
                      borderRadius: 1,
                      background: currentStep > i + 1 ? "rgba(99,102,241,0.4)" : "rgba(255,255,255,0.06)",
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>

        {/* Form fields */}
        <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: 16 }}>
          {fields.map((field) => {
            const fieldEnter = spring({
              frame: frame - field.delay,
              fps,
              config: { damping: 14, stiffness: 100 },
            });
            const typeProgress = interpolate(
              frame,
              [field.typeStart, field.typeEnd],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            const visibleChars = Math.floor(typeProgress * field.value.length);
            const cursorOpacity = visibleChars < field.value.length && frame > field.typeStart
              ? (Math.sin(frame * 0.3) > 0 ? 1 : 0)
              : 0;

            return (
              <div
                key={field.label}
                style={{
                  opacity: interpolate(fieldEnter, [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(fieldEnter, [0, 1], [20, 0])}px)`,
                }}
              >
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 6, fontWeight: 600, letterSpacing: 1 }}>
                  {field.label}
                </div>
                <div
                  style={{
                    padding: "12px 16px",
                    borderRadius: 10,
                    background: "rgba(255,255,255,0.04)",
                    border: frame >= field.typeStart && visibleChars < field.value.length
                      ? "1px solid rgba(99,102,241,0.4)"
                      : "1px solid rgba(255,255,255,0.08)",
                    fontSize: 16,
                    color: "white",
                    minHeight: 44,
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  {frame >= field.typeStart && (
                    <span>
                      {field.value.slice(0, visibleChars)}
                      <span
                        style={{
                          opacity: cursorOpacity,
                          borderRight: "2px solid #818cf8",
                          marginLeft: 1,
                          display: "inline-block",
                          height: 18,
                        }}
                      />
                    </span>
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

/* ------------------------------------------------------------------ */
/*  SCENE 3: L'AI Lavora — Neural network with SVG path animations     */
/* ------------------------------------------------------------------ */

const ProcessScene3 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  // Neural network node positions (3 layers)
  const layers = [
    // Input layer
    [
      { x: 200, y: 250 },
      { x: 200, y: 400 },
      { x: 200, y: 550 },
      { x: 200, y: 700 },
    ],
    // Hidden layer
    [
      { x: 600, y: 300 },
      { x: 600, y: 475 },
      { x: 600, y: 650 },
    ],
    // Output layer
    [
      { x: 1000, y: 375 },
      { x: 1000, y: 575 },
    ],
  ];

  // Connection paths between layers
  const connections: { path: string; delay: number }[] = [];
  layers.forEach((layer, li) => {
    if (li < layers.length - 1) {
      layer.forEach((node, ni) => {
        layers[li + 1].forEach((next, nni) => {
          connections.push({
            path: `M ${node.x} ${node.y} C ${(node.x + next.x) / 2} ${node.y}, ${(node.x + next.x) / 2} ${next.y}, ${next.x} ${next.y}`,
            delay: li * 20 + ni * 5 + nni * 3,
          });
        });
      });
    }
  });

  // Pulsing effect for data flow
  const pulsePhase = frame * 0.06;

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
      <GradientOrb color="rgba(99,102,241,0.15)" size={600} x="30%" y="30%" phaseOffset={0} />
      <GradientOrb color="rgba(168,85,247,0.12)" size={500} x="60%" y="50%" phaseOffset={40} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          width: "100%",
          height: "100%",
        }}
      >
        {/* Title overlay at top */}
        <div
          style={{
            position: "absolute",
            top: 60,
            left: 0,
            right: 0,
            textAlign: "center",
            zIndex: 2,
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
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
              marginBottom: 16,
            }}
          >
            <span style={{ fontSize: 14, color: "#a5b4fc", letterSpacing: 1.5, fontWeight: 600 }}>STEP 3</span>
          </div>
          <h2 style={{ fontSize: 48, fontWeight: 800, color: "white" }}>
            {"L'AI "}
            <span style={{ background: "linear-gradient(135deg, #60a5fa, #a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              lavora
            </span>
          </h2>
        </div>

        {/* Neural network SVG */}
        <svg
          viewBox="0 0 1200 900"
          style={{
            width: "100%",
            height: "100%",
            position: "absolute",
            top: 0,
            left: 0,
          }}
        >
          <defs>
            <linearGradient id="connectionGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="50%" stopColor="#8b5cf6" />
              <stop offset="100%" stopColor="#a855f7" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Connection paths with evolvePath animation */}
          {connections.map((conn, i) => {
            const pathProgress = interpolate(
              frame,
              [conn.delay, conn.delay + 35],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            const evolved = evolvePath(pathProgress, conn.path);
            const pulseOpacity = interpolate(
              Math.sin(pulsePhase + i * 0.3),
              [-1, 1],
              [0.15, 0.5]
            );

            return (
              <path
                key={i}
                d={conn.path}
                fill="none"
                stroke="url(#connectionGrad)"
                strokeWidth={2}
                opacity={pulseOpacity}
                strokeDasharray={evolved.strokeDasharray}
                strokeDashoffset={evolved.strokeDashoffset}
              />
            );
          })}

          {/* Nodes */}
          {layers.map((layer, li) =>
            layer.map((node, ni) => {
              const nodeEnter = spring({
                frame: frame - (li * 15 + ni * 5),
                fps,
                config: { damping: 12, stiffness: 100 },
              });
              const nodeScale = interpolate(nodeEnter, [0, 1], [0, 1]);
              const glowIntensity = interpolate(
                Math.sin(pulsePhase + li * 2 + ni),
                [-1, 1],
                [0.3, 1]
              );
              const nodeColor = li === 0 ? "#3b82f6" : li === 1 ? "#8b5cf6" : "#a855f7";

              return (
                <g key={`${li}-${ni}`} filter="url(#glow)">
                  {/* Outer glow */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={22 * nodeScale}
                    fill={`${nodeColor}20`}
                    opacity={glowIntensity}
                  />
                  {/* Node circle */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={14 * nodeScale}
                    fill="#0a0a0a"
                    stroke={nodeColor}
                    strokeWidth={2}
                    opacity={nodeScale}
                  />
                  {/* Center dot */}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={5 * nodeScale}
                    fill={nodeColor}
                    opacity={glowIntensity}
                  />
                </g>
              );
            })
          )}

          {/* Layer labels */}
          <text x={200} y={820} textAnchor="middle" fill="#64748b" fontSize={14} fontFamily={FONT} fontWeight={600}>
            INPUT
          </text>
          <text x={600} y={820} textAnchor="middle" fill="#64748b" fontSize={14} fontFamily={FONT} fontWeight={600}>
            AI ENGINE
          </text>
          <text x={1000} y={820} textAnchor="middle" fill="#64748b" fontSize={14} fontFamily={FONT} fontWeight={600}>
            OUTPUT
          </text>
        </svg>
      </div>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/*  SCENE 4: Sito Pronto — Before/after with celebration               */
/* ------------------------------------------------------------------ */

const ProcessScene4 = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15 } });

  // Before -> After transition
  const revealProgress = interpolate(frame, [20, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });

  // Celebration confetti
  const confettiColors = ["#3b82f6", "#8b5cf6", "#22c55e", "#f59e0b", "#ec4899", "#06b6d4"];
  const confetti = Array.from({ length: 30 }, (_, i) => ({
    x: seededRandom(i * 5 + 1) * 1920,
    startY: -20 - seededRandom(i * 5 + 2) * 200,
    speed: 2 + seededRandom(i * 5 + 3) * 4,
    size: 4 + seededRandom(i * 5 + 4) * 7,
    color: confettiColors[Math.floor(seededRandom(i * 5 + 5) * confettiColors.length)],
    wobble: seededRandom(i * 5 + 6) * Math.PI * 2,
    rotation: seededRandom(i * 5 + 7) * 360,
  }));

  const confettiProgress = interpolate(frame, [50, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // "Sito Pronto!" badge
  const badgeEnter = spring({
    frame: frame - 50,
    fps,
    config: { damping: 10, stiffness: 120 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
      }}
    >
      <GradientOrb color="rgba(34,197,94,0.12)" size={500} x="40%" y="25%" phaseOffset={0} />
      <GradientOrb color="rgba(59,130,246,0.08)" size={400} x="15%" y="60%" phaseOffset={60} />

      {/* Confetti */}
      {confettiProgress > 0 &&
        confetti.map((c, i) => {
          const y = c.startY + confettiProgress * (1080 + 400) * (c.speed / 6);
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
          flexDirection: "column",
          alignItems: "center",
          gap: 32,
        }}
      >
        {/* Title */}
        <div
          style={{
            opacity: interpolate(titleEnter, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(titleEnter, [0, 1], [20, 0])}px)`,
            textAlign: "center",
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
            <span style={{ fontSize: 14, color: "#86efac", letterSpacing: 1.5, fontWeight: 600 }}>STEP 4</span>
          </div>
          <h2 style={{ fontSize: 48, fontWeight: 800, color: "white" }}>
            Il tuo sito e{" "}
            <span style={{ background: "linear-gradient(135deg, #22c55e, #3b82f6)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              pronto!
            </span>
          </h2>
        </div>

        {/* Before / After */}
        <div style={{ display: "flex", gap: 32, alignItems: "center" }}>
          {/* Before: blank canvas */}
          <div
            style={{
              width: 400,
              borderRadius: 14,
              overflow: "hidden",
              border: "1px solid rgba(255,255,255,0.06)",
              opacity: interpolate(revealProgress, [0, 0.5], [1, 0.3], { extrapolateRight: "clamp" }),
              transform: `scale(${interpolate(revealProgress, [0, 1], [1, 0.85])})`,
            }}
          >
            <div style={{ height: 30, background: "#161616", display: "flex", alignItems: "center", padding: "0 10px", gap: 5 }}>
              <div style={{ display: "flex", gap: 4 }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#ff5f57" }} />
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#ffbd2e" }} />
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#28c840" }} />
              </div>
            </div>
            <div
              style={{
                height: 200,
                background: "#111",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div style={{ textAlign: "center" }}>
                <div style={{ width: 40, height: 40, borderRadius: 8, border: "2px dashed rgba(255,255,255,0.1)", margin: "0 auto 12px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span style={{ color: "rgba(255,255,255,0.15)", fontSize: 20 }}>+</span>
                </div>
                <p style={{ fontSize: 12, color: "#475569" }}>Pagina vuota</p>
              </div>
            </div>
          </div>

          {/* Arrow */}
          <div style={{ opacity: interpolate(revealProgress, [0.2, 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
            <svg width={40} height={40} viewBox="0 0 40 40">
              <path d="M8 20 L28 20 M22 12 L30 20 L22 28" fill="none" stroke="url(#arrowGradP)" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" />
              <defs>
                <linearGradient id="arrowGradP" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#22c55e" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          {/* After: complete website */}
          <div
            style={{
              width: 400,
              borderRadius: 14,
              overflow: "hidden",
              border: "1px solid rgba(255,255,255,0.08)",
              boxShadow: `0 25px 80px rgba(0,0,0,0.5), 0 0 ${revealProgress * 40}px rgba(34,197,94,0.15)`,
              opacity: interpolate(revealProgress, [0.3, 0.7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              transform: `scale(${interpolate(revealProgress, [0.3, 0.7], [0.9, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })})`,
            }}
          >
            <div style={{ height: 30, background: "#161616", display: "flex", alignItems: "center", padding: "0 10px", gap: 5 }}>
              <div style={{ display: "flex", gap: 4 }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#ff5f57" }} />
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#ffbd2e" }} />
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#28c840" }} />
              </div>
              <div style={{ flex: 1, textAlign: "center", fontSize: 10, color: "#64748b", fontFamily: "monospace" }}>
                bella-vista.e-quipe.app
              </div>
            </div>
            <div style={{ background: "linear-gradient(135deg, #0a1a0a, #152a15)", padding: 16 }}>
              {/* Nav */}
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 14 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: "white" }}>Bella Vista</span>
                <div style={{ display: "flex", gap: 8, fontSize: 8, color: "rgba(255,255,255,0.5)" }}>
                  <span>Menu</span><span>About</span><span>Contatti</span>
                </div>
              </div>
              {/* Hero */}
              <h3 style={{ fontSize: 18, fontWeight: 800, color: "white", marginBottom: 4 }}>
                Sapori autentici,
                <br />
                <span style={{ color: "#22c55e" }}>esperienza unica</span>
              </h3>
              <p style={{ fontSize: 9, color: "rgba(255,255,255,0.5)", marginBottom: 10 }}>
                Tradizione e innovazione dal 1998
              </p>
              <div style={{ display: "flex", gap: 8 }}>
                <div style={{ padding: "5px 12px", borderRadius: 5, background: "#22c55e", color: "white", fontSize: 9, fontWeight: 600 }}>Prenota</div>
                <div style={{ padding: "5px 12px", borderRadius: 5, background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.1)", color: "white", fontSize: 9 }}>Menu</div>
              </div>
              {/* Mini sections */}
              <div style={{ display: "flex", gap: 6, marginTop: 12 }}>
                {["Chi Siamo", "Menu", "Galleria", "Contatti"].map((s) => (
                  <div key={s} style={{ flex: 1, padding: "8px 4px", borderRadius: 6, background: "rgba(255,255,255,0.03)", textAlign: "center", fontSize: 8, color: "#64748b" }}>
                    {s}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Badge */}
        <div
          style={{
            opacity: interpolate(badgeEnter, [0, 1], [0, 1]),
            transform: `scale(${interpolate(badgeEnter, [0, 1], [0.5, 1])})`,
            display: "flex",
            alignItems: "center",
            gap: 12,
            padding: "14px 28px",
            borderRadius: 20,
            background: "rgba(34,197,94,0.1)",
            border: "1px solid rgba(34,197,94,0.25)",
            boxShadow: "0 0 30px rgba(34,197,94,0.15)",
          }}
        >
          <svg width={24} height={24} viewBox="0 0 24 24">
            <circle cx={12} cy={12} r={12} fill="#22c55e" />
            <path d="M7 12 L10 15.5 L17 8.5" fill="none" stroke="white" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span style={{ fontSize: 18, fontWeight: 700, color: "#86efac" }}>
            Sito generato in 47 secondi
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
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={95}>
        <ProcessScene1 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={100}>
        <ProcessScene2 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={95}>
        <ProcessScene3 />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={wipe({ direction: "from-left" })}
        timing={linearTiming({ durationInFrames: 15 })}
      />

      <TransitionSeries.Sequence durationInFrames={115}>
        <ProcessScene4 />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};

export const PROCESS_VIDEO_CONFIG = {
  id: "ProcessVideo",
  fps: 30,
  durationInFrames: 360,
  width: 1920,
  height: 1080,
};
