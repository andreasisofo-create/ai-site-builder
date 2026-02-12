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

export const StatsVideoComposition = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });

  const stats = [
    { label: "Siti Generati", target: 2847, suffix: "+", delay: 15, color: "#3b82f6" },
    { label: "Template Disponibili", target: 148, suffix: "", delay: 25, color: "#7c3aed" },
    { label: "Fatturato Clienti", target: 1.2, suffix: "M+", prefix: "\u20AC", isDecimal: true, delay: 35, color: "#22c55e" },
    { label: "Valutazione Media", target: 4.8, suffix: "/5", isDecimal: true, delay: 45, color: "#f59e0b" },
  ];

  // Bar chart data
  const barData = [
    { label: "Gen", value: 45, color: "#3b82f6" },
    { label: "Feb", value: 62, color: "#3b82f6" },
    { label: "Mar", value: 78, color: "#7c3aed" },
    { label: "Apr", value: 95, color: "#7c3aed" },
    { label: "Mag", value: 110, color: "#3b82f6" },
    { label: "Giu", value: 135, color: "#7c3aed" },
  ];
  const maxBarValue = 150;

  return (
    <AbsoluteFill
      style={{
        background: "#ffffff",
        fontFamily: FONT,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Subtle grid */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage:
            "linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <GradientOrb color="rgba(59,130,246,0.06)" size={500} x="10%" y="10%" phaseOffset={0} />
      <GradientOrb color="rgba(124,58,237,0.05)" size={400} x="70%" y="60%" phaseOffset={50} />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 48,
          width: "100%",
          maxWidth: 1100,
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
              background: "rgba(59,130,246,0.08)",
              border: "1px solid rgba(59,130,246,0.15)",
              color: "#3b82f6",
              fontSize: 13,
              fontWeight: 600,
              letterSpacing: 1.5,
              marginBottom: 16,
            }}
          >
            I NOSTRI NUMERI
          </div>
          <h2
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: "#0c1222",
              lineHeight: 1.2,
            }}
          >
            Risultati che{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              parlano
            </span>
          </h2>
        </div>

        {/* Stats grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20, width: "100%" }}>
          {stats.map((stat) => {
            const cardEnter = spring({
              frame: frame - stat.delay,
              fps,
              config: { damping: 12, stiffness: 90 },
            });
            const counterProgress = interpolate(
              frame,
              [stat.delay + 5, stat.delay + 60],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.25, 0.1, 0.25, 1) }
            );
            const currentValue = stat.isDecimal
              ? (counterProgress * stat.target).toFixed(1)
              : Math.round(counterProgress * stat.target).toLocaleString("it-IT");

            return (
              <div
                key={stat.label}
                style={{
                  padding: "28px 20px",
                  borderRadius: 16,
                  background: "#f8fafc",
                  border: "1px solid #e2e8f0",
                  textAlign: "center",
                  opacity: interpolate(cardEnter, [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(cardEnter, [0, 1], [40, 0])}px) scale(${interpolate(cardEnter, [0, 1], [0.9, 1])})`,
                }}
              >
                <div
                  style={{
                    fontSize: 48,
                    fontWeight: 900,
                    background: `linear-gradient(135deg, ${stat.color}, ${stat.color}cc)`,
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    fontVariantNumeric: "tabular-nums",
                    lineHeight: 1.1,
                    marginBottom: 12,
                  }}
                >
                  {stat.prefix || ""}{currentValue}{stat.suffix}
                </div>
                <div style={{ fontSize: 14, color: "#64748b", fontWeight: 500 }}>
                  {stat.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* Bar chart */}
        <div
          style={{
            width: "100%",
            padding: "28px 32px 20px",
            borderRadius: 16,
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
          }}
        >
          <div style={{ fontSize: 14, color: "#64748b", fontWeight: 600, marginBottom: 20 }}>
            Crescita Mensile
          </div>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 20, height: 180 }}>
            {barData.map((bar, i) => {
              const barEnter = spring({
                frame: frame - (80 + i * 8),
                fps,
                config: { damping: 12, stiffness: 80 },
              });
              const barHeight = (bar.value / maxBarValue) * 160;

              return (
                <div
                  key={bar.label}
                  style={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <span
                    style={{
                      fontSize: 12,
                      fontWeight: 700,
                      color: "#0c1222",
                      opacity: interpolate(barEnter, [0, 1], [0, 1]),
                    }}
                  >
                    {bar.value}
                  </span>
                  <div
                    style={{
                      width: "100%",
                      maxWidth: 60,
                      height: barHeight * interpolate(barEnter, [0, 1], [0, 1]),
                      borderRadius: "8px 8px 4px 4px",
                      background: `linear-gradient(180deg, ${bar.color}, ${bar.color}aa)`,
                      boxShadow: `0 4px 15px ${bar.color}25`,
                    }}
                  />
                  <span style={{ fontSize: 11, color: "#94a3b8", fontWeight: 500 }}>
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

export const STATS_VIDEO_CONFIG = {
  id: "StatsVideo",
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
};
