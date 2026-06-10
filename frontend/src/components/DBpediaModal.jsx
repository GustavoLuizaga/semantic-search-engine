import ToggleSwitch from "./ToggleSwitch";

export default function DBpediaModal({
  show,
  tempMode,
  setTempMode,
  offlineAvailable,
  onAccept,
}) {
  if (!show) return null;

  const isOffline = tempMode === "offline";
  const toggleDisabled = !isOffline && !offlineAvailable;

  return (
    <div className="fixed inset-0 z-100 flex items-center justify-center p-4 bg-zinc-900/40 backdrop-blur-sm">
      <div className="bg-white dark:bg-zinc-800 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden animate-in fade-in zoom-in-95 duration-200 border border-zinc-200 dark:border-zinc-700">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-5">
            Configurar DBpedia
          </h3>

          {/* Switch row */}
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Activar Modo Offline
            </span>
            <ToggleSwitch
              checked={isOffline}
              onChange={(val) => setTempMode(val ? "offline" : "online")}
              disabled={toggleDisabled}
            />
          </div>

          {/* Aviso servidor inactivo */}
          {!offlineAvailable && !isOffline && (
            <p className="text-[11px] text-red-500 mt-1 mb-3">
              Servidor local inactivo. No se puede activar.
            </p>
          )}

          {/* Advertencia modo offline */}
          <div
            className={`transition-all duration-300 overflow-hidden ${
              isOffline ? "max-h-24 opacity-100 mt-4" : "max-h-0 opacity-0 mt-0"
            }`}
          >
            <div className="p-3 bg-zinc-100 dark:bg-zinc-700/50 rounded-xl">
              <p className="text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed">
                El modo offline es una version de prueba y podria estar
                incompleta o tener fallas :,v
              </p>
            </div>
          </div>

          {/* Botón aceptar */}
          <div className="mt-6">
            <button
              onClick={onAccept}
              className="w-full py-2.5 bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 rounded-xl text-sm font-medium transition-colors hover:bg-zinc-800 dark:hover:bg-zinc-200"
            >
              Aceptar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
