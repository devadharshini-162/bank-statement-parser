import { useState, useRef, useCallback, useEffect } from "react";
import axios from "axios";
import {
  Upload, FileText, Zap, Download, RotateCcw,
  TrendingDown, TrendingUp, AlertTriangle, Hash,
  CheckCircle, XCircle, Search, Activity, Wifi, Clock
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, BarChart, Bar, XAxis, YAxis } from "recharts";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const formatCurrency = (val) =>
  val != null && val !== "" && !isNaN(val)
    ? `$${Number(val).toFixed(2)}`
    : "—";

function Header({ onHistoryClick }) {
  return (
    <header className="fade-up" style={{
      padding: "1.75rem 2.5rem",
      borderBottom: "1px solid var(--border)",
      display: "flex", alignItems: "center", justifyContent: "space-between"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{
          width: 42, height: 42, borderRadius: 12,
          background: "linear-gradient(135deg, #00c896, #0070c0)",
          display: "flex", alignItems: "center", justifyContent: "center",
          animation: "float 3s ease-in-out infinite"
        }}>
          <Activity size={20} color="#080e1a" strokeWidth={2.5} />
        </div>
        <div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 900, letterSpacing: "-0.03em" }}>
            StatementAI
          </h1>
          <p style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: 1, fontWeight: 400 }}>
            Bank Statement Intelligence
          </p>
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <button onClick={onHistoryClick} style={{
          background: "none", border: "1px solid var(--border)", borderRadius: "8px",
          padding: "6px 12px", color: "var(--text-secondary)", fontSize: "12px",
          display: "flex", alignItems: "center", gap: "6px", cursor: "pointer",
          fontWeight: 600, fontFamily: "Cabinet Grotesk", transition: "all 0.2s"
        }}>
          <Clock size={14} />
          History
        </button>
        <div style={{
          display: "flex", alignItems: "center", gap: 6,
          fontSize: "11px", color: "var(--emerald)",
          background: "var(--emerald-dim)", border: "1px solid var(--emerald-glow)",
          borderRadius: 20, padding: "4px 12px", fontWeight: 700
        }}>
          <Wifi size={11} strokeWidth={2.5} />
          LIVE
        </div>
      </div>
    </header>
  );
}

function UploadZone({ onUpload, loading }) {
  const inputRef = useRef();
  const [drag, setDrag] = useState(false);
  const [file, setFile] = useState(null);

  const handleFile = (f) => {
    if (!f || !f.name.endsWith(".pdf")) return alert("Please upload a PDF file.");
    setFile(f);
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setDrag(false);
    handleFile(e.dataTransfer.files[0]);
  }, []);

  return (
    <div className="fade-up-1" style={{ marginBottom: "1.5rem" }}>
      <div
        className={`drop-zone ${drag ? "drag-over" : ""}`}
        style={{ padding: "3rem 2rem", textAlign: "center" }}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        onClick={() => !file && inputRef.current.click()}
      >
        <input ref={inputRef} type="file" accept=".pdf" style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])} />

        <div style={{
          width: 72, height: 72, borderRadius: 20, margin: "0 auto 1.25rem",
          background: drag ? "var(--emerald-dim)" : "var(--navy-3)",
          border: `2px solid ${drag ? "var(--emerald)" : "var(--border)"}`,
          display: "flex", alignItems: "center", justifyContent: "center",
          transition: "all 0.3s ease",
          animation: "float 4s ease-in-out infinite"
        }}>
          {file
            ? <FileText size={32} color="var(--emerald)" strokeWidth={1.5} />
            : <Upload size={32} color={drag ? "var(--emerald)" : "var(--text-secondary)"} strokeWidth={1.5} />
          }
        </div>

        {file ? (
          <>
            <p style={{ color: "var(--emerald)", fontWeight: 700, fontSize: "1rem", fontFamily: "Cabinet Grotesk" }}>
              {file.name}
            </p>
            <p style={{ color: "var(--text-secondary)", fontSize: "12px", marginTop: 6 }}>
              {(file.size / 1024).toFixed(1)} KB
              <span style={{
                marginLeft: 10, cursor: "pointer", color: "var(--emerald)",
                textDecoration: "underline"
              }} onClick={(e) => { e.stopPropagation(); inputRef.current.click(); }}>
                Change file
              </span>
            </p>
          </>
        ) : (
          <>
            <p style={{ fontFamily: "Cabinet Grotesk", fontWeight: 800, fontSize: "1.15rem" }}>
              Drop your bank statement here
            </p>
            <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginTop: 8, lineHeight: 1.6 }}>
              Supports digital and scanned PDFs<br />
              SBI · HDFC · Axis · Canara · and more
            </p>
          </>
        )}
      </div>

      {file && (
        <button
          className="glow-btn fade-up"
          disabled={loading}
          onClick={() => onUpload(file)}
          style={{
            width: "100%", padding: "1rem", fontSize: "1rem",
            marginTop: "1rem", display: "flex", alignItems: "center",
            justifyContent: "center", gap: "8px"
          }}
        >
          <Zap size={18} strokeWidth={2.5} />
          {loading ? "Analysing with Gemini AI..." : "Parse Statement"}
        </button>
      )}
    </div>
  );
}

function LoadingState() {
  const steps = [
    "Detecting PDF type",
    "Extracting content",
    "Sending to Gemini AI",
    "Structuring transactions",
    "Validating data",
  ];
  const [step, setStep] = useState(0);

  useState(() => {
    const iv = setInterval(() =>
      setStep((s) => (s < steps.length - 1 ? s + 1 : s)), 2200);
    return () => clearInterval(iv);
  });

  return (
    <div className="glass fade-up" style={{ padding: "3rem", textAlign: "center", marginBottom: "1.5rem" }}>
      <div className="spinner" style={{ margin: "0 auto 1.5rem" }} />
      <h3 style={{ fontFamily: "Cabinet Grotesk", fontWeight: 800, marginBottom: "0.5rem", fontSize: "1.1rem" }}>
        Processing your statement
      </h3>
      <p style={{ color: "var(--emerald)", fontSize: "13px", fontWeight: 600 }}>
        {steps[step]}...
      </p>
      <div style={{ display: "flex", gap: 6, justifyContent: "center", marginTop: "1.75rem" }}>
        {steps.map((_, i) => (
          <div key={i} style={{
            height: 4, borderRadius: 2,
            width: i <= step ? 28 : 8,
            background: i <= step ? "var(--emerald)" : "var(--border)",
            transition: "all 0.5s ease"
          }} />
        ))}
      </div>
    </div>
  );
}

function StatCards({ data }) {
  const stats = [
    {
      label: "Transactions",
      value: data.total_transactions,
      icon: <Hash size={18} strokeWidth={2} />,
      color: "#7eb8ff"
    },
    {
      label: "Total Debits",
      value: formatCurrency(data.total_debits),
      icon: <TrendingDown size={18} strokeWidth={2} />,
      color: "var(--red)"
    },
    {
      label: "Total Credits",
      value: formatCurrency(data.total_credits),
      icon: <TrendingUp size={18} strokeWidth={2} />,
      color: "var(--emerald)"
    },
    {
      label: "Anomalies",
      value: data.anomalies_count,
      icon: <AlertTriangle size={18} strokeWidth={2} />,
      color: "var(--gold)"
    },
  ];

  return (
    <div className="fade-up-2" style={{
      display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
      gap: "1rem", marginBottom: "1.5rem"
    }}>
      {stats.map((s, i) => (
        <div key={i} className="stat-card">
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: `${s.color}18`,
            border: `1px solid ${s.color}30`,
            display: "flex", alignItems: "center", justifyContent: "center",
            color: s.color, marginBottom: "0.75rem"
          }}>
            {s.icon}
          </div>
          <div style={{
            fontSize: "1.5rem", fontFamily: "Cabinet Grotesk",
            fontWeight: 900, color: s.color, letterSpacing: "-0.02em"
          }}>
            {s.value}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: 3, fontWeight: 500 }}>
            {s.label}
          </div>
        </div>
      ))}
    </div>
  );
}

const CATEGORY_COLORS = {
  Food: "#ff7b72",
  Transport: "#79c0ff",
  Salary: "#56d364",
  EMI: "#d2a8ff",
  Utilities: "#ffa657",
  ATM: "#8b949e",
  UPI: "#6cb6ff",
  Charges: "#f85149",
  Other: "#8b949e",
};

function Dashboard({ transactions }) {
  const categoryTotals = {};
  let validDebits = 0;
  transactions.forEach((t) => {
    if (t.debit) {
      validDebits++;
      const cat = t.category || "Other";
      categoryTotals[cat] = (categoryTotals[cat] || 0) + Number(t.debit);
    }
  });

  const pieData = Object.keys(categoryTotals).map((key) => ({
    name: key,
    value: categoryTotals[key],
  }));

  if (validDebits === 0) return null;

  return (
    <div className="fade-up-2 glass" style={{ marginBottom: "1.5rem", padding: "1.5rem" }}>
      <h3 style={{ fontFamily: "Cabinet Grotesk", fontWeight: 800, fontSize: "1rem", marginBottom: "1rem" }}>
        Spending by Category
      </h3>
      <div style={{ height: 260, width: "100%" }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={100}
              paddingAngle={4}
              dataKey="value"
              stroke="var(--navy)"
              strokeWidth={3}
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.name] || CATEGORY_COLORS.Other} />
              ))}
            </Pie>
            <RechartsTooltip 
              formatter={(value) => formatCurrency(value)}
              contentStyle={{ background: "var(--navy)", border: "1px solid var(--border)", borderRadius: "8px", fontSize: "13px" }}
              itemStyle={{ color: "var(--text-primary)" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", justifyContent: "center", marginTop: "1rem" }}>
        {pieData.map((entry, idx) => (
          <div key={idx} style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "11px", color: "var(--text-secondary)" }}>
            <div style={{ width: 10, height: 10, borderRadius: "3px", backgroundColor: CATEGORY_COLORS[entry.name] || CATEGORY_COLORS.Other }} />
            {entry.name}
          </div>
        ))}
      </div>
    </div>
  );
}

function HistoryModal({ onClose }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/history`)
      .then(res => { setHistory(res.data); setLoading(false); })
      .catch(err => { console.error(err); setLoading(false); });
  }, []);

  return (
    <div style={{
      position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
      background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)",
      zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: "1.5rem"
    }}>
      <div className="glass fade-up" style={{
        width: "100%", maxWidth: 700, maxHeight: "85vh", overflow: "hidden",
        display: "flex", flexDirection: "column"
      }}>
        <div style={{ padding: "1.5rem", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h3 style={{ fontFamily: "Cabinet Grotesk", fontWeight: 800, fontSize: "1.2rem" }}>Processing History</h3>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: 4 }}>Previously parsed statements</p>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer" }}>
            <XCircle size={24} color="var(--text-secondary)" />
          </button>
        </div>
        <div style={{ padding: "1.5rem", overflowY: "auto", flex: 1 }}>
          {loading ? (
            <div className="spinner" style={{ margin: "2rem auto" }} />
          ) : history.length === 0 ? (
            <p style={{ textAlign: "center", color: "var(--text-secondary)", fontSize: "13px" }}>No history found.</p>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
              <thead>
                <tr style={{ background: "var(--navy-3)" }}>
                  <th style={{ padding: "10px", textAlign: "left", color: "var(--text-secondary)", fontSize: "10px", textTransform: "uppercase" }}>Date</th>
                  <th style={{ padding: "10px", textAlign: "left", color: "var(--text-secondary)", fontSize: "10px", textTransform: "uppercase" }}>File</th>
                  <th style={{ padding: "10px", textAlign: "right", color: "var(--text-secondary)", fontSize: "10px", textTransform: "uppercase" }}>Txns</th>
                  <th style={{ padding: "10px", textAlign: "right", color: "var(--text-secondary)", fontSize: "10px", textTransform: "uppercase" }}>Debits</th>
                  <th style={{ padding: "10px", textAlign: "right", color: "var(--text-secondary)", fontSize: "10px", textTransform: "uppercase" }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "10px", color: "var(--text-secondary)" }}>{h.timestamp.split('T')[0]}</td>
                    <td style={{ padding: "10px", fontWeight: 500 }}>{h.filename}</td>
                    <td style={{ padding: "10px", textAlign: "right" }}>{h.total_transactions}</td>
                    <td style={{ padding: "10px", textAlign: "right", color: "var(--red)" }}>{formatCurrency(h.total_debits)}</td>
                    <td style={{ padding: "10px", textAlign: "right" }}>
                      <span className={h.is_valid ? "badge-valid" : "badge-invalid"}>{h.is_valid ? "Valid" : "Flagged"}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultsTable({ transactions, anomalies }) {
  const anomalySet = new Set(anomalies || []);
  const [search, setSearch] = useState("");

  const filtered = transactions.filter((t) =>
    Object.values(t).some((v) =>
      String(v).toLowerCase().includes(search.toLowerCase())
    )
  );

  return (
    <div className="glass fade-up-3" style={{ marginBottom: "1.5rem", overflow: "hidden" }}>
      <div style={{
        padding: "1.25rem 1.5rem", borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        gap: "1rem", flexWrap: "wrap"
      }}>
        <h3 style={{ fontFamily: "Cabinet Grotesk", fontWeight: 800, fontSize: "1rem" }}>
          Transactions
          <span style={{
            marginLeft: 10, fontSize: "12px", color: "var(--text-secondary)",
            fontFamily: "Satoshi", fontWeight: 500
          }}>
            {filtered.length} rows
          </span>
        </h3>
        <div style={{
          display: "flex", alignItems: "center", gap: 8,
          background: "var(--navy)", border: "1px solid var(--border)",
          borderRadius: 8, padding: "6px 12px"
        }}>
          <Search size={13} color="var(--text-secondary)" />
          <input
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: "none", border: "none", color: "var(--text-primary)",
              fontSize: "13px", outline: "none", width: 160
            }}
          />
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ background: "var(--navy-3)" }}>
              {["Date", "Description", "Category", "Debit", "Credit", "Balance"].map((h) => (
                <th key={h} style={{
                  padding: "10px 16px",
                  textAlign: h === "Description" ? "left" : "right",
                  color: "var(--text-secondary)", fontWeight: 700,
                  fontSize: "10px", textTransform: "uppercase",
                  letterSpacing: "0.08em", whiteSpace: "nowrap",
                  fontFamily: "Cabinet Grotesk"
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((t, i) => (
              <tr key={i}
                className={`table-row ${anomalySet.has(i) ? "anomaly-row" : ""}`}
                style={{ borderBottom: "1px solid var(--border)" }}>
                <td style={{
                  padding: "10px 16px", color: "var(--text-secondary)",
                  whiteSpace: "nowrap", textAlign: "right", fontWeight: 500
                }}>{t.date || "—"}</td>
                <td style={{
                  padding: "10px 16px", maxWidth: 260,
                  overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap"
                }}>
                  {anomalySet.has(i) && (
                    <AlertTriangle size={12} color="var(--gold)"
                      style={{ marginRight: 6, verticalAlign: "middle" }} />
                  )}
                  {t.description || "—"}
                </td>
                <td style={{ padding: "10px 16px", textAlign: "left" }}>
                  {t.category ? (
                    <span style={{
                      fontSize: "10px", fontWeight: 700, padding: "3px 8px", borderRadius: "12px",
                      backgroundColor: `${CATEGORY_COLORS[t.category] || CATEGORY_COLORS.Other}15`,
                      color: CATEGORY_COLORS[t.category] || CATEGORY_COLORS.Other,
                      border: `1px solid ${CATEGORY_COLORS[t.category] || CATEGORY_COLORS.Other}30`
                    }}>
                      {t.category}
                    </span>
                  ) : "—"}
                </td>
                <td style={{
                  padding: "10px 16px", textAlign: "right",
                  color: t.debit ? "var(--red)" : "var(--text-secondary)",
                  fontWeight: t.debit ? 600 : 400
                }}>
                  {t.debit ? `−${formatCurrency(t.debit)}` : "—"}
                </td>
                <td style={{
                  padding: "10px 16px", textAlign: "right",
                  color: t.credit ? "var(--emerald)" : "var(--text-secondary)",
                  fontWeight: t.credit ? 600 : 400
                }}>
                  {t.credit ? `+${formatCurrency(t.credit)}` : "—"}
                </td>
                <td style={{
                  padding: "10px 16px", textAlign: "right",
                  fontWeight: 600, whiteSpace: "nowrap"
                }}>
                  {formatCurrency(t.balance)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DownloadBar({ result, onReset }) {
  return (
    <div className="glass fade-up" style={{
      padding: "1.25rem 1.5rem", marginBottom: "1.5rem",
      display: "flex", alignItems: "center",
      justifyContent: "space-between", flexWrap: "wrap", gap: "1rem"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        <div style={{
          width: 42, height: 42, borderRadius: 12,
          background: "var(--emerald-dim)", border: "1px solid var(--emerald-glow)",
          display: "flex", alignItems: "center", justifyContent: "center"
        }}>
          <CheckCircle size={22} color="var(--emerald)" strokeWidth={2} />
        </div>
        <div>
          <p style={{ fontFamily: "Cabinet Grotesk", fontWeight: 800, fontSize: "0.95rem" }}>
            Statement parsed successfully
          </p>
          <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: 2 }}>
            {result.filename}
          </p>
        </div>
        <span className={result.is_valid ? "badge-valid" : "badge-invalid"}>
          {result.is_valid ? "Valid" : "Anomalies Found"}
        </span>
      </div>
      <div style={{ display: "flex", gap: "0.75rem" }}>
        <a href={`${API}${result.excel_download_path}`} download style={{ textDecoration: "none" }}>
          <button className="glow-btn" style={{
            padding: "0.65rem 1.25rem", fontSize: "13px",
            display: "flex", alignItems: "center", gap: "7px"
          }}>
            <Download size={15} strokeWidth={2.5} />
            Download Excel
          </button>
        </a>
        <button onClick={onReset} style={{
          padding: "0.65rem 1.25rem", fontSize: "13px",
          fontFamily: "Cabinet Grotesk", fontWeight: 700,
          background: "transparent", border: "1px solid var(--border)",
          borderRadius: 10, color: "var(--text-primary)", cursor: "pointer",
          transition: "all 0.2s", display: "flex", alignItems: "center", gap: "7px"
        }}>
          <RotateCcw size={14} strokeWidth={2.5} />
          Parse Another
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  const handleUpload = async (file) => {
    setLoading(true); setError(null); setResult(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const { data } = await axios.post(`${API}/parse`, form);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => { setResult(null); setError(null); };

  return (
    <>
      <div className="mesh-bg" />
      <div style={{ position: "relative", zIndex: 1, minHeight: "100vh" }}>
        <Header onHistoryClick={() => setShowHistory(true)} />
        {showHistory && <HistoryModal onClose={() => setShowHistory(false)} />}
        <main style={{ maxWidth: 900, margin: "0 auto", padding: "2.5rem 1.5rem" }}>

          {!result && !loading && (
            <>
              <div className="fade-up" style={{ marginBottom: "2.5rem" }}>
                <div style={{
                  display: "inline-flex", alignItems: "center", gap: 7,
                  background: "var(--emerald-dim)", border: "1px solid var(--emerald-glow)",
                  borderRadius: 20, padding: "4px 14px", marginBottom: "1.25rem"
                }}>
                  <Zap size={12} color="var(--emerald)" strokeWidth={2.5} />
                  <span style={{ fontSize: "11px", color: "var(--emerald)", fontWeight: 700 }}>
                    Powered by Gemini AI
                  </span>
                </div>
                <h2 style={{
                  fontSize: "2.2rem", fontWeight: 900,
                  letterSpacing: "-0.04em", lineHeight: 1.15
                }}>
                  Turn any bank statement<br />
                  <span style={{ color: "var(--emerald)" }}>into structured data</span>
                </h2>
                <p style={{
                  color: "var(--text-secondary)", marginTop: "1rem",
                  fontSize: "0.95rem", lineHeight: 1.7, maxWidth: 480
                }}>
                  Upload a PDF — digital or scanned. Gemini AI extracts every
                  transaction in seconds and exports a clean Excel file.
                </p>
              </div>
              <UploadZone onUpload={handleUpload} loading={loading} />
            </>
          )}

          {loading && <LoadingState />}

          {error && (
            <div className="glass fade-up" style={{
              padding: "1.25rem 1.5rem", marginBottom: "1.5rem",
              borderColor: "var(--red)", background: "rgba(255,77,109,0.08)",
              display: "flex", alignItems: "flex-start", gap: 12
            }}>
              <XCircle size={20} color="var(--red)" style={{ marginTop: 2, flexShrink: 0 }} />
              <div>
                <p style={{ color: "var(--red)", fontWeight: 700, fontFamily: "Cabinet Grotesk" }}>
                  Parsing failed
                </p>
                <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginTop: 4 }}>
                  {error}
                </p>
                <button onClick={handleReset} style={{
                  marginTop: "0.75rem", color: "var(--emerald)", background: "none",
                  border: "none", cursor: "pointer", fontSize: "13px",
                  fontWeight: 600, padding: 0
                }}>
                  Try again
                </button>
              </div>
            </div>
          )}

          {result && (
            <>
              <DownloadBar result={result} onReset={handleReset} />
              <StatCards data={result} />
              <Dashboard transactions={result.transactions} />
              {result.transactions && result.transactions.length > 0 && (
                <ResultsTable
                  transactions={result.transactions}
                  anomalies={result.anomalies || []}
                />
              )}
            </>
          )}

          <footer className="fade-up-4" style={{
            marginTop: "4rem", paddingTop: "1.5rem",
            borderTop: "1px solid var(--border)",
            display: "flex", justifyContent: "space-between",
            alignItems: "center", flexWrap: "wrap", gap: "1rem"
          }}>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
              StatementAI · Built by Deva Dharshini · CIT Chennai
            </p>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
              SBI · HDFC · Axis · Canara · and more
            </p>
          </footer>
        </main>
      </div>
    </>
  );
}