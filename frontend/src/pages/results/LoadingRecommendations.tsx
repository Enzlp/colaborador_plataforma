import { Loader2, Search, Settings, Sparkles } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function LoadingRecommendations() {
  const [step, setStep] = useState(0);
  
  const steps = [
    { icon: Search, text: "Analizando trabajos académicos..." },
    { icon: Settings, text: "Calculando similitudes..." },
    { icon: Sparkles, text: "Generando tus recomendaciones personalizadas..." }
  ];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % steps.length);
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);
  
  const CurrentIcon = steps[step].icon;
  
  return (
    <div className="flex flex-col justify-center items-center p-8 space-y-6">
      {/* Animated icon */}
      <div className="relative">
        <Loader2 className="w-16 h-16 animate-spin" style={{ color: '#00d1b2' }} />
        <CurrentIcon className="w-8 h-8 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" style={{ color: '#00b89c' }} />
      </div>
      
      {/* Progress bar */}
      <div className="w-full max-w-md space-y-3">
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full rounded-full transition-all duration-500"
            style={{ 
              width: `${((step + 1) / steps.length) * 100}%`,
              background: 'linear-gradient(to right, #00d1b2, #00e5c0)'
            }}
          />
        </div>
        
        {/* Current step text */}
        <p className="text-center text-gray-700 font-medium transition-opacity duration-300">
          {steps[step].text}
        </p>
      </div>
      
      {/* Time estimate */}
      <p className="text-sm text-gray-500">
        Esto puede tomar hasta 15 segundos
      </p>
      
      {/* Step indicators */}
      <div className="flex gap-2">
        {steps.map((_, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index <= step ? 'scale-110' : 'bg-gray-300'
            }`}
            style={index <= step ? { backgroundColor: '#00d1b2' } : {}}
          />
        ))}
      </div>
    </div>
  );
}