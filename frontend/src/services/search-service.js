export const searchQuery = async (query, source = "local", language = "es") => {
  const endpoint =
    source === "dbpedia"
      ? "http://localhost:8000/search/dbpedia"
      : "http://localhost:8000/search";

  const payload = source === "dbpedia" ? { query } : { query, language };

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
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