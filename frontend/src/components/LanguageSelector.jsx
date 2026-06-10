// LanguageSelector.jsx MODIFICADO Y OPTIMIZADO PARA LA BARRA

import React, { useState, useRef, useEffect } from "react";

const CheckIcon = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const ChevronDownIcon = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="6 9 12 15 18 9"></polyline>
  </svg>
);

const SpanishIcon = () => (
  <svg
    width="100%"
    height="100%"
    viewBox="0 0 20 14"
    fill="none"
    aria-hidden="true"
    preserveAspectRatio="xMidYMid slice"
  >
    <rect width="20" height="14" fill="#D52B1E" />
    <rect y="4.67" width="20" height="4.66" fill="#F9D616" />
    <rect y="9.34" width="20" height="4.66" fill="#007A33" />
  </svg>
);

const EnglishIcon = () => (
  <svg
    width="100%"
    height="100%"
    viewBox="0 0 20 14"
    fill="none"
    aria-hidden="true"
    preserveAspectRatio="xMidYMid slice"
  >
    <rect width="20" height="14" fill="#B22234" />
    <path
      d="M0 2H20M0 4H20M0 6H20M0 8H20M0 10H20M0 12H20"
      stroke="#FFFFFF"
      strokeWidth="1"
    />
    <rect width="8.6" height="7.6" fill="#3C3B6E" />
  </svg>
);

const FrenchIcon = () => (
  <svg
    width="100%"
    height="100%"
    viewBox="0 0 20 14"
    fill="none"
    aria-hidden="true"
    preserveAspectRatio="xMidYMid slice"
  >
    <rect width="20" height="14" fill="#FFFFFF" />
    <rect width="6.67" height="14" fill="#0055A4" />
    <rect x="13.33" width="6.67" height="14" fill="#EF4135" />
  </svg>
);

const LanguageIcon = ({ value }) => {
  if (value === "en") return <EnglishIcon />;
  if (value === "fr") return <FrenchIcon />;
  return <SpanishIcon />;
};

export default function LanguageSelector({ language, setLanguage }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Simplificamos los labels a formato corto para que encaje perfecto
  const options = [
    { value: "es", label: "ES", fullTitle: "Españoppl" },
    { value: "en", label: "EN", fullTitle: "English" },
    { value: "fr", label: "FR", fullTitle: "Français" },
  ];

  const selectedOption =
    options.find((option) => option.value === language) || options[0];

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
          bg-transparent pl-1 pr-2 py-1.5 rounded-xl
          text-zinc-500 dark:text-zinc-400
          text-xs font-bold tracking-wider
          hover:text-zinc-800 dark:hover:text-zinc-100
          transition-colors duration-200
          outline-none cursor-pointer shrink-0
        "
      >
        {/* Tu bolita de país aumentada y perfectamente redonda */}
        <div className="w-6 h-6 rounded-full overflow-hidden shrink-0 border border-zinc-200 dark:border-zinc-700 shadow-sm">
          <LanguageIcon value={selectedOption.value} />
        </div>
        <span>{selectedOption.label}</span>
        <div
          className={`transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
        >
          <ChevronDownIcon />
        </div>
      </button>

      {/* Desplegable alineado perfectamente con el botón interno */}
      {isOpen && (
        <div
          className="
          absolute z-30 bottom-full left-0 mb-3 w-40 origin-bottom-left
          bg-white dark:bg-[#1e1e20]
          rounded-xl shadow-2xl
          border border-zinc-200 dark:border-zinc-800
          p-1 flex flex-col gap-0.5
        "
        >
          {options.map((option) => {
            const isSelected = language === option.value;

            return (
              <div
                key={option.value}
                onClick={() => {
                  setLanguage(option.value);
                  setIsOpen(false);
                }}
                className={`
                  flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer
                  transition-colors duration-150 text-xs font-medium
                  hover:bg-zinc-100 dark:hover:bg-[#2a2a2c]
                  ${isSelected ? "bg-zinc-50 dark:bg-[#2a2a2c] text-zinc-900 dark:text-zinc-50" : "text-zinc-500 dark:text-zinc-400"}
                `}
              >
                <div className="w-4 h-4 rounded-full overflow-hidden shrink-0 border border-zinc-200 dark:border-zinc-700">
                  <LanguageIcon value={option.value} />
                </div>

                <span className="flex-1 text-[11px] font-semibold">
                  {option.fullTitle}
                </span>

                {isSelected && (
                  <div className="text-zinc-800 dark:text-zinc-200 shrink-0">
                    <CheckIcon />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
