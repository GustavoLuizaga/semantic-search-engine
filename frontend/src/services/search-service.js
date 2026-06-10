export const searchQuery = async (query, source = "local", language = "es", mode = "online") => {
  const endpoint =
    source === "dbpedia"
      ? "http://localhost:8000/search/dbpedia"
      : "http://localhost:8000/search";

  try {
    // Armamos el body incluyendo el mode si es dbpedia
    const bodyData = { query: query, language: language };
    if (source === "dbpedia") {
      bodyData.mode = mode;
    }

    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(bodyData), // Aquí ya enviamos el mode
    });

    const result = await response.json();

    return {
      answer: result.answer,
      data: result.data,
    };
  } catch (error) {
    throw error;
  }
};

export const checkOfflineStatus = async () => {
  try {
    const response = await fetch("http://localhost:8000/search/dbpedia/offline-status");
    if (!response.ok) return false;
    const data = await response.json();
    return data.offline_available;
  } catch (error) {
    console.error("Error verificando Fuseki:", error);
    return false;
  }
};