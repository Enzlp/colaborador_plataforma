import { Info, Award } from "lucide-react";
import { useState } from "react";

type MetricsCardProps = {
  peso1: number;
  peso2: number;
  setPeso1: React.Dispatch<React.SetStateAction<number>>;
  setPeso2: React.Dispatch<React.SetStateAction<number>>;
  fetchFunction: () => Promise<void>;
};

export default function MetricsCard({
  peso1,
  peso2,
  setPeso1,
  setPeso2,
  fetchFunction,
}: MetricsCardProps) {
  const [showInfo, setShowInfo] = useState(false);

  const handlePeso1 = (v: number) => {
    v = Math.min(1, Math.max(0, v));
    setPeso1(v);
    setPeso2(1 - v);
  };

  const handlePeso2 = (v: number) => {
    v = Math.min(1, Math.max(0, v));
    setPeso2(v);
    setPeso1(1 - v);
  };

  const infoMetrics =
    "Este modelo combina un enfoque basado en contenido (afinidad temática) y un enfoque de red de colaboración. Los scores se normalizan y se combinan según los pesos que definas, permitiendo priorizar recomendaciones por interés o por red. Los pesos deben sumar 1.";

return (
  <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-5 w-full h-full flex flex-col">
    {/* Contenido superior: header + sliders */}
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Award className="w-5 h-5 text-purple-600" />
        <h3 className="text-xl font-bold text-gray-900">Ajuste de Pesos</h3>
        <div
          onMouseEnter={() => setShowInfo(true)}
          onMouseLeave={() => setShowInfo(false)}
          className="relative"
        >
          <button className="text-gray-400 hover:text-purple-600 transition-colors">
            <Info className="w-4 h-4" />
          </button>
          {showInfo && (
            <div className="absolute z-20 w-72 p-3 left-6 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-xs rounded-lg shadow-xl">
              {infoMetrics}
            </div>
          )}
        </div>
      </div>

      {/* Sliders y suma */}
      <div className="space-y-4 flex-1">
        {/* Afinidad temática */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm text-gray-600">Afinidad temática</label>
            <span className="text-sm text-teal-700">{peso1.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={peso1}
            onChange={(e) => handlePeso1(Number(e.target.value))}
            className="w-full h-2 bg-gradient-to-r from-teal-200 to-teal-500 rounded-lg appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #5eead4 0%, #14b8a6 ${
                peso1 * 100
              }%, #e5e7eb ${peso1 * 100}%, #e5e7eb 100%)`,
            }}
          />
        </div>

        {/* Red de colaboración */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm text-gray-600">Red de colaboración</label>
            <span className="text-sm text-purple-700">{peso2.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={peso2}
            onChange={(e) => handlePeso2(Number(e.target.value))}
            className="w-full h-2 bg-gradient-to-r from-purple-200 to-purple-500 rounded-lg appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #e9d5ff 0%, #a855f7 ${
                peso2 * 100
              }%, #e5e7eb ${peso2 * 100}%, #e5e7eb 100%)`,
            }}
          />
        </div>

      </div>
    </div>

    {/* Botón aplicar abajo */}
    <div className="mt-4 flex justify-end">
      <button
        className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-lg hover:from-teal-600 hover:to-cyan-700 transition-all shadow-md hover:shadow-lg font-medium"
        onClick={fetchFunction}
      >
        Aplicar Pesos
      </button>
    </div>
  </div>
);

}

