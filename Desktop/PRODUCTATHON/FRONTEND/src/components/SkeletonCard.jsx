import './SkeletonCard.css';

export default function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-card__image" />
      <div className="skeleton-card__body">
        <div className="skeleton-card__row">
          <div>
            <div className="skeleton skeleton-card__title" />
            <div className="skeleton skeleton-card__subtitle" />
          </div>
          <div className="skeleton skeleton-card__price" />
        </div>
        <div className="skeleton skeleton-card__rating" />
        <div className="skeleton-card__ai">
          <div className="skeleton skeleton-card__ai-line" />
          <div className="skeleton skeleton-card__ai-line skeleton-card__ai-line--short" />
        </div>
        <div className="skeleton-card__actions-row">
          <div className="skeleton skeleton-card__btn" />
          <div className="skeleton skeleton-card__btn skeleton-card__btn--small" />
        </div>
      </div>
    </div>
  );
}
