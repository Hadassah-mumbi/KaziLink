export default function ErrorMessage({ message, onClose }) {
  if (!message) return null;
  return (
    <div className="error-box">
      <span>{message}</span>
      {onClose && <button onClick={onClose}>×</button>}
    </div>
  );
}
