import React, { useState, useRef, useEffect } from "react";
import { translations } from "../utils/translations"; // Importamos las traducciones

const CheckIcon = () => (
  <svg
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const ChevronDownIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="6 9 12 15 18 9"></polyline>
  </svg>
);

export default function SourceSelector({ source, setSource, language }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Obtenemos el diccionario actual
  const t = translations[language] || translations.es;

  // Definimos las opciones dentro para que lean dinámicamente de 't'
  const options = [
    {
      value: "local",
      title: t.localTitle,
      description: t.localDescription,
      isNew: false,
    },
    {
      value: "dbpedia",
      title: t.dbpediaTitle,
      description: t.dbpediaDescription,
      isNew: true,
    },
  ];

  const selectedOption =
    options.find((opt) => opt.value === source) || options[0];

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="
          flex items-center gap-1.5
          bg-transparent
          px-2 py-2
          text-zinc-500 dark:text-zinc-400
          text-sm font-medium
          hover:text-zinc-800 dark:hover:text-zinc-100
          transition-colors duration-200
          outline-none cursor-pointer
        "
      >
        <span>{selectedOption.title}</span>
        <div
          className={`transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
        >
          <ChevronDownIcon />
        </div>
      </button>

      {isOpen && (
        <div
          className="
          absolute z-10 bottom-full mb-2 w-80 origin-bottom-left
          bg-white dark:bg-[#1e1e20]
          rounded-2xl shadow-xl
          border border-zinc-200 dark:border-zinc-700
          p-2 flex flex-col gap-1
        "
        >
          {options.map((opt) => {
            const isSelected = source === opt.value;

            return (
              <div
                key={opt.value}
                onClick={() => {
                  setSource(opt.value);
                  setIsOpen(false);
                }}
                className={`
                  flex items-start gap-3 p-3 rounded-xl cursor-pointer
                  transition-colors duration-150
                  hover:bg-zinc-100 dark:hover:bg-[#2a2a2c]
                  ${isSelected ? "bg-zinc-50 dark:bg-[#2a2a2c]" : ""}
                `}
              >
                <div className="mt-0.5 w-5 shrink-0 text-zinc-800 dark:text-zinc-200">
                  {isSelected && <CheckIcon />}
                </div>

                <div className="flex-1 flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                      {opt.title}
                    </span>

                    {/* ETIQUETA NUEVO TRADUCIDA */}
                    {opt.isNew && (
                      <span
                        className="
                        px-2 py-0.5 text-[10px] font-medium tracking-wide
                        bg-zinc-200 dark:bg-zinc-700
                        text-zinc-700 dark:text-zinc-300
                        rounded-full
                      "
                      >
                        {t.newBadge}
                      </span>
                    )}
                  </div>

                  <span className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                    {opt.description}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
