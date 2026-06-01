import { Loader2, User, Award, BookOpen } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function LoadingAuthor() {
  const [step, setStep] = useState(0);
  
  const steps = [
    { icon: User, text: "Cargando perfil del autor..." },
    { icon: Award, text: "Obteniendo métricas..." },
    { icon: BookOpen, text: "Preparando información..." }
  ];
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % steps.length);
    }, 1500);
    
    return () => clearInterval(interval);
  }, []);
  
  const CurrentIcon = steps[step].icon;
  
  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="flex flex-col items-center space-y-4">
        {/* Animated icon */}
        <div className="relative">
          <Loader2 className="w-12 h-12 sm:w-16 sm:h-16 animate-spin" style={{ color: '#00d1b2' }} />
          <CurrentIcon className="w-6 h-6 sm:w-8 sm:h-8 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" style={{ color: '#00b89c' }} />
        </div>
        
        {/* Current step text */}
        <p className="text-center text-gray-700 text-sm sm:text-base font-medium transition-opacity duration-300">
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
    </div>
  );
}