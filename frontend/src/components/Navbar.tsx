import { useNavigate } from "react-router-dom";
import { HelpCircle, Globe } from 'lucide-react';

function Navbar() {
  const navigate = useNavigate();
  return (
    <nav className="bg-white/80 backdrop-blur-sm border-b border-gray-200 px-6 py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')} >
                <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg">
                    <Globe className="w-6 h-6 text-white" />
                    </div>
                    <div>
                    <span className="text-teal-600 block">Colaborador IA</span>
                    <span className="text-xs text-gray-500">Red Académica Latinoamericana</span>
                </div>
            </div>
            
            <a 
                href='/about'
                className='w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 border-gray-300 flex items-center justify-center hover:border-teal-500 hover:text-teal-500 transition-colors'
                aria-label='informacion'>
                <HelpCircle className='w-4 h-4 sm:w-5 sm:h-5' />
            </a>
        </div>
    </nav>

  );
}

export default Navbar;