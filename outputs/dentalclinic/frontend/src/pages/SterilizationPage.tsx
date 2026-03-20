import { useState, useEffect } from 'react';
import { apiFetch } from '../api/apiFetch';
import { API_BASE } from '../config/api';

interface Instrument {
  id: string;
  name: string;
  type: string;
  status: string;
  location: string;
  totalUses: number;
  maxUses: number;
  lastSterilizedAt: string;
}
interface SterilizationCycle {
  id: string;
  cycleNumber: string;
  method: string;
  temperature: string;
  duration: string;
  operator: string;
  startedAt: string;
  completedAt: string | null;
  status: string;
  instrumentIds: string[];
}
interface SterilizationStats {
  totalInstruments: number;
  pendingSterilization: number;
  inProgress: number;
  ready: number;
  outOfService: number;
  cyclesThisMonth: number;
}

const INST_STATUS: Record<string, { bg: string; color: string; label: string }> = {
  READY:             { bg: '#e8f5e9', color: '#2e7d32', label: 'Listo' },
  PENDING:           { bg: '#fff3e0', color: '#e65100', label: 'Pendiente esterilización' },
  IN_USE:            { bg: '#e3f2fd', color: '#1565c0', label: 'En uso' },
  IN_STERILIZATION:  { bg: '#f3e5f5', color: '#6a1b9a', label: 'Esterilizando' },
  OUT_OF_SERVICE:    { bg: '#f5f5f5', color: '#757575', label: 'Baja' },
};

const CYCLE_STATUS: Record<string, { bg: string; color: string }> = {
  COMPLETED:   { bg: '#e8f5e9', color: '#2e7d32' },
  IN_PROGRESS: { bg: '#fff3e0', color: '#e65100' },
  FAILED:      { bg: '#ffebee', color: '#c62828' },
};

export default function SterilizationPage() {
  const [tab, setTab] = useState<'instruments' | 'cycles' | 'new-cycle'>('instruments');
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [cycles, setCycles] = useState<SterilizationCycle[]>([]);
  const [stats, setStats] = useState<SterilizationStats | null>(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [cycleForm, setCycleForm] = useState({ method: 'AUTOCLAVE_134', operator: '' });
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const loadAll = () => {
    setLoading(true);
    Promise.all([
      apiFetch(`${API_BASE}/api/sterilization/instruments`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/sterilization/cycles`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/sterilization/stats`).then(r => r.json()),
    ]).then(([inst, cyc, st]) => {
      setInstruments(Array.isArray(inst) ? inst : []);
      setCycles(Array.isArray(cyc) ? cyc : []);
      setStats(st as SterilizationStats);
    }).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { loadAll(); }, []);

  const filteredInstruments = instruments.filter(i => !filterStatus || i.status === filterStatus);

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleCreateCycle = async () => {
    if (selectedIds.size === 0 || !cycleForm.operator) return;
    setMsg(null);
    const res = await apiFetch(`${API_BASE}/api/sterilization/cycles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        method: cycleForm.method,
        temperature: cycleForm.method === 'AUTOCLAVE_134' ? '134°C' : '121°C',
        duration: cycleForm.method === 'AUTOCLAVE_134' ? '18 min' : '30 min',
        operator: cycleForm.operator,
        instrumentIds: Array.from(selectedIds),
      }),
    });
    if (res.ok) {
      setMsg({ ok: true, text: 'Ciclo iniciado correctamente.' });
      setSelectedIds(new Set());
      loadAll();
      setTab('cycles');
    } else {
      setMsg({ ok: false, text: 'Error al iniciar el ciclo.' });
    }
  };

  const completeCycle = async (id: string) => {
    const res = await apiFetch(`${API_BASE}/api/sterilization/cycles/${id}/complete`, { method: 'PUT' });
    if (res.ok) loadAll();
  };

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: '8px 20px', cursor: 'pointer', background: 'none', border: 'none',
    borderBottom: active ? '3px solid #1976d2' : '3px solid transparent',
    fontWeight: active ? 700 : 400, color: active ? '#1976d2' : '#555', fontSize: 15,
  });

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ color: '#1976d2', marginBottom: 8 }}>Control de Esterilización</h2>

      {stats && (
        <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
          {[
            { label: 'Listos', value: stats.ready, color: '#2e7d32', bg: '#e8f5e9' },
            { label: 'Pendientes', value: stats.pendingSterilization, color: '#e65100', bg: '#fff3e0' },
            { label: 'Esterilizando', value: stats.inProgress, color: '#6a1b9a', bg: '#f3e5f5' },
            { label: 'Baja', value: stats.outOfService, color: '#757575', bg: '#f5f5f5' },
            { label: 'Ciclos este mes', value: stats.cyclesThisMonth, color: '#1565c0', bg: '#e3f2fd' },
          ].map(({ label, value, color, bg }) => (
            <div key={label} style={{ background: bg, border: `1px solid ${color}`, borderRadius: 8, padding: '10px 18px', textAlign: 'center', minWidth: 100 }}>
              <div style={{ fontSize: 26, fontWeight: 800, color }}>{value}</div>
              <div style={{ fontSize: 12, color: '#555' }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: 24 }}>
        <button style={tabStyle(tab === 'instruments')} onClick={() => setTab('instruments')}>Instrumental</button>
        <button style={tabStyle(tab === 'cycles')} onClick={() => setTab('cycles')}>Ciclos</button>
        <button style={tabStyle(tab === 'new-cycle')} onClick={() => setTab('new-cycle')}>+ Nuevo ciclo</button>
      </div>

      {loading && <p>Cargando...</p>}
      {msg && (
        <div style={{ padding: '8px 16px', borderRadius: 4, background: msg.ok ? '#e8f5e9' : '#ffebee', color: msg.ok ? '#2e7d32' : '#c62828', fontWeight: 600, marginBottom: 12 }}>
          {msg.text}
        </div>
      )}

      {/* INSTRUMENTS */}
      {tab === 'instruments' && !loading && (
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
            {['', 'READY', 'PENDING', 'IN_USE', 'IN_STERILIZATION', 'OUT_OF_SERVICE'].map(s => (
              <button key={s} onClick={() => setFilterStatus(s)}
                style={{ padding: '4px 12px', borderRadius: 16, border: '1px solid #1976d2', cursor: 'pointer',
                  background: filterStatus === s ? '#1976d2' : '#fff', color: filterStatus === s ? '#fff' : '#1976d2', fontWeight: 600, fontSize: 12 }}>
                {s ? (INST_STATUS[s]?.label || s) : 'Todos'}
              </button>
            ))}
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#1976d2', color: '#fff' }}>
                {['Nombre', 'Tipo', 'Estado', 'Ubicación', 'Usos', 'Última esterilización'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredInstruments.map((inst, i) => {
                const cfg = INST_STATUS[inst.status] || { bg: '#f5f5f5', color: '#333', label: inst.status };
                const usageRatio = inst.totalUses / inst.maxUses;
                return (
                  <tr key={inst.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 600 }}>{inst.name}</td>
                    <td style={{ padding: '8px 12px', fontSize: 12, color: '#555' }}>{inst.type}</td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ background: cfg.bg, color: cfg.color, borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600 }}>{cfg.label}</span>
                    </td>
                    <td style={{ padding: '8px 12px', fontSize: 12 }}>{inst.location}</td>
                    <td style={{ padding: '8px 12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ background: '#f0f0f0', borderRadius: 4, height: 8, width: 60 }}>
                          <div style={{ width: `${usageRatio * 100}%`, height: '100%', borderRadius: 4,
                            background: usageRatio > 0.9 ? '#c62828' : usageRatio > 0.7 ? '#ff9800' : '#4caf50' }} />
                        </div>
                        <span style={{ fontSize: 12, color: usageRatio > 0.9 ? '#c62828' : '#555' }}>
                          {inst.totalUses}/{inst.maxUses}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '8px 12px', fontSize: 12, color: '#555' }}>
                      {inst.lastSterilizedAt?.replace('T', ' ') || '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* CYCLES */}
      {tab === 'cycles' && !loading && (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#1976d2', color: '#fff' }}>
              {['Nº Ciclo', 'Método', 'Operador', 'Inicio', 'Fin', 'Instrumentos', 'Estado', 'Acciones'].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {cycles.map((c, i) => {
              const cfg = CYCLE_STATUS[c.status] || { bg: '#f5f5f5', color: '#333' };
              return (
                <tr key={c.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px 12px', fontWeight: 700 }}>{c.cycleNumber}</td>
                  <td style={{ padding: '8px 12px', fontSize: 12 }}>{c.method.replace('_', ' ')} {c.temperature}</td>
                  <td style={{ padding: '8px 12px' }}>{c.operator}</td>
                  <td style={{ padding: '8px 12px', fontSize: 12 }}>{c.startedAt?.replace('T', ' ')}</td>
                  <td style={{ padding: '8px 12px', fontSize: 12 }}>{c.completedAt?.replace('T', ' ') || '—'}</td>
                  <td style={{ padding: '8px 12px', fontSize: 12 }}>{c.instrumentIds.length} uds.</td>
                  <td style={{ padding: '8px 12px' }}>
                    <span style={{ background: cfg.bg, color: cfg.color, borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600 }}>{c.status}</span>
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    {c.status === 'IN_PROGRESS' && (
                      <button onClick={() => completeCycle(c.id)}
                        style={{ padding: '3px 10px', background: '#e8f5e9', color: '#2e7d32', border: '1px solid #2e7d32', borderRadius: 4, cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                        ✓ Completar
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {/* NEW CYCLE */}
      {tab === 'new-cycle' && !loading && (
        <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 400px' }}>
            <h3 style={{ marginBottom: 12 }}>1. Seleccionar instrumental</h3>
            <div style={{ border: '1px solid #e0e0e0', borderRadius: 8, overflow: 'hidden' }}>
              {instruments.filter(i => i.status === 'PENDING').map((inst, i) => (
                <div key={inst.id} onClick={() => toggleSelect(inst.id)}
                  style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px',
                    background: selectedIds.has(inst.id) ? '#e3f2fd' : i % 2 === 0 ? '#fff' : '#f9f9f9',
                    borderBottom: '1px solid #eee', cursor: 'pointer' }}>
                  <input type="checkbox" checked={selectedIds.has(inst.id)} readOnly />
                  <div>
                    <div style={{ fontWeight: 600 }}>{inst.name}</div>
                    <div style={{ fontSize: 12, color: '#888' }}>{inst.location}</div>
                  </div>
                </div>
              ))}
              {instruments.filter(i => i.status === 'PENDING').length === 0 && (
                <p style={{ padding: 16, color: '#888' }}>No hay instrumental pendiente de esterilización.</p>
              )}
            </div>
            <p style={{ fontSize: 13, color: '#555', marginTop: 8 }}>{selectedIds.size} instrumento(s) seleccionados</p>
          </div>
          <div style={{ flex: '0 0 280px' }}>
            <h3 style={{ marginBottom: 12 }}>2. Configurar ciclo</h3>
            <label style={{ display: 'block', marginBottom: 12 }}>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Método</span>
              <select value={cycleForm.method} onChange={e => setCycleForm(f => ({ ...f, method: e.target.value }))}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }}>
                <option value="AUTOCLAVE_134">Autoclave 134°C (18 min)</option>
                <option value="AUTOCLAVE_121">Autoclave 121°C (30 min)</option>
                <option value="QUIMICA">Esterilización química</option>
              </select>
            </label>
            <label style={{ display: 'block', marginBottom: 16 }}>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Operador *</span>
              <input type="text" value={cycleForm.operator} placeholder="Nombre del responsable"
                onChange={e => setCycleForm(f => ({ ...f, operator: e.target.value }))}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
            </label>
            <button onClick={handleCreateCycle}
              disabled={selectedIds.size === 0 || !cycleForm.operator}
              style={{ width: '100%', padding: '10px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600, fontSize: 15 }}>
              Iniciar ciclo
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
