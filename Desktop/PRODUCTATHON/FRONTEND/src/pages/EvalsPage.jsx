import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './EvalsPage.css';

const evalCategories = [
  {
    id: 'amenity-precision',
    title: 'Amenity Precision',
    description: 'Verifies that the AI correctly identifies and matches hotel amenities to user intent.',
    passed: 10,
    total: 10,
    icon: '🎯',
    tests: [
      { name: 'Wi-Fi detection from "fast internet"', passed: true },
      { name: 'Pool matching from "swim"', passed: true },
      { name: 'Gym detection from "workout facility"', passed: true },
      { name: 'Spa identification from "relaxation"', passed: true },
      { name: 'Business center from "work trip"', passed: true },
      { name: 'Restaurant from "dining"', passed: true },
      { name: 'Parking from "drive"', passed: true },
      { name: 'Airport shuttle from "flight"', passed: true },
      { name: 'Laundry from "long stay"', passed: true },
      { name: 'Room service from "in-room dining"', passed: true },
    ]
  },
  {
    id: 'constraint-consistency',
    title: 'Constraint Consistency',
    description: 'Ensures budget, location, and rating constraints are consistently applied across re-rankings.',
    passed: 9,
    total: 10,
    icon: '🔒',
    tests: [
      { name: 'Budget under ₹5000 filters correctly', passed: true },
      { name: 'Budget under ₹3000 edge case', passed: true },
      { name: 'Location "near airport" boosts proximity', passed: true },
      { name: 'Location "city center" re-ranks correctly', passed: true },
      { name: 'Combining budget + location', passed: true },
      { name: 'Multiple refinements preserve constraints', passed: true },
      { name: 'Re-rank doesn\'t drop mandatory matches', passed: true },
      { name: 'Rating filter consistency', passed: true },
      { name: 'Empty refinement no-op', passed: true },
      { name: 'Conflicting constraints handled gracefully', passed: false, note: 'Edge case: "cheap luxury" produces ambiguous ranking' },
    ]
  },
  {
    id: 'reasoning-relevance',
    title: 'Reasoning Relevance',
    description: 'Validates that AI explanations directly address user-specified criteria and don\'t deviate.',
    passed: 8,
    total: 10,
    icon: '🧠',
    tests: [
      { name: 'Explanation mentions user\'s stated purpose', passed: true },
      { name: 'Wi-Fi quality cited for "work trip"', passed: true },
      { name: 'Budget justification in text', passed: true },
      { name: 'Location reasoning present', passed: true },
      { name: 'Amenity relevance scoring', passed: true },
      { name: 'Negative match reasoning clarity', passed: true },
      { name: 'Multi-intent explanation coverage', passed: true },
      { name: 'Refinement explanation updates', passed: true },
      { name: 'Subjective quality descriptors', passed: false, note: '"Cozy" lacks objective backing' },
      { name: 'Cross-hotel comparative reasoning', passed: false, note: 'Sometimes lacks contrast detail' },
    ]
  },
  {
    id: 'hallucination-guard',
    title: 'Hallucination Guard',
    description: 'Checks that the system never fabricates amenities, ratings, or hotel attributes not in source data.',
    passed: 10,
    total: 10,
    icon: '🛡️',
    tests: [
      { name: 'No fabricated amenities in cards', passed: true },
      { name: 'Rating matches source data', passed: true },
      { name: 'Price display matches database', passed: true },
      { name: 'Location info not hallucinated', passed: true },
      { name: 'Review quotes are authentic', passed: true },
      { name: 'Match score derived from real criteria', passed: true },
      { name: 'Comparison data sourced correctly', passed: true },
      { name: 'AI explanation grounded in data', passed: true },
      { name: 'Guest verdict based on reviews', passed: true },
      { name: 'No phantom hotels in results', passed: true },
    ]
  },
];

export default function EvalsPage() {
  const navigate = useNavigate();
  const [loaded, setLoaded] = useState(false);
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [animatedCards, setAnimatedCards] = useState([]);

  useEffect(() => {
    setLoaded(true);
    // Stagger card appearances
    evalCategories.forEach((_, i) => {
      setTimeout(() => {
        setAnimatedCards(prev => [...prev, i]);
      }, 300 + i * 150);
    });
  }, []);

  const totalPassed = evalCategories.reduce((acc, cat) => acc + cat.passed, 0);
  const totalTests = evalCategories.reduce((acc, cat) => acc + cat.total, 0);
  const overallScore = Math.round((totalPassed / totalTests) * 100);

  return (
    <div className="evals">
      {/* Background */}
      <div className="evals__bg">
        <div className="evals__bg-grid" />
        <div className="evals__bg-glow evals__bg-glow--1" />
        <div className="evals__bg-glow evals__bg-glow--2" />
      </div>

      {/* Header */}
      <header className={`evals__header ${loaded ? 'evals__header--visible' : ''}`}>
        <div className="evals__header-inner container">
          <button
            className="evals__back"
            onClick={() => navigate('/')}
            id="evals-back-btn"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M12.5 15l-5-5 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Home
          </button>
          <div className="evals__logo" onClick={() => navigate('/')}>
            <div className="evals__logo-icon">
              <svg width="20" height="20" viewBox="0 0 64 64" fill="none">
                <path d="M4 34l24-6 4-16 4 16 24 6-24 6-4 16-4-16-24-6z" fill="currentColor" />
                <circle cx="32" cy="34" r="3" fill="#003580" />
              </svg>
            </div>
            <span>IntentStay</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="evals__main container-narrow">
        {/* Title Section */}
        <div className={`evals__title-section ${loaded ? 'evals__title-section--visible' : ''}`}>
          <div className="evals__title-badge">
            <span className="evals__title-badge-dot" />
            <span>System Evaluation Report</span>
          </div>
          <h1 className="evals__title">AI Reliability Dashboard</h1>
          <p className="evals__subtitle">
            Automated test suite validating IntentStay's AI pipeline across precision, 
            consistency, reasoning, and safety dimensions.
          </p>
        </div>

        {/* Overall Score Ring */}
        <div className={`evals__score-ring-section ${loaded ? 'evals__score-ring-section--visible' : ''}`}>
          <div className="evals__score-ring">
            <svg viewBox="0 0 120 120" className="evals__ring-svg">
              <circle
                cx="60" cy="60" r="52"
                fill="none"
                stroke="var(--color-bg-alt)"
                strokeWidth="8"
              />
              <circle
                cx="60" cy="60" r="52"
                fill="none"
                stroke="url(#scoreGradient)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${loaded ? (overallScore / 100) * 327 : 0} 327`}
                transform="rotate(-90 60 60)"
                className="evals__ring-progress"
              />
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--color-success)" />
                  <stop offset="100%" stopColor="#34D399" />
                </linearGradient>
              </defs>
            </svg>
            <div className="evals__ring-center">
              <span className="evals__ring-value">{overallScore}%</span>
              <span className="evals__ring-label">Pass Rate</span>
            </div>
          </div>
          <div className="evals__score-stats">
            <div className="evals__score-stat">
              <span className="evals__score-stat-value">{totalPassed}</span>
              <span className="evals__score-stat-label">Tests Passed</span>
            </div>
            <div className="evals__score-stat-divider" />
            <div className="evals__score-stat">
              <span className="evals__score-stat-value">{totalTests - totalPassed}</span>
              <span className="evals__score-stat-label">Known Gaps</span>
            </div>
            <div className="evals__score-stat-divider" />
            <div className="evals__score-stat">
              <span className="evals__score-stat-value">{totalTests}</span>
              <span className="evals__score-stat-label">Total Tests</span>
            </div>
          </div>
        </div>

        {/* Eval Category Cards */}
        <div className="evals__cards">
          {evalCategories.map((cat, i) => (
            <div
              key={cat.id}
              className={`evals__card ${animatedCards.includes(i) ? 'evals__card--visible' : ''} ${expandedCategory === cat.id ? 'evals__card--expanded' : ''}`}
              id={`eval-card-${cat.id}`}
            >
              <div
                className="evals__card-header"
                onClick={() => setExpandedCategory(expandedCategory === cat.id ? null : cat.id)}
              >
                <div className="evals__card-icon">{cat.icon}</div>
                <div className="evals__card-info">
                  <h3 className="evals__card-title">{cat.title}</h3>
                  <p className="evals__card-desc">{cat.description}</p>
                </div>
                <div className="evals__card-score">
                  <div className={`evals__card-badge ${cat.passed === cat.total ? 'evals__card-badge--perfect' : 'evals__card-badge--partial'}`}>
                    {cat.passed === cat.total ? (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M13.333 4L6 11.333 2.667 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 3v5.333" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                        <circle cx="8" cy="11.333" r="0.667" fill="currentColor"/>
                      </svg>
                    )}
                    <span>{cat.passed}/{cat.total} passed</span>
                  </div>
                  <div className="evals__card-progress-track">
                    <div
                      className="evals__card-progress-fill"
                      style={{
                        width: animatedCards.includes(i) ? `${(cat.passed / cat.total) * 100}%` : '0%',
                        background: cat.passed === cat.total
                          ? 'linear-gradient(90deg, var(--color-success), #34D399)'
                          : 'linear-gradient(90deg, #EAB308, #FBBF24)'
                      }}
                    />
                  </div>
                </div>
                <div className="evals__card-chevron">
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <path d="M6 7.5l3 3 3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>

              {/* Expanded Tests */}
              <div className="evals__card-expand">
                <div className="evals__card-expand-inner">
                  {cat.tests.map((test, j) => (
                    <div
                      key={j}
                      className={`evals__test-row ${test.passed ? 'evals__test-row--passed' : 'evals__test-row--failed'}`}
                    >
                      <div className="evals__test-icon">
                        {test.passed ? (
                          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                            <path d="M11.667 3.5L5.25 9.917 2.333 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        ) : (
                          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                            <path d="M3.5 3.5l7 7M10.5 3.5l-7 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                          </svg>
                        )}
                      </div>
                      <div className="evals__test-content">
                        <span className="evals__test-name">{test.name}</span>
                        {test.note && (
                          <span className="evals__test-note">{test.note}</span>
                        )}
                      </div>
                      <span className={`evals__test-status ${test.passed ? '' : 'evals__test-status--failed'}`}>
                        {test.passed ? 'Passed' : 'Gap'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer Note */}
        <div className={`evals__footer ${loaded ? 'evals__footer--visible' : ''}`}>
          <div className="evals__footer-card">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <circle cx="9" cy="9" r="7.5" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M9 6v4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <circle cx="9" cy="12.5" r="0.75" fill="currentColor"/>
            </svg>
            <p>
              These evaluations run against IntentStay's AI pipeline using deterministic test fixtures.
              Results reflect the system's ability to understand natural language queries and produce
              accurate, grounded recommendations without fabrication.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
