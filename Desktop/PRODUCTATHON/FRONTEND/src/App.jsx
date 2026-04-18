import { Routes, Route, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import LandingPage from './pages/LandingPage';
import DiscoverPage from './pages/DiscoverPage';
import ResultsPage from './pages/ResultsPage';
import DetailsPage from './pages/DetailsPage';
import EvalsPage from './pages/EvalsPage';
import './App.css';

function App() {
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const [transitionStage, setTransitionStage] = useState('page-enter-active');

  useEffect(() => {
    if (location.pathname !== displayLocation.pathname) {
      setTransitionStage('page-exit-active');
      const timeout = setTimeout(() => {
        setDisplayLocation(location);
        setTransitionStage('page-enter-active');
      }, 300);
      return () => clearTimeout(timeout);
    }
  }, [location, displayLocation]);

  return (
    <div className="app">
      <div className={`page-transition-wrapper ${transitionStage}`}>
        <Routes location={displayLocation}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/discover" element={<DiscoverPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/details/:id" element={<DetailsPage />} />
          <Route path="/evals" element={<EvalsPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
