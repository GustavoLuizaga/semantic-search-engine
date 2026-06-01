import { translations } from "../utils/translations";

export default function Thinking({ language }) {
  const t = translations[language] || translations.es;

  return (
    <div
      className="flex items-center gap-3 px-4 py-3 rounded-2xl 
                 bg-zinc-100/80 dark:bg-zinc-800/80 
                 border border-zinc-200 dark:border-zinc-700
                 backdrop-blur-sm shadow-sm w-fit"
    >
      <div className="flex gap-1">
        <span className="w-2 h-2 rounded-full bg-zinc-400 animate-pulse"></span>
        <span className="w-2 h-2 rounded-full bg-zinc-400 animate-pulse delay-150"></span>
        <span className="w-2 h-2 rounded-full bg-zinc-400 animate-pulse delay-300"></span>
      </div>

      <span className="text-sm text-zinc-500 dark:text-zinc-400">
        {t.thinking}
      </span>
    </div>
  );
}
