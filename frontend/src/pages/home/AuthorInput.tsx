import { useEffect, useState, useRef } from "react";

interface Author {
  author_id: string;
  display_name: string;
}

type AuthorInputProps = {
  value?: string;          // author_id
  displayName?: string;    // nombre del autor seleccionado
  onChangeValue: (authorId: string, displayName: string) => void;
};

function AuthorInput({ onChangeValue, value, displayName }: AuthorInputProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Author[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [hasSelected, setHasSelected] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const itemRefs = useRef<(HTMLLIElement | null)[]>([]);
  const cacheRef = useRef<Map<string, Author[]>>(new Map());

  /* Reset cuando el valor externo se limpia */
  useEffect(() => {
    // Si hay un autor seleccionado, mostrar su display_name
    if (displayName) {
      setQuery(displayName);
      setHasSelected(true);
      setIsOpen(false);
    }

    // Solo resetear si value es vacío
    if (!value) {
      setQuery("");
      setResults([]);
      setHighlightedIndex(-1);
      setHasSelected(false);
      setIsOpen(false);
      setLoading(false);
    }
  }, [value, displayName]);


  /* Autocomplete con debounce + cache */
  useEffect(() => {
    if (hasSelected || !query) return;

    // Limpiar resultados viejos al empezar nueva búsqueda
    setResults([]);

    // 1️⃣ Cache inmediato (UX instantánea)
    if (cacheRef.current.has(query)) {
      setResults(cacheRef.current.get(query)!);
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    let isCurrentQuery = true; 

    setLoading(true);

    const timeoutId = setTimeout(() => {
      fetch(
        `http://127.0.0.1:8000/api/authorsearch/?search=${query}`,
        { signal: controller.signal }
      )
        .then((res) => res.json())
        .then((data: Author[]) => {
          // Solo actualizar si este query sigue siendo el actual
          if (isCurrentQuery) {
            cacheRef.current.set(query, data); // 2️⃣ cache
            setResults(data);
            setHighlightedIndex(-1);
          }
        })
        .catch((err) => {
          if (err.name !== "AbortError") console.error(err);
        })
        .finally(() => {
          if (isCurrentQuery) {
            setLoading(false);
          }
        });
    }, 50);

    return () => {
      isCurrentQuery = false; 
      controller.abort();
      clearTimeout(timeoutId);
    };
  }, [query, hasSelected]);

  /* Auto-scroll */
  useEffect(() => {
    if (highlightedIndex >= 0 && itemRefs.current[highlightedIndex]) {
      itemRefs.current[highlightedIndex]?.scrollIntoView({
        block: "nearest",
      });
    }
  }, [highlightedIndex]);

  const handleSelect = (author: Author) => {
    setHasSelected(true);
    onChangeValue(author.author_id, author.display_name); 
    setQuery(author.display_name);
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
        if (highlightedIndex >= 0) {
          handleSelect(results[highlightedIndex]);
        }
        break;

      case "Escape":
        setIsOpen(false);
        break;
    }
  };

  return (
    <div className="w-full relative">
      <input
        type="text"
        placeholder="Ej: María García, Juan Pérez..."
        value={query}
        onChange={(e) => {
          const val = e.target.value;
          setHasSelected(false);
          setQuery(val);

          if (val === "") {
            onChangeValue("", "");
            setIsOpen(false);
            setResults([]);
            setLoading(false);
            return;
          }

          setIsOpen(true);
          setLoading(true);
          setResults([]); // Limpiar resultados viejos inmediatamente
        }}
        onKeyDown={handleKeyDown}
        className="
          w-full px-3 sm:px-4 py-2.5 sm:py-3
          border border-gray-300 rounded-lg
          focus:ring-2 focus:ring-teal-500
          outline-none
          text-sm sm:text-base
        "
      />

      {isOpen && (
        <ul className="
          absolute top-full left-0 w-full
          bg-white border border-gray-300
          rounded-b-lg shadow-md mt-1
          max-h-48 sm:max-h-64 overflow-y-auto z-20
        ">
          {loading && (
            <li className="px-3 py-2 text-gray-400 text-sm sm:text-base">
              Buscando autores…
            </li>
          )}

          {!loading && results.length === 0 && (
            <li className="px-3 py-2 text-gray-400 text-sm sm:text-base">
              Sin resultados
            </li>
          )}

          {!loading &&
            results.map((item, index) => (
              <li
                key={item.author_id}
                ref={(el) => {itemRefs.current[index] = el}}
                className={`px-3 py-2 cursor-pointer text-sm sm:text-base ${
                  index === highlightedIndex
                    ? "bg-teal-100"
                    : "hover:bg-gray-100"
                }`}
                onClick={() => handleSelect(item)}
                onMouseEnter={() => setHighlightedIndex(index)}
              >
                {item.display_name}
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}

export default AuthorInput;