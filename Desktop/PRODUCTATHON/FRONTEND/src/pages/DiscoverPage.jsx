import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './DiscoverPage.css';

const examplePrompts = [
  "Work trip in Delhi with fast Wi-Fi",
  "Family weekend with pool under ₹5000",
  "Cheap stay near city center",
  "Luxury hotel for a special occasion",
  "Quiet place near the airport under ₹6000",
];

export default function DiscoverPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [loaded, setLoaded] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    setLoaded(true);
    inputRef.current?.focus();
  }, []);

  const handleSearch = () => {
    if (!query.trim()) return;
    setIsSearching(true);
    // Simulate a brief loading delay for UX
    setTimeout(() => {
      navigate('/results', { state: { query: query.trim() } });
    }, 800);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleChipClick = (prompt) => {
    setQuery(prompt);
    inputRef.current?.focus();
  };

  return (
    <div className="discover">
      {/* Background */}
      <div className="discover__bg">
        <div className="discover__blob discover__blob--1" />
        <div className="discover__blob discover__blob--2" />
      </div>

      {/* Back button */}
      <button
        className="discover__back"
        onClick={() => navigate('/')}
        id="discover-back-btn"
        style={{ opacity: loaded ? 1 : 0 }}
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12.5 15l-5-5 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Back
      </button>

      {/* Main Card */}
      <main className={`discover__card ${loaded ? 'discover__card--visible' : ''}`}>
        <div className="discover__card-inner">
          {/* Header */}
          <div className="discover__header">
            <div className="discover__icon-wrapper">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <path d="M14 2C7.373 2 2 7.373 2 14s5.373 12 12 12 12-5.373 12-12S20.627 2 14 2z" stroke="currentColor" strokeWidth="2"/>
                <path d="M14 9v10M9 14h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h1 className="discover__title">Where are you headed?</h1>
            <p className="discover__subtitle">
              Describe your ideal stay in plain English — our AI does the rest.
            </p>
          </div>

          {/* Input */}
          <div className={`discover__input-wrapper ${query ? 'discover__input-wrapper--active' : ''}`}>
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" className="discover__input-icon">
              <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="2"/>
              <path d="M15 15l4.5 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <input
              ref={inputRef}
              type="text"
              className="discover__input"
              placeholder="Describe your trip in one sentence…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              id="discover-input"
            />
            {query && (
              <button
                className="discover__clear-btn"
                onClick={() => setQuery('')}
                id="discover-clear-btn"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
            )}
          </div>

          {/* Example Prompts */}
          <div className="discover__prompts">
            <span className="discover__prompts-label">Try these:</span>
            <div className="discover__chips stagger-children">
              {examplePrompts.map((prompt, i) => (
                <button
                  key={i}
                  className="chip"
                  onClick={() => handleChipClick(prompt)}
                  id={`discover-chip-${i}`}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Search Button */}
          <button
            className={`btn-primary discover__search-btn ${isSearching ? 'discover__search-btn--loading' : ''}`}
            onClick={handleSearch}
            disabled={!query.trim() || isSearching}
            id="discover-search-btn"
          >
            {isSearching ? (
              <>
                <div className="discover__spinner" />
                Finding hotels...
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M5 12l5 5 5-5M10 17V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{transform: 'rotate(180deg)', transformOrigin: 'center'}}/>
                </svg>
                Find Hotels
              </>
            )}
          </button>
        </div>
      </main>

      {/* Footer hint */}
      <div className={`discover__footer ${loaded ? 'discover__footer--visible' : ''}`}>
        <p>Powered by AI • Results in seconds</p>
      </div>
    </div>
  );
}
