// AutorWorks.tsx
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import LoadingWorks from './LoadingWorks';
import { ExternalLink, ChevronLeft, ChevronRight, BookOpen, SlidersHorizontal } from "lucide-react";


interface Work {
  cited_by_count: number;
  display_name: string;
  doi: string;
  id: string;
  is_paratext: boolean;
  is_retracted: boolean;
  language: string;
  publication_date: string;
  publication_year: number;
  title: string;
  type: string;
}

interface Concept {
  id: string;
  display_name: string;
}

export default function AuthorWorks() {
  const { authorId } = useParams<{ authorId: string }>();
  const [allWorks, setAllWorks] = useState<Work[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [selectedConceptId, setSelectedConceptId] = useState<string>("");
  const location = useLocation();

  const itemsPerPage = 10;

  const totalPages = Math.ceil(allWorks.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentWorks = allWorks.slice(startIndex, endIndex);

  const cList: Concept[] = location.state?.conceptList || [];

  useEffect(() => {
    if (!authorId) return;

    setLoading(true);
    fetch(`http://127.0.0.1:8000/api/authors/${authorId}/works/?limit=100`)
      .then((res) => {
        if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
        return res.json();
      })
      .then((data: { results: Work[]; count: number }) => {
        setAllWorks(data.results);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error al obtener datos:", err);
        setLoading(false);
      });
  }, [authorId]);

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedConceptId]);

  const getWorkTypeColor = (type: string) => {
    if (type.includes("article")) return "bg-blue-100 text-blue-700";
    if (type.includes("proceedings") || type.includes("conference"))
      return "bg-purple-100 text-purple-700";
    if (type.includes("chapter")) return "bg-green-100 text-green-700";
    if (type.includes("preprint")) return "bg-orange-100 text-orange-700";
    return "bg-gray-100 text-gray-700";
  };

  const getPageNumbers = () => {
    const pages = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
      return pages;
    }
    pages.push(1);
    if (currentPage > 3) pages.push("...");
    const start = Math.max(2, currentPage - 1);
    const end = Math.min(totalPages - 1, currentPage + 1);
    for (let i = start; i <= end; i++) pages.push(i);
    if (currentPage < totalPages - 2) pages.push("...");
    pages.push(totalPages);
    return pages;
  };

  const handlePageClick = (page: number) => setCurrentPage(page);
  const handleNext = () => currentPage < totalPages && setCurrentPage((p) => p + 1);
  const handlePrev = () => currentPage > 1 && setCurrentPage((p) => p - 1);

  if (loading) return <LoadingWorks />;


  const fetchFilter = () => {
    if (!authorId) return;

    setLoading(true);

    const params = new URLSearchParams({
      limit: "100",
    });

    if (selectedConceptId) {
      params.append("concept_id", selectedConceptId);
    }

    fetch(`http://127.0.0.1:8000/api/authors/${authorId}/works/?${params.toString()}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
        return res.json();
      })
      .then((data: { results: Work[]; count: number }) => {
        setAllWorks(data.results);
        setCurrentPage(1); // reset paginación
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error al filtrar trabajos:", err);
        setLoading(false);
      });
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">

      {/* Header */}
      <div className="p-4 sm:p-6 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
        {/* Bloque izquierdo */}
        <div className="flex flex-col">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-lg sm:text-xl font-semibold">
              Publicaciones Recientes
            </h2>
          </div>
          <p className="text-gray-600 text-xs sm:text-sm">
            Mostrando página {currentPage} de {totalPages}
          </p>
        </div>

        {/* Bloque derecho */}
        {cList.length > 0 && (
          <div className="flex items-center gap-2">
            <select
              value={selectedConceptId}
              onChange={(e) => setSelectedConceptId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                        focus:outline-none focus:ring-2 focus:ring-teal-500
                        focus:border-transparent bg-white"
            >
              <option value="">Todos los conceptos</option>
              {cList.map((concept) => (
                <option key={concept.id} value={concept.id}>
                  {concept.display_name}
                </option>
              ))}
            </select>
            <button
              className="inline-flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-lg hover:from-teal-600 hover:to-cyan-700 transition-all shadow-md hover:shadow-lg font-medium"
              onClick={fetchFilter}
            >
              <SlidersHorizontal className="w-4 h-4" />
              Filtrar
            </button>
          </div>
        )}
      </div>

      {/* Estado vacío */}
      {!loading && allWorks.length === 0 && (
        <div className="p-8 text-center text-gray-500">
          <p className="text-sm sm:text-base">
            No se encontraron publicaciones para este filtro.
          </p>
          {cList.length > 0 && (
            <p className="mt-2 text-xs text-gray-400">
              Prueba seleccionando otro concepto.
            </p>
          )}
        </div>
      )}

      {/* Contenido solo si hay resultados */}
      {allWorks.length > 0 && (
        <>
          {/* Cards móvil */}
          <div className="block lg:hidden p-4 sm:p-6 space-y-4">
            {currentWorks.map((work) => (
              <div
                key={work.id}
                className="border rounded-2xl p-4 sm:p-5 bg-white shadow-md hover:shadow-lg transition-shadow w-full break-words"
              >
                <h3 className="font-semibold text-sm sm:text-base mb-1">
                  {work.title || work.display_name}
                </h3>

                {work.is_retracted && (
                  <span className="inline-block px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs mb-2">
                    Retractado
                  </span>
                )}

                <p className="text-xs sm:text-sm text-gray-600">
                  <strong>Año:</strong> {work.publication_year || "N/A"}
                </p>

                <p className="text-xs mt-1">
                  <span
                    className={`inline-block px-2 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${getWorkTypeColor(
                      work.type
                    )}`}
                  >
                    {work.type}
                  </span>
                </p>

                <p className="text-xs sm:text-sm text-gray-700 mt-2">
                  <strong>Citas:</strong>{" "}
                  {work.cited_by_count.toLocaleString()}
                </p>

                <div className="mt-3 flex flex-col gap-1 text-xs sm:text-sm">
                  {work.doi && (
                    <a
                      href={
                        work.doi.startsWith("http")
                          ? work.doi
                          : `https://doi.org/${work.doi}`
                      }
                      target="_blank"
                      className="text-teal-600 hover:text-teal-700 inline-flex items-center gap-1"
                    >
                      DOI <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  <a
                    href={work.id}
                    target="_blank"
                    className="text-teal-600 hover:text-teal-700 inline-flex items-center gap-1"
                  >
                    OpenAlex <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>

          {/* Tabla desktop */}
          <div className="hidden lg:block overflow-x-auto">
            <table className="w-full border-collapse min-w-[700px]">
              <thead className="bg-gray-50 border-b border-gray-200 text-left text-sm text-gray-600 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">Título</th>
                  <th className="px-6 py-3">Año</th>
                  <th className="px-6 py-3">Tipo</th>
                  <th className="px-6 py-3">Citas</th>
                  <th className="px-6 py-3">Enlaces</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {currentWorks.map((work) => (
                  <tr
                    key={work.id}
                    className="hover:bg-gray-50 transition-all duration-150"
                  >
                    <td className="px-6 py-4 w-full break-words">
                      {work.title ? (
                        <span
                          dangerouslySetInnerHTML={{
                            __html: work.title
                              .replace(/<mml:/g, "<")
                              .replace(/<\/mml:/g, "</")
                              .replace(/xmlns:mml="[^"]*"/g, "")
                              .replace(/altimg="[^"]*"/g, ""),
                          }}
                        />
                      ) : (
                        <span>{work.display_name}</span>
                      )}
                      {work.is_retracted && (
                        <span className="ml-2 px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">
                          Retractado
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {work.publication_year}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 rounded-full text-sm font-semibold ${getWorkTypeColor(
                          work.type
                        )}`}
                      >
                        {work.type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {work.cited_by_count.toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1 text-sm">
                        {work.doi && (
                          <a
                            href={
                              work.doi.startsWith("http")
                                ? work.doi
                                : `https://doi.org/${work.doi}`
                            }
                            target="_blank"
                            className="text-teal-600 hover:text-teal-700 inline-flex items-center gap-1"
                          >
                            DOI <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                        <a
                          href={work.id}
                          target="_blank"
                          className="text-teal-600 hover:text-teal-700 inline-flex items-center gap-1"
                        >
                          OpenAlex <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-4 sm:px-6 py-3 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-2 sm:gap-4">
            <div className="flex gap-2 w-full sm:w-auto justify-between sm:justify-start">
              <button
                onClick={handlePrev}
                disabled={currentPage === 1}
                className="inline-flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm flex-1 sm:flex-none justify-center"
              >
                <ChevronLeft className="w-4 h-4" />
                <span className="hidden sm:inline">Anterior</span>
              </button>
              <button
                onClick={handleNext}
                disabled={currentPage === totalPages}
                className="inline-flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm flex-1 sm:flex-none justify-center"
              >
                <span className="hidden sm:inline">Siguiente</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 flex justify-center sm:justify-end mt-2 sm:mt-0">
              <div className="flex items-center gap-2 sm:hidden text-xs text-gray-600">
                <span>Página</span>
                <span className="font-semibold">{currentPage}</span>
                <span>de</span>
                <span className="font-semibold">{totalPages}</span>
              </div>
              <div className="hidden sm:flex items-center gap-2 overflow-x-auto no-scrollbar px-1">
                {getPageNumbers().map((page, i) =>
                  typeof page === "number" ? (
                    <button
                      key={i}
                      onClick={() => handlePageClick(page)}
                      className={`w-9 h-9 sm:w-10 sm:h-10 rounded-lg text-sm flex items-center justify-center transition-colors ${
                        currentPage === page
                          ? "bg-teal-500 text-white"
                          : "hover:bg-gray-100 text-gray-700"
                      }`}
                    >
                      {page}
                    </button>
                  ) : (
                    <span key={i} className="px-2 text-gray-500">
                      ...
                    </span>
                  )
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );

}
