import { useState, useEffect } from 'react';
import { apiFetch } from '../api/apiFetch';
import { API_BASE } from '../config/api';

interface InsuranceClaim {
  id: string;
  patientId: string;
  patientName: string;
  insurer: string;
  policyNumber: string;
  procedure: string;
  amount: number;
  coveredAmount: number;
  status: string;
  submittedDate: string;
  resolvedDate: string | null;
  notes: string;
}
interface ClaimStats {
  total: number;
  pending: number;
  approved: number;
  paid: number;
  rejected: number;
  totalAmount: number;
  coveredAmount: number;
}

const STATUS_CONFIG: Record<string, { bg: string; color: string; label: string }> = {
  PENDING:  { bg: '#fff3e0', color: '#e65100', label: 'Pendiente' },
  APPROVED: { bg: '#e3f2fd', color: '#1565c0', label: 'Aprobada' },
  PAID:     { bg: '#e8f5e9', color: '#2e7d32', label: 'Pagada' },
  REJECTED: { bg: '#ffebee', color: '#c62828', label: 'Rechazada' },
};

const INSURERS = ['MAPFRE', 'AXA', 'SANITAS', 'DKV', 'ASISA', 'ADESLAS', 'GENERALI'];

export default function InsuranceClaimsPage() {
  const [tab, setTab] = useState<'list' | 'new' | 'stats'>('list');
  const [claims, setClaims] = useState<InsuranceClaim[]>([]);
  const [stats, setStats] = useState<ClaimStats | null>(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ patientId: '', patientName: '', insurer: 'MAPFRE', policyNumber: '', procedure: '', amount: 0, coveredAmount: 0, notes: '' });
  const [saveMsg, setSaveMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const loadData = () => {
    setLoading(true);
    const url = filterStatus ? `${API_BASE}/api/insurance-claims?status=${filterStatus}` : `${API_BASE}/api/insurance-claims`;
    Promise.all([
      apiFetch(url).then(r => r.json()),
      apiFetch(`${API_BASE}/api/insurance-claims/stats`).then(r => r.json()),
    ]).then(([c, s]) => {
      setClaims(Array.isArray(c) ? c : []);
      setStats(s as ClaimStats);
    }).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { loadData(); }, [filterStatus]);

  const updateStatus = async (id: string, status: string) => {
    const res = await apiFetch(`${API_BASE}/api/insurance-claims/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (res.ok) {
      const updated: InsuranceClaim = await res.json();
      setClaims(prev => prev.map(c => c.id === id ? updated : c));
    }
  };

  const handleCreate = async () => {
    setSaveMsg(null);
    try {
      const res = await apiFetch(`${API_BASE}/api/insurance-claims`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        const created: InsuranceClaim = await res.json();
        setClaims(prev => [created, ...prev]);
        setSaveMsg({ ok: true, text: 'Reclamación creada correctamente.' });
        setForm({ patientId: '', patientName: '', insurer: 'MAPFRE', policyNumber: '', procedure: '', amount: 0, coveredAmount: 0, notes: '' });
        setTab('list');
      } else {
        setSaveMsg({ ok: false, text: 'Error al crear la reclamación.' });
      }
    } catch {
      setSaveMsg({ ok: false, text: 'Error de conexión.' });
    }
  };

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: '8px 20px', cursor: 'pointer', background: 'none', border: 'none',
    borderBottom: active ? '3px solid #1976d2' : '3px solid transparent',
    fontWeight: active ? 700 : 400, color: active ? '#1976d2' : '#555', fontSize: 15,
  });

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ color: '#1976d2', marginBottom: 16 }}>Reclamaciones a Seguros</h2>
      <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: 24 }}>
        <button style={tabStyle(tab === 'list')} onClick={() => setTab('list')}>Reclamaciones</button>
        <button style={tabStyle(tab === 'stats')} onClick={() => setTab('stats')}>Estadísticas</button>
        <button style={tabStyle(tab === 'new')} onClick={() => setTab('new')}>+ Nueva reclamación</button>
      </div>

      {/* LIST */}
      {tab === 'list' && (
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 16, alignItems: 'center' }}>
            <span style={{ fontWeight: 600 }}>Filtrar por estado:</span>
            {['', 'PENDING', 'APPROVED', 'PAID', 'REJECTED'].map(s => (
              <button key={s} onClick={() => setFilterStatus(s)}
                style={{ padding: '4px 14px', borderRadius: 16, border: '1px solid #1976d2', cursor: 'pointer',
                  background: filterStatus === s ? '#1976d2' : '#fff', color: filterStatus === s ? '#fff' : '#1976d2', fontWeight: 600, fontSize: 13 }}>
                {s || 'Todos'}
              </button>
            ))}
          </div>
          {loading && <p>Cargando...</p>}
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#1976d2', color: '#fff' }}>
                {['Fecha', 'Paciente', 'Aseguradora', 'Procedimiento', 'Importe', 'Cubierto', 'Estado', 'Acciones'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {claims.map((c, i) => {
                const cfg = STATUS_CONFIG[c.status] || { bg: '#f5f5f5', color: '#333', label: c.status };
                return (
                  <tr key={c.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '8px 12px', whiteSpace: 'nowrap' }}>{c.submittedDate}</td>
                    <td style={{ padding: '8px 12px' }}>{c.patientName}</td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ fontWeight: 700 }}>{c.insurer}</span>
                      <br /><span style={{ fontSize: 11, color: '#888' }}>{c.policyNumber}</span>
                    </td>
                    <td style={{ padding: '8px 12px' }}>{c.procedure}</td>
                    <td style={{ padding: '8px 12px' }}>{c.amount.toFixed(2)} €</td>
                    <td style={{ padding: '8px 12px', color: '#2e7d32', fontWeight: 600 }}>{c.coveredAmount.toFixed(2)} €</td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ background: cfg.bg, color: cfg.color, borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600 }}>
                        {cfg.label}
                      </span>
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <div style={{ display: 'flex', gap: 4 }}>
                        {c.status === 'PENDING' && (
                          <button onClick={() => updateStatus(c.id, 'APPROVED')}
                            style={{ padding: '3px 8px', fontSize: 11, background: '#e3f2fd', color: '#1565c0', border: '1px solid #1565c0', borderRadius: 4, cursor: 'pointer' }}>
                            Aprobar
                          </button>
                        )}
                        {c.status === 'APPROVED' && (
                          <button onClick={() => updateStatus(c.id, 'PAID')}
                            style={{ padding: '3px 8px', fontSize: 11, background: '#e8f5e9', color: '#2e7d32', border: '1px solid #2e7d32', borderRadius: 4, cursor: 'pointer' }}>
                            Pagada
                          </button>
                        )}
                        {(c.status === 'PENDING' || c.status === 'APPROVED') && (
                          <button onClick={() => updateStatus(c.id, 'REJECTED')}
                            style={{ padding: '3px 8px', fontSize: 11, background: '#ffebee', color: '#c62828', border: '1px solid #c62828', borderRadius: 4, cursor: 'pointer' }}>
                            Rechazar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* STATS */}
      {tab === 'stats' && stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16 }}>
          {[
            { label: 'Total reclamaciones', value: stats.total, color: '#1976d2', bg: '#e3f2fd' },
            { label: 'Pendientes', value: stats.pending, color: '#e65100', bg: '#fff3e0' },
            { label: 'Aprobadas', value: stats.approved, color: '#1565c0', bg: '#e3f2fd' },
            { label: 'Pagadas', value: stats.paid, color: '#2e7d32', bg: '#e8f5e9' },
            { label: 'Rechazadas', value: stats.rejected, color: '#c62828', bg: '#ffebee' },
            { label: 'Importe total', value: `${stats.totalAmount.toFixed(2)} €`, color: '#333', bg: '#f5f5f5' },
            { label: 'Cubierto por seguros', value: `${stats.coveredAmount.toFixed(2)} €`, color: '#2e7d32', bg: '#e8f5e9' },
          ].map(({ label, value, color, bg }) => (
            <div key={label} style={{ background: bg, border: `1px solid ${color}`, borderRadius: 10, padding: '20px 24px', textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 800, color }}>{value}</div>
              <div style={{ fontSize: 13, color: '#555', marginTop: 4 }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* NEW FORM */}
      {tab === 'new' && (
        <div style={{ maxWidth: 620, display: 'flex', flexDirection: 'column', gap: 14 }}>
          {[
            { field: 'patientId', label: 'UUID Paciente *' },
            { field: 'patientName', label: 'Nombre paciente *' },
            { field: 'policyNumber', label: 'Nº Póliza' },
            { field: 'procedure', label: 'Procedimiento *' },
          ].map(({ field, label }) => (
            <label key={field}>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>{label}</span>
              <input type="text" value={(form as any)[field]} onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
            </label>
          ))}
          <label>
            <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Aseguradora *</span>
            <select value={form.insurer} onChange={e => setForm(f => ({ ...f, insurer: e.target.value }))}
              style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }}>
              {INSURERS.map(ins => <option key={ins} value={ins}>{ins}</option>)}
            </select>
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <label>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Importe total (€) *</span>
              <input type="number" value={form.amount} onChange={e => setForm(f => ({ ...f, amount: +e.target.value }))}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
            </label>
            <label>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Importe cubierto (€)</span>
              <input type="number" value={form.coveredAmount} onChange={e => setForm(f => ({ ...f, coveredAmount: +e.target.value }))}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
            </label>
          </div>
          <label>
            <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Notas</span>
            <textarea value={form.notes} rows={3} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc', fontFamily: 'inherit' }} />
          </label>
          <button onClick={handleCreate} disabled={!form.patientId || !form.patientName || !form.procedure || form.amount <= 0}
            style={{ padding: '10px 24px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600, alignSelf: 'flex-start' }}>
            Crear reclamación
          </button>
          {saveMsg && (
            <div style={{ padding: '10px 16px', borderRadius: 4, background: saveMsg.ok ? '#e8f5e9' : '#ffebee', color: saveMsg.ok ? '#2e7d32' : '#c62828', fontWeight: 600 }}>
              {saveMsg.text}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
