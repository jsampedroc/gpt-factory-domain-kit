import { useState, useEffect } from 'react';
import { apiFetch } from '../api/apiFetch';
import { API_BASE } from '../config/api';

interface BackupEntry {
  id: string;
  filename: string;
  type: string;
  status: string;
  sizeBytes: number;
  s3Key: string;
  s3Bucket: string;
  createdAt: string;
  completedAt: string | null;
  errorMessage: string | null;
}
interface BackupConfig {
  autoBackupEnabled: boolean;
  cronExpression: string;
  s3Bucket: string;
  s3Region: string;
  retentionDays: string;
  includedDatasets: string[];
}
interface BackupStats {
  totalBackups: number;
  successfulBackups: number;
  failedBackups: number;
  totalSizeBytes: number;
  lastBackupAt: string;
  nextScheduledAt: string;
}

const STATUS_CFG: Record<string, { bg: string; color: string; icon: string }> = {
  SUCCESS:     { bg: '#e8f5e9', color: '#2e7d32', icon: '✓' },
  FAILED:      { bg: '#ffebee', color: '#c62828', icon: '✗' },
  IN_PROGRESS: { bg: '#fff3e0', color: '#e65100', icon: '⏳' },
};

function formatBytes(bytes: number): string {
  if (bytes === 0) return '—';
  if (bytes >= 1024 * 1024 * 1024) return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
  if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  return (bytes / 1024).toFixed(0) + ' KB';
}

const DATASETS = ['PATIENTS', 'APPOINTMENTS', 'INVOICES', 'CLINICAL_RECORDS', 'DOCUMENTS', 'COMMUNICATIONS', 'STAFF'];
const REGIONS = ['eu-west-1', 'eu-central-1', 'us-east-1', 'us-west-2', 'ap-southeast-1'];

export default function BackupPage() {
  const [tab, setTab] = useState<'backups' | 'config' | 'stats'>('backups');
  const [backups, setBackups] = useState<BackupEntry[]>([]);
  const [config, setConfig] = useState<BackupConfig | null>(null);
  const [stats, setStats] = useState<BackupStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [editConfig, setEditConfig] = useState<BackupConfig | null>(null);

  const loadAll = () => {
    setLoading(true);
    Promise.all([
      apiFetch(`${API_BASE}/api/backups`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/backups/config`).then(r => r.json()),
      apiFetch(`${API_BASE}/api/backups/stats`).then(r => r.json()),
    ]).then(([b, c, s]) => {
      setBackups(Array.isArray(b) ? b : []);
      setConfig(c as BackupConfig);
      setEditConfig(c as BackupConfig);
      setStats(s as BackupStats);
    }).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { loadAll(); }, []);

  const triggerBackup = async () => {
    setTriggering(true);
    setMsg(null);
    try {
      const res = await apiFetch(`${API_BASE}/api/backups/trigger`, { method: 'POST' });
      if (res.ok) {
        const newBackup: BackupEntry = await res.json();
        setBackups(prev => [newBackup, ...prev]);
        setMsg({ ok: true, text: `Backup completado: ${newBackup.filename} (${formatBytes(newBackup.sizeBytes)})` });
        loadAll();
      } else {
        setMsg({ ok: false, text: 'Error al iniciar el backup.' });
      }
    } catch {
      setMsg({ ok: false, text: 'Error de conexión.' });
    } finally {
      setTriggering(false);
    }
  };

  const deleteBackup = async (id: string, filename: string) => {
    if (!confirm(`¿Eliminar backup "${filename}" de S3?`)) return;
    const res = await apiFetch(`${API_BASE}/api/backups/${id}`, { method: 'DELETE' });
    if (res.ok) {
      setBackups(prev => prev.filter(b => b.id !== id));
      setMsg({ ok: true, text: 'Backup eliminado correctamente.' });
    }
  };

  const saveConfig = async () => {
    if (!editConfig) return;
    const res = await apiFetch(`${API_BASE}/api/backups/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editConfig),
    });
    if (res.ok) {
      const updated: BackupConfig = await res.json();
      setConfig(updated);
      setMsg({ ok: true, text: 'Configuración guardada correctamente.' });
    }
  };

  const toggleDataset = (dataset: string) => {
    if (!editConfig) return;
    const current = editConfig.includedDatasets;
    const next = current.includes(dataset)
      ? current.filter(d => d !== dataset)
      : [...current, dataset];
    setEditConfig({ ...editConfig, includedDatasets: next });
  };

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: '8px 20px', cursor: 'pointer', background: 'none', border: 'none',
    borderBottom: active ? '3px solid #1976d2' : '3px solid transparent',
    fontWeight: active ? 700 : 400, color: active ? '#1976d2' : '#555', fontSize: 15,
  });

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <h2 style={{ color: '#1976d2', margin: 0 }}>Backup automático · AWS S3</h2>
        <button onClick={triggerBackup} disabled={triggering}
          style={{ padding: '10px 24px', background: triggering ? '#90caf9' : '#1976d2', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontWeight: 700, fontSize: 15, display: 'flex', alignItems: 'center', gap: 8 }}>
          {triggering ? '⏳ Realizando backup...' : '☁ Backup manual ahora'}
        </button>
      </div>

      {msg && (
        <div style={{ padding: '10px 16px', borderRadius: 4, background: msg.ok ? '#e8f5e9' : '#ffebee', color: msg.ok ? '#2e7d32' : '#c62828', fontWeight: 600, marginBottom: 12 }}
          onClick={() => setMsg(null)}>
          {msg.text}
        </div>
      )}

      <div style={{ display: 'flex', borderBottom: '1px solid #ddd', marginBottom: 24 }}>
        <button style={tabStyle(tab === 'backups')} onClick={() => setTab('backups')}>Historial</button>
        <button style={tabStyle(tab === 'stats')} onClick={() => setTab('stats')}>Estadísticas</button>
        <button style={tabStyle(tab === 'config')} onClick={() => setTab('config')}>Configuración</button>
      </div>

      {loading && <p>Cargando...</p>}

      {/* HISTORY */}
      {tab === 'backups' && !loading && (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#1976d2', color: '#fff' }}>
              {['Archivo', 'Tipo', 'Estado', 'Tamaño', 'S3 Key', 'Fecha inicio', 'Completado', 'Acciones'].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {backups.map((b, i) => {
              const cfg = STATUS_CFG[b.status] || { bg: '#f5f5f5', color: '#333', icon: '?' };
              return (
                <tr key={b.id} style={{ background: i % 2 === 0 ? '#fff' : '#f9f9f9', borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px 12px', fontWeight: 600, fontSize: 12 }}>{b.filename}</td>
                  <td style={{ padding: '8px 12px' }}>
                    <span style={{ background: b.type === 'MANUAL' ? '#fff3e0' : '#e3f2fd', color: b.type === 'MANUAL' ? '#e65100' : '#1565c0', borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600 }}>
                      {b.type}
                    </span>
                  </td>
                  <td style={{ padding: '8px 12px' }}>
                    <span style={{ background: cfg.bg, color: cfg.color, borderRadius: 12, padding: '2px 10px', fontSize: 12, fontWeight: 600 }}>
                      {cfg.icon} {b.status}
                    </span>
                    {b.errorMessage && (
                      <div style={{ fontSize: 11, color: '#c62828', marginTop: 2 }}>{b.errorMessage}</div>
                    )}
                  </td>
                  <td style={{ padding: '8px 12px', fontWeight: 600 }}>{formatBytes(b.sizeBytes)}</td>
                  <td style={{ padding: '8px 12px', fontSize: 11, color: '#888', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    s3://{b.s3Bucket}/{b.s3Key}
                  </td>
                  <td style={{ padding: '8px 12px', fontSize: 12 }}>{b.createdAt}</td>
                  <td style={{ padding: '8px 12px', fontSize: 12 }}>{b.completedAt || '—'}</td>
                  <td style={{ padding: '8px 12px' }}>
                    {b.status === 'SUCCESS' && (
                      <button onClick={() => deleteBackup(b.id, b.filename)}
                        style={{ padding: '3px 10px', background: '#ffebee', color: '#c62828', border: '1px solid #c62828', borderRadius: 4, cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                        🗑 Eliminar
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {/* STATS */}
      {tab === 'stats' && !loading && stats && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 16, marginBottom: 24 }}>
            {[
              { label: 'Total backups', value: stats.totalBackups, color: '#1976d2', bg: '#e3f2fd' },
              { label: 'Exitosos', value: stats.successfulBackups, color: '#2e7d32', bg: '#e8f5e9' },
              { label: 'Fallidos', value: stats.failedBackups, color: '#c62828', bg: '#ffebee' },
              { label: 'Almacenamiento total', value: formatBytes(stats.totalSizeBytes), color: '#6a1b9a', bg: '#f3e5f5' },
            ].map(({ label, value, color, bg }) => (
              <div key={label} style={{ background: bg, border: `1px solid ${color}`, borderRadius: 10, padding: '18px 20px', textAlign: 'center' }}>
                <div style={{ fontSize: 28, fontWeight: 800, color }}>{value}</div>
                <div style={{ fontSize: 12, color: '#555', marginTop: 4 }}>{label}</div>
              </div>
            ))}
          </div>
          <div style={{ background: '#f9f9f9', border: '1px solid #e0e0e0', borderRadius: 8, padding: 16, display: 'flex', gap: 32, flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Último backup exitoso</div>
              <div style={{ fontWeight: 700, fontSize: 15 }}>🕐 {stats.lastBackupAt}</div>
            </div>
            <div>
              <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Próximo backup programado</div>
              <div style={{ fontWeight: 700, fontSize: 15, color: '#1976d2' }}>⏰ {stats.nextScheduledAt}</div>
            </div>
            <div>
              <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Tasa de éxito</div>
              <div style={{ fontWeight: 700, fontSize: 15, color: '#2e7d32' }}>
                {stats.totalBackups > 0 ? Math.round(stats.successfulBackups / stats.totalBackups * 100) : 0}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CONFIG */}
      {tab === 'config' && !loading && editConfig && (
        <div style={{ maxWidth: 600, display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div style={{ background: '#e8f5e9', border: '1px solid #a5d6a7', borderRadius: 8, padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 700 }}>Backup automático diario</div>
              <div style={{ fontSize: 13, color: '#555' }}>Se ejecuta todos los días a las 02:00 AM</div>
            </div>
            <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
              <span style={{ fontSize: 14, fontWeight: 600 }}>{editConfig.autoBackupEnabled ? 'Activado' : 'Desactivado'}</span>
              <div onClick={() => setEditConfig(c => c ? { ...c, autoBackupEnabled: !c.autoBackupEnabled } : c)}
                style={{ width: 44, height: 24, borderRadius: 12, background: editConfig.autoBackupEnabled ? '#1976d2' : '#ccc', cursor: 'pointer', position: 'relative', transition: 'background 0.2s' }}>
                <div style={{ width: 20, height: 20, borderRadius: 10, background: '#fff', position: 'absolute', top: 2, left: editConfig.autoBackupEnabled ? 22 : 2, transition: 'left 0.2s', boxShadow: '0 1px 3px rgba(0,0,0,.3)' }} />
              </div>
            </label>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <label>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>S3 Bucket</span>
              <input type="text" value={editConfig.s3Bucket}
                onChange={e => setEditConfig(c => c ? { ...c, s3Bucket: e.target.value } : c)}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
            </label>
            <label>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Región AWS</span>
              <select value={editConfig.s3Region}
                onChange={e => setEditConfig(c => c ? { ...c, s3Region: e.target.value } : c)}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }}>
                {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </label>
            <label>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Expresión cron</span>
              <input type="text" value={editConfig.cronExpression}
                onChange={e => setEditConfig(c => c ? { ...c, cronExpression: e.target.value } : c)}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc', fontFamily: 'monospace' }} />
              <span style={{ fontSize: 11, color: '#888' }}>Formato: min hora día mes díasemana</span>
            </label>
            <label>
              <span style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>Retención (días)</span>
              <input type="number" value={editConfig.retentionDays}
                onChange={e => setEditConfig(c => c ? { ...c, retentionDays: e.target.value } : c)}
                style={{ width: '100%', padding: '7px 10px', borderRadius: 4, border: '1px solid #ccc' }} />
            </label>
          </div>

          <div>
            <span style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Datasets incluidos en el backup</span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {DATASETS.map(ds => (
                <label key={ds} onClick={() => toggleDataset(ds)}
                  style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer',
                    background: editConfig.includedDatasets.includes(ds) ? '#e3f2fd' : '#f5f5f5',
                    border: `1px solid ${editConfig.includedDatasets.includes(ds) ? '#1976d2' : '#ddd'}`,
                    borderRadius: 6, padding: '6px 12px', userSelect: 'none' }}>
                  <input type="checkbox" checked={editConfig.includedDatasets.includes(ds)} readOnly />
                  <span style={{ fontSize: 13, fontWeight: 600, color: editConfig.includedDatasets.includes(ds) ? '#1565c0' : '#555' }}>{ds}</span>
                </label>
              ))}
            </div>
          </div>

          <button onClick={saveConfig}
            style={{ padding: '10px 28px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 700, alignSelf: 'flex-start' }}>
            Guardar configuración
          </button>
        </div>
      )}
    </div>
  );
}
