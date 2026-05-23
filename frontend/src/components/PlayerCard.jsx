export default function PlayerCard({ data, source }) {
  if (!data || typeof data !== "object" || Array.isArray(data)) return null;

  const {
    foto,
    equipos_trayectoria,
    fecha_nacimiento,
    nombre,
    posicion,
    equipo,
    dorsal,
    nacionalidad,
    estatura,
    ...restoCampos
  } = data;

  // Campos que ya mostramos visualmente, no en la lista genérica
  const camposExcluidos = new Set([
    "foto",
    "nombre",
    "posicion",
    "equipo",
    "dorsal",
    "nacionalidad",
    "estatura",
    "fecha_nacimiento",
    "equipos_trayectoria",
  ]);

  const camposExtra = Object.entries(restoCampos).filter(
    ([key]) => !camposExcluidos.has(key),
  );

  const equiposUnicos = foto
    ? [
        ...new Set(
          (equipos_trayectoria ?? []).filter(
            (e) =>
              !e.toLowerCase().includes("under") &&
              !e.toLowerCase().includes("academy") &&
              !e.toLowerCase().includes("reservas") &&
              !e.toLowerCase().includes("sub-"),
          ),
        ),
      ]
    : [];

  const fechaFormateada = fecha_nacimiento
    ? new Date(fecha_nacimiento).toLocaleDateString("es-ES", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : null;

  // Sin foto: layout lista simple (modo no-DBpedia)
  if (!foto) {
    return (
      <article className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 shadow-sm">
        <h2 className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500 mb-4">
          Datos
        </h2>
        <div className="space-y-3">
          {Object.entries(data).map(([key, value]) => (
            <div
              key={key}
              className="flex justify-between gap-4 pb-2 border-b border-zinc-100 dark:border-zinc-700 last:border-0"
            >
              <span className="font-medium capitalize text-zinc-500 min-w-fit">
                {key}:
              </span>
              <span className="text-right text-zinc-700 dark:text-zinc-200">
                {Array.isArray(value) ? value.join(", ") : String(value)}
              </span>
            </div>
          ))}
        </div>
      </article>
    );
  }

  // Con foto: layout card DBpedia
  return (
    <article className="p-5 rounded-2xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 shadow-sm">
      <div className="flex gap-5 items-start">
        {/* Foto */}
        <div className="relative shrink-0">
          <div className="w-24 h-28 rounded-xl overflow-hidden border border-zinc-200 dark:border-zinc-600">
            <img
              src={foto}
              alt={nombre}
              className="w-full h-full object-cover object-top"
              onError={(e) => {
                e.target.style.display = "none";
                e.target.parentElement.innerHTML =
                  '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:2rem;background:#f4f4f5">⚽</div>';
              }}
            />
          </div>
          {dorsal && (
            <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-amber-500 text-zinc-900 text-[11px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap">
              #{dorsal}
            </span>
          )}
        </div>

        {/* Info principal */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {nombre && (
              <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
                {nombre}
              </h3>
            )}
            {source === "dbpedia" && (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400">
                DBpedia
              </span>
            )}
          </div>

          <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-4">
            {[posicion, equipo].filter(Boolean).join(" · ")}
          </p>

          <div className="grid grid-cols-2 gap-x-4 gap-y-3">
            {nacionalidad && (
              <div>
                <p className="text-[11px] text-zinc-400 dark:text-zinc-500">
                  Nacionalidad
                </p>
                <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                  {nacionalidad}
                </p>
              </div>
            )}
            {fechaFormateada && (
              <div>
                <p className="text-[11px] text-zinc-400 dark:text-zinc-500">
                  Nacimiento
                </p>
                <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                  {fechaFormateada}
                </p>
              </div>
            )}
            {estatura && (
              <div>
                <p className="text-[11px] text-zinc-400 dark:text-zinc-500">
                  Estatura
                </p>
                <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                  {estatura}
                </p>
              </div>
            )}
            {equiposUnicos.length > 0 && (
              <div>
                <p className="text-[11px] text-zinc-400 dark:text-zinc-500">
                  Trayectoria
                </p>
                <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                  {equiposUnicos.length} clubes
                </p>
              </div>
            )}
            {/* Campos extra que no conocemos de antemano */}
            {camposExtra.map(([key, value]) => (
              <div key={key}>
                <p className="text-[11px] text-zinc-400 dark:text-zinc-500 capitalize">
                  {key}
                </p>
                <p className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                  {String(value)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trayectoria */}
      {equiposUnicos.length > 0 && (
        <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-700">
          <p className="text-[11px] text-zinc-400 dark:text-zinc-500 mb-2 uppercase tracking-wider">
            Trayectoria
          </p>
          <div className="flex flex-wrap gap-1.5">
            {equiposUnicos.map((e) => (
              <span
                key={e}
                className="text-xs px-2 py-1 rounded-lg bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300"
              >
                {e}
              </span>
            ))}
          </div>
        </div>
      )}
    </article>
  );
}
