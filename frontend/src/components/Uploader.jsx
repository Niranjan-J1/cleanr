import { useState, useRef } from "react"

export default function Uploader({ onUpload }) {
  const [dragging, setDragging] = useState(false)
  const [selected, setSelected] = useState(null)
  const inputRef = useRef()

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function handleFile(file) {
    if (!file.name.endsWith(".csv")) {
      alert("Only CSV files are supported")
      return
    }
    setSelected(file)
  }

  function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div style={{ animation: "fadeUp 0.35s ease both" }}>
      <div style={{ marginBottom: 52 }}>
        <div style={{
          display: "inline-block",
          fontFamily: "var(--mono)",
          fontSize: 11,
          color: "var(--green)",
          background: "var(--green-dim)",
          border: "1px solid var(--green-border)",
          padding: "3px 10px",
          borderRadius: 3,
          marginBottom: 20,
          letterSpacing: 1,
        }}>
          CSV CLEANER
        </div>
        <h1 style={{
          fontSize: 40,
          fontWeight: 700,
          lineHeight: 1.15,
          letterSpacing: -1.5,
          marginBottom: 14,
          color: "var(--text)",
        }}>
          Turn messy data<br />
          into <span style={{ color: "var(--green)" }}>clean data.</span>
        </h1>
        <p style={{
          color: "var(--text-2)",
          fontSize: 15,
          maxWidth: 440,
          lineHeight: 1.65,
        }}>
          Upload a CSV with any combination of inconsistent dates, missing values,
          duplicates, or mixed types. We detect every issue and let you choose how to fix them.
        </p>
      </div>

      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !selected && inputRef.current.click()}
        style={{
          border: `1px dashed ${dragging ? "var(--green)" : selected ? "var(--border-mid)" : "var(--border-mid)"}`,
          borderRadius: "var(--radius)",
          padding: selected ? "24px 28px" : "52px 32px",
          textAlign: "center",
          cursor: selected ? "default" : "pointer",
          background: dragging
            ? "var(--green-dim)"
            : selected
            ? "var(--surface)"
            : "var(--bg-subtle)",
          transition: "all 0.2s ease",
          marginBottom: 12,
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          style={{ display: "none" }}
          onChange={e => handleFile(e.target.files[0])}
        />

        {selected ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14, textAlign: "left" }}>
              <div style={{
                width: 40,
                height: 40,
                background: "var(--green-dim)",
                border: "1px solid var(--green-border)",
                borderRadius: "var(--radius)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 16,
                flexShrink: 0,
              }}>
                📄
              </div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 500, color: "var(--text)", marginBottom: 2 }}>
                  {selected.name}
                </div>
                <div style={{ fontSize: 12, color: "var(--text-3)", fontFamily: "var(--mono)" }}>
                  {formatSize(selected.size)}
                </div>
              </div>
            </div>
            <button
              onClick={e => { e.stopPropagation(); setSelected(null) }}
              style={{
                background: "var(--surface-2)",
                color: "var(--text-3)",
                fontSize: 12,
                padding: "5px 12px",
                borderRadius: "var(--radius)",
                border: "1px solid var(--border)",
              }}
            >
              Remove
            </button>
          </div>
        ) : (
          <>
            <div style={{ fontSize: 28, marginBottom: 14, opacity: 0.6 }}>⬆</div>
            <p style={{ color: "var(--text-2)", fontSize: 14, marginBottom: 6, fontWeight: 500 }}>
              {dragging ? "Drop it here" : "Drag your CSV here"}
            </p>
            <p style={{ color: "var(--text-3)", fontSize: 12 }}>
              or click to browse — max 100MB
            </p>
          </>
        )}
      </div>

      {selected && (
        <button
          onClick={() => onUpload(selected)}
          style={{
            width: "100%",
            background: "var(--green)",
            color: "#000",
            fontWeight: 600,
            fontSize: 14,
            padding: "13px 24px",
            borderRadius: "var(--radius)",
            letterSpacing: 0.3,
            transition: "opacity 0.15s",
          }}
          onMouseEnter={e => e.target.style.opacity = 0.88}
          onMouseLeave={e => e.target.style.opacity = 1}
        >
          Analyze CSV
        </button>
      )}

      <div style={{
        marginTop: 40,
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        gap: 12,
      }}>
        {[
          { icon: "🔍", label: "5 detectors", desc: "Missing values, duplicates, dates, types, whitespace" },
          { icon: "⚖️", label: "You decide", desc: "Ambiguous fixes require your input — no silent data changes" },
          { icon: "🔒", label: "Private", desc: "Files deleted after 24 hours, never used for training" },
        ].map((item, i) => (
          <div key={i} style={{
            background: "var(--bg-subtle)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)",
            padding: "16px",
          }}>
            <div style={{ fontSize: 20, marginBottom: 8 }}>{item.icon}</div>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, color: "var(--text)" }}>
              {item.label}
            </div>
            <div style={{ fontSize: 12, color: "var(--text-3)", lineHeight: 1.5 }}>
              {item.desc}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}