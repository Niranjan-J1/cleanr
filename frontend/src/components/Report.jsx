import { useState } from "react"

const SEVERITY_COLOR = {
  HIGH:   "#ff3c3c",
  MEDIUM: "#ffaa00",
  LOW:    "#00ff88",
}

const TIER_LABEL = {
  AUTO:      "Auto-fix",
  SUGGEST:   "Your choice",
  FLAG_ONLY: "Review",
}

export default function Report({ report, onFix }) {
  const [selections, setSelections] = useState({})

  const autoIssues    = report.issues.filter(i => i.fix_tier === "AUTO")
  const suggestIssues = report.issues.filter(i => i.fix_tier === "SUGGEST")

  function select(issue, action) {
    const key = `${issue.column}:${issue.issue_type}`
    setSelections(prev => ({ ...prev, [key]: action }))
  }

  function allSuggestAnswered() {
    return suggestIssues.every(i => {
      const key = `${i.column}:${i.issue_type}`
      return key in selections
    })
  }

  function handleApply() {
    onFix(selections)
  }

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: -1, marginBottom: 8 }}>
          Found <span style={{ color: "#00ff88" }}>{report.total_issues} issues</span>
        </h2>
        <p style={{ color: "#666", fontSize: 13 }}>
          {report.rows_analyzed} rows · {report.cols_analyzed} columns · {report.processing_ms}ms
        </p>
      </div>

      {autoIssues.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: "#444", letterSpacing: 2, marginBottom: 12 }}>
            AUTO-FIXED — applied automatically
          </div>
          {autoIssues.map((issue, i) => (
            <IssueCard key={i} issue={issue} onSelect={select} selection={null} auto />
          ))}
        </div>
      )}

      {suggestIssues.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: "#ffaa00", letterSpacing: 2, marginBottom: 12 }}>
            YOUR DECISION — choose how to handle these
          </div>
          {suggestIssues.map((issue, i) => {
            const key = `${issue.column}:${issue.issue_type}`
            return (
              <IssueCard
                key={i}
                issue={issue}
                onSelect={select}
                selection={selections[key]}
              />
            )
          })}
        </div>
      )}

      <button
        onClick={handleApply}
        disabled={!allSuggestAnswered()}
        style={{
          background: allSuggestAnswered() ? "#00ff88" : "#1a1a1a",
          color: allSuggestAnswered() ? "#000" : "#444",
          fontWeight: 700,
          fontSize: 14,
          padding: "14px 32px",
          width: "100%",
          letterSpacing: 1,
          cursor: allSuggestAnswered() ? "pointer" : "not-allowed",
          transition: "all 0.2s",
        }}
      >
        {allSuggestAnswered() ? "APPLY FIXES →" : `ANSWER ALL ${suggestIssues.length} DECISIONS TO CONTINUE`}
      </button>
    </div>
  )
}

function IssueCard({ issue, onSelect, selection, auto }) {
  return (
    <div style={{
      border: "1px solid #1e1e1e",
      padding: "20px 24px",
      marginBottom: 2,
      background: auto ? "rgba(0,255,136,0.02)" : "transparent",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div>
          <span style={{
            fontSize: 10,
            color: SEVERITY_COLOR[issue.severity],
            border: `1px solid ${SEVERITY_COLOR[issue.severity]}`,
            padding: "2px 8px",
            marginRight: 8,
            opacity: 0.7,
          }}>
            {issue.severity}
          </span>
          <span style={{ fontSize: 10, color: "#444", border: "1px solid #222", padding: "2px 8px" }}>
            {TIER_LABEL[issue.fix_tier]}
          </span>
        </div>
        <span style={{ fontSize: 12, color: "#444" }}>
          {issue.affected_rows} rows ({issue.affected_pct}%)
        </span>
      </div>

      <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
        {issue.column ? `${issue.column}` : "Row level"}
        <span style={{ color: "#444", fontWeight: 400, marginLeft: 8, fontSize: 12 }}>
          {issue.issue_type}
        </span>
      </div>

      <div style={{ fontSize: 12, color: "#666", marginBottom: 12 }}>
        {issue.suggested_fix}
      </div>

      {issue.examples.length > 0 && (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
          {issue.examples.slice(0, 4).map((ex, i) => (
            <span key={i} style={{
              fontSize: 11,
              background: "#111",
              border: "1px solid #222",
              padding: "2px 8px",
              fontFamily: "monospace",
              color: "#888",
            }}>
              {ex}
            </span>
          ))}
        </div>
      )}

      {!auto && issue.fix_options.length > 0 && (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {issue.fix_options.map((opt, i) => (
            <button
              key={i}
              onClick={() => onSelect(issue, opt.action)}
              style={{
                fontSize: 12,
                padding: "6px 14px",
                border: `1px solid ${selection === opt.action ? "#00ff88" : "#222"}`,
                background: selection === opt.action ? "rgba(0,255,136,0.1)" : "transparent",
                color: selection === opt.action ? "#00ff88" : "#666",
                transition: "all 0.15s",
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}

      {auto && (
        <div style={{ fontSize: 12, color: "#00ff88", opacity: 0.6 }}>
          ✓ Will be applied automatically
        </div>
      )}
    </div>
  )
}