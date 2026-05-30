// App.jsx MODIFICADO

import { useSemanticSearch } from "./hooks/useSemanticSearch";
import { useTheme } from "./hooks/useTheme";
import SourceBadge from "./components/SourceBadge";
import BackgroundPlayer from "./components/BackgroundPlayer";
import SearchInput from "./components/SearchInput";
import ResultsSection from "./components/ResultsSection";
import ThemeToggle from "./components/ThemeToggle";
import { translations } from "./utils/translations";

function App() {
  const {
    inputRef,
    results,
    isLoading,
    error,
    handleSearch,
    source,
    setSource,
    language,
    setLanguage,
  } = useSemanticSearch();
  const { isDarkMode, toggleTheme } = useTheme();
  const t = translations[language] || translations.es;

  return (
    <div className="min-h-screen transition-colors duration-300 bg-zinc-50 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 antialiased">
      <BackgroundPlayer isDarkMode={isDarkMode} />

      <ThemeToggle isDarkMode={isDarkMode} onToggle={toggleTheme} />

      {/* pb-36 mantiene el colchón para que los resultados no se tapen */}
      <main className="max-w-3xl mx-auto px-6 pt-20 pb-36 flex flex-col items-center relative z-10">
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
