import { useState, useEffect } from "react";
import { useSemanticSearch } from "./hooks/useSemanticSearch";
import Typewriter from "./components/Typewriter";
import Thinking from "./components/Thinking";
import { CiSun } from "react-icons/ci";
import { FaMoon } from "react-icons/fa";

function App() {
  const { inputRef, results, isLoading, error, handleSearch } =
    useSemanticSearch();

  // Estado para el modo oscuro
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem("theme") === "dark";
  });

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDarkMode]);

  return (
    <div className="min-h-screen transition-colors duration-300 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 antialiased">
      {/* Botón flotante Día/Noche */}
      <button
        onClick={() => setIsDarkMode(!isDarkMode)}
        className="absolute top-6 right-6 p-2 rounded-full bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 transition"
      >
        {isDarkMode ? (
          <CiSun className="text-yellow-400" />
        ) : (
          <FaMoon className="text-blue-900" />
        )}
      </button>

      <main className="max-w-2xl mx-auto px-6 py-24 flex flex-col items-center">
        <header className="w-full text-center mb-12">
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-white">
            Buscador Semantico de futbol
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-2">
            Preguntale a la ontologia
          </p>
        </header>

        <section className="w-full space-y-6 mb-10 min-h-37.5">
          {error && (
            <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-400">
              {error}
            </div>
          )}

          {isLoading && (
            <div className="flex justify-start">
              <Thinking />
            </div>
          )}

          {results?.answer && !isLoading && (
            <article className="p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm">
              <h2 className="text-xs font-bold tracking-wider uppercase text-zinc-400 dark:text-zinc-500 mb-3 flex items-center gap-2">
                Respuesta
              </h2>
              <p className="text-zinc-800 dark:text-zinc-200 leading-relaxed text-sm font-normal">
                <Typewriter text={results.answer} speed={25} />
              </p>
            </article>
          )}
        </section>

        {/* Formulario de Búsqueda (Pegado al fondo visualmente) */}
        <section className="w-full sticky bottom-6">
          <form
            onSubmit={handleSearch}
            className="flex gap-3 w-full bg-white dark:bg-zinc-900 p-2 rounded-2xl shadow-lg border border-zinc-200 dark:border-zinc-800"
          >
            <div className="relative flex-1">
              <input
                type="text"
                ref={inputRef}
                disabled={isLoading}
                placeholder="Escribe tu pregunta (ej. ¿Quién es el máximo goleador?)..."
                className="w-full bg-transparent py-3 px-4 
                           text-sm text-zinc-800 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-600
                           focus:outline-none disabled:opacity-50"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 text-sm font-medium py-3 px-6 rounded-xl
                         transition-all duration-200 
                         hover:bg-zinc-800 dark:hover:bg-zinc-200 
                         disabled:bg-zinc-300 dark:disabled:bg-zinc-700 disabled:cursor-not-allowed"
            >
              Enviar
            </button>
          </form>
        </section>
      </main>
    </div>
  );
}

export default App;
