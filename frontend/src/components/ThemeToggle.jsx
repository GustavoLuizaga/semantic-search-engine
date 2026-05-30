import { FaMoon } from "react-icons/fa";

export default function ThemeToggle({ isDarkMode, onToggle }) {
  return (
    <button
      onClick={onToggle}
      className="absolute top-6 right-6 rounded-full overflow-hidden
                 hover:ring-2 hover:ring-zinc-400 dark:hover:ring-zinc-500
                 transition-all duration-200"
      style={{ width: "32px", height: "32px" }}
      aria-label="Cambiar tema"
    >
      <div
        className="flex flex-col transition-transform duration-500 ease-in-out"
        style={{
          transform: isDarkMode ? "translateY(0%)" : "translateY(-50%)",
          height: "200%",
          width: "100%",
        }}
      >
        {/* Sol jpeg — modo oscuro */}
        <div
          style={{
            width: "32px",
            height: "32px",
            flexShrink: 0,
            overflow: "hidden",
          }}
        >
          <img
            src="/sun.jpg"
            alt="activar modo claro"
            style={{
              width: "100%",
              height: "100%",
              objectFit: "contain", // ← contain para no cortar el sol
              objectPosition: "center",
            }}
          />
        </div>

        {/* Luna react-icon — modo claro */}
        <div
          style={{ width: "32px", height: "32px", flexShrink: 0 }}
          className="flex items-center justify-center bg-zinc-800 dark:bg-zinc-800"
        >
          <FaMoon className="text-yellow-500" style={{ fontSize: "16px" }} />
        </div>
      </div>
    </button>
  );
}
