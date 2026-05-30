import { useState, useRef } from "react";
import { searchQuery } from "../services/search-service";
import { translations } from "../utils/translations";

export function useSemanticSearch() {
  const inputRef = useRef(null);
  
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [source, setSource] = useState("local");
  const [language, setLanguage] = useState("es");

  const handleSearch = async (e) => {
    const t = translations[language] || translations.es;
    e.preventDefault();

    const query = inputRef.current?.value?.trim();

    if (!query) return;

    setIsLoading(true);

    // limpiar errores anteriores
    setError(null);

    try {
      const searchResults = await searchQuery(query, source, language);

      setResults(searchResults);
    } catch (err) {
      console.error(err);

      // limpiar resultados anteriores
      setResults(null);

      // backend muerto / sin conexión
      if (err.name === "TypeError") {
        setError(
          t.errorBackend
        );
      } else {
        setError(
          t.errorGeneric
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
    inputRef,
    results,
    isLoading,
    error,
    handleSearch,
    source,
    setSource,
    language,
    setLanguage,
  };
}