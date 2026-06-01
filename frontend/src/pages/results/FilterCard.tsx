import { useState } from "react";
import { SlidersHorizontal } from "lucide-react";
import { Info} from "lucide-react";

type FilterCardProps = {
  filterFunction: (by: string, limit: number, country: string) => void;
};

export default function FilterCard({ filterFunction }: FilterCardProps) {
  const [orderVal, setOrderVal] = useState<string>("sim");
  const [resultLimit, setResultLimit] = useState<number>(50);
  const [countryCode, setCountryCode] = useState<string>("");
  const [showInfoFilter, setShowInfoFilter] = useState(false);

  const infoFilter =
    "Puedes ordenar y filtrar las recomendaciones según la similitud temática, el número de citas o el número de trabajos. También es posible filtrar por país y limitar la cantidad de resultados hasta 200. Estos filtros y el ordenamiento se aplican sobre el total de autores recomendados.";


  const latamCountryCodes: { [key: string]: string } = {
    AR: "Argentina",
    BO: "Bolivia",
    BR: "Brazil",
    CL: "Chile",
    CO: "Colombia",
    CR: "Costa Rica",
    CU: "Cuba",
    DO: "Dominican Republic",
    EC: "Ecuador",
    GT: "Guatemala",
    HN: "Honduras",
    MX: "Mexico",
    NI: "Nicaragua",
    PA: "Panama",
    PE: "Peru",
    PR: "Puerto Rico",
    PY: "Paraguay",
    SV: "El Salvador",
    UY: "Uruguay",
    VE: "Venezuela",
  };

return (
  <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-5 h-full flex flex-col">
    {/* Controles ocupan todo el espacio */}
    <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
      
      {/* Filtrado general arriba */}
      <div className="md:col-span-3 flex items-center gap-2 mb-4">
        <SlidersHorizontal className="w-5 h-5 text-teal-600" />
        <h2 className="text-xl font-bold text-gray-900">Filtros</h2>
        <div
          onMouseEnter={() => setShowInfoFilter(true)}
          onMouseLeave={() => setShowInfoFilter(false)}
          className="relative"
        >
          <button className="text-gray-400 hover:text-teal-600 transition-colors">
            <Info className="w-5 h-5" />
          </button>
          {showInfoFilter && (
            <div className="absolute z-20 w-72 p-3 left-6 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-xs rounded-lg shadow-xl">
              {infoFilter}
            </div>
          )}
        </div>
      </div>

      {/* Ordenamiento */}
      <div>
        <label className="block text-sm text-gray-600 mb-2 font-medium">Ordenar por</label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent bg-white"
          value={orderVal}
          onChange={(e) => setOrderVal(e.target.value)}
        >
          <option value="sim">Similitud</option>
          <option value="cites">Nº de citas</option>
          <option value="works">Nº de trabajos</option>
        </select>
      </div>

      {/* Filtro por país */}
      <div>
        <label className="block text-sm text-gray-600 mb-2 font-medium">País</label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent bg-white"
          value={countryCode}
          onChange={(e) => setCountryCode(e.target.value)}
        >
          <option value="">Todos los países</option>
          {Object.entries(latamCountryCodes).map(([code, name]) => (
            <option key={code} value={code}>
              {name}
            </option>
          ))}
        </select>
      </div>

      {/* Límite de resultados */}
      <div>
        <label className="block text-sm text-gray-600 mb-2 font-medium">
          Máx. resultados ({resultLimit})
        </label>
        <input
          type="range"
          min="10"
          max="200"
          step="10"
          value={resultLimit}
          onChange={(e) =>
            setResultLimit(Math.min(200, Math.max(10, Number(e.target.value))))
          }
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>10</span>
          <span>200</span>
        </div>
      </div>
    </div>

    {/* Botón aplicar */}
    <div className="mt-5 flex justify-end">
      <button
        className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-lg hover:from-teal-600 hover:to-cyan-700 transition-all shadow-md hover:shadow-lg font-medium"
        onClick={() => filterFunction(orderVal, resultLimit, countryCode)}
      >
        <SlidersHorizontal className="w-4 h-4" />
        Aplicar Filtros
      </button>
    </div>
  </div>
);



}