import { useEffect, useState, useRef } from "react";

interface Concept {
  id: number;
  display_name: string;
}

type ConceptInputProps = {
  selected: Concept[];
  onSelectedChange: (concepts: Concept[]) => void;
};

function ConceptInput({ selected, onSelectedChange }: ConceptInputProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Concept[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const itemRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const cacheRef = useRef<Map<string, Concept[]>>(new Map());

  /* Autocomplete con debounce + cache */
  useEffect(() => {
    if (!query) {
      setResults([]);
      setIsOpen(false);
      setLoading(false);
      return;
    }

    // 1️⃣ Cache inmediato (UX instantánea)
    if (cacheRef.current.has(query)) {
      const cached = cacheRef.current.get(query)!;
      const filtered = cached.filter(
        (item) => !selected.some((s) => s.id === item.id)
      );
      setResults(filtered);
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    setLoading(true);

    const timeoutId = setTimeout(() => {
      fetch(
        `http://127.0.0.1:8000/api/concept/?search=${query}`,
        { signal: controller.signal }
      )
        .then((res) => res.json())
        .then((data: Concept[]) => {
          cacheRef.current.set(query, data); // 2️⃣ cache
          const filtered = data.filter(
            (item) => !selected.some((s) => s.id === item.id)
          );
          setResults(filtered);
          setHighlightedIndex(-1);
        })
        .catch((err) => {
          if (err.name !== "AbortError") console.error(err);
        })
        .finally(() => {
          setLoading(false);
        });
    }, 300);

    return () => {
      controller.abort();
      clearTimeout(timeoutId);
    };
  }, [query, selected]);

  /* Auto-scroll */
  useEffect(() => {
    if (highlightedIndex >= 0 && itemRefs.current[highlightedIndex]) {
      itemRefs.current[highlightedIndex]?.scrollIntoView({
        block: "nearest",
        behavior: "smooth"
      });
    }
  }, [highlightedIndex]);

  const addTag = (concept: Concept) => {
    onSelectedChange([...selected, concept]);
    setQuery("");
    setResults([]);
    setIsOpen(false);
    setHighlightedIndex(-1);
  };


  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || results.length === 0) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;

      case "ArrowUp":
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;

      case "Enter":
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < results.length) {
          addTag(results[highlightedIndex]);
        }
        break;

      case "Escape":
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  return (
    <div className="w-full">
      <label htmlFor="concepts" className="block mb-2 text-gray-700 text-sm sm:text-base">
        Conceptos de interés
      </label>
      
      <div className="relative">
        <input
          id="concepts"
          type="text"
          value={query}
          onChange={(e) => {
            const val = e.target.value;
            setQuery(val);

            if (val === "") {
              setIsOpen(false);
              setResults([]);
              return;
            }

            setIsOpen(true);
            setLoading(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder="Escribe un concepto en inglés..."
          className="w-full pl-4 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none text-sm sm:text-base"
        />
        
        {isOpen && (
          <div className="absolute top-full z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {loading && (
              <div className="px-4 py-2 text-gray-400 text-sm sm:text-base">
                Buscando conceptos…
              </div>
            )}

            {!loading && results.length === 0 && (
              <div className="px-4 py-2 text-gray-400 text-sm sm:text-base">
                Sin resultados
              </div>
            )}

            {!loading &&
              results.map((concept, index) => (
                <button
                  key={concept.id}
                  ref={(el) => {
                    itemRefs.current[index] = el;
                  }}
                  type="button"
                  onClick={() => addTag(concept)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={`w-full text-left px-4 py-2 transition-colors text-sm sm:text-base ${
                    index === highlightedIndex
                      ? "bg-teal-100"
                      : "hover:bg-teal-50"
                  }`}
                >
                  {concept.display_name}
                </button>
              ))}
          </div>
        )}
      </div>

      
    </div>
  );
}

export default ConceptInput;