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
      alert("Please upload a CSV file")
      return
    }
    setSelected(file)
  }

  return (
    <div>
      <div style={{ marginBottom: 48 }}>
        <h1 style={{ fontSize: 42, fontWeight: 800, letterSpacing: -2, marginBottom: 12 }}>
          Clean your <span style={{ color: "#00ff88" }}>messy CSV</span>
        </h1>
        <p style={{ color: "#666", fontSize: 15 }}>
          Upload any CSV. We detect issues, you choose the fixes, download clean data.
        </p>
      </div>

      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
        style={{
          border: `2px dashed ${dragging ? "#00ff88" : selected ? "rgba(0,255,136,0.4)" : "#222"}`,
          borderRadius: 2,
          padding: "64px 32px",
          textAlign: "center",
          cursor: "pointer",
          background: dragging ? "rgba(0,255,136,0.03)" : "transparent",
          transition: "all 0.2s",
          marginBottom: 24,
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          style={{ display: "none" }}
          onChange={e => handleFile(e.target.files[0])}
        />
        <div style={{ fontSize: 32, marginBottom: 16 }}>📂</div>
        {selected ? (
          <>
            <p style={{ color: "#00ff88", fontSize: 15, marginBottom: 4 }}>{selected.name}</p>
            <p style={{ color: "#444", fontSize: 12 }}>{(selected.size / 1024).toFixed(1)} KB</p>
          </>
        ) : (
          <>
            <p style={{ color: "#666", fontSize: 15, marginBottom: 8 }}>
              Drag and drop your CSV here
            </p>
            <p style={{ color: "#333", fontSize: 12 }}>or click to browse — max 100MB</p>
          </>
        )}
      </div>

      {selected && (
        <button
          onClick={() => onUpload(selected)}
          style={{
            background: "#00ff88",
            color: "#000",
            fontWeight: 700,
            fontSize: 14,
            padding: "14px 32px",
            width: "100%",
            letterSpacing: 1,
          }}
        >
          ANALYZE CSV →
        </button>
      )}
    </div>
  )
}