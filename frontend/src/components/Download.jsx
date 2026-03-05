export default function Download({ jobId, cleanInfo, onReset, apiBase }) {
  if (!cleanInfo) return null;

  const removed = cleanInfo.rows_in - cleanInfo.rows_out;

  return (
    <div
      style={{
        animation: "fadeUp 0.35s ease both",
        textAlign: "center",
        padding: "80px 0 60px",
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          background: "var(--green-dim)",
          border: "1px solid var(--green-border)",
          borderRadius: "50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          margin: "0 auto 24px",
          fontSize: 22,
        }}
      >
        ✓
      </div>

      <h2
        style={{
          fontSize: 28,
          fontWeight: 700,
          letterSpacing: -0.8,
          marginBottom: 8,
          color: "var(--text)",
        }}
      >
        Your CSV is clean
      </h2>

      <p style={{ color: "var(--text-2)", fontSize: 14, marginBottom: 32 }}>
        {cleanInfo.rows_out} clean rows ready to download
        {removed > 0 && (
          <span style={{ color: "var(--text-3)" }}>
            {" "}
            · {removed} row{removed !== 1 ? "s" : ""} removed
          </span>
        )}
      </p>

      <div
        style={{
          display: "inline-flex",
          gap: 12,
          flexWrap: "wrap",
          justifyContent: "center",
          marginBottom: 48,
        }}
      >
        <a
          href={`${apiBase}/download/${jobId}`}
          download
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            background: "var(--green)",
            color: "#000",
            fontWeight: 600,
            fontSize: 14,
            padding: "12px 28px",
            borderRadius: "var(--radius)",
            letterSpacing: 0.2,
            transition: "opacity 0.15s",
            textDecoration: "none",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = 0.88)}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = 1)}
        >
          ⬇ Download clean CSV
        </a>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 10,
          maxWidth: 320,
          margin: "0 auto 40px",
          textAlign: "left",
        }}
      >
        {[
          ["Rows in", cleanInfo.rows_in],
          ["Rows out", cleanInfo.rows_out],
          ["Removed", removed],
          ["Status", "Clean"],
        ].map(([label, value]) => (
          <div
            key={label}
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              padding: "12px 16px",
            }}
          >
            <div
              style={{
                fontSize: 11,
                color: "var(--text-3)",
                marginBottom: 4,
              }}
            >
              {label}
            </div>
            <div
              style={{
                fontSize: 16,
                fontWeight: 600,
                fontFamily: "var(--mono)",
                color:
                  label === "Status"
                    ? "var(--green)"
                    : "var(--text)",
              }}
            >
              {value}
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={onReset}
        style={{
          background: "transparent",
          color: "var(--text-3)",
          fontSize: 13,
          padding: "8px 20px",
          borderRadius: "var(--radius)",
          border: "1px solid var(--border)",
          transition: "all 0.15s",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = "var(--border-mid)";
          e.currentTarget.style.color = "var(--text-2)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = "var(--border)";
          e.currentTarget.style.color = "var(--text-3)";
        }}
      >
        Clean another file
      </button>
    </div>
  );
}