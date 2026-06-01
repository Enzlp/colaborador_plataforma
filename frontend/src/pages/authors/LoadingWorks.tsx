import { Loader2, FileText, BookOpen, Search } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function LoadingWorks() {
  const [step, setStep] = useState(0);
  
  const steps = [
    { icon: Search, text: "Buscando publicaciones..." },
    { icon: FileText, text: "Cargando trabajos académicos..." },
    { icon: BookOpen, text: "Preparando resultados..." }
  ];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % steps.length);
    }, 1500);
    
    return () => clearInterval(interval);
  }, []);
  
  const CurrentIcon = steps[step].icon;
  
  return (
    <div className="flex flex-col rounded-xl p-6 items-center justify-center space-y-4">
      {/* Animated icon */}
      <div className="relative">
        <Loader2 className="w-12 h-12 animate-spin" style={{ color: '#00d1b2' }} />
        <CurrentIcon className="w-6 h-6 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" style={{ color: '#00b89c' }} />
      </div>
      
      {/* Current step text */}
      <p className="text-center text-gray-700 text-sm font-medium transition-opacity duration-300">
        {steps[step].text}
      </p>
      
      {/* Step indicators */}
      <div className="flex gap-2">
        {steps.map((_, index) => (
          <div
            key={index}
            className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
              index <= step ? 'scale-110' : 'bg-gray-300'
            }`}
            style={index <= step ? { backgroundColor: '#00d1b2' } : {}}
          />
        ))}
      </div>
    </div>
  );
}