import { useState, useEffect } from 'react';
import { apiFetch } from '../api/apiFetch';
import { API_BASE } from '../config/api';

interface NpsSurvey {
  id: string;
  patientId: string;
  patientName: string;
  dentistName: string;
  score: number;
  comment: string;
  category: string;
  date: string;
}
interface NpsStats {
  npsScore: number;
  promoters: number;
  passives: number;
  detractors: number;
  total: number;
  categoryAverages: Record<string, number>;
}

function ScoreColor(score: number) {
  if (score >= 9) return '#2e7d32';
  if (score >= 7) return '#e65100';
  return '#c62828';
}

export default function NpsPage() {
  const [tab, setTab] = useState<'dashboard' | 'surveys' | 'new'>('dashboard');
  const [stats, setStats] = useState<NpsStats | null>(null);
  const [surveys, setSurveys] = useState<NpsSurvey[]>([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ patientId: '', patientName: '', dentistName: '', score: 9, comment: '', category: 'ATENCION' });
  const [saveMsg, setSaveMsg] = useState<{ ok: boolean; text: string } | null>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      apiFetch(`${API_BASE}/api/nps/stats`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/nps`).then(r => r.json()),
    ]).then(([s, sv]) => {
      setStats(s as NpsStats);
      setSurveys(Array.isArray(sv) ? sv : []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleSubmit = async () => {
    setSaveMsg(null);
    try {
      const res = await apiFetch(`${API_BASE}/api/nps`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        const newSurvey: NpsSurvey = await res.json();
        setSurveys(prev => [newSurvey, ...prev]);
        setSaveMsg({ ok: true, text: 'Encuesta registrada correctamente.' });
        setForm({ patientId: '', patientName: '', dentistName: '', score: 9, comment: '', category: 'ATENCION' });
        setTab('surveys');
      } else {
        setSaveMsg({ ok: false, text: 'Error al guardar la encuesta.' });
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

  const NPS_COLOR = stats && stats.npsScore >= 50 ? '#2e7d32' : stats && stats.npsScore >= 0 ? '#e65100' : '#c62828';

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1976d2', marginBottom: 16 }}>Encuestas NPS – Satisfacción del Paciente</h2>
      <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: 24 }}>
        <button style={tabStyle(tab === 'dashboard')} onClick={() => setTab('dashboard')}>Dashboard</button>
        <button style={tabStyle(tab === 'surveys')} onClick={() => setTab('surveys')}>Encuestas</button>
        <button style={tabStyle(tab === 'new')} onClick={() => setTab('new')}>+ Nueva encuesta</button>
      </div>

      {loading && <p>Cargando...</p>}

      {/* DASHBOARD */}
      {tab === 'dashboard' && !loading && stats && (
        <div>
          {/* Big NPS score */}
          <div style={{ display: 'flex', gap: 24, marginBottom: 32, flexWrap: 'wrap' }}>
            <div style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 12, padding: '24px 40px', textAlign: 'center', boxShadow: '0 2px 8px rgba(0,0,0,.08)' }}>
              <div style={{ fontSize: 64, fontWeight: 900, color: NPS_COLOR, lineHeight: 1 }}>{stats.npsScore}</div>
              <div style={{ fontSize: 16, color: '#888', marginTop: 4 }}>NPS Score</div>
            </div>
            <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
              {[
                { label: 'Promotores', value: stats.promoters, color: '#2e7d32', bg: '#e8f5e9', icon: '😊' },
                { label: 'Neutros', value: stats.passives, color: '#e65100', bg: '#fff3e0', icon: '😐' },
                { label: 'Detractores', value: stats.detractors, color: '#c62828', bg: '#ffebee', icon: '😞' },
              ].map(({ label, value, color, bg, icon }) => (
                <div key={label} style={{ background: bg, border: `1px solid ${color}`, borderRadius: 10, padding: '16px 24px', textAlign: 'center', minWidth: 110 }}>
                  <div style={{ fontSize: 28 }}>{icon}</div>
                  <div style={{ fontSize: 28, fontWeight: 700, color }}>{value}</div>
                  <div style={{ fontSize: 13, color: '#555' }}>{label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Category averages */}
          <h3 style={{ marginBottom: 12 }}>Puntuación por categoría</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {Object.entries(stats.categoryAverages).map(([cat, avg]) => (
              <div key={cat} style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 8, padding: '12px 16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontWeight: 600 }}>{cat.replace(/_/g, ' ')}</span>
                  <span style={{ fontWeight: 700, color: ScoreColor(avg) }}>{avg.toFixed(1)} / 10</span>
                </div>
                <div style={{ background: '#f0f0f0', borderRadius: 4, height: 10 }}>
                  <div style={{
                    width: `${avg * 10}%`, height: '100%', borderRadius: 4,
                    background: ScoreColor(avg),
                  }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SURVEYS LIST */}
      {tab === 'surveys' && !loading && (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#1976d2', color: '#fff' }}>
              {['Fecha', 'Paciente', 'Dentista', 'Categoría', 'Puntuación', 'Comentario'].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {surveys.map((s, i) => (
              <tr key={s.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '8px 12px', whiteSpace: 'nowrap' }}>{s.date}</td>
                <td style={{ padding: '8px 12px' }}>{s.patientName}</td>
                <td style={{ padding: '8px 12px' }}>{s.dentistName}</td>
                <td style={{ padding: '8px 12px', fontSize: 12 }}>{s.category.replace(/_/g, ' ')}</td>
                <td style={{ padding: '8px 12px' }}>
                  <span style={{
                    background: ScoreColor(s.score), color: '#fff',
                    borderRadius: 20, padding: '2px 12px', fontWeight: 700, fontSize: 14,
                  }}>{s.score}</span>
                </td>
                <td style={{ padding: '8px 12px', color: '#555', fontStyle: 'italic' }}>{s.comment}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* NEW SURVEY */}
      {tab === 'new' && (
        <div style={{ maxWidth: 560, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {(['patientId', 'patientName', 'dentistName'] as const).map(field => (
            <label key={field}>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>
                {field === 'patientId' ? 'UUID Paciente' : field === 'patientName' ? 'Nombre paciente' : 'Dentista'}
              </span>
              <input type="text" value={form[field]} onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
            </label>
          ))}
          <label>
            <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Categoría</span>
            <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
              style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }}>
              {['INSTALACIONES','ATENCION','TIEMPO_ESPERA','RESULTADO_TRATAMIENTO','PRECIO'].map(c => (
                <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </label>
          <label>
            <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>
              Puntuación: <span style={{ color: ScoreColor(form.score), fontWeight: 900 }}>{form.score}</span> / 10
            </span>
            <input type="range" min={0} max={10} value={form.score}
              onChange={e => setForm(f => ({ ...f, score: +e.target.value }))}
              style={{ width: '100%' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#888' }}>
              <span>😞 Detractor (0-6)</span><span>😐 Neutro (7-8)</span><span>😊 Promotor (9-10)</span>
            </div>
          </label>
          <label>
            <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Comentario</span>
            <textarea value={form.comment} rows={3} onChange={e => setForm(f => ({ ...f, comment: e.target.value }))}
              style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc', fontFamily: 'inherit' }} />
          </label>
          <button onClick={handleSubmit}
            style={{ padding: '10px 24px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600, alignSelf: 'flex-start' }}>
            Guardar encuesta
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
