import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
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

const CheckIcon = () => (
  <svg width={18} height={18} viewBox="0 0 18 18">
    <circle cx={9} cy={9} r={9} fill="rgba(59,130,246,0.12)" />
    <path
      d="M5.5 9 L7.8 11.5 L12.5 6.5"
      fill="none"
      stroke="#3b82f6"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const PricingVideoComposition = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleEnter = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });

  const plans = [
    {
      name: "Starter",
      price: "29",
      period: "/mese",
      features: [
        "1 sito web",
        "5 template",
        "SSL incluso",
        "Supporto email",
      ],
      popular: false,
      delay: 30,
    },
    {
      name: "Professional",
      price: "79",
      period: "/mese",
      features: [
        "5 siti web",
        "19 template",
        "Dominio personalizzato",
        "Animazioni GSAP",
        "Supporto prioritario",
        "Analytics avanzati",
      ],
      popular: true,
      delay: 45,
    },
    {
      name: "Enterprise",
      price: "199",
      period: "/mese",
      features: [
        "Siti illimitati",
        "Template custom",
        "API access",
        "White label",
        "Account manager",
      ],
      popular: false,
      delay: 60,
    },
  ];

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

      <GradientOrb color="rgba(59,130,246,0.06)" size={500} x="15%" y="20%" phaseOffset={0} />
      <GradientOrb color="rgba(124,58,237,0.05)" size={400} x="70%" y="55%" phaseOffset={50} />

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
            PREZZI TRASPARENTI
          </div>
          <h2
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: "#0c1222",
              lineHeight: 1.2,
            }}
          >
            Scegli il piano{" "}
            <span
              style={{
                background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              perfetto
            </span>
          </h2>
        </div>

        {/* Pricing cards */}
        <div style={{ display: "flex", gap: 24, width: "100%", alignItems: "stretch" }}>
          {plans.map((plan) => {
            const cardEnter = spring({
              frame: frame - plan.delay,
              fps,
              config: { damping: 12, stiffness: 80 },
            });

            // Popular card has extra scale bounce
            const popularBounce = plan.popular
              ? spring({
                  frame: frame - plan.delay - 10,
                  fps,
                  config: { damping: 8, stiffness: 120 },
                })
              : 0;
            const extraScale = plan.popular ? interpolate(popularBounce, [0, 1], [1, 1.03]) : 1;

            // Shimmer on popular card
            const shimmer = plan.popular
              ? interpolate(Math.sin(frame * 0.06), [-1, 1], [0.8, 1])
              : 1;

            return (
              <div
                key={plan.name}
                style={{
                  flex: 1,
                  padding: plan.popular ? "36px 28px" : "32px 24px",
                  borderRadius: 20,
                  background: "#ffffff",
                  border: plan.popular
                    ? "2px solid #3b82f6"
                    : "1px solid #e2e8f0",
                  boxShadow: plan.popular
                    ? `0 20px 60px rgba(59,130,246,0.15), 0 0 ${shimmer * 20}px rgba(59,130,246,0.08)`
                    : "0 4px 16px rgba(0,0,0,0.04)",
                  opacity: interpolate(cardEnter, [0, 1], [0, 1]),
                  transform: `translateY(${interpolate(cardEnter, [0, 1], [60, 0])}px) scale(${interpolate(cardEnter, [0, 1], [0.85, 1]) * extraScale})`,
                  display: "flex",
                  flexDirection: "column",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                {/* Popular badge */}
                {plan.popular && (
                  <div
                    style={{
                      position: "absolute",
                      top: 16,
                      right: 16,
                      padding: "4px 12px",
                      borderRadius: 12,
                      background: "linear-gradient(135deg, #3b82f6, #7c3aed)",
                      color: "white",
                      fontSize: 11,
                      fontWeight: 700,
                      letterSpacing: 0.5,
                    }}
                  >
                    POPOLARE
                  </div>
                )}

                {/* Plan name */}
                <div style={{ fontSize: 18, fontWeight: 600, color: "#64748b", marginBottom: 16 }}>
                  {plan.name}
                </div>

                {/* Price */}
                <div style={{ marginBottom: 24 }}>
                  <span
                    style={{
                      fontSize: 56,
                      fontWeight: 900,
                      background: plan.popular
                        ? "linear-gradient(135deg, #3b82f6, #7c3aed)"
                        : "linear-gradient(135deg, #0c1222, #1e293b)",
                      WebkitBackgroundClip: "text",
                      WebkitTextFillColor: "transparent",
                      lineHeight: 1,
                    }}
                  >
                    {"\u20AC"}{plan.price}
                  </span>
                  <span style={{ fontSize: 16, color: "#94a3b8", fontWeight: 500 }}>
                    {plan.period}
                  </span>
                </div>

                {/* Features */}
                <div style={{ display: "flex", flexDirection: "column", gap: 14, flex: 1 }}>
                  {plan.features.map((feature, fi) => {
                    const featureEnter = spring({
                      frame: frame - (plan.delay + 15 + fi * 6),
                      fps,
                      config: { damping: 14, stiffness: 100 },
                    });

                    return (
                      <div
                        key={feature}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                          opacity: interpolate(featureEnter, [0, 1], [0, 1]),
                          transform: `translateX(${interpolate(featureEnter, [0, 1], [20, 0])}px)`,
                        }}
                      >
                        <CheckIcon />
                        <span style={{ fontSize: 14, color: "#475569" }}>
                          {feature}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* CTA button */}
                <div
                  style={{
                    marginTop: 28,
                    padding: "14px 24px",
                    borderRadius: 12,
                    background: plan.popular
                      ? "linear-gradient(135deg, #3b82f6, #7c3aed)"
                      : "#f1f5f9",
                    color: plan.popular ? "white" : "#3b82f6",
                    fontSize: 16,
                    fontWeight: 700,
                    textAlign: "center",
                    boxShadow: plan.popular ? "0 8px 25px rgba(59,130,246,0.25)" : "none",
                  }}
                >
                  Inizia Ora
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const PRICING_VIDEO_CONFIG = {
  id: "PricingVideo",
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
};
