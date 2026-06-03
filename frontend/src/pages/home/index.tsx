import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, User, X, Sparkles } from 'lucide-react';
import AuthorInput from "./AuthorInput";
import ConceptInput from "./ConceptInput";

interface Concept {
  id: number;
  display_name: string;
}

/**
 * Pagina principal de la plataforma. Contiene modos de búsqueda, importa inputs para búsqueda y agrega etiquetas de conceptos seleccionados. También posee boton
 * que redirige a la página de resultados.
 */
export default function Home() {
  const [selected, setSelected] = useState<Concept[]>([]);
  const [authorVal, setAuthorVal] = useState<string>("");
  const [searchMode, setSearchMode] = useState<'both' | 'concepts' | 'author'>('both');
  const [authorDisplayName, setAuthorDisplayName] = useState<string>("");
  
  const navigate = useNavigate();

  const handleSearchModeChange = (mode: 'both' | 'concepts' | 'author') => {
    setSearchMode(mode);
  };

  const searchRecommended = (e: React.FormEvent) => {
    e.preventDefault();

    let conceptList: Concept[] = [];
    let authorId: string = "";

    if (searchMode === 'concepts') {
      conceptList = selected;
    } else if (searchMode === 'author') {
      authorId = authorVal;
    } else if (searchMode === 'both') {
      conceptList = selected;
      authorId = authorVal;
    }

    if (conceptList.length > 0 || authorId !== "") {
      navigate("/results", { state: { conceptList, authorId } });
    }
  };

  const loadAuthorConcepts = () => {
    if (!authorVal) return;
    const cleanId = authorVal.includes("openalex.org/")
      ? authorVal.split("openalex.org/")[1]
      : authorVal;
    fetch(`http://127.0.0.1:8000/api/authors/${cleanId}/concepts/`)
      .then((res) => res.json())
      .then((data: Concept[]) => {
        const nuevos = data.filter(
          (c) => !selected.some((s) => s.id === c.id)
        );
        setSelected((prev) => [...prev, ...nuevos]);
      })
      .catch((err) => console.error(err));
  };

  const isSearchEnabled = () => {
    if (searchMode === 'both') {
      return selected.length > 0 || authorVal.trim().length > 0;
    }
    if (searchMode === 'concepts') {
      return selected.length > 0;
    }
    if (searchMode === 'author') {
      return authorVal.trim().length > 0;
    }
    return false;
  };

  const handleRemoveConcept = (conceptToRemove: Concept) => {
    setSelected(selected.filter(c => c.id !== conceptToRemove.id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-cyan-50">
      <div className="flex items-center justify-center p-4 sm:p-6 md:p-8" style={{ minHeight: 'calc(100vh - 89px)' }}>
        <div className="w-full max-w-4xl">
          <div className="text-center mb-8 sm:mb-10 px-2">
            <div className="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-2xl mb-4 sm:mb-6 shadow-xl">
              <Sparkles className="w-7 h-7 sm:w-8 sm:h-8 text-white" />
            </div>
            <h1 className="mb-3 bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent text-2xl sm:text-3xl md:text-4xl font-bold">
              Encuentra investigadores en IA
            </h1>
            <p className="text-gray-600 text-sm sm:text-base md:text-lg max-w-2xl mx-auto">
              Esta plataforma te ayuda a descubrir investigadores en IA en Latinoamérica con los que podrías colaborar, 
              a partir de intereses temáticos y redes reales de coautoría, utilizando datos de OpenAlex.
            </p>
          </div>

          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-4 sm:p-6 mb-4 sm:mb-6">
            <div className="flex items-center gap-2 mb-3 sm:mb-4">
              <div className="w-1 h-5 sm:h-6 bg-gradient-to-b from-teal-500 to-cyan-600 rounded-full"></div>
              <label className="text-gray-700 font-medium text-sm sm:text-base">Selecciona tu método de búsqueda</label>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
              <button
                type="button"
                onClick={() => handleSearchModeChange('both')}
                className={`group p-4 sm:p-5 rounded-xl border-2 transition-all duration-200 ${
                  searchMode === 'both'
                    ? 'border-teal-500 bg-gradient-to-br from-teal-50 to-cyan-50 shadow-md scale-105'
                    : 'border-gray-200 bg-white hover:border-teal-300 hover:shadow-md hover:scale-102'
                }`}
              >
                <div className={`flex items-center justify-center gap-2 mb-2 sm:mb-3 ${
                  searchMode === 'both' ? 'text-teal-600' : 'text-gray-400 group-hover:text-teal-500'
                }`}>
                  <Search className="w-4 h-4 sm:w-5 sm:h-5" />
                  <User className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <div className={`font-semibold text-sm sm:text-base ${searchMode === 'both' ? 'text-teal-900' : 'text-gray-900'}`}>Búsqueda Híbrida</div>
                <div className="text-gray-500 text-xs sm:text-sm mt-1">Conceptos + Autor</div>
              </button>

              <button
                type="button"
                onClick={() => handleSearchModeChange('concepts')}
                className={`group p-4 sm:p-5 rounded-xl border-2 transition-all duration-200 ${
                  searchMode === 'concepts'
                    ? 'border-teal-500 bg-gradient-to-br from-teal-50 to-cyan-50 shadow-md scale-105'
                    : 'border-gray-200 bg-white hover:border-teal-300 hover:shadow-md hover:scale-102'
                }`}
              >
                <div className={`flex items-center justify-center gap-2 mb-2 sm:mb-3 ${
                  searchMode === 'concepts' ? 'text-teal-600' : 'text-gray-400 group-hover:text-teal-500'
                }`}>
                  <Search className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <div className={`font-semibold text-sm sm:text-base ${searchMode === 'concepts' ? 'text-teal-900' : 'text-gray-900'}`}>Por Conceptos</div>
                <div className="text-gray-500 text-xs sm:text-sm mt-1">Temas de interés</div>
              </button>

              <button
                type="button"
                onClick={() => handleSearchModeChange('author')}
                className={`group p-4 sm:p-5 rounded-xl border-2 transition-all duration-200 ${
                  searchMode === 'author'
                    ? 'border-teal-500 bg-gradient-to-br from-teal-50 to-cyan-50 shadow-md scale-105'
                    : 'border-gray-200 bg-white hover:border-teal-300 hover:shadow-md hover:scale-102'
                }`}
              >
                <div className={`flex items-center justify-center gap-2 mb-2 sm:mb-3 ${
                  searchMode === 'author' ? 'text-teal-600' : 'text-gray-400 group-hover:text-teal-500'
                }`}>
                  <User className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <div className={`font-semibold text-sm sm:text-base ${searchMode === 'author' ? 'text-teal-900' : 'text-gray-900'}`}>Por Investigador</div>
                <div className="text-gray-500 text-xs sm:text-sm mt-1">Nombre de autor</div>
              </button>
            </div>
          </div>

          <form onSubmit={searchRecommended} className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-100 p-5 sm:p-6 md:p-8">
            {(searchMode === 'both' || searchMode === 'concepts') && (
              <div className="mb-6 sm:mb-8">
                <div className="flex items-center gap-2 mb-2 sm:mb-3">
                  <Search className="w-4 h-4 text-teal-600" />
                  <label className="text-gray-700 font-medium text-sm sm:text-base">
                    Conceptos de interés
                  </label>
                </div>
                <ConceptInput 
                  selected={selected}
                  onSelectedChange={setSelected}
                />
                
                {selected.length > 0 && (
                  <div className="mt-3 sm:mt-4 p-3 sm:p-4 bg-gradient-to-br from-teal-50 to-cyan-50 rounded-xl border border-teal-100">
                    <div className="flex items-center justify-between mb-2 sm:mb-3">
                      <div className="text-xs sm:text-sm text-teal-700">
                        <span className="font-medium">{selected.length}</span> concepto{selected.length !== 1 ? 's' : ''} seleccionado{selected.length !== 1 ? 's' : ''}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selected.map((concept) => (
                        <span
                          key={concept.id}
                          className="inline-flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1 sm:py-1.5 bg-white text-teal-700 rounded-lg border border-teal-200 shadow-sm text-xs sm:text-sm"
                        >
                          <span className="break-all">{concept.display_name}</span>
                          <button
                            type="button"
                            onClick={() => handleRemoveConcept(concept)}
                            className="hover:bg-teal-100 rounded-full p-0.5 transition-colors flex-shrink-0"
                            aria-label={`Remover ${concept.display_name}`}
                          >
                            <X className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {searchMode === 'both' && (
              <div className="flex items-center gap-3 sm:gap-4 mb-6 sm:mb-8">
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
                <span className="text-gray-400 bg-white px-2 sm:px-3 py-1 rounded-full border border-gray-200 text-xs sm:text-sm">
                  y/o
                </span>
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
              </div>
            )}

            {(searchMode === 'both' || searchMode === 'author') && (
              <div className="mb-6 sm:mb-8">
                <div className="flex items-center gap-2 mb-2 sm:mb-3">
                  <User className="w-4 h-4 text-teal-600" />
                  <label htmlFor="author" className="text-gray-700 font-medium text-sm sm:text-base">
                    Nombre del investigador
                  </label>
                </div>
                <AuthorInput
                  value={authorVal}
                  displayName={authorDisplayName}
                  onChangeValue={(id, name) => {
                    setAuthorVal(id);
                    setAuthorDisplayName(name);
                  }}
                />
              </div>
            )}

            {searchMode === 'both' && (
              <div className="mb-6 sm:mb-8">
                <button
                  type="button"    
                  disabled={authorVal === ""}
                  className="w-full py-2.5 sm:py-3 px-4 bg-indigo-500 hover:bg-indigo-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl transition-all shadow-md hover:shadow-lg disabled:shadow-none font-medium text-sm sm:text-base"
                  onClick={loadAuthorConcepts}
                >
                  Cargar conceptos asociados al investigador
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={!isSearchEnabled()}
              className="w-full py-3 sm:py-4 px-4 sm:px-6 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-xl hover:from-teal-600 hover:to-cyan-700 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl disabled:shadow-none font-medium text-sm sm:text-base"
            >
              <Search className="w-4 h-4 sm:w-5 sm:h-5" />
              <span>Recomendar investigadores</span>
            </button>

            <div className="mt-4 sm:mt-5 p-3 sm:p-4 bg-gray-50 rounded-xl border border-gray-200">
              <p className="text-gray-600 text-xs sm:text-sm text-center">
                {searchMode === 'both' && '💡 Combina conceptos y autor para resultados más precisos y personalizados'}
                {searchMode === 'concepts' && '💡 Agrega múltiples conceptos para ampliar tu búsqueda de investigadores'}
                {searchMode === 'author' && '💡 Encuentra investigadores con redes de colaboración relacionadas'}
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}