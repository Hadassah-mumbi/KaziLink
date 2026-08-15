export default function Loading({ label = "Loading..." }) {
  return (
    <div className="loading">
      <span className="spinner" />
      <span>{label}</span>
    </div>
  );
}
