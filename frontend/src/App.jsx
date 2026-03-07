import { useState } from "react"
import Uploader from "./components/Uploader"
import Report from "./components/Report"
import Download from "./components/Download"
import "./index.css"

const API = "http://127.0.0.1:8000"

export default function App() {
  const [stage, setStage]         = useState("upload")
  const [jobId, setJobId]         = useState(null)
  const [report, setReport]       = useState(null)
  const [cleanInfo, setCleanInfo] = useState(null)
  const [error, setError]         = useState(null)

  async function handleUpload(file) {
    setStage("analyzing")
    setError(null)
    try {
      const form = new FormData()
      form.append("file", file)
      const res  = await fetch(`${API}/upload`, { method: "POST", body: form })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Upload failed")
      setJobId(data.job_id)
      const reportRes  = await fetch(`${API}/report/${data.job_id}`)
      const reportData = await reportRes.json()
      setReport(reportData)
      setStage("report")
    } catch (err) {
      setError(err.message)
      setStage("upload")
    }
  }

  async function handleFix(selections) {
    setError(null)
    try {
      const res  = await fetch(`${API}/fix/${jobId}`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(selections),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "Fix failed")
      setCleanInfo(data)
      setStage("done")
    } catch (err) {
      setError(err.message)
    }
  }

  function handleReset() {
    setStage("upload")
    setJobId(null)
    setReport(null)
    setCleanInfo(null)
    setError(null)
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Header stage={stage} />
      <main style={{
        flex: 1,
        padding: "56px 24px",
        maxWidth: 780,
        margin: "0 auto",
        width: "100%",
        animation: "fadeUp 0.4s ease both",
      }}>
        {error && <ErrorBanner message={error} onClose={() => setError(null)} />}
        {stage === "upload"    && <Uploader onUpload={handleUpload} />}
        {stage === "analyzing" && <Analyzing />}
        {stage === "report"    && <Report report={report} onFix={handleFix} />}
        {stage === "done"      && <Download jobId={jobId} cleanInfo={cleanInfo} onReset={handleReset} apiBase={API} />}
      </main>
      <Footer />
    </div>
  )
}

function Header({ stage }) {
  const steps = ["upload", "analyzing", "report", "done"]
  const stepLabels = ["Upload", "Analyze", "Review", "Download"]
  const current = steps.indexOf(stage)

  return (
    <header style={{
      borderBottom: "1px solid var(--border)",
      padding: "0 32px",
      height: 56,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      background: "var(--bg-subtle)",
      position: "sticky",
      top: 0,
      zIndex: 10,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{
          fontFamily: "var(--mono)",
          fontSize: 16,
          fontWeight: 500,
          letterSpacing: -0.5,
          color: "var(--text)",
        }}>
          cleanr
        </span>
        <span style={{
          fontSize: 10,
          fontFamily: "var(--mono)",
          background: "var(--green-dim)",
          color: "var(--green)",
          padding: "2px 7px",
          borderRadius: 3,
          border: "1px solid var(--green-border)",
          letterSpacing: 1,
        }}>
          beta
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {stepLabels.map((label, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              opacity: i > current ? 0.3 : 1,
              transition: "opacity 0.3s",
            }}>
              <div style={{
                width: 20,
                height: 20,
                borderRadius: "50%",
                background: i < current ? "var(--green)" : i === current ? "var(--surface-2)" : "transparent",
                border: i === current ? "1px solid var(--green)" : i < current ? "none" : "1px solid var(--border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 10,
                fontFamily: "var(--mono)",
                color: i < current ? "#000" : i === current ? "var(--green)" : "var(--text-3)",
                flexShrink: 0,
              }}>
                {i < current ? "✓" : i + 1}
              </div>
              <span style={{
                fontSize: 12,
                color: i === current ? "var(--text)" : "var(--text-3)",
                fontWeight: i === current ? 500 : 400,
              }}>
                {label}
              </span>
            </div>
            {i < stepLabels.length - 1 && (
              <div style={{
                width: 20,
                height: 1,
                background: i < current ? "var(--green-border)" : "var(--border)",
                margin: "0 2px",
              }} />
            )}
          </div>
        ))}
      </div>
    </header>
  )
}

function Analyzing() {
  return (
    <div style={{ textAlign: "center", padding: "100px 0" }}>
      <div style={{
        width: 36,
        height: 36,
        border: "1.5px solid var(--border-mid)",
        borderTop: "1.5px solid var(--green)",
        borderRadius: "50%",
        margin: "0 auto 20px",
        animation: "spin 0.7s linear infinite",
      }} />
      <p style={{ color: "var(--text-2)", fontSize: 14 }}>Scanning your data...</p>
      <p style={{ color: "var(--text-3)", fontSize: 12, marginTop: 6, fontFamily: "var(--mono)" }}>
        running 5 detectors
      </p>
    </div>
  )
}

function ErrorBanner({ message, onClose }) {
  return (
    <div style={{
      background: "var(--red-dim)",
      border: "1px solid var(--red-border)",
      borderRadius: "var(--radius)",
      padding: "12px 16px",
      marginBottom: 24,
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      animation: "fadeUp 0.2s ease both",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ color: "var(--red)", fontSize: 14 }}>⚠</span>
        <span style={{ color: "var(--red)", fontSize: 13 }}>{message}</span>
      </div>
      <button
        onClick={onClose}
        style={{
          background: "transparent",
          color: "var(--text-3)",
          fontSize: 16,
          lineHeight: 1,
          padding: "0 4px",
        }}
      >
        ×
      </button>
    </div>
  )
}

function Footer() {
  return (
    <footer style={{
      borderTop: "1px solid var(--border)",
      padding: "16px 32px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
    }}>
      <span style={{ fontSize: 12, color: "var(--text-3)", fontFamily: "var(--mono)" }}>
        cleanr — csv cleaning engine
      </span>
      <span style={{ fontSize: 12, color: "var(--text-3)" }}>
        max 100MB · data deleted after 24h
      </span>
    </footer>
  )

}


function applyRecommended() {
    const recommended = {}
    report.issues.forEach(issue => {
        if (issue.fix_tier === 'SUGGEST' && issue.fix_options?.length > 0) {
            const key = `${issue.column}:${issue.issue_type}`
            recommended[key] = issue.fix_options[0].action
        }
    })
    setSelections(recommended)
}

<button onClick={applyRecommended}>
    ✦ Apply all recommended
</button>