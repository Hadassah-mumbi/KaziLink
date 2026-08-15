import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20 }}>
          <h3>Something went wrong rendering this view.</h3>
          <pre style={{ whiteSpace: "pre-wrap", background: "#fff", padding: 12, borderRadius: 8 }}>{String(this.state.error)}</pre>
        </div>
      );
    }

    return this.props.children;
  }
}
