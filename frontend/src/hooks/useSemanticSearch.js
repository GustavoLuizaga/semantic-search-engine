import { useState, useRef } from "react";
import { searchQuery } from "../services/search-service";

export function useSemanticSearch() {
  const inputRef = useRef(null);

  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();

    const query = inputRef.current?.value?.trim();

    if (!query) return;

    setIsLoading(true);

    // limpiar errores anteriores
    setError(null);

    try {
      const searchResults = await searchQuery(query);

      setResults(searchResults);
    } catch (err) {
      console.error(err);

      // limpiar resultados anteriores
      setResults(null);

      // backend muerto / sin conexión
      if (err.name === "TypeError") {
        setError(
          "No se pudo conectar con el backend semántico."
        );
      } else {
        setError(
          "Ocurrió un error durante la búsqueda."
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
  };
}