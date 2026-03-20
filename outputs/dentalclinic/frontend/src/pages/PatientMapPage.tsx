import { useState, useEffect } from 'react';
import { apiFetch } from '../api/apiFetch';
import { API_BASE } from '../config/api';

interface PatientLocation {
  patientId: string;
  patientName: string;
  city: string;
  postalCode: string;
  province: string;
  lat: number;
  lng: number;
  appointmentsCount: number;
  lastVisit: string;
}
interface MapStats {
  totalPatients: number;
  byProvince: Record<string, number>;
  byPostalCode: Record<string, number>;
  centerLat: number;
  centerLng: number;
}

export default function PatientMapPage() {
  const [patients, setPatients] = useState<PatientLocation[]>([]);
  const [stats, setStats] = useState<MapStats | null>(null);
  const [selected, setSelected] = useState<PatientLocation | null>(null);
  const [filterCity, setFilterCity] = useState('');
  const [viewMode, setViewMode] = useState<'map' | 'list' | 'heatmap'>('map');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      apiFetch(`${API_BASE}/api/patient-map`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/patient-map/stats`).then(r => r.json()),
    ]).then(([p, s]) => {
      setPatients(Array.isArray(p) ? p : []);
      setStats(s as MapStats);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const filtered = patients.filter(p =>
    !filterCity || p.city.toLowerCase().includes(filterCity.toLowerCase())
  );

  // SVG map of Spain region (simplified, centered on Madrid)
  const LAT_MIN = 39.9, LAT_MAX = 40.8, LNG_MIN = -4.2, LNG_MAX = -3.2;
  const MAP_W = 700, MAP_H = 400;
  const toX = (lng: number) => ((lng - LNG_MIN) / (LNG_MAX - LNG_MIN)) * MAP_W;
  const toY = (lat: number) => MAP_H - ((lat - LAT_MIN) / (LAT_MAX - LAT_MIN)) * MAP_H;
  const maxAppts = Math.max(...patients.map(p => p.appointmentsCount), 1);

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ color: '#1976d2', marginBottom: 8 }}>Mapa de Pacientes</h2>

      {stats && (
        <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
          <div style={{ background: '#e3f2fd', border: '1px solid #1976d2', borderRadius: 8, padding: '10px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: '#1976d2' }}>{stats.totalPatients}</div>
            <div style={{ fontSize: 12, color: '#555' }}>Pacientes geolocalizados</div>
          </div>
          {Object.entries(stats.byProvince).map(([prov, count]) => (
            <div key={prov} style={{ background: '#f5f5f5', border: '1px solid #ccc', borderRadius: 8, padding: '10px 16px', textAlign: 'center' }}>
              <div style={{ fontSize: 22, fontWeight: 700, color: '#333' }}>{count}</div>
              <div style={{ fontSize: 12, color: '#555' }}>{prov}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center', flexWrap: 'wrap' }}>
        <input type="text" placeholder="Filtrar por ciudad..." value={filterCity}
          onChange={e => setFilterCity(e.target.value)}
          style={{ padding: '7px 12px', borderRadius: 4, border: '1px solid #ccc', width: 200 }} />
        {(['map', 'heatmap', 'list'] as const).map(mode => (
          <button key={mode} onClick={() => setViewMode(mode)}
            style={{ padding: '6px 16px', borderRadius: 4, border: '1px solid #1976d2', cursor: 'pointer',
              background: viewMode === mode ? '#1976d2' : '#fff', color: viewMode === mode ? '#fff' : '#1976d2', fontWeight: 600 }}>
            {mode === 'map' ? '📍 Mapa' : mode === 'heatmap' ? '🔥 Densidad' : '📋 Lista'}
          </button>
        ))}
      </div>

      {loading && <p>Cargando...</p>}

      {/* SVG MAP */}
      {viewMode === 'map' && !loading && (
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <div style={{ background: '#e8f4f8', border: '1px solid #90caf9', borderRadius: 8, overflow: 'hidden', position: 'relative', flex: '1 1 600px' }}>
            <div style={{ padding: '8px 12px', background: '#1976d2', color: '#fff', fontSize: 13, fontWeight: 600 }}>
              Área metropolitana de Madrid · Escala aproximada
            </div>
            <svg width={MAP_W} height={MAP_H} style={{ display: 'block' }}>
              {/* Grid lines */}
              {[40.0, 40.2, 40.4, 40.6, 40.8].map(lat => (
                <line key={lat} x1={0} y1={toY(lat)} x2={MAP_W} y2={toY(lat)}
                  stroke="#b0bec5" strokeWidth={0.5} strokeDasharray="4,4" />
              ))}
              {[-4.0, -3.8, -3.6, -3.4, -3.2].map(lng => (
                <line key={lng} x1={toX(lng)} y1={0} x2={toX(lng)} y2={MAP_H}
                  stroke="#b0bec5" strokeWidth={0.5} strokeDasharray="4,4" />
              ))}
              {/* Patient dots */}
              {filtered.map(p => {
                const cx = toX(p.lng), cy = toY(p.lat);
                const r = 6 + (p.appointmentsCount / maxAppts) * 12;
                const isSelected = selected?.patientId === p.patientId;
                return (
                  <g key={p.patientId} onClick={() => setSelected(isSelected ? null : p)} style={{ cursor: 'pointer' }}>
                    <circle cx={cx} cy={cy} r={r}
                      fill={isSelected ? '#ff5722' : '#1976d2'}
                      fillOpacity={0.7}
                      stroke={isSelected ? '#bf360c' : '#0d47a1'}
                      strokeWidth={isSelected ? 2 : 1} />
                    <text x={cx} y={cy + r + 12} textAnchor="middle" fontSize={10} fill="#333">
                      {p.city}
                    </text>
                  </g>
                );
              })}
            </svg>
            <div style={{ padding: '4px 12px', background: '#f5f5f5', fontSize: 11, color: '#888' }}>
              El tamaño del punto indica el número de citas. Haz clic para ver detalles.
            </div>
          </div>

          {selected && (
            <div style={{ flex: '0 0 240px', background: '#fff', border: '1px solid #e0e0e0', borderRadius: 8, padding: 16, boxShadow: '0 2px 8px rgba(0,0,0,.1)', height: 'fit-content' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <h3 style={{ margin: 0, fontSize: 15, color: '#1976d2' }}>Detalles paciente</h3>
                <button onClick={() => setSelected(null)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#888', fontSize: 18, padding: 0, lineHeight: 1 }}>×</button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 14 }}>
                <div><strong>Nombre:</strong> {selected.patientName}</div>
                <div><strong>Ciudad:</strong> {selected.city}</div>
                <div><strong>C.P.:</strong> {selected.postalCode}</div>
                <div><strong>Provincia:</strong> {selected.province}</div>
                <div><strong>Citas totales:</strong> {selected.appointmentsCount}</div>
                <div><strong>Última visita:</strong> {selected.lastVisit}</div>
                <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                  📍 {selected.lat.toFixed(4)}, {selected.lng.toFixed(4)}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* HEATMAP */}
      {viewMode === 'heatmap' && !loading && (
        <div style={{ background: '#1a237e', borderRadius: 8, overflow: 'hidden' }}>
          <div style={{ padding: '8px 12px', color: '#fff', fontSize: 13, fontWeight: 600 }}>
            Densidad de pacientes por zona
          </div>
          <svg width={MAP_W} height={MAP_H} style={{ display: 'block' }}>
            {filtered.map(p => {
              const cx = toX(p.lng), cy = toY(p.lat);
              const r = 20 + (p.appointmentsCount / maxAppts) * 40;
              return (
                <circle key={p.patientId} cx={cx} cy={cy} r={r}
                  fill={`rgba(255, ${Math.round(200 - p.appointmentsCount * 10)}, 0, 0.4)`}
                  stroke="none" />
              );
            })}
            {filtered.map(p => (
              <text key={p.patientId + '_label'} x={toX(p.lng)} y={toY(p.lat) + 4}
                textAnchor="middle" fontSize={9} fill="#fff" fontWeight="bold">
                {p.city}
              </text>
            ))}
          </svg>
        </div>
      )}

      {/* LIST */}
      {viewMode === 'list' && !loading && (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#1976d2', color: '#fff' }}>
              {['Paciente', 'Ciudad', 'C.P.', 'Provincia', 'Nº Citas', 'Última visita'].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((p, i) => (
              <tr key={p.patientId} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '8px 12px', fontWeight: 600 }}>{p.patientName}</td>
                <td style={{ padding: '8px 12px' }}>{p.city}</td>
                <td style={{ padding: '8px 12px' }}>{p.postalCode}</td>
                <td style={{ padding: '8px 12px' }}>{p.province}</td>
                <td style={{ padding: '8px 12px' }}>
                  <span style={{ background: '#e3f2fd', color: '#1565c0', borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 700 }}>
                    {p.appointmentsCount}
                  </span>
                </td>
                <td style={{ padding: '8px 12px', color: '#555' }}>{p.lastVisit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
