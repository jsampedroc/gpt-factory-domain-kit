import { useState, useEffect } from 'react';
import { apiFetch } from '../api/apiFetch';
import { API_BASE } from '../config/api';

interface PreVisitForm {
  id: string;
  patientId: string;
  patientName: string;
  appointmentId: string;
  date: string;
  status: string;
  allergies: string[] | null;
  currentMedications: string[] | null;
  medicalConditions: string[] | null;
  chiefComplaint: string | null;
  painScale: string | null;
  painLocation: string | null;
  painSince: string | null;
  painType: string | null;
  smoker: boolean;
  alcoholConsumer: boolean;
  bruxism: boolean;
  gdprConsent: boolean;
  treatmentConsent: boolean;
  submittedAt: string | null;
}

const PAIN_SCALE_COLOR = (s: string | null) => {
  if (!s) return '#888';
  const n = parseInt(s);
  if (n >= 8) return '#c62828';
  if (n >= 5) return '#e65100';
  if (n >= 1) return '#f9a825';
  return '#2e7d32';
};

export default function PreVisitFormPage() {
  const [tab, setTab] = useState<'list' | 'fill' | 'detail'>('list');
  const [forms, setForms] = useState<PreVisitForm[]>([]);
  const [selectedForm, setSelectedForm] = useState<PreVisitForm | null>(null);
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState('');
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  // New form creation
  const [newForm, setNewForm] = useState({ patientId: '', patientName: '', appointmentId: '' });

  // Fill form state
  const [fillData, setFillData] = useState({
    allergies: '', currentMedications: '', medicalConditions: '',
    chiefComplaint: '', painScale: '0', painLocation: '', painSince: '', painType: 'Sin dolor',
    smoker: false, alcoholConsumer: false, bruxism: false,
    gdprConsent: false, treatmentConsent: false,
  });

  const loadForms = () => {
    setLoading(true);
    const url = filterStatus ? `${API_BASE}/api/previsit-forms?status=${filterStatus}` : `${API_BASE}/api/previsit-forms`;
    apiFetch(url).then(r => r.json())
      .then(data => setForms(Array.isArray(data) ? data : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadForms(); }, [filterStatus]);

  const handleCreateForm = async () => {
    if (!newForm.patientId || !newForm.patientName) return;
    const res = await apiFetch(`${API_BASE}/api/previsit-forms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newForm),
    });
    if (res.ok) {
      const created: PreVisitForm = await res.json();
      setForms(prev => [created, ...prev]);
      setSelectedForm(created);
      setMsg({ ok: true, text: 'Formulario creado. El paciente puede rellenarlo ahora.' });
      setNewForm({ patientId: '', patientName: '', appointmentId: '' });
      setTab('fill');
    }
  };

  const handleSubmitForm = async () => {
    if (!selectedForm) return;
    setMsg(null);
    const payload = {
      ...selectedForm,
      allergies: fillData.allergies ? fillData.allergies.split(',').map(s => s.trim()) : [],
      currentMedications: fillData.currentMedications ? fillData.currentMedications.split(',').map(s => s.trim()) : [],
      medicalConditions: fillData.medicalConditions ? fillData.medicalConditions.split(',').map(s => s.trim()) : [],
      chiefComplaint: fillData.chiefComplaint,
      painScale: fillData.painScale,
      painLocation: fillData.painLocation,
      painSince: fillData.painSince,
      painType: fillData.painType,
      smoker: fillData.smoker,
      alcoholConsumer: fillData.alcoholConsumer,
      bruxism: fillData.bruxism,
      gdprConsent: fillData.gdprConsent,
      treatmentConsent: fillData.treatmentConsent,
    };
    const res = await apiFetch(`${API_BASE}/api/previsit-forms/${selectedForm.id}/submit`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      const updated: PreVisitForm = await res.json();
      setForms(prev => prev.map(f => f.id === updated.id ? updated : f));
      setSelectedForm(updated);
      setMsg({ ok: true, text: 'Formulario enviado correctamente. ¡Gracias!' });
      setTab('detail');
    } else {
      setMsg({ ok: false, text: 'Error al enviar el formulario.' });
    }
  };

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: '8px 20px', cursor: 'pointer', background: 'none', border: 'none',
    borderBottom: active ? '3px solid #1976d2' : '3px solid transparent',
    fontWeight: active ? 700 : 400, color: active ? '#1976d2' : '#555', fontSize: 15,
  });

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      <h2 style={{ color: '#1976d2', marginBottom: 16 }}>Formularios Pre-Visita</h2>
      <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: 24 }}>
        <button style={tabStyle(tab === 'list')} onClick={() => setTab('list')}>Formularios</button>
        <button style={tabStyle(tab === 'fill')} onClick={() => setTab('fill')}>Rellenar formulario</button>
        {selectedForm && tab === 'detail' && (
          <button style={tabStyle(true)}>Ver detalle</button>
        )}
      </div>

      {msg && (
        <div style={{ padding: '10px 16px', borderRadius: 4, background: msg.ok ? '#e8f5e9' : '#ffebee', color: msg.ok ? '#2e7d32' : '#c62828', fontWeight: 600, marginBottom: 16 }}>
          {msg.text}
        </div>
      )}

      {/* LIST */}
      {tab === 'list' && (
        <div>
          {/* Create new */}
          <div style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 8, padding: 16, marginBottom: 20 }}>
            <h3 style={{ marginTop: 0, marginBottom: 12 }}>Crear nuevo formulario</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: 10, alignItems: 'end' }}>
              {[{ f: 'patientId', l: 'UUID Paciente *' }, { f: 'patientName', l: 'Nombre paciente *' }, { f: 'appointmentId', l: 'ID Cita (opcional)' }].map(({ f, l }) => (
                <label key={f}>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4, fontSize: 13 }}>{l}</span>
                  <input type="text" value={(newForm as any)[f]} onChange={e => setNewForm(prev => ({ ...prev, [f]: e.target.value }))}
                    style={{ width: '100%', padding: '6px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
                </label>
              ))}
              <button onClick={handleCreateForm} disabled={!newForm.patientId || !newForm.patientName}
                style={{ padding: '8px 16px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600, height: 36 }}>
                Crear
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            {['', 'PENDING', 'COMPLETED'].map(s => (
              <button key={s} onClick={() => setFilterStatus(s)}
                style={{ padding: '4px 14px', borderRadius: 16, border: '1px solid #1976d2', cursor: 'pointer',
                  background: filterStatus === s ? '#1976d2' : '#fff', color: filterStatus === s ? '#fff' : '#1976d2', fontWeight: 600, fontSize: 13 }}>
                {s === '' ? 'Todos' : s === 'PENDING' ? 'Pendientes' : 'Completados'}
              </button>
            ))}
          </div>

          {loading && <p>Cargando...</p>}
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#1976d2', color: '#fff' }}>
                {['Paciente', 'Fecha', 'Estado', 'Enviado', 'Acciones'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {forms.map((f, i) => (
                <tr key={f.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px 12px', fontWeight: 600 }}>{f.patientName}</td>
                  <td style={{ padding: '8px 12px' }}>{f.date}</td>
                  <td style={{ padding: '8px 12px' }}>
                    <span style={{
                      background: f.status === 'COMPLETED' ? '#e8f5e9' : '#fff3e0',
                      color: f.status === 'COMPLETED' ? '#2e7d32' : '#e65100',
                      borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600,
                    }}>{f.status === 'COMPLETED' ? 'Completado' : 'Pendiente'}</span>
                  </td>
                  <td style={{ padding: '8px 12px', fontSize: 12, color: '#555' }}>{f.submittedAt || '—'}</td>
                  <td style={{ padding: '8px 12px' }}>
                    <div style={{ display: 'flex', gap: 6 }}>
                      {f.status === 'PENDING' && (
                        <button onClick={() => { setSelectedForm(f); setTab('fill'); }}
                          style={{ padding: '3px 10px', background: '#e3f2fd', color: '#1565c0', border: '1px solid #1565c0', borderRadius: 4, cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                          Rellenar
                        </button>
                      )}
                      {f.status === 'COMPLETED' && (
                        <button onClick={() => { setSelectedForm(f); setTab('detail'); }}
                          style={{ padding: '3px 10px', background: '#e8f5e9', color: '#2e7d32', border: '1px solid #2e7d32', borderRadius: 4, cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                          Ver
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* FILL FORM */}
      {tab === 'fill' && (
        <div style={{ maxWidth: 680 }}>
          {selectedForm && (
            <div style={{ background: '#e3f2fd', border: '1px solid #90caf9', borderRadius: 8, padding: '12px 16px', marginBottom: 20 }}>
              <strong>Paciente:</strong> {selectedForm.patientName} &nbsp;·&nbsp; <strong>Cita:</strong> {selectedForm.date}
            </div>
          )}

          <section style={{ marginBottom: 24 }}>
            <h3 style={{ color: '#1976d2', borderBottom: '2px solid #e0e0e0', paddingBottom: 8 }}>🩺 Historial médico</h3>
            {[
              { f: 'allergies', l: 'Alergias conocidas (separadas por coma)', ph: 'Ej: Penicilina, Aspirina' },
              { f: 'currentMedications', l: 'Medicación actual', ph: 'Ej: Ibuprofeno 400mg, Omeprazol' },
              { f: 'medicalConditions', l: 'Enfermedades / condiciones médicas', ph: 'Ej: Diabetes, Hipertensión' },
            ].map(({ f, l, ph }) => (
              <label key={f} style={{ display: 'block', marginBottom: 12 }}>
                <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>{l}</span>
                <input type="text" value={(fillData as any)[f]} placeholder={ph}
                  onChange={e => setFillData(d => ({ ...d, [f]: e.target.value }))}
                  style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
              </label>
            ))}
          </section>

          <section style={{ marginBottom: 24 }}>
            <h3 style={{ color: '#1976d2', borderBottom: '2px solid #e0e0e0', paddingBottom: 8 }}>😮 Motivo de la visita</h3>
            <label style={{ display: 'block', marginBottom: 12 }}>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>¿Cuál es el motivo principal de su visita?</span>
              <textarea value={fillData.chiefComplaint} rows={3}
                onChange={e => setFillData(d => ({ ...d, chiefComplaint: e.target.value }))}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc', fontFamily: 'inherit' }} />
            </label>
            <label style={{ display: 'block', marginBottom: 12 }}>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>
                Nivel de dolor: <span style={{ color: PAIN_SCALE_COLOR(fillData.painScale), fontWeight: 900, fontSize: 18 }}>{fillData.painScale}/10</span>
              </span>
              <input type="range" min={0} max={10} value={fillData.painScale}
                onChange={e => setFillData(d => ({ ...d, painScale: e.target.value }))}
                style={{ width: '100%' }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#888' }}>
                <span>Sin dolor</span><span>Moderado</span><span>Severo</span>
              </div>
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
              {[
                { f: 'painLocation', l: 'Localización del dolor', ph: 'Ej: Muela del juicio' },
                { f: 'painSince', l: 'Desde cuándo', ph: 'Ej: 3 días' },
                { f: 'painType', l: 'Tipo de dolor', ph: 'Pulsátil, continuo...' },
              ].map(({ f, l, ph }) => (
                <label key={f}>
                  <span style={{ display: 'block', fontWeight: 600, marginBottom: 4, fontSize: 13 }}>{l}</span>
                  <input type="text" value={(fillData as any)[f]} placeholder={ph}
                    onChange={e => setFillData(d => ({ ...d, [f]: e.target.value }))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: 4, border: '1px solid #ccc' }} />
                </label>
              ))}
            </div>
          </section>

          <section style={{ marginBottom: 24 }}>
            <h3 style={{ color: '#1976d2', borderBottom: '2px solid #e0e0e0', paddingBottom: 8 }}>🏃 Hábitos</h3>
            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
              {[
                { f: 'smoker', l: '🚬 Fumador/a' },
                { f: 'alcoholConsumer', l: '🍷 Consumo de alcohol' },
                { f: 'bruxism', l: '😬 Bruxismo (rechinar dientes)' },
              ].map(({ f, l }) => (
                <label key={f} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 15 }}>
                  <input type="checkbox" checked={(fillData as any)[f]}
                    onChange={e => setFillData(d => ({ ...d, [f]: e.target.checked }))} />
                  {l}
                </label>
              ))}
            </div>
          </section>

          <section style={{ marginBottom: 24 }}>
            <h3 style={{ color: '#1976d2', borderBottom: '2px solid #e0e0e0', paddingBottom: 8 }}>✅ Consentimientos</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <label style={{ display: 'flex', alignItems: 'flex-start', gap: 10, cursor: 'pointer' }}>
                <input type="checkbox" checked={fillData.gdprConsent}
                  onChange={e => setFillData(d => ({ ...d, gdprConsent: e.target.checked }))}
                  style={{ marginTop: 2 }} />
                <span style={{ fontSize: 14 }}>He leído y acepto la <strong>Política de Privacidad (RGPD)</strong>. Consiento el tratamiento de mis datos personales con fines de gestión clínica.</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'flex-start', gap: 10, cursor: 'pointer' }}>
                <input type="checkbox" checked={fillData.treatmentConsent}
                  onChange={e => setFillData(d => ({ ...d, treatmentConsent: e.target.checked }))}
                  style={{ marginTop: 2 }} />
                <span style={{ fontSize: 14 }}>Consiento la realización de los tratamientos dentales que el profesional considere necesarios, habiendo sido informado/a de los mismos.</span>
              </label>
            </div>
          </section>

          <button onClick={handleSubmitForm}
            disabled={!fillData.gdprConsent || !fillData.treatmentConsent || !fillData.chiefComplaint}
            style={{ padding: '12px 32px', background: '#388e3c', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 700, fontSize: 16 }}>
            ✓ Enviar formulario
          </button>
          {(!fillData.gdprConsent || !fillData.treatmentConsent) && (
            <p style={{ fontSize: 12, color: '#888', marginTop: 8 }}>* Debes aceptar ambos consentimientos para enviar el formulario.</p>
          )}
        </div>
      )}

      {/* DETAIL VIEW */}
      {tab === 'detail' && selectedForm && selectedForm.status === 'COMPLETED' && (
        <div style={{ maxWidth: 680 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {[
              { label: 'Paciente', value: selectedForm.patientName },
              { label: 'Fecha', value: selectedForm.date },
              { label: 'Enviado', value: selectedForm.submittedAt || '—' },
              { label: 'Estado', value: 'COMPLETADO' },
            ].map(({ label, value }) => (
              <div key={label} style={{ background: '#f9f9f9', border: '1px solid #e0e0e0', borderRadius: 6, padding: '10px 14px' }}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>{label}</div>
                <div style={{ fontWeight: 600 }}>{value}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
            {[
              { label: 'Alergias', value: selectedForm.allergies?.join(', ') || 'Ninguna' },
              { label: 'Medicación', value: selectedForm.currentMedications?.join(', ') || 'Ninguna' },
              { label: 'Enfermedades', value: selectedForm.medicalConditions?.join(', ') || 'Ninguna' },
              { label: 'Motivo de visita', value: selectedForm.chiefComplaint || '—' },
              { label: 'Nivel de dolor', value: selectedForm.painScale ? `${selectedForm.painScale}/10` : '0/10' },
              { label: 'Localización del dolor', value: selectedForm.painLocation || '—' },
              { label: 'Desde cuándo', value: selectedForm.painSince || '—' },
              { label: 'Tipo de dolor', value: selectedForm.painType || '—' },
            ].map(({ label, value }) => (
              <div key={label} style={{ display: 'flex', gap: 12 }}>
                <span style={{ fontWeight: 600, minWidth: 180, color: '#555' }}>{label}:</span>
                <span>{value}</span>
              </div>
            ))}
            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', marginTop: 4 }}>
              {[
                { label: 'Fumador/a', value: selectedForm.smoker },
                { label: 'Alcohol', value: selectedForm.alcoholConsumer },
                { label: 'Bruxismo', value: selectedForm.bruxism },
                { label: 'Consentimiento RGPD', value: selectedForm.gdprConsent },
                { label: 'Consentimiento tratamiento', value: selectedForm.treatmentConsent },
              ].map(({ label, value }) => (
                <span key={label} style={{
                  background: value ? '#e8f5e9' : '#f5f5f5',
                  color: value ? '#2e7d32' : '#888',
                  borderRadius: 12, padding: '3px 12px', fontSize: 13, fontWeight: 600,
                }}>
                  {value ? '✓' : '✗'} {label}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
