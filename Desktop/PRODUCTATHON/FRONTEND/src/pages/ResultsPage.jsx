import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { discover, refine as refineApi, compare as compareApi } from '../api';
import HotelCard from '../components/HotelCard';
import SkeletonCard from '../components/SkeletonCard';
import ConfidenceBar from '../components/ConfidenceBar';
import ComparisonModal from '../components/ComparisonModal';
import './ResultsPage.css';

// Map backend hotel shape → shape your HotelCard expects
function mapHotel(h, aiResponse) {
  return {
    id: h.id,
    name: h.name,
    location: `${h.area}, ${h.city}`,
    distance: '',
    price: h.price_per_night,
    currency: '₹',
    rating: h.rating,
    reviews: h.review_count || 0,
    stars: h.stars,
    matchScore: Math.round(h.match_score * 100),
    amenities: (h.amenities || []).map(a => a.replace(/_/g, ' ')),
    highlights: h.review_tags || [],
    aiExplanation: h.guest_verdict || '',
    aiExplanationLong: h.guest_verdict || '',
    images: [
      `https://source.unsplash.com/800x500/?hotel,${encodeURIComponent(h.city)}`,
    ],
    childFriendly: h.child_friendly,
    guestReviews: (h.review_tags || []).slice(0, 3).map((tag, i) => ({
      name: ['Priya S.', 'Rahul M.', 'Anjali K.'][i] || 'Guest',
      rating: 4,
      text: tag,
    })),
    // Keep raw id for API calls
    rawId: h.id,
  };
}

// Derive quick-refine chips from the AI response / intent
function deriveChips(intent) {
  const chips = [];
  if (!intent) return chips;
  if (!intent.budget_per_night) {
    chips.push({ label: 'Under ₹5000', icon: '💰' });
    chips.push({ label: 'Under ₹8000', icon: '💳' });
  }
  if (!(intent.must_have || []).includes('pool')) {
    chips.push({ label: 'Add pool', icon: '🏊' });
  }
  if (!(intent.must_have || []).includes('gym')) {
    chips.push({ label: 'Add gym', icon: '🏋️' });
  }
  if (intent.purpose === 'work' && !(intent.must_have || []).includes('quiet_rooms')) {
    chips.push({ label: 'Quiet rooms', icon: '🔇' });
  }
  return chips.slice(0, 4);
}

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const initialQuery = location.state?.query || 'Work trip in Delhi with fast Wi-Fi';

  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [aiResponse, setAiResponse] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [constraintInput, setConstraintInput] = useState('');
  const [isRefining, setIsRefining] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [confidence, setConfidence] = useState(null);
  const [refinementChips, setRefinementChips] = useState([]);
  const [selectedForCompare, setSelectedForCompare] = useState([]);
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonText, setComparisonText] = useState('');
  const [comparisonLoading, setComparisonLoading] = useState(false);

  // ── Initial discover call ──────────────────────────────────────────────────
  useEffect(() => {
    setLoaded(true);
    setLoading(true);
    setError(null);

    discover(initialQuery)
      .then(data => {
        const mapped = (data.hotels || []).map(h => mapHotel(h, data.response));
        setResults(mapped);
        setAiResponse(data.response || '');
        setConfidence(data.confidence || null);
        setRefinementChips(deriveChips(data.intent));
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // ── Refine call ────────────────────────────────────────────────────────────
  const handleRefine = (text) => {
    const refinement = text || constraintInput;
    if (!refinement.trim()) return;
    setIsRefining(true);
    setError(null);

    refineApi(refinement)
      .then(data => {
        const mapped = (data.hotels || []).map(h => mapHotel(h, data.response));
        setResults(mapped);
        setAiResponse(data.response || '');
        setQuery(q => `${q} · ${refinement}`);
        setConfidence(data.confidence || null);
        setRefinementChips(deriveChips(data.intent));
        setConstraintInput('');
        setIsRefining(false);
        setSelectedForCompare([]);
      })
      .catch(err => {
        setError(err.message);
        setIsRefining(false);
      });
  };

  const handleConstraintKeyDown = (e) => {
    if (e.key === 'Enter') handleRefine();
  };

  // ── Compare call ───────────────────────────────────────────────────────────
  const handleCompare = async () => {
    if (selectedForCompare.length !== 2) return;
    setComparisonLoading(true);
    setShowComparison(true);
    try {
      const data = await compareApi(selectedForCompare[0], selectedForCompare[1]);
      setComparisonText(data.comparison || '');
    } catch (err) {
      setComparisonText('Could not load comparison. Please try again.');
    }
    setComparisonLoading(false);
  };

  const toggleCompare = (hotelId) => {
    setSelectedForCompare(prev => {
      if (prev.includes(hotelId)) return prev.filter(id => id !== hotelId);
      if (prev.length >= 2) return [prev[1], hotelId];
      return [...prev, hotelId];
    });
  };

  const getComparisonHotels = () => {
    if (selectedForCompare.length !== 2) return [null, null];
    return [
      results.find(h => h.id === selectedForCompare[0]),
      results.find(h => h.id === selectedForCompare[1]),
    ];
  };

  return (
    <div className="results">
      {/* Header */}
      <header className={`results__header ${loaded ? 'results__header--visible' : ''}`}>
        <div className="results__header-inner container">
          <button className="results__back" onClick={() => navigate('/discover')} id="results-back-btn">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M12.5 15l-5-5 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            New Search
          </button>
          <div className="results__logo" onClick={() => navigate('/')}>
            <div className="results__logo-icon">
              <svg width="20" height="20" viewBox="0 0 64 64" fill="none">
                <path d="M4 34l24-6 4-16 4 16 24 6-24 6-4 16-4-16-24-6z" fill="currentColor"/>
                <circle cx="32" cy="34" r="3" fill="#003580"/>
              </svg>
            </div>
            <span>IntentStay</span>
          </div>
        </div>
      </header>

      <main className="results__main container-narrow">
        {/* Query Pill */}
        <div className={`results__query-section ${loaded ? 'results__query-section--visible' : ''}`}>
          <span className="results__query-label">Your Intent</span>
          <div className="results__query-pill">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M9 6v6M6 9h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            <span>"{initialQuery}"</span>
          </div>
          <p className="results__count">
            {loading ? 'Analysing your trip...' : error ? '⚠ Could not load results' : `${results.length} hotels matched your intent`}
          </p>
        </div>

        {/* AI Concierge Response */}
        {!loading && aiResponse && (
          <div className="results__ai-response">
            <div className="results__ai-label">✦ AI Concierge</div>
            <div className="results__ai-bubble">{aiResponse}</div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="results__error">
            <p>⚠ {error}</p>
            <p style={{fontSize: '13px', marginTop: '8px', opacity: 0.7}}>Make sure the Flask server is running and your ngrok URL is set in .env</p>
          </div>
        )}

        {/* Confidence Bar */}
        {!loading && confidence && <ConfidenceBar confidence={confidence} />}

        {/* Refinement Chips */}
        {!loading && refinementChips.length > 0 && (
          <div className="results__chips-section">
            <span className="results__chips-label">Quick refinements</span>
            <div className="results__chips">
              {refinementChips.map((chip, i) => (
                <button
                  key={i}
                  className="results__chip glass-panel"
                  onClick={() => handleRefine(chip.label)}
                  id={`refine-chip-${i}`}
                  style={{ animationDelay: `${i * 60}ms` }}
                >
                  <span className="results__chip-icon">{chip.icon}</span>
                  <span>{chip.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Hotel Cards */}
        <div className="results__cards stagger-children">
          {loading ? (
            <><SkeletonCard /><SkeletonCard /><SkeletonCard /></>
          ) : (
            results.map((hotel, i) => (
              <HotelCard
                key={hotel.id}
                hotel={hotel}
                index={i}
                onViewDetails={() => navigate(`/details/${hotel.id}`, { state: { query, hotel } })}
                isSelected={selectedForCompare.includes(hotel.id)}
                onToggleCompare={toggleCompare}
              />
            ))
          )}
        </div>

        {/* Refine Input */}
        {!loading && (
          <div className={`results__refine ${loaded ? 'results__refine--visible' : ''}`}>
            <div className="results__refine-card">
              <h3 className="results__refine-title">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M11 5H6a2 2 0 00-2 2v6a2 2 0 002 2h8a2 2 0 002-2v-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                  <path d="M15 2l-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                Change anything?
              </h3>
              <div className="results__refine-input-group">
                <input
                  type="text"
                  className="results__refine-input"
                  placeholder="e.g. drop budget to ₹4000 · add pool · closer to city"
                  value={constraintInput}
                  onChange={(e) => setConstraintInput(e.target.value)}
                  onKeyDown={handleConstraintKeyDown}
                  id="results-refine-input"
                />
                <button
                  className="btn-primary results__refine-btn"
                  onClick={() => handleRefine()}
                  disabled={!constraintInput.trim() || isRefining}
                  id="results-refine-btn"
                >
                  {isRefining ? <div className="results__spinner" /> : 'Refine'}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Floating Compare Button */}
      {selectedForCompare.length === 2 && (
        <div className="results__compare-fab">
          <button
            className="btn-primary results__compare-btn"
            onClick={handleCompare}
            id="compare-hotels-btn"
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M6 2H3a1.5 1.5 0 00-1.5 1.5v12A1.5 1.5 0 003 17h3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M12 2h3a1.5 1.5 0 011.5 1.5v12A1.5 1.5 0 0115 17h-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M9 1v16" stroke="currentColor" strokeWidth="1.5" strokeDasharray="2.5 2.5"/>
            </svg>
            Compare Selected Hotels
          </button>
        </div>
      )}

      {selectedForCompare.length === 1 && !loading && (
        <div className="results__compare-hint">
          <span>Select 1 more hotel to compare</span>
        </div>
      )}

      {/* Comparison Modal */}
      {showComparison && (() => {
        const [h1, h2] = getComparisonHotels();
        if (!h1 || !h2) return null;
        return (
          <ComparisonModal
            hotel1={h1}
            hotel2={h2}
            comparisonText={comparisonText}
            comparisonLoading={comparisonLoading}
            onClose={() => { setShowComparison(false); setComparisonText(''); }}
          />
        );
      })()}
    </div>
  );
}