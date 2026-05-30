import { useState, useEffect } from "react";
import { useSemanticSearch } from "./hooks/useSemanticSearch";
import Typewriter from "./components/Typewriter";
import Thinking from "./components/Thinking";
// App.jsx MODIFICADO

import { translations } from "./utils/translations";

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
  const t = translations[language] || translations.es;

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

      {/* pb-36 mantiene el colchón para que los resultados no se tapen */}
      <main className="max-w-3xl mx-auto px-6 pt-20 pb-36 flex flex-col items-center relative z-10">
        {/* Header */}
        <header className="w-full text-center mb-12">
          <h1 className="text-3xl font-semibold tracking-tight">{t.title}</h1>
          <SourceBadge source={source} language={language} />
        </header>

        <ResultsSection
          results={results}
          isLoading={isLoading}
          error={error}
          source={source}
          language={language}
        />

        {/* Le pasamos setLanguage a SearchInput para que adentro maneje el selector */}
        <SearchInput
          onSubmit={handleSearch}
          isLoading={isLoading}
          source={source}
          setSource={setSource}
          language={language}
          setLanguage={setLanguage}
          inputRef={inputRef}
        />
      </main>

      {/* ¡Borrados los elementos flotantes conflictivos de aquí! */}
    </div>
  );
}

export default App;
