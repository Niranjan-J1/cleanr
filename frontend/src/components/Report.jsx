import { useState } from "react"

const SEVERITY = {
  HIGH:   { color: "var(--red)",   bg: "var(--red-dim)",   border: "var(--red-border)"   },
  MEDIUM: { color: "var(--amber)", bg: "var(--amber-dim)", border: "var(--amber-border)" },
  LOW:    { color: "var(--green)", bg: "var(--green-dim)", border: "var(--green-border)" },
}

export default function Report({ report, onFix }) {
  const [selections, setSelections] = useState({})

  const autoIssues    = report.issues.filter(i => i.fix_tier === "AUTO")
  const suggestIssues = report.issues.filter(i => i.fix_tier === "SUGGEST")

  function select(issue, action) {
    const key = `${issue.column}:${issue.issue_type}`
    setSelections(prev => ({ ...prev, [key]: action }))
  }

  // Pre-select first fix option for every SUGGEST issue
  function applyRecommended() {
    const recommended = {}
    suggestIssues.forEach(issue => {
      if (issue.fix_options?.length > 0) {
        const key = `${issue.column}:${issue.issue_type}`
        recommended[key] = issue.fix_options[0].action
      }
    })
    setSelections(recommended)
  }

  const answeredCount = suggestIssues.filter(i => {
    const key = `${i.column}:${i.issue_type}`
    return key in selections
  }).length
  const allAnswered = answeredCount === suggestIssues.length

  return (
    <div style={{ animation: "fadeUp 0.35s ease both" }}>

      {/* Summary bar */}
      <div style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius)",
        padding: "20px 24px",
        marginBottom: 32,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: 16,
      }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.5, marginBottom: 4 }}>
            {report.total_issues} issue{report.total_issues !== 1 ? "s" : ""} found
          </h2>
          <p style={{ fontSize: 13, color: "var(--text-2)" }}>
            {report.rows_analyzed} rows · {report.cols_analyzed} columns · {report.processing_ms}ms
          </p>
        </div>
        <div style={{ display: "flex", gap: 16 }}>
          <Stat label="Auto-fixed" value={autoIssues.length} color="var(--green)" />
          <Stat label="Need input" value={suggestIssues.length} color="var(--amber)" />
        </div>
      </div>

      {/* Apply all recommended banner */}
      {suggestIssues.length > 0 && (
        <div style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius)",
          padding: "14px 20px",
          marginBottom: 24,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 16,
          flexWrap: "wrap",
        }}>
          <div>
            <p style={{ fontSize: 13, fontWeight: 500, color: "var(--text)", marginBottom: 2 }}>
              ✦ Let the AI decide
            </p>
            <p style={{ fontSize: 12, color: "var(--text-3)" }}>
              Pre-selects the recommended fix for each issue. You can still change any individual decision.
            </p>
          </div>
          <button
            onClick={applyRecommended}
            style={{
              fontSize: 12,
              fontWeight: 600,
              padding: "8px 18px",
              borderRadius: "var(--radius)",
              background: "var(--green-dim)",
              color: "var(--green)",
              border: "1px solid var(--green-border)",
              cursor: "pointer",
              whiteSpace: "nowrap",
              transition: "all 0.15s",
            }}
          >
            Apply all recommended
          </button>
        </div>
      )}

      {/* Auto issues */}
      {autoIssues.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <SectionLabel color="var(--green)">
            Auto-fixed — no input needed
          </SectionLabel>
          {autoIssues.map((issue, i) => (
            <IssueCard key={i} issue={issue} auto />
          ))}
        </div>
      )}

      {/* Suggest issues */}
      {suggestIssues.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <SectionLabel color="var(--amber)">
            Your decision — {answeredCount}/{suggestIssues.length} answered
          </SectionLabel>
          {suggestIssues.map((issue, i) => {
            const key = `${issue.column}:${issue.issue_type}`
            return (
              <IssueCard
                key={i}
                issue={issue}
                selection={selections[key]}
                onSelect={(action) => select(issue, action)}
              />
            )
          })}
        </div>
      )}

      {/* Apply button */}
      <div style={{
        position: "sticky",
        bottom: 24,
        paddingTop: 16,
      }}>
        <button
          onClick={() => onFix(selections)}
          disabled={!allAnswered}
          style={{
            width: "100%",
            background: allAnswered ? "var(--green)" : "var(--surface-2)",
            color: allAnswered ? "#000" : "var(--text-3)",
            fontWeight: 600,
            fontSize: 14,
            padding: "14px 24px",
            borderRadius: "var(--radius)",
            border: allAnswered ? "none" : "1px solid var(--border)",
            cursor: allAnswered ? "pointer" : "not-allowed",
            transition: "all 0.2s",
            letterSpacing: 0.2,
          }}
        >
          {allAnswered
            ? "Apply fixes and clean CSV"
            : `Answer ${suggestIssues.length - answeredCount} more decision${suggestIssues.length - answeredCount !== 1 ? "s" : ""} to continue`
          }
        </button>
      </div>
    </div>
  )
}

function Stat({ label, value, color }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 22, fontWeight: 700, color, fontFamily: "var(--mono)" }}>
        {value}
      </div>
      <div style={{ fontSize: 11, color: "var(--text-3)" }}>{label}</div>
    </div>
  )
}

function SectionLabel({ children, color }) {
  return (
    <div style={{
      fontSize: 11,
      fontFamily: "var(--mono)",
      color,
      letterSpacing: 1,
      textTransform: "uppercase",
      marginBottom: 10,
      paddingLeft: 2,
      opacity: 0.8,
    }}>
      {children}
    </div>
  )
}

function IssueCard({ issue, auto, selection, onSelect }) {
  const sev = SEVERITY[issue.severity]

  return (
    <div style={{
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderLeft: `3px solid ${sev.color}`,
      borderRadius: "var(--radius)",
      padding: "18px 20px",
      marginBottom: 8,
      transition: "border-color 0.2s",
    }}>
      {/* Top row */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        marginBottom: 10,
        flexWrap: "wrap",
        gap: 8,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <span style={{
            fontSize: 11,
            fontFamily: "var(--mono)",
            color: sev.color,
            background: sev.bg,
            border: `1px solid ${sev.border}`,
            padding: "2px 8px",
            borderRadius: 3,
          }}>
            {issue.severity}
          </span>
          <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text)" }}>
            {issue.column || "All rows"}
          </span>
          <span style={{
            fontSize: 11,
            color: "var(--text-3)",
            fontFamily: "var(--mono)",
          }}>
            {issue.issue_type}
          </span>
        </div>
        <span style={{
          fontSize: 12,
          color: "var(--text-3)",
          fontFamily: "var(--mono)",
          flexShrink: 0,
        }}>
          {issue.affected_rows} rows · {issue.affected_pct}%
        </span>
      </div>

      {/* Description */}
      <p style={{
        fontSize: 13,
        color: "var(--text-2)",
        marginBottom: issue.examples.length > 0 ? 12 : 0,
        lineHeight: 1.55,
      }}>
        {issue.suggested_fix}
      </p>

      {/* Examples */}
      {issue.examples.length > 0 && (
        <div style={{
          display: "flex",
          gap: 6,
          flexWrap: "wrap",
          marginBottom: issue.fix_options?.length > 0 ? 14 : 0,
        }}>
          {issue.examples.slice(0, 5).map((ex, i) => (
            <span key={i} style={{
              fontSize: 11,
              fontFamily: "var(--mono)",
              background: "var(--bg)",
              border: "1px solid var(--border-mid)",
              color: "var(--text-2)",
              padding: "3px 8px",
              borderRadius: 3,
            }}>
              {ex}
            </span>
          ))}
        </div>
      )}

      {/* Auto badge */}
      {auto && (
        <div style={{
          fontSize: 12,
          color: "var(--green)",
          display: "flex",
          alignItems: "center",
          gap: 6,
          opacity: 0.7,
        }}>
          <span>✓</span> Applied automatically
        </div>
      )}

      {/* Fix options */}
      {!auto && issue.fix_options?.length > 0 && (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {issue.fix_options.map((opt, i) => {
            const selected = selection === opt.action
            // First option is the recommended one
            const isRecommended = i === 0
            return (
              <button
                key={i}
                onClick={() => onSelect(opt.action)}
                style={{
                  fontSize: 12,
                  padding: "7px 14px",
                  borderRadius: "var(--radius)",
                  border: `1px solid ${selected ? "var(--green)" : "var(--border-mid)"}`,
                  background: selected ? "var(--green-dim)" : "var(--bg)",
                  color: selected ? "var(--green)" : "var(--text-2)",
                  transition: "all 0.15s",
                  fontWeight: selected ? 500 : 400,
                  position: "relative",
                }}
              >
                {opt.label}
                {isRecommended && (
                  <span style={{
                    marginLeft: 6,
                    fontSize: 9,
                    fontFamily: "var(--mono)",
                    color: selected ? "var(--green)" : "var(--text-3)",
                    opacity: 0.7,
                    textTransform: "uppercase",
                    letterSpacing: 0.5,
                  }}>
                    ✦ rec
                  </span>
                )}
                {opt.preview && opt.preview !== "blank" && opt.preview !== "no change" && (
                  <span style={{
                    marginLeft: 6,
                    fontFamily: "var(--mono)",
                    fontSize: 10,
                    opacity: 0.6,
                  }}>
                    → {opt.preview}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}