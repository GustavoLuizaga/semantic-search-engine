export default function BackgroundPlayer({ isDarkMode }) {
  return (
    <div
      className="absolute top-0 left-0 pointer-events-none z-0 overflow-hidden"
      style={{
        width: "clamp(180px, 30vw, 420px)",
        height: "clamp(240px, 55vh, 680px)",
      }}
    >
      {/* Jugador modo oscuro */}
      <div
        className="absolute inset-0 transition-opacity duration-700"
        style={{
          opacity: isDarkMode ? 1 : 0,
          backgroundImage: "url('/ronaldo.jpg')",
          backgroundRepeat: "no-repeat",
          backgroundSize: "cover",
          backgroundPosition: "top center",
          // Mantenemos el 100% de visibilidad hasta el 50% del gradiente, y difuminamos hasta el 95%
          WebkitMaskImage:
            "radial-gradient(ellipse 90% 85% at 10% 8%, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 50%, rgba(0,0,0,0.6) 75%, rgba(0,0,0,0) 95%)",
          maskImage:
            "radial-gradient(ellipse 90% 85% at 10% 8%, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 50%, rgba(0,0,0,0.6) 75%, rgba(0,0,0,0) 95%)",
          filter: "brightness(0.6)",
        }}
      />

      {/* Jugador modo luz */}
      <div
        className="absolute inset-0 transition-opacity duration-700"
        style={{
          opacity: isDarkMode ? 0 : 1,
          backgroundImage: "url('/boca.jpg')",
          backgroundRepeat: "no-repeat",
          backgroundSize: "cover",
          backgroundPosition: "top center",
          // Mismos valores ajustados aquí
          WebkitMaskImage:
            "radial-gradient(ellipse 90% 85% at 10% 8%, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 50%, rgba(0,0,0,0.6) 75%, rgba(0,0,0,0) 95%)",
          maskImage:
            "radial-gradient(ellipse 90% 85% at 10% 8%, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 50%, rgba(0,0,0,0.6) 75%, rgba(0,0,0,0) 95%)",
          filter: "brightness(0.75)",
        }}
      />
    </div>
  );
}
