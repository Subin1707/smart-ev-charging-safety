import { useEffect, useMemo, useState } from 'react'
import { FileCheck2, FileUp, Search, Upload, X } from 'lucide-react'
import { getRequirementEvidence, getVerificationRequirements, getVerificationSummary, verifySpecification } from '../services/verificationService'

const FILTERS = ['ALL', 'PASS', 'FAIL', 'INCONCLUSIVE', 'NOT_MAPPED', 'NOT_VERIFIABLE']

function Status({ value }) {
  return <span className={`verification-status status-${String(value ?? 'UNKNOWN').toLowerCase()}`}>{value ?? 'UNKNOWN'}</span>
}

function SummaryCard({ label, value, tone }) {
  return <article className={`summary-card ${tone}`}><span>{label}</span><strong>{value ?? 0}</strong></article>
}

function JsonBlock({ value }) {
  return <pre className="json-block">{JSON.stringify(value ?? {}, null, 2)}</pre>
}

function Detail({ record, evidence, onClose }) {
  const [tab, setTab] = useState('IR')
  const tabs = ['IR', 'GENERATED CODE', 'PRODUCTION', 'VERIFICATION', 'EVIDENCE']
  return <aside className="verification-detail">
    <div className="detail-heading"><div><span className="eyebrow">REQUIREMENT DETAIL</span><h2>{record.requirement_id}</h2></div><button className="icon-button" type="button" onClick={onClose} aria-label="Close detail"><X size={18} /></button></div>
    <Status value={record.result} />
    <section className="detail-section"><h3>Specification</h3><p>{record.specification}</p></section>
    <section className="detail-meta"><div><span>Property type</span><strong>{record.property_type ?? 'unknown'}</strong></div><div><span>Mapping</span><strong>{record.production_mapping?.status ?? 'NOT_MAPPED'}</strong></div></section>
    <div className="detail-tabs">{tabs.map((name) => <button className={tab === name ? 'active' : ''} type="button" key={name} onClick={() => setTab(name)}>{name}</button>)}</div>
    {tab === 'IR' && <JsonBlock value={record.ir} />}
    {tab === 'GENERATED CODE' && <div className="artifact-list">{(record.generated_code ?? []).map((item) => <code key={item}>{item}</code>)}</div>}
    {tab === 'PRODUCTION' && <div className="mapping-panel"><strong>{record.production_mapping?.status ?? 'NOT_MAPPED'}</strong><p>{(record.production_code ?? []).join(', ') || 'No production symbol mapped to this requirement.'}</p></div>}
    {tab === 'VERIFICATION' && <div className="tool-list">{(record.verification_tools ?? []).map((tool) => <div key={`${tool.level ?? ""}:${tool.name ?? tool}`}><span>{tool.name ?? tool}{tool.level ? ` (${tool.level})` : ""}</span><Status value={tool.status ?? "UNKNOWN"} /></div>)}</div>}
    {tab === 'EVIDENCE' && <div className="artifact-list">{(record.evidence ?? []).map((item) => <code key={item}>{item}</code>)}{(evidence?.evidence ?? []).map((item) => <pre className="evidence-preview" key={item.path}>{item.content}</pre>)}</div>}
    {record.counterexample && <section className="counterexample"><h3>Counterexample</h3><JsonBlock value={record.counterexample} /></section>}
  </aside>
}

export function VerificationPage() {
  const [summary, setSummary] = useState(null)
  const [records, setRecords] = useState([])
  const [selected, setSelected] = useState(null)
  const [evidence, setEvidence] = useState(null)
  const [filter, setFilter] = useState('ALL')
  const [query, setQuery] = useState('')
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const load = () => Promise.all([getVerificationSummary(), getVerificationRequirements()]).then(([nextSummary, nextRecords]) => { setSummary(nextSummary); setRecords(nextRecords) })
  useEffect(() => { load().catch((error) => setMessage(error.message)) }, [])
  useEffect(() => { if (selected) getRequirementEvidence(selected.requirement_id).then(setEvidence).catch(() => setEvidence(null)) }, [selected])
  const filtered = useMemo(() => records.filter((record) => (filter === 'ALL' || record.result === filter) && `${record.requirement_id} ${record.specification}`.toLowerCase().includes(query.toLowerCase())), [records, filter, query])
  const upload = async () => {
    if (!file) return
    setBusy(true); setMessage('Analyzing specification...')
    try { await verifySpecification(file); await load(); setMessage('Verification completed.') } catch (error) { setMessage(error.message) } finally { setBusy(false) }
  }
  return <main className="verification-page verification-workspace">
    <header className="verification-header"><div><p className="eyebrow">SPECIFICATION VERIFICATION GENERATOR</p><h1>Verification Workspace</h1><p className="verification-generated">Evidence-backed production and standalone checks</p></div><FileCheck2 size={38} color="var(--cyan)" /></header>
    <section className="upload-strip"><label className="file-picker"><FileUp size={18} /> Choose specification<input type="file" accept=".xlsx,.csv,.txt" onChange={(event) => setFile(event.target.files?.[0] ?? null)} /></label><span>{file ? file.name : 'Supported: .xlsx, .csv, .txt'}</span><button className="primary-button" type="button" disabled={!file || busy} onClick={upload}><Upload size={16} /> {busy ? 'VERIFYING...' : 'GENERATE & VERIFY'}</button></section>
    {message && <p className="verification-note">{message}</p>}
    <section className="summary-grid"><SummaryCard label="Requirements" value={summary?.total} tone="neutral" /><SummaryCard label="PASS" value={summary?.pass} tone="pass" /><SummaryCard label="FAIL" value={summary?.fail} tone="fail" /><SummaryCard label="NOT MAPPED" value={summary?.not_mapped} tone="mapped" /><SummaryCard label="NOT VERIFIABLE" value={summary?.not_verifiable} tone="unknown" /></section>
    <section className="coverage-strip">{Object.entries(summary?.coverage ?? {}).map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{(value * 100).toFixed(1)}%</strong></div>)}</section>
    <section className="requirements-section"><div className="verification-section-heading"><div><h2>Requirements</h2><span>{filtered.length} records</span></div><div className="table-tools"><div className="search-box"><Search size={15} /><input aria-label="Search requirement" placeholder="Search requirement..." value={query} onChange={(event) => setQuery(event.target.value)} /></div><div className="filter-row">{FILTERS.map((item) => <button className={filter === item ? 'active' : ''} key={item} type="button" onClick={() => setFilter(item)}>{item}</button>)}</div></div></div><div className="requirements-table"><div className="table-row table-head"><span>ID</span><span>Requirement</span><span>Type</span><span>Mapping</span><span>Result</span></div>{filtered.map((record) => <button className="table-row" type="button" key={record.requirement_id} onClick={() => setSelected(record)}><strong>{record.requirement_id}</strong><span>{record.specification}</span><span>{record.property_type}</span><span>{record.production_mapping?.status ?? 'NOT_MAPPED'}</span><Status value={record.result} /></button>)}</div></section>
    {selected && <Detail record={selected} evidence={evidence} onClose={() => setSelected(null)} />}
  </main>
}
