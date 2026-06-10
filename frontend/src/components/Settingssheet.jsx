import { useEffect, useRef } from "react";
import ToggleSwitch from "./ToggleSwitch";
import { translations } from "../utils/translations";

const SOURCES = (t) => [
  { value: "local", label: t.localTitle },
  { value: "dbpedia", label: t.dbpediaTitle },
];

const LANGUAGES = [
  { value: "es", label: "Español", code: "ES" },
  { value: "en", label: "English", code: "EN" },
  { value: "fr", label: "Français", code: "FR" },
];

const FlagES = () => (
  <svg
    viewBox="0 0 20 14"
    width="20"
    height="14"
    aria-hidden="true"
    preserveAspectRatio="xMidYMid slice"
  >
    <rect width="20" height="14" fill="#D52B1E" />
    <rect y="4.67" width="20" height="4.66" fill="#F9D616" />
    <rect y="9.34" width="20" height="4.66" fill="#007A33" />
  </svg>
);

const FlagEN = () => (
  <svg
    viewBox="0 0 20 14"
    width="20"
    height="14"
    aria-hidden="true"
    preserveAspectRatio="xMidYMid slice"
  >
    <rect width="20" height="14" fill="#B22234" />
    <path
      d="M0 2H20M0 4H20M0 6H20M0 8H20M0 10H20M0 12H20"
      stroke="#FFFFFF"
      strokeWidth="1"
    />
    <rect width="8.6" height="7.6" fill="#3C3B6E" />
  </svg>
);

const FlagFR = () => (
  <svg
    viewBox="0 0 20 14"
    width="20"
    height="14"
    aria-hidden="true"
    preserveAspectRatio="xMidYMid slice"
  >
    <rect width="20" height="14" fill="#FFFFFF" />
    <rect width="6.67" height="14" fill="#0055A4" />
    <rect x="13.33" width="6.67" height="14" fill="#EF4135" />
  </svg>
);

const Flag = ({ value }) => {
  if (value === "en") return <FlagEN />;
  if (value === "fr") return <FlagFR />;
  return <FlagES />;
};

export default function SettingsSheet({
  show,
  onClose,
  source,
  setSource,
  language,
  setLanguage,
  mode,
  setMode,
  offlineAvailable,
}) {
  const t = translations[language] || translations.es;
  const overlayRef = useRef(null);

  // Cierra con Escape
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  // Bloquea el scroll del body mientras está abierto
  useEffect(() => {
    document.body.style.overflow = show ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [show]);

  const isOffline = mode === "offline";
  const toggleDisabled = !isOffline && !offlineAvailable;

  return (
    <>
      {/* ── Overlay ── */}
      <div
        ref={overlayRef}
        onClick={onClose}
        className={`
          fixed inset-0 z-40 bg-zinc-900/40 backdrop-blur-sm
          transition-opacity duration-300
          ${show ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"}
        `}
      />

      {/* ── Panel ── */}
      <div
        className={`
          fixed bottom-0 left-0 right-0 z-50
          bg-white dark:bg-zinc-800
          border-t border-zinc-200 dark:border-zinc-700
          rounded-t-2xl shadow-2xl
          transition-transform duration-300 ease-out
          ${show ? "translate-y-0" : "translate-y-full"}
        `}
      >
        {/* Drag handle visual */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 rounded-full bg-zinc-300 dark:bg-zinc-600" />
        </div>

        <div className="px-6 pt-3 pb-8 space-y-6">
          {/* Título */}
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
            Configuración
          </h3>

          {/* ── Fuente ── */}
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
              Fuente
            </p>
            <div className="flex gap-2 w-full">
              {SOURCES(t).map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setSource(opt.value)}
                  className={`
                    flex-1 py-2.5 rounded-xl text-sm font-medium border transition-all duration-150
                    ${
                      source === opt.value
                        ? "bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-transparent"
                        : "bg-transparent text-zinc-600 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-500"
                    }
                  `}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
              Idioma
            </p>
            <div className="flex w-full gap-2 overflow-x-auto pb-2 sm:pb-0 snap-x snap-mandatory [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] scrollbar-none">
              {LANGUAGES.map((opt) => {
                const isSelected = language === opt.value;
                return (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setLanguage(opt.value)}
                    className={`
                      flex-1 min-w-30 snap-center
                      flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium border transition-all duration-150
                      ${
                        isSelected
                          ? "bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 border-transparent"
                          : "bg-transparent text-zinc-600 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-500"
                      }
                    `}
                  >
                    <div className="w-5 h-5 rounded-full overflow-hidden shrink-0 border border-zinc-200 dark:border-zinc-700 shadow-sm [&>svg]:w-full [&>svg]:h-full">
                      <Flag value={opt.value} />
                    </div>
                    <span>{opt.code}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* ── Modo DBpedia (solo si source === dbpedia) ── */}
          {source === "dbpedia" && (
            <div className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
                Modo DBpedia
              </p>
              <div className="flex items-center justify-between p-3 rounded-xl bg-zinc-50 dark:bg-zinc-700/40 border border-zinc-200 dark:border-zinc-700">
                <div>
                  <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                    Modo Offline
                  </p>
                  {!offlineAvailable && !isOffline && (
                    <p className="text-[11px] text-red-500 mt-0.5">
                      Servidor local inactivo
                    </p>
                  )}
                  {isOffline && (
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5">
                      Versión de prueba, puede fallar
                    </p>
                  )}
                </div>
                <ToggleSwitch
                  checked={isOffline}
                  onChange={(val) => setMode(val ? "offline" : "online")}
                  disabled={toggleDisabled}
                />
              </div>
            </div>
          )}

          {/* ── Botón cerrar ── */}
          <button
            type="button"
            onClick={onClose}
            className="w-full py-3 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 rounded-xl text-sm font-medium transition-colors hover:bg-zinc-700 dark:hover:bg-zinc-200"
          >
            Listo
          </button>
        </div>
      </div>
    </>
  );
}
