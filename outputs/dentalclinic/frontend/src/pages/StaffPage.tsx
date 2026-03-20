import { useState, useEffect } from 'react';
import { apiFetch } from '../api/apiFetch';
import { API_BASE } from '../config/api';

interface StaffMember {
  id: string;
  name: string;
  role: string;
  email: string;
  phone: string;
  contractType: string;
  hoursPerWeek: number;
  status: string;
  joinDate: string;
}
interface VacationRequest {
  id: string;
  staffId: string;
  staffName: string;
  from: string;
  to: string;
  status: string;
  notes: string;
}
interface ScheduleEntry {
  staffId: string;
  staffName: string;
  dayOfWeek: string;
  startTime: string;
  endTime: string;
}

const ROLE_LABELS: Record<string, string> = {
  DENTIST: '🦷 Dentista', RECEPTIONIST: '📋 Recepcionista',
  ASSISTANT: '🩺 Asistente', AUXILIARY: '🔧 Auxiliar',
};
const STATUS_CFG: Record<string, { bg: string; color: string }> = {
  ACTIVE:    { bg: '#e8f5e9', color: '#2e7d32' },
  ON_LEAVE:  { bg: '#fff3e0', color: '#e65100' },
  INACTIVE:  { bg: '#f5f5f5', color: '#757575' },
};
const VAC_CFG: Record<string, { bg: string; color: string }> = {
  APPROVED: { bg: '#e8f5e9', color: '#2e7d32' },
  PENDING:  { bg: '#fff3e0', color: '#e65100' },
  REJECTED: { bg: '#ffebee', color: '#c62828' },
};
const DAYS = ['LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO'];

export default function StaffPage() {
  const [tab, setTab] = useState<'team' | 'schedule' | 'vacations' | 'hours'>('team');
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [schedules, setSchedules] = useState<ScheduleEntry[]>([]);
  const [vacations, setVacations] = useState<VacationRequest[]>([]);
  const [hours, setHours] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [showVacForm, setShowVacForm] = useState(false);
  const [form, setForm] = useState({ name: '', role: 'DENTIST', email: '', phone: '', contractType: 'FULL_TIME', hoursPerWeek: 40, joinDate: new Date().toISOString().substring(0, 10) });
  const [vacForm, setVacForm] = useState({ staffId: '', staffName: '', from: '', to: '', notes: '' });
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      apiFetch(`${API_BASE}/api/staff`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/staff/schedules`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/staff/vacations`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/staff/hours`).then(r => r.json()),
    ]).then(([s, sch, v, h]) => {
      setStaff(Array.isArray(s) ? s : []);
      setSchedules(Array.isArray(sch) ? sch : []);
      setVacations(Array.isArray(v) ? v : []);
      setHours(h && typeof h === 'object' ? h : {});
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleCreateStaff = async () => {
    const res = await apiFetch(`${API_BASE}/api/staff`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form),
    });
    if (res.ok) {
      const created: StaffMember = await res.json();
      setStaff(prev => [...prev, created]);
      setShowForm(false);
      setSaveMsg('Empleado creado correctamente.');
    }
  };

  const handleCreateVacation = async () => {
    const res = await apiFetch(`${API_BASE}/api/staff/vacations`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(vacForm),
    });
    if (res.ok) {
      const created: VacationRequest = await res.json();
      setVacations(prev => [...prev, created]);
      setShowVacForm(false);
      setSaveMsg('Solicitud enviada.');
    }
  };

  const approveVacation = async (id: string) => {
    const res = await apiFetch(`${API_BASE}/api/staff/vacations/${id}/approve`, { method: 'PUT' });
    if (res.ok) {
      const updated: VacationRequest = await res.json();
      setVacations(prev => prev.map(v => v.id === id ? updated : v));
    }
  };

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: '8px 20px', cursor: 'pointer', background: 'none', border: 'none',
    borderBottom: active ? '3px solid #1976d2' : '3px solid transparent',
    fontWeight: active ? 700 : 400, color: active ? '#1976d2' : '#555', fontSize: 15,
  });

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ color: '#1976d2', marginBottom: 16 }}>Gestión de Empleados</h2>
      {saveMsg && (
        <div style={{ background: '#e8f5e9', color: '#2e7d32', padding: '8px 16px', borderRadius: 6, marginBottom: 12, fontWeight: 600 }}
          onClick={() => setSaveMsg(null)} role="alert">{saveMsg}</div>
      )}
      <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: 24 }}>
        <button style={tabStyle(tab === 'team')} onClick={() => setTab('team')}>Equipo</button>
        <button style={tabStyle(tab === 'schedule')} onClick={() => setTab('schedule')}>Horarios</button>
        <button style={tabStyle(tab === 'vacations')} onClick={() => setTab('vacations')}>Vacaciones / Ausencias</button>
        <button style={tabStyle(tab === 'hours')} onClick={() => setTab('hours')}>Horas mes</button>
      </div>

      {loading && <p>Cargando...</p>}

      {/* TEAM */}
      {tab === 'team' && !loading && (
        <div>
          <button onClick={() => setShowForm(v => !v)}
            style={{ marginBottom: 16, padding: '8px 20px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600 }}>
            {showForm ? 'Cancelar' : '+ Nuevo empleado'}
          </button>
          {showForm && (
            <div style={{ background: '#f5f5f5', padding: 20, borderRadius: 8, marginBottom: 20, border: '1px solid #ddd' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                {[{ f: 'name', l: 'Nombre completo *' }, { f: 'email', l: 'Email' }, { f: 'phone', l: 'Teléfono' }].map(({ f, l }) => (
                  <label key={f}>
                    <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>{l}</span>
                    <input type="text" value={(form as any)[f]} onChange={e => setForm(ff => ({ ...ff, [f]: e.target.value }))}
                      style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }} />
                  </label>
                ))}
                <label>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Rol</span>
                  <select value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }}>
                    {Object.entries(ROLE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                  </select>
                </label>
                <label>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Contrato</span>
                  <select value={form.contractType} onChange={e => setForm(f => ({ ...f, contractType: e.target.value }))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }}>
                    <option value="FULL_TIME">Jornada completa</option>
                    <option value="PART_TIME">Media jornada</option>
                    <option value="FREELANCE">Autónomo</option>
                  </select>
                </label>
                <label>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Horas/semana</span>
                  <input type="number" value={form.hoursPerWeek} onChange={e => setForm(f => ({ ...f, hoursPerWeek: +e.target.value }))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }} />
                </label>
                <label>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Fecha incorporación</span>
                  <input type="date" value={form.joinDate} onChange={e => setForm(f => ({ ...f, joinDate: e.target.value }))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }} />
                </label>
              </div>
              <button onClick={handleCreateStaff} disabled={!form.name}
                style={{ padding: '8px 20px', background: '#388e3c', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600 }}>
                Guardar
              </button>
            </div>
          )}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
            {staff.map(sm => {
              const statusCfg = STATUS_CFG[sm.status] || { bg: '#f5f5f5', color: '#333' };
              return (
                <div key={sm.id} style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 10, padding: 18, boxShadow: '0 1px 4px rgba(0,0,0,.07)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 15 }}>{sm.name}</div>
                      <div style={{ fontSize: 13, color: '#555', marginTop: 2 }}>{ROLE_LABELS[sm.role] || sm.role}</div>
                    </div>
                    <span style={{ background: statusCfg.bg, color: statusCfg.color, borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600 }}>
                      {sm.status}
                    </span>
                  </div>
                  <div style={{ fontSize: 13, color: '#555' }}>📧 {sm.email}</div>
                  <div style={{ fontSize: 13, color: '#555' }}>📞 {sm.phone}</div>
                  <div style={{ fontSize: 13, color: '#888', marginTop: 4 }}>
                    {sm.contractType === 'FULL_TIME' ? 'Jornada completa' : sm.contractType === 'PART_TIME' ? 'Media jornada' : 'Autónomo'} · {sm.hoursPerWeek}h/sem
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* SCHEDULE GRID */}
      {tab === 'schedule' && !loading && (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#1976d2', color: '#fff' }}>
                <th style={{ padding: '8px 12px', textAlign: 'left' }}>Empleado</th>
                {DAYS.map(d => <th key={d} style={{ padding: '8px 12px', textAlign: 'center', minWidth: 90 }}>{d}</th>)}
              </tr>
            </thead>
            <tbody>
              {staff.map((sm, i) => (
                <tr key={sm.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px 12px', fontWeight: 600 }}>{sm.name}</td>
                  {DAYS.map(day => {
                    const entry = schedules.find(s => s.staffId === sm.id && s.dayOfWeek === day);
                    return (
                      <td key={day} style={{ padding: '6px 8px', textAlign: 'center' }}>
                        {entry ? (
                          <span style={{ background: '#e3f2fd', color: '#1565c0', borderRadius: 4, padding: '3px 8px', fontSize: 11, fontWeight: 600 }}>
                            {entry.startTime}-{entry.endTime}
                          </span>
                        ) : (
                          <span style={{ color: '#ccc', fontSize: 12 }}>—</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* VACATIONS */}
      {tab === 'vacations' && !loading && (
        <div>
          <button onClick={() => setShowVacForm(v => !v)}
            style={{ marginBottom: 16, padding: '8px 20px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600 }}>
            {showVacForm ? 'Cancelar' : '+ Solicitar vacaciones'}
          </button>
          {showVacForm && (
            <div style={{ background: '#f5f5f5', padding: 20, borderRadius: 8, marginBottom: 20, border: '1px solid #ddd' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                <label>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Empleado</span>
                  <select value={vacForm.staffId} onChange={e => {
                    const sm = staff.find(s => s.id === e.target.value);
                    setVacForm(f => ({ ...f, staffId: e.target.value, staffName: sm?.name || '' }));
                  }} style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }}>
                    <option value="">-- Seleccionar --</option>
                    {staff.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </label>
                <label>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Desde</span>
                  <input type="date" value={vacForm.from} onChange={e => setVacForm(f => ({ ...f, from: e.target.value }))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }} />
                </label>
                <label>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Hasta</span>
                  <input type="date" value={vacForm.to} onChange={e => setVacForm(f => ({ ...f, to: e.target.value }))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }} />
                </label>
                <label>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Motivo</span>
                  <input type="text" value={vacForm.notes} onChange={e => setVacForm(f => ({ ...f, notes: e.target.value }))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }} />
                </label>
              </div>
              <button onClick={handleCreateVacation} disabled={!vacForm.staffId || !vacForm.from || !vacForm.to}
                style={{ padding: '8px 20px', background: '#388e3c', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600 }}>
                Enviar solicitud
              </button>
            </div>
          )}
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#1976d2', color: '#fff' }}>
                {['Empleado', 'Desde', 'Hasta', 'Estado', 'Notas', 'Acciones'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {vacations.map((v, i) => {
                const cfg = VAC_CFG[v.status] || { bg: '#f5f5f5', color: '#333' };
                return (
                  <tr key={v.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 600 }}>{v.staffName}</td>
                    <td style={{ padding: '8px 12px' }}>{v.from}</td>
                    <td style={{ padding: '8px 12px' }}>{v.to}</td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ background: cfg.bg, color: cfg.color, borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600 }}>{v.status}</span>
                    </td>
                    <td style={{ padding: '8px 12px', color: '#555' }}>{v.notes}</td>
                    <td style={{ padding: '8px 12px' }}>
                      {v.status === 'PENDING' && (
                        <button onClick={() => approveVacation(v.id)}
                          style={{ padding: '3px 10px', background: '#e8f5e9', color: '#2e7d32', border: '1px solid #2e7d32', borderRadius: 4, cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                          Aprobar
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* MONTHLY HOURS */}
      {tab === 'hours' && !loading && (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#1976d2', color: '#fff' }}>
              {['Empleado', 'Rol', 'Horas contrato/mes', 'Horas trabajadas', 'Diferencia'].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(hours).map(([id, data]: [string, any], i) => {
              const diff = (data.workedHours - data.contractHours).toFixed(1);
              const diffNum = parseFloat(diff);
              return (
                <tr key={id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px 12px', fontWeight: 600 }}>{data.name}</td>
                  <td style={{ padding: '8px 12px' }}>{ROLE_LABELS[data.role] || data.role}</td>
                  <td style={{ padding: '8px 12px' }}>{data.contractHours}h</td>
                  <td style={{ padding: '8px 12px' }}>{data.workedHours.toFixed(1)}h</td>
                  <td style={{ padding: '8px 12px', fontWeight: 700, color: diffNum >= 0 ? '#2e7d32' : '#c62828' }}>
                    {diffNum >= 0 ? '+' : ''}{diff}h
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
