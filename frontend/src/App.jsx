import { useSemanticSearch } from "./hooks/useSemanticSearch";

function App() {
  const { inputRef, results, isLoading, error, handleSearch } =
    useSemanticSearch();

  return (
    <div className="min-h-screen bg-white text-zinc-900 antialiased selection:bg-zinc-900 selection:text-white">
      <main className="max-w-2xl mx-auto px-6 py-24 flex flex-col items-center">
        {/* Encabezado */}
        <header className="w-full text-center mb-12">
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
            Buscador Semántico
          </h1>
          <p className="text-sm text-zinc-400 mt-2 font-light">
            Introduce tu consulta para obtener respuestas asistidas por IA.
          </p>
        </header>

        {/* Formulario de Búsqueda */}
        <section className="w-full mb-10">
          <form onSubmit={handleSearch} className="flex gap-3 w-full">
            <div className="relative flex-1">
              <input
                type="text"
                ref={inputRef}
                disabled={isLoading}
                placeholder="Escribe tu pregunta..."
                className="w-full bg-zinc-50 border border-zinc-200 rounded-lg py-2.5 px-4 
                           text-sm text-zinc-800 placeholder-zinc-400
                           transition-all duration-200
                           focus:outline-none focus:border-zinc-900 focus:bg-white
                           disabled:opacity-50"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="bg-zinc-900 text-white text-sm font-medium py-2.5 px-6 rounded-lg
                         transition-all duration-200 
                         hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:ring-offset-2
                         disabled:bg-zinc-300 disabled:cursor-not-allowed"
            >
              {isLoading ? "Buscando..." : "Buscar"}
            </button>
          </form>
        </section>

        {/* Sección de Resultados / Estado */}
        <section className="w-full space-y-4">
          {/* Estado de Error */}
          {error && (
            <div className="p-4 rounded-lg bg-zinc-50 border border-zinc-200 text-sm text-zinc-600">
              {error}
            </div>
          )}

          {/* Renderizado del Resultado Semántico */}
          {results?.answer && !isLoading && (
            <article className="p-6 rounded-xl border border-zinc-200 bg-white shadow-sm transition-all">
              <h2 className="text-xs font-medium tracking-wider uppercase text-zinc-400 mb-3">
                Respuesta Encontrada
              </h2>
              <p className="text-zinc-800 leading-relaxed text-sm font-normal">
                {results.answer}
              </p>
            </article>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
