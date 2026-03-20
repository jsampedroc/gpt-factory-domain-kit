import { useState, useEffect } from 'react';
import { apiFetch } from '../api/apiFetch';
import { API_BASE } from '../config/api';

interface Operatory {
  id: string;
  name: string;
  type: string;
  status: string;
  color: string;
  notes: string;
}
interface OperatorySchedule {
  id: string;
  operatoryId: string;
  patientName: string;
  dentistName: string;
  procedure: string;
  startTime: string;
  endTime: string;
  status: string;
}
interface OccupancyStats {
  operatoryId: string;
  operatoryName: string;
  totalSlots: number;
  occupiedSlots: number;
  occupancyRate: number;
}

const STATUS_COLOR: Record<string, string> = {
  AVAILABLE: '#2e7d32',
  OCCUPIED: '#1565c0',
  MAINTENANCE: '#e65100',
  INACTIVE: '#757575',
};

const STATUS_BG: Record<string, string> = {
  AVAILABLE: '#e8f5e9',
  OCCUPIED: '#e3f2fd',
  MAINTENANCE: '#fff3e0',
  INACTIVE: '#f5f5f5',
};

const SCHED_COLOR: Record<string, string> = {
  CONFIRMED: '#1565c0',
  IN_PROGRESS: '#2e7d32',
  COMPLETED: '#757575',
  CANCELLED: '#c62828',
};

export default function OperatoryPage() {
  const [tab, setTab] = useState<'overview' | 'schedule' | 'occupancy'>('overview');
  const [operatories, setOperatories] = useState<Operatory[]>([]);
  const [schedule, setSchedule] = useState<OperatorySchedule[]>([]);
  const [occupancy, setOccupancy] = useState<OccupancyStats[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      apiFetch(`${API_BASE}/api/operatories`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/operatories/schedule/today`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/operatories/occupancy`).then(r => r.json()),
    ]).then(([ops, sch, occ]) => {
      setOperatories(Array.isArray(ops) ? ops : []);
      setSchedule(Array.isArray(sch) ? sch : []);
      setOccupancy(Array.isArray(occ) ? occ : []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const changeStatus = async (id: string, status: string) => {
    const res = await apiFetch(`${API_BASE}/api/operatories/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (res.ok) {
      const updated: Operatory = await res.json();
      setOperatories(prev => prev.map(o => o.id === id ? updated : o));
    }
  };

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: '8px 20px', cursor: 'pointer', background: 'none', border: 'none',
    borderBottom: active ? '3px solid #1976d2' : '3px solid transparent',
    fontWeight: active ? 700 : 400, color: active ? '#1976d2' : '#555', fontSize: 15,
  });

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ color: '#1976d2', marginBottom: 16 }}>Gestión de Sillones</h2>
      <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: 24 }}>
        <button style={tabStyle(tab === 'overview')} onClick={() => setTab('overview')}>Vista general</button>
        <button style={tabStyle(tab === 'schedule')} onClick={() => setTab('schedule')}>Agenda hoy</button>
        <button style={tabStyle(tab === 'occupancy')} onClick={() => setTab('occupancy')}>Ocupación</button>
      </div>

      {loading && <p>Cargando...</p>}

      {/* OVERVIEW */}
      {tab === 'overview' && !loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 16 }}>
          {operatories.map(op => (
            <div key={op.id} style={{
              border: `2px solid ${op.color}`, borderRadius: 10, padding: 16, background: '#fff',
              boxShadow: '0 2px 8px rgba(0,0,0,.08)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontWeight: 700, fontSize: 16 }}>🦷 {op.name}</span>
                <span style={{
                  background: STATUS_BG[op.status] || '#f5f5f5',
                  color: STATUS_COLOR[op.status] || '#333',
                  borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600,
                }}>{op.status}</span>
              </div>
              <p style={{ color: '#888', fontSize: 13, margin: '4px 0 12px' }}>{op.notes}</p>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {(['AVAILABLE', 'OCCUPIED', 'MAINTENANCE'] as const).filter(s => s !== op.status).map(s => (
                  <button key={s} onClick={() => changeStatus(op.id, s)}
                    style={{ padding: '4px 10px', fontSize: 11, background: STATUS_BG[s], color: STATUS_COLOR[s],
                      border: `1px solid ${STATUS_COLOR[s]}`, borderRadius: 4, cursor: 'pointer', fontWeight: 600 }}>
                    → {s}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SCHEDULE TODAY */}
      {tab === 'schedule' && !loading && (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#1976d2', color: '#fff' }}>
              {['Hora inicio', 'Hora fin', 'Sillón', 'Paciente', 'Dentista', 'Procedimiento', 'Estado'].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {schedule.length === 0 && (
              <tr><td colSpan={7} style={{ padding: 20, color: '#888', textAlign: 'center' }}>Sin citas para hoy</td></tr>
            )}
            {schedule.map((s, i) => {
              const op = operatories.find(o => o.id === s.operatoryId);
              return (
                <tr key={s.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px 12px' }}>{s.startTime.split('T')[1]}</td>
                  <td style={{ padding: '8px 12px' }}>{s.endTime.split('T')[1]}</td>
                  <td style={{ padding: '8px 12px' }}>{op?.name || s.operatoryId}</td>
                  <td style={{ padding: '8px 12px', fontWeight: 600 }}>{s.patientName}</td>
                  <td style={{ padding: '8px 12px' }}>{s.dentistName}</td>
                  <td style={{ padding: '8px 12px' }}>{s.procedure}</td>
                  <td style={{ padding: '8px 12px' }}>
                    <span style={{
                      background: SCHED_COLOR[s.status] || '#888', color: '#fff',
                      borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600,
                    }}>{s.status}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {/* OCCUPANCY */}
      {tab === 'occupancy' && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {occupancy.map(o => (
            <div key={o.operatoryId} style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 8, padding: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontWeight: 700, fontSize: 15 }}>{o.operatoryName}</span>
                <span style={{ fontWeight: 700, color: o.occupancyRate > 70 ? '#c62828' : o.occupancyRate > 40 ? '#e65100' : '#2e7d32' }}>
                  {o.occupancyRate}%
                </span>
              </div>
              <div style={{ background: '#f0f0f0', borderRadius: 4, height: 12, overflow: 'hidden' }}>
                <div style={{
                  width: `${o.occupancyRate}%`, height: '100%',
                  background: o.occupancyRate > 70 ? '#c62828' : o.occupancyRate > 40 ? '#ff9800' : '#4caf50',
                  transition: 'width 0.4s',
                }} />
              </div>
              <p style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                {o.occupiedSlots} de {o.totalSlots} slots ocupados hoy
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
