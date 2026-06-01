import Typewriter from "./Typewriter";
import Thinking from "./Thinking";
import PlayerCard from "./PlayerCard";
import { translations } from "../utils/translations";

export default function ResultsSection({
  results,
  isLoading,
  error,
  source,
  language,
}) {
  const t = translations[language] || translations.es;
  const isDataArray = Array.isArray(results?.data);
  const isDataObject =
    results?.data &&
    typeof results.data === "object" &&
    !Array.isArray(results.data);

  const dataRows = isDataArray ? results.data : [];
  const dataColumns = dataRows.reduce((columns, row) => {
    if (row && typeof row === "object") {
      Object.keys(row).forEach((key) => {
        if (!columns.includes(key)) columns.push(key);
      });
    }
    return columns;
  }, []);

  return (
    <section className="w-full space-y-6 mb-10 min-h-30">
      {error && (
        <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 text-sm">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="flex justify-start">
          <Thinking language={language} />
        </div>
      )}

      {results?.answer && !isLoading && (
        <article className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 shadow-sm">
          <h2 className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500 mb-3">
            {t.answer}
          </h2>
          <p className="text-sm leading-relaxed text-zinc-700 dark:text-zinc-200 whitespace-pre-wrap">
            <Typewriter text={results.answer} speed={20} />
          </p>
        </article>
      )}

      {dataRows.length > 0 && !isLoading && (
        <article className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 shadow-sm">
          <h2 className="text-xs font-semibold tracking-wider uppercase text-zinc-400 dark:text-zinc-500 mb-4">
            {t.data}
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left border-collapse">
              <thead>
                <tr className="border-b border-zinc-200 dark:border-zinc-700">
                  {dataColumns.map((col) => (
                    <th
                      key={col}
                      className="py-2 pr-4 font-medium capitalize text-zinc-500"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dataRows.map((row, i) => (
                  <tr
                    key={i}
                    className="border-b border-zinc-100 dark:border-zinc-700 last:border-0"
                  >
                    {dataColumns.map((col) => (
                      <td
                        key={col}
                        className="py-2 pr-4 text-zinc-700 dark:text-zinc-200 align-top"
                      >
                        {row?.[col] ?? "-"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      )}

      {isDataObject &&
        !isLoading &&
        (results.intent === "ganador_mundial" ? (
          <WorldCupCard data={results.data} language={language} />
        ) : (
          <PlayerCard data={results.data} source={source} language={language} />
        ))}
    </section>
  );
}
