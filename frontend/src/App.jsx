import { useState } from "react"
import Uploader from "./components/Uploader"
import Report from "./components/Report"
import Download from "./components/Download"
import "./index.css"

const API = "http://127.0.0.1:8000"

export default function App() {
  const [stage, setStage]       = useState("upload")   // upload | analyzing | report | done
  const [jobId, setJobId]       = useState(null)
  const [report, setReport]     = useState(null)
  const [cleanInfo, setCleanInfo] = useState(null)
  const [error, setError]       = useState(null)

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
      <Header />
      <main style={{ flex: 1, padding: "48px 24px", maxWidth: 900, margin: "0 auto", width: "100%" }}>
        {error && <ErrorBanner message={error} />}
        {stage === "upload"    && <Uploader onUpload={handleUpload} />}
        {stage === "analyzing" && <Analyzing />}
        {stage === "report"    && <Report report={report} onFix={handleFix} />}
        {stage === "done"      && <Download jobId={jobId} cleanInfo={cleanInfo} onReset={handleReset} apiBase={API} />}
      </main>
    </div>
  )
}

function Header() {
  return (
    <header style={{
      borderBottom: "1px solid #1e1e1e",
      padding: "20px 32px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 22, fontWeight: 800, letterSpacing: -1 }}>
          CLEAN<span style={{ color: "#00ff88" }}>R</span>
        </span>
        <span style={{
          fontSize: 10,
          background: "rgba(0,255,136,0.1)",
          color: "#00ff88",
          padding: "2px 8px",
          border: "1px solid rgba(0,255,136,0.3)",
          letterSpacing: 2,
        }}>BETA</span>
      </div>
      <span style={{ fontSize: 12, color: "#444" }}>AI-powered CSV cleaning</span>
    </header>
  )
}

function Analyzing() {
  return (
    <div style={{ textAlign: "center", padding: "80px 0" }}>
      <div style={{
        width: 48, height: 48,
        border: "2px solid #1e1e1e",
        borderTop: "2px solid #00ff88",
        borderRadius: "50%",
        margin: "0 auto 24px",
        animation: "spin 0.8s linear infinite",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
      <p style={{ color: "#666", fontSize: 14 }}>Analyzing your CSV...</p>
    </div>
  )
}

function ErrorBanner({ message }) {
  return (
    <div style={{
      background: "rgba(255,60,60,0.08)",
      border: "1px solid rgba(255,60,60,0.3)",
      color: "#ff6666",
      padding: "12px 16px",
      fontSize: 13,
      marginBottom: 24,
    }}>
      {message}
    </div>
  )
}