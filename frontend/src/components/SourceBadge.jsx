import { translations } from "../utils/translations";

function SourceBadge({ source, language }) {
  const t = translations[language] || translations.es;
  return (
    <div
      className={`
        mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium
        ${
          source === "dbpedia"
            ? "bg-yellow-500/10 text-yellow-500 border border-yellow-500/20"
            : "bg-blue-500/10 text-blue-500 border border-blue-500/20"
        }
      `}
    >
      {source === "dbpedia" ? t.dbpedia : t.ownOntology}
    </div>
  );
}

export default SourceBadge;
