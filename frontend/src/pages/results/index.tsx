import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import RecommendedCard from "./RecommendedCard";
import FilterCard from "./FilterCard";
import MetricsCard from "./MetricsCard";
import { Info, TrendingUp, ChevronRight, Globe } from "lucide-react";


interface Concept {
  id: string;
  display_name: string;
}

type ConceptScore = {
  concept_id: string;
  score: number;
  display_name: string;
};

type Recommendation = {
  author_id: string;
  orcid: string | null;
  display_name: string;
  country_code: string;
  institution_name: string;
  similarity_score: number;
  cb_score: number;
  cf_score: number;
  works_count: number;
  cited_by_count: number;
  top_concepts: ConceptScore[];
};

/**
 * Página de resultados de recomendaciones. Contiene los componentes de filtros y ajuste de pesos. Y la tabla de resultados. 
 */
export default function Results() {
  const location = useLocation();

  const [loading, setLoading] = useState(true);
  const [totalResult, setTotalResult] = useState(0);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  const [conceptList, setConceptList] = useState<Concept[]>([]);
  const [authorId, setAuthorId] = useState("");

  const [peso1, setPeso1] = useState(0.5);
  const [peso2, setPeso2] = useState(0.5);

  const [currentOrderBy, setCurrentOrderBy] = useState("sim");
  const [currentLimit, setCurrentLimit] = useState(50);
  const [currentCountry, setCurrentCountry] = useState("");

  const [showInfoRec, setShowInfoRec] = useState(false);

  const infoRecommendations =
    "Las recomendaciones se generan combinando afinidad temática y la red de colaboración del autor seleccionado. Dependiendo de tu elección, se usa un modelo individual o un sistema híbrido. Los scores están normalizados para poder compararlos.";

  useEffect(() => {
    if (!location.state) return;

    const cList: Concept[] = location.state.conceptList ?? [];
    const aId: string = location.state.authorId ?? "";

    if (cList.length > 0) setConceptList(cList);
    if (aId !== "") setAuthorId(aId);
  }, []);


const fetchRecommendations = async (overrides: Partial<any> = {}) => {
  try {
    setLoading(true);
    setRecommendations([]); 

    const payload: any = {
      order_by: currentOrderBy,
      limit: currentLimit,
      ...overrides, 
    };

    if (conceptList.length > 0) payload.concept_vector = conceptList;
    if (authorId !== "") payload.author_id = authorId;

    const country = overrides.country_code !== undefined
      ? overrides.country_code
      : currentCountry;
    if (country) payload.country_code = country;

    if (conceptList.length > 0 && authorId !== "") {
      payload.alpha = peso1;
      payload.beta = peso2;
    }

    const response = await fetch("http://127.0.0.1:8000/api/recommendation/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error(`HTTP error ${response.status}`);

    const data = await response.json();
    setRecommendations(data.recommendations);
    setTotalResult(data.total_recommendations);
  } catch (err) {
    console.error(err);
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    if (conceptList.length === 0 && authorId === "") return;
    fetchRecommendations();
  }, [conceptList, authorId]);

  const applyFilters = (by: string, limit: number, country: string) => {
    setCurrentOrderBy(by);
    setCurrentLimit(limit);
    setCurrentCountry(country);

    fetchRecommendations({
      order_by: by,
      limit,
      country_code: country || undefined,
    });
  };

  const weightedFetch = async () => {
    fetchRecommendations({
      alpha: peso1,
      beta: peso2,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-teal-50 px-4 md:px-8 py-6">
      <div className="max-w-7xl mx-auto">

        <div className="mb-6 bg-white rounded-2xl shadow-lg border border-gray-100 p-6">

          <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
            <span>Inicio</span>
            <ChevronRight className="w-4 h-4" />
            <span className="text-teal-600 font-medium">Resultados</span>
          </div>

          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
            Investigadores Recomendados
          </h1>

          <p className="mb-4">
            Los investigadores se muestran con un porcentaje que indica su relevancia según tu búsqueda.
          </p>

          <div className="flex items-center gap-2 text-gray-600">
            <TrendingUp className="w-5 h-5 text-teal-600" />
            <p className="text-sm md:text-base">
              Mostrando{" "}
              <span className="font-bold text-teal-700">{totalResult}</span>{" "}
              resultados
            </p>

            <div
              onMouseEnter={() => setShowInfoRec(true)}
              onMouseLeave={() => setShowInfoRec(false)}
              className="relative ml-3"
            >
              <button className="text-gray-400 hover:text-teal-600">
                <Info className="w-5 h-5" />
              </button>

              {showInfoRec && (
                <div className="absolute z-20 w-72 p-3 left-6 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-xs rounded-lg shadow-xl">
                  {infoRecommendations}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="mb-6 flex flex-col lg:flex-row gap-6 items-stretch">

          <div className="w-full lg:w-2/3">
            <FilterCard filterFunction={applyFilters} />
          </div>

          {conceptList.length > 0 && authorId !== "" ? (
            <div className="w-full lg:w-1/3">
              <MetricsCard
                peso1={peso1}
                peso2={peso2}
                setPeso1={setPeso1}
                setPeso2={setPeso2}
                fetchFunction={weightedFetch}
              />
            </div>
          ) : (
            <div className="rounded-2xl shadow-md border border-gray-100 w-full lg:w-1/3 flex bg-gradient-to-r from-teal-500 to-cyan-600">
              <div className="p-6 flex items-center gap-4">
                <p className="text-white text-sm">
                  Usa la búsqueda híbrida para ajustar los parámetros del modelo.
                </p>
                <Globe className="w-12 h-12 text-white opacity-80" />
              </div>
            </div>
          )}
        </div>

        <RecommendedCard recs={recommendations} loading={loading} />
      </div>
    </div>
  );
}
