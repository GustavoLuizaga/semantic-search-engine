import { FaRegSun } from "react-icons/fa6";
import { FaMoon } from "react-icons/fa";
import { useSemanticSearch } from "./hooks/useSemanticSearch";
import { useTheme } from "./hooks/useTheme";
import SourceBadge from "./components/SourceBadge";
import BackgroundPlayer from "./components/BackgroundPlayer";
import SearchInput from "./components/SearchInput";
import ResultsSection from "./components/ResultsSection";
import ThemeToggle from "./components/ThemeToggle";

function App() {
  const {
    inputRef,
    results,
    isLoading,
    error,
    handleSearch,
    source,
    setSource,
  } = useSemanticSearch();
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen transition-colors duration-300 bg-zinc-50 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 antialiased">
      <BackgroundPlayer isDarkMode={isDarkMode} />

      <ThemeToggle isDarkMode={isDarkMode} onToggle={toggleTheme} />

      <main className="max-w-3xl mx-auto px-6 py-20 flex flex-col items-center">
        <header className="w-full text-center mb-12">
          <h1 className="text-3xl font-semibold tracking-tight">
            Buscador Metasemantico de futbol
          </h1>
          <SourceBadge source={source} />
        </header>

        <ResultsSection
          results={results}
          isLoading={isLoading}
          error={error}
          source={source}
        />
        <SearchInput
          onSubmit={handleSearch}
          isLoading={isLoading}
          source={source}
          setSource={setSource}
          inputRef={inputRef}
        />
      </main>
    </div>
  );
}

export default App;
