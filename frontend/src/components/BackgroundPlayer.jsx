import React from "react";

export default function BackgroundPlayer() {
  return (
    <div
      className="absolute top-0 left-0 pointer-events-none z-0"
      style={{
        width: "55%",
        height: "90%",
        backgroundImage: "url('/jugador.webp')",
        backgroundRepeat: "no-repeat",
        backgroundSize: "cover",
        backgroundPosition: "top center",
        opacity: 0.55,
        // Arco de desvanecimiento: sólido arriba-izquierda, se disuelve hacia abajo-derecha
        WebkitMaskImage: `
          radial-gradient(
            ellipse 85% 90% at 15% 10%,
            rgba(0,0,0,1) 0%,
            rgba(0,0,0,0.85) 30%,
            rgba(0,0,0,0.4) 55%,
            rgba(0,0,0,0) 75%
          )
        `,
        maskImage: `
          radial-gradient(
            ellipse 85% 90% at 15% 10%,
            rgba(0,0,0,1) 0%,
            rgba(0,0,0,0.85) 30%,
            rgba(0,0,0,0.4) 55%,
            rgba(0,0,0,0) 75%
          )
        `,
      }}
    />
  );
}
