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

/* ── Aurora blob ─────────────────────────────────────────── */
const AuroraBlob = ({
  color,
  size,
  x,
  y,
  phaseOffset,
  driftScale = 1,
}: {
  color: string;
  size: number;
  x: string;
  y: string;
  phaseOffset: number;
  driftScale?: number;
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const breathe = interpolate(
    frame,
    [0, durationInFrames * 0.3, durationInFrames * 0.7, durationInFrames],
    [1, 1.25, 0.95, 1.15],
    { extrapolateRight: "clamp" }
  );

  const driftX = Math.sin((frame + phaseOffset) * 0.015) * 30 * driftScale;
  const driftY = Math.cos((frame + phaseOffset) * 0.012) * 20 * driftScale;

  return (
    <div
      style={{
        position: "absolute",
        width: size,
        height: size,
        borderRadius: "50%",
        background: color,
        filter: `blur(${size * 0.45}px)`,
        opacity: 0.45,
        left: x,
        top: y,
        transform: `scale(${breathe}) translate(${driftX}px, ${driftY}px)`,
      }}
    />
  );
};

/* ── Check icon (frosted style) ──────────────────────────── */
const CheckIcon = ({ golden }: { golden?: boolean }) => (
  <svg width={22} height={22} viewBox="0 0 22 22">
    <circle
      cx={11}
      cy={11}
      r={11}
      fill={golden ? "rgba(255,215,0,0.15)" : "rgba(0,255,136,0.12)"}
    />
    <path
      d="M6.5 11 L9.5 14 L15.5 7.5"
      fill="none"
      stroke={golden ? "#ffd700" : "#00ff88"}
      strokeWidth={2.2}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

/* ── Plan data ───────────────────────────────────────────── */
const plans = [
  {
    name: "STARTER",
    price: "€0",
    subtitle: "Gratis per sempre",
    features: ["1 sito web", "3 template base", "SSL incluso"],
    popular: false,
    enterDelay: 30,
  },
  {
    name: "SITO WEB",
    price: "€200",
    subtitle: "Pagamento unico",
    features: [
      "19 template premium",
      "Animazioni GSAP",
      "Dominio personalizzato",
      "Supporto prioritario",
    ],
    popular: true,
    enterDelay: 45,
  },
  {
    name: "PREMIUM",
    price: "€500",
    subtitle: "Tutto incluso",
    features: [
      "Siti illimitati",
      "Template custom",
      "Analytics avanzati",
      "Account manager dedicato",
    ],
    popular: false,
    enterDelay: 60,
  },
];

/* ── Main composition ────────────────────────────────────── */
export const PricingVideo = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  /* Title fade-in: frames 0-30 */
  const titleOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 30], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "#0f0f1a",
        fontFamily: FONT,
        overflow: "hidden",
      }}
    >
      {/* ── Aurora background blobs ── */}
      <AuroraBlob
        color="#00ff88"
        size={600}
        x="-5%"
        y="-10%"
        phaseOffset={0}
        driftScale={1.2}
      />
      <AuroraBlob
        color="#0088ff"
        size={500}
        x="55%"
        y="50%"
        phaseOffset={80}
        driftScale={0.9}
      />
      <AuroraBlob
        color="#8800ff"
        size={550}
        x="70%"
        y="-15%"
        phaseOffset={160}
        driftScale={1.1}
      />
      <AuroraBlob
        color="#0088ff"
        size={350}
        x="20%"
        y="65%"
        phaseOffset={220}
        driftScale={0.7}
      />

      {/* ── Content layer ── */}
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1,
        }}
      >
        {/* ── Title ── */}
        <div
          style={{
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            textAlign: "center",
            marginBottom: 60,
          }}
        >
          <h1
            style={{
              fontSize: 64,
              fontWeight: 900,
              color: "#ffffff",
              letterSpacing: 6,
              margin: 0,
              textTransform: "uppercase",
            }}
          >
            I Nostri Piani
          </h1>
          <div
            style={{
              width: 80,
              height: 3,
              background: "linear-gradient(90deg, #00ff88, #0088ff)",
              borderRadius: 2,
              margin: "16px auto 0",
              opacity: titleOpacity,
            }}
          />
        </div>

        {/* ── Pricing cards row ── */}
        <div
          style={{
            display: "flex",
            gap: 36,
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {plans.map((plan, planIndex) => {
            /* Card entrance: frames 30-90 with stagger */
            const cardSpring = spring({
              frame: frame - plan.enterDelay,
              fps,
              config: { damping: 14, stiffness: 70 },
            });
            const cardOpacity = interpolate(cardSpring, [0, 1], [0, 1]);
            const cardY = interpolate(cardSpring, [0, 1], [80, 0]);
            const cardScale = interpolate(cardSpring, [0, 1], [0.85, 1]);

            /* Gentle floating after entrance */
            const floatY =
              frame > plan.enterDelay + 30
                ? Math.sin((frame + planIndex * 40) * 0.04) * 4
                : 0;

            /* Card dimensions */
            const cardWidth = plan.popular ? 400 : 360;
            const cardPadding = plan.popular ? 44 : 36;

            /* Popular golden glow pulse */
            const glowIntensity = plan.popular
              ? interpolate(
                  Math.sin(frame * 0.05),
                  [-1, 1],
                  [0.3, 0.7]
                )
              : 0;

            return (
              <div
                key={plan.name}
                style={{
                  width: cardWidth,
                  padding: cardPadding,
                  borderRadius: 24,
                  background: "rgba(255,255,255,0.08)",
                  border: plan.popular
                    ? `2px solid rgba(255,215,0,${0.4 + glowIntensity * 0.3})`
                    : "1px solid rgba(255,255,255,0.1)",
                  boxShadow: plan.popular
                    ? `0 0 ${30 + glowIntensity * 20}px rgba(255,215,0,${glowIntensity * 0.25}), 0 20px 60px rgba(0,0,0,0.3)`
                    : "0 8px 32px rgba(0,0,0,0.2)",
                  opacity: cardOpacity,
                  transform: `translateY(${cardY + floatY}px) scale(${cardScale})`,
                  display: "flex",
                  flexDirection: "column",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                {/* Inner glass sheen */}
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: "40%",
                    background:
                      "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, transparent 100%)",
                    borderRadius: "24px 24px 0 0",
                    pointerEvents: "none",
                  }}
                />

                {/* Popular badge */}
                {plan.popular && (
                  <div
                    style={{
                      position: "absolute",
                      top: 20,
                      right: 20,
                      padding: "6px 16px",
                      borderRadius: 14,
                      background: "linear-gradient(135deg, #ffd700, #ffaa00)",
                      color: "#0f0f1a",
                      fontSize: 13,
                      fontWeight: 800,
                      letterSpacing: 1.5,
                      textTransform: "uppercase",
                    }}
                  >
                    Popolare
                  </div>
                )}

                {/* Plan name */}
                <div
                  style={{
                    fontSize: 56,
                    fontWeight: 800,
                    color: "rgba(255,255,255,0.5)",
                    letterSpacing: 4,
                    marginBottom: 20,
                    textTransform: "uppercase",
                  }}
                >
                  {plan.name}
                </div>

                {/* Price */}
                <div style={{ marginBottom: 6 }}>
                  <span
                    style={{
                      fontSize: 96,
                      fontWeight: 900,
                      color: plan.popular ? "#ffd700" : "#ffffff",
                      lineHeight: 1,
                      letterSpacing: -2,
                    }}
                  >
                    {plan.price}
                  </span>
                </div>

                {/* Subtitle */}
                <div
                  style={{
                    fontSize: 20,
                    fontWeight: 500,
                    color: "rgba(255,255,255,0.45)",
                    marginBottom: 32,
                    letterSpacing: 1,
                  }}
                >
                  {plan.subtitle}
                </div>

                {/* Divider */}
                <div
                  style={{
                    width: "100%",
                    height: 1,
                    background: "rgba(255,255,255,0.08)",
                    marginBottom: 28,
                  }}
                />

                {/* Features with stagger: frames 90-180 */}
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 18,
                    flex: 1,
                  }}
                >
                  {plan.features.map((feature, fi) => {
                    const featureStart = 90 + plan.enterDelay - 30 + fi * 12;
                    const featureOpacity = interpolate(
                      frame,
                      [featureStart, featureStart + 20],
                      [0, 1],
                      {
                        extrapolateLeft: "clamp",
                        extrapolateRight: "clamp",
                      }
                    );
                    const featureX = interpolate(
                      frame,
                      [featureStart, featureStart + 20],
                      [25, 0],
                      {
                        extrapolateLeft: "clamp",
                        extrapolateRight: "clamp",
                      }
                    );

                    return (
                      <div
                        key={feature}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 14,
                          opacity: featureOpacity,
                          transform: `translateX(${featureX}px)`,
                        }}
                      >
                        <CheckIcon golden={plan.popular} />
                        <span
                          style={{
                            fontSize: 24,
                            fontWeight: 500,
                            color: "rgba(255,255,255,0.75)",
                          }}
                        >
                          {feature}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* CTA button */}
                <div
                  style={{
                    marginTop: 36,
                    padding: "16px 28px",
                    borderRadius: 14,
                    background: plan.popular
                      ? "linear-gradient(135deg, #ffd700, #ffaa00)"
                      : "rgba(255,255,255,0.08)",
                    border: plan.popular
                      ? "none"
                      : "1px solid rgba(255,255,255,0.12)",
                    color: plan.popular ? "#0f0f1a" : "rgba(255,255,255,0.8)",
                    fontSize: 20,
                    fontWeight: 700,
                    textAlign: "center",
                    letterSpacing: 1,
                  }}
                >
                  {plan.popular ? "Scegli Questo Piano" : "Inizia Ora"}
                </div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* Keep backward-compatible alias */
export const PricingVideoComposition = PricingVideo;

export const PRICING_VIDEO_CONFIG = {
  id: "PricingVideo",
  fps: 30,
  durationInFrames: 300,
  width: 1920,
  height: 1080,
};
