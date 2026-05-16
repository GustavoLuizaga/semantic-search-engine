import { useState, useEffect } from "react";
import { useSemanticSearch } from "./hooks/useSemanticSearch";
import Typewriter from "./components/Typewriter";
import Thinking from "./components/Thinking";
import { FaRegSun } from "react-icons/fa6";
import { FaMoon } from "react-icons/fa";

function App() {
  const { inputRef, results, isLoading, error, handleSearch } =
    useSemanticSearch();
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem("theme") === "dark";
  });
  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDarkMode);
    localStorage.setItem("theme", isDarkMode ? "dark" : "light");
  }, [isDarkMode]);
  const isDataArray = Array.isArray(results?.data);
  const isDataObject =
    results?.data &&
    typeof results.data === "object" &&
    !Array.isArray(results.data);

  const dataRows = isDataArray ? results.data : [];

  const dataColumns = dataRows.reduce((columns, row) => {
    if (row && typeof row === "object") {
      Object.keys(row).forEach((key) => {
        if (!columns.includes(key)) {
          columns.push(key);
        }
      });
    }

    return columns;
  }, []);

  return (
    <div className="min-h-screen transition-colors duration-300 bg-zinc-50 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 antialiased">
      <button
        onClick={() => setIsDarkMode(!isDarkMode)}
        className="absolute top-6 right-6 p-2 rounded-full bg-zinc-200 dark:bg-zinc-800 hover:bg-zinc-300 dark:hover:bg-zinc-700 transition"
      >
        {isDarkMode ? (
          <FaRegSun className="text-orange-600" />
        ) : (
          <FaMoon className="text-yellow-500" />
        )}
      </button>

      <main className="max-w-3xl mx-auto px-6 py-20 flex flex-col items-center">
        {/* Header */}
        <header className="w-full text-center mb-12">
          <h1 className="text-3xl font-semibold tracking-tight">
            Buscador Metasemantico de futbol
          </h1>
        </header>

        {/* Resultados */}
        <section className="w-full space-y-6 mb-10 min-h-30">
          {/* Error */}
          {error && (
            <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 text-sm">
              {error}
            </div>
          )}

          {isLoading && (
            <div className="flex justify-start">
              <Thinking />
            </div>
          )}
          {results?.answer && !isLoading && (
            <article className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 shadow-sm">
              <h2 className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500 mb-3 flex items-center gap-2">
                RESPUESTA
              </h2>

              <p className="text-sm leading-relaxed text-zinc-700 dark:text-zinc-200 whitespace-pre-wrap">
                <Typewriter text={results.answer} speed={20} />
              </p>
            </article>
          )}

          {/* Tabla */}
          {dataRows.length > 0 && !isLoading && (
            <article className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 shadow-sm">
              <h2 className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500 mb-4">
                Datos
              </h2>

              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left border-collapse">
                  <thead>
                    <tr className="border-b border-zinc-200 dark:border-zinc-700">
                      {dataColumns.map((column) => (
                        <th
                          key={column}
                          className="py-2 pr-4 font-medium capitalize text-zinc-500"
                        >
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    {dataRows.map((row, index) => (
                      <tr
                        key={index}
                        className="border-b border-zinc-100 dark:border-zinc-700 last:border-0"
                      >
                        {dataColumns.map((column) => (
                          <td
                            key={column}
                            className="py-2 pr-4 text-zinc-700 dark:text-zinc-200 align-top"
                          >
                            {row?.[column] ?? "-"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          )}
          {isDataObject && !isLoading && (
            <article className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 shadow-sm">
              <h2 className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500 mb-4">
                Datos
              </h2>

              <div className="space-y-3">
                {Object.entries(results.data).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex justify-between gap-4 pb-2 border-b border-zinc-100 dark:border-zinc-700 last:border-0"
                  >
                    <span className="font-medium capitalize text-zinc-500 min-w-fit">
                      {key}:
                    </span>

                    <span className="text-right text-zinc-700 dark:text-zinc-200">
                      {String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </article>
          )}
        </section>

        {/* Input */}
        <section className="w-full sticky bottom-6">
          <form
            onSubmit={handleSearch}
            className="flex gap-3 w-full bg-white dark:bg-zinc-800 p-2 rounded-2xl shadow-lg border border-zinc-200 dark:border-zinc-700"
          >
            <div className="relative flex-1">
              <input
                type="text"
                ref={inputRef}
                disabled={isLoading}
                placeholder="Escribe tu pregunta..."
                className="w-full bg-transparent py-3 px-4 text-sm
                           text-zinc-800 dark:text-zinc-100
                           placeholder-zinc-400 dark:placeholder-zinc-500
                           focus:outline-none
                           disabled:opacity-50"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 text-sm font-medium py-3 px-6 rounded-xl
                         transition-all duration-200
                         hover:bg-zinc-800 dark:hover:bg-zinc-200
                         disabled:bg-zinc-400 dark:disabled:bg-zinc-700
                         disabled:cursor-not-allowed"
            >
              {isLoading ? "..." : "Enviar"}
            </button>
          </form>
        </section>
      </main>
    </div>
  );
}

export default App;
