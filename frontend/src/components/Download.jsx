export default function Download({ jobId, cleanInfo, onReset, apiBase }) {
  if (!cleanInfo) return null;

  const rowsRemoved = cleanInfo.rows_in - cleanInfo.rows_out;

  return (
    <div style={{ textAlign: "center", padding: "64px 0" }}>

      <div style={{ fontSize: 48, marginBottom: 24 }}>✓</div>

      <h2
        style={{
          fontSize: 28,
          fontWeight: 800,
          letterSpacing: -1,
          marginBottom: 8,
        }}
      >
        Your CSV is <span style={{ color: "#00ff88" }}>clean</span>
      </h2>

      <p style={{ color: "#666", fontSize: 14, marginBottom: 8 }}>
        {cleanInfo.rows_in} rows in — {cleanInfo.rows_out} rows out
      </p>

      <p style={{ color: "#444", fontSize: 12, marginBottom: 40 }}>
        {rowsRemoved} rows removed
      </p>

      <a
        href={`${apiBase}/download/${jobId}`}
        download
        style={{
          display: "inline-block",
          background: "#00ff88",
          color: "#000",
          fontWeight: 700,
          fontSize: 14,
          padding: "14px 48px",
          letterSpacing: 1,
          marginBottom: 16,
          textDecoration: "none",
          borderRadius: 4,
        }}
      >
        DOWNLOAD CLEAN CSV
      </a>

      <div>
        <button
          onClick={onReset}
          style={{
            background: "transparent",
            color: "#444",
            fontSize: 13,
            padding: "8px 16px",
            border: "1px solid #222",
            marginTop: 16,
            cursor: "pointer",
          }}
        >
          Clean another file
        </button>
      </div>

    </div>
  );
}