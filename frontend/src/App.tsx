import './App.css'
import Navbar from './components/Navbar'
import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import Home from './pages/home/index';
import Results from './pages/results';
import Authors from './pages/authors';
import About from './pages/about';

function App() {
  return (
    <Router>
      <div className="flex flex-col w-full h-full">
        <Navbar />

        <Routes>
          <Route path = "/" element = {<Home />} />
          <Route path="/results" element={<Results />} />
          <Route path="/authors/:authorId" element={<Authors />}/>
          <Route path="/about" element={<About />}/>
        </Routes>
      </div>
    </Router>
  )
}

export default App
