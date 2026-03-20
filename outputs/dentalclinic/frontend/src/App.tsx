import { Link, Route, Routes, useNavigate } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';
import { useAuth } from './auth/AuthProvider';
import { useI18n } from './context/I18nContext';
import DashboardPage from './pages/DashboardPage';
import NotificationBell from './components/Notifications/NotificationBell';
import LanguageSwitcher from './components/LanguageSwitcher';
import PatientPage from './pages/PatientPage';
import DentistPage from './pages/DentistPage';
import AppointmentPage from './pages/AppointmentPage';
import TreatmentPage from './pages/TreatmentPage';
import InvoicePage from './pages/InvoicePage';
import CalendarPage from './pages/CalendarPage';
import WaitingRoomPage from './pages/WaitingRoomPage';
import ReportsPage from './pages/ReportsPage';
import TreatmentPlanPage from './pages/TreatmentPlanPage';
import PatientPortalPage from './pages/PatientPortalPage';
import PrescriptionPage from './pages/PrescriptionPage';
import StockPage from './pages/StockPage';
import PaymentPage from './pages/PaymentPage';
import ConsentPage from './pages/ConsentPage';
import AnamnesisPage from './pages/AnamnesisPage';
import CommunicationPage from './pages/CommunicationPage';
import ClinicalPhotosPage from './pages/ClinicalPhotosPage';
import LocationsPage from './pages/LocationsPage';
import OnlineBookingPage from './pages/OnlineBookingPage';
import AdvancedCalendarPage from './pages/AdvancedCalendarPage';
import RecurringAppointmentsPage from './pages/RecurringAppointmentsPage';
import CashRegisterPage from './pages/CashRegisterPage';
import GdprPage from './pages/GdprPage';
import WaitlistPage from './pages/WaitlistPage';
import OperatoryPage from './pages/OperatoryPage';
import NpsPage from './pages/NpsPage';
import InsuranceClaimsPage from './pages/InsuranceClaimsPage';
import StaffPage from './pages/StaffPage';
import SterilizationPage from './pages/SterilizationPage';
import PatientMapPage from './pages/PatientMapPage';
import PreVisitFormPage from './pages/PreVisitFormPage';

interface NavItem { label: string; to: string; }
interface NavGroup { label: string; items: NavItem[]; }

const NAV_GROUPS: NavGroup[] = [
  {
    label: 'Pacientes',
    items: [
      { label: 'Pacientes', to: '/patients' },
      { label: 'Dentistas', to: '/dentists' },
      { label: 'Anamnesis', to: '/anamnesis' },
      { label: 'Formulario pre-visita', to: '/previsit-forms' },
      { label: 'Mapa de pacientes', to: '/patient-map' },
      { label: 'Fotos clínicas', to: '/clinical-photos' },
      { label: 'Portal paciente', to: '/portal' },
      { label: 'Mensajes', to: '/communications' },
    ],
  },
  {
    label: 'Agenda',
    items: [
      { label: 'Citas', to: '/appointments' },
      { label: 'Calendario', to: '/calendar' },
      { label: 'Sala de espera', to: '/waiting-room' },
      { label: 'Reserva online', to: '/booking' },
      { label: 'Calendario avanzado', to: '/advanced-calendar' },
      { label: 'Citas recurrentes', to: '/recurring' },
      { label: 'Sillones', to: '/operatories' },
    ],
  },
  {
    label: 'Clínica',
    items: [
      { label: 'Tratamientos', to: '/treatments' },
      { label: 'Planes de trat.', to: '/treatment-plans' },
      { label: 'Recetas', to: '/prescriptions' },
      { label: 'Consentimientos', to: '/consents' },
      { label: 'Esterilización', to: '/sterilization' },
    ],
  },
  {
    label: 'Finanzas',
    items: [
      { label: 'Facturas', to: '/invoices' },
      { label: 'TPV / Cobros', to: '/payments' },
      { label: 'Stock', to: '/stock' },
      { label: 'Cuadre de caja', to: '/cash-register' },
      { label: 'Reclamaciones seg.', to: '/insurance-claims' },
    ],
  },
  {
    label: 'Gestión',
    items: [
      { label: 'Informes', to: '/reports' },
      { label: 'Sedes', to: '/locations' },
      { label: 'RGPD', to: '/gdpr' },
      { label: 'Lista de espera', to: '/waitlist' },
      { label: 'Encuestas NPS', to: '/nps' },
      { label: 'Empleados', to: '/staff' },
    ],
  },
];

function NavDropdown({ group }: { group: NavGroup }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          background: 'none', border: 'none', color: '#fff', cursor: 'pointer',
          padding: '14px 16px', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 4,
        }}
      >
        {group.label} <span style={{ fontSize: 10, opacity: 0.8 }}>▼</span>
      </button>
      {open && (
        <div style={{
          position: 'absolute', top: '100%', left: 0, background: '#fff',
          boxShadow: '0 4px 16px rgba(0,0,0,.15)', borderRadius: 4, minWidth: 180,
          zIndex: 1000, overflow: 'hidden',
        }}>
          {group.items.map(item => (
            <button
              key={item.to}
              onClick={() => { navigate(item.to); setOpen(false); }}
              style={{
                display: 'block', width: '100%', textAlign: 'left',
                padding: '10px 16px', background: 'none', border: 'none',
                color: '#1976d2', cursor: 'pointer', fontSize: '0.875rem',
                borderBottom: '1px solid #f0f0f0',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = '#f0f7ff')}
              onMouseLeave={e => (e.currentTarget.style.background = 'none')}
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const { authenticated, username, roles, login, logout } = useAuth();
  const { t } = useI18n();

  if (!authenticated) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 120 }}>
        <h1>Patient Manager</h1>
        <p>Inicia sesión para continuar</p>
        <button onClick={login} style={{ padding: '10px 24px', fontSize: 16 }}>
          {t('login')}
        </button>
      </div>
    );
  }

  return (
    <>
      <nav style={{ display: 'flex', background: '#1976d2', alignItems: 'center', width: '100%', position: 'sticky', top: 0, zIndex: 100 }}>
        <Link to="/" style={{ color: '#fff', fontWeight: 700, textDecoration: 'none', padding: '14px 20px', fontSize: '1rem', whiteSpace: 'nowrap' }}>
          🦷 DentalClinic
        </Link>
        {NAV_GROUPS.map(group => (
          <NavDropdown key={group.label} group={group} />
        ))}
        <span style={{ marginLeft: 'auto', color: '#fff', fontSize: '0.8rem', padding: '0 8px', whiteSpace: 'nowrap' }}>
          {username} ({roles.join(', ')})
        </span>
        <LanguageSwitcher />
        <NotificationBell />
        <button
          onClick={logout}
          style={{ background: 'rgba(255,255,255,.15)', color: '#fff', border: 'none', borderRadius: 4, padding: '6px 14px', cursor: 'pointer', margin: '0 8px', whiteSpace: 'nowrap' }}
        >{t('logout')}</button>
      </nav>
      <main style={{ padding: 24 }}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/patients" element={<PatientPage />} />
          <Route path="/dentists" element={<DentistPage />} />
          <Route path="/appointments" element={<AppointmentPage />} />
          <Route path="/treatments" element={<TreatmentPage />} />
          <Route path="/invoices" element={<InvoicePage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/waiting-room" element={<WaitingRoomPage />} />
          <Route path="/treatment-plans" element={<TreatmentPlanPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/portal" element={<PatientPortalPage />} />
          <Route path="/prescriptions" element={<PrescriptionPage />} />
          <Route path="/stock" element={<StockPage />} />
          <Route path="/payments" element={<PaymentPage />} />
          <Route path="/consents" element={<ConsentPage />} />
          <Route path="/anamnesis" element={<AnamnesisPage />} />
          <Route path="/communications" element={<CommunicationPage />} />
          <Route path="/clinical-photos" element={<ClinicalPhotosPage />} />
          <Route path="/locations" element={<LocationsPage />} />
          <Route path="/booking" element={<OnlineBookingPage />} />
          <Route path="/advanced-calendar" element={<AdvancedCalendarPage />} />
          <Route path="/recurring" element={<RecurringAppointmentsPage />} />
          <Route path="/cash-register" element={<CashRegisterPage />} />
          <Route path="/gdpr" element={<GdprPage />} />
          <Route path="/waitlist" element={<WaitlistPage />} />
          <Route path="/operatories" element={<OperatoryPage />} />
          <Route path="/nps" element={<NpsPage />} />
          <Route path="/insurance-claims" element={<InsuranceClaimsPage />} />
          <Route path="/staff" element={<StaffPage />} />
          <Route path="/sterilization" element={<SterilizationPage />} />
          <Route path="/patient-map" element={<PatientMapPage />} />
          <Route path="/previsit-forms" element={<PreVisitFormPage />} />
        </Routes>
      </main>
    </>
  );
}
