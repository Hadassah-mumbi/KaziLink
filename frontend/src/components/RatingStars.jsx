export default function RatingStars({ value = 0, size = 16 }) {
  const rounded = Math.round(Number(value) || 0);
  return (
    <span className="rating-stars" aria-label={`${value} out of 5`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span key={star} style={{ fontSize: size }} className={star <= rounded ? "filled" : ""}>★</span>
      ))}
    </span>
  );
}
