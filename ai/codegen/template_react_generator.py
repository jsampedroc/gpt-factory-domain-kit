"""
TemplateReactGenerator
======================
Deterministic React + TypeScript code generator.
Generates one consistent frontend per domain entity:

  - TypeScript model interface  (frontend/src/types/{Entity}.ts)
  - API service                 (frontend/src/api/{entity}Api.ts)
  - List component              (frontend/src/components/{Entity}/{Entity}List.tsx)
  - Form component              (frontend/src/components/{Entity}/{Entity}Form.tsx)
  - Page component              (frontend/src/pages/{Entity}Page.tsx)

Plus project scaffold files (generated once):
  - package.json, vite.config.ts, tsconfig.json,
    index.html, src/main.tsx, src/App.tsx
"""

from __future__ import annotations
import json


JAVA_TO_TS = {
    "String": "string",
    "Integer": "number",
    "Long": "number",
    "Double": "number",
    "Float": "number",
    "Boolean": "boolean",
    "boolean": "boolean",
    "int": "number",
    "long": "number",
    "double": "number",
    "float": "number",
    "UUID": "string",
    "LocalDate": "string",
    "LocalDateTime": "string",
    "Instant": "string",
    "BigDecimal": "number",
}


def _ts_type(java_type: str) -> str:
    if not java_type:
        return "unknown"
    if java_type.startswith("List<"):
        inner = java_type[5:-1]
        return f"{_ts_type(inner)}[]"
    if java_type.startswith("Optional<"):
        inner = java_type[9:-1]
        return f"{_ts_type(inner)} | null"
    if java_type in JAVA_TO_TS:
        return JAVA_TO_TS[java_type]
    # Domain VO type inference — keeps frontend aligned with backend *Response DTOs
    outer = java_type.split("<")[0]
    if outer.endswith("Id"):
        return "string"
    if any(outer.endswith(s) for s in ("Status", "Type", "Kind", "State", "Category", "Role")):
        return "string"
    if outer in ("Money", "Price", "Amount"):
        return "number"
    # Unknown → string (safe default)
    return "string"


def _camel(name: str) -> str:
    return name[0].lower() + name[1:] if name else name


def _label(name: str) -> str:
    """'firstName' → 'First Name'"""
    import re
    s = re.sub(r"([A-Z])", r" \1", name).strip()
    return s[0].upper() + s[1:]


class TemplateReactGenerator:

    # ------------------------------------------------------------------ #
    # Shared TypeScript types                                              #
    # ------------------------------------------------------------------ #

    def generate_page_response_type(self) -> str:
        return """export interface PageResponse<T> {
  content: T[];
  page: number;
  size: number;
  total: number;
  totalPages: number;
  last: boolean;
}
"""

    # ------------------------------------------------------------------ #
    # TypeScript model interface                                           #
    # ------------------------------------------------------------------ #

    def generate_model(self, entity: str, fields: list) -> str:
        lines = []
        for f in fields:
            name = f.get("name", "")
            ts = _ts_type(f.get("type", "string"))
            lines.append(f"  {name}: {ts};")
        fields_str = "\n".join(lines) if lines else "  id: string;"
        return f"""export interface {entity} {{
  id: string;
{fields_str}
}}
"""

    # ------------------------------------------------------------------ #
    # API service                                                          #
    # ------------------------------------------------------------------ #

    def generate_api_service(self, entity: str, base_url_var: str = "API_BASE") -> str:
        lower = _camel(entity)
        return f"""import type {{ {entity} }} from '../types/{entity}';
import type {{ PageResponse }} from '../types/PageResponse';
import {{ apiFetch }} from './apiFetch';

const {base_url_var} = import.meta.env.VITE_API_URL ?? 'http://localhost:8080';
const ENDPOINT = `${{{base_url_var}}}/{lower}s`;

export async function getAll{entity}s(
  page = 0,
  size = 20,
  search = ''
): Promise<PageResponse<{entity}>> {{
  const params = new URLSearchParams({{ page: String(page), size: String(size), search }});
  const res = await apiFetch(`${{ENDPOINT}}?${{params}}`);
  if (!res.ok) throw new Error('Failed to fetch {lower}s');
  return res.json();
}}

export async function get{entity}ById(id: string): Promise<{entity}> {{
  const res = await apiFetch(`${{ENDPOINT}}/${{id}}`);
  if (!res.ok) throw new Error(`{entity} ${{id}} not found`);
  return res.json();
}}

export async function create{entity}(data: Omit<{entity}, 'id'>): Promise<{entity}> {{
  const res = await apiFetch(ENDPOINT, {{
    method: 'POST',
    body: JSON.stringify(data),
  }});
  if (!res.ok) throw res;
  return res.json();
}}

export async function update{entity}(id: string, data: Partial<{entity}>): Promise<{entity}> {{
  const res = await apiFetch(`${{ENDPOINT}}/${{id}}`, {{
    method: 'PUT',
    body: JSON.stringify(data),
  }});
  if (!res.ok) throw res;
  return res.json();
}}

export async function delete{entity}(id: string): Promise<void> {{
  const res = await apiFetch(`${{ENDPOINT}}/${{id}}`, {{ method: 'DELETE' }});
  if (!res.ok) throw new Error(`Failed to delete {lower} ${{id}}`);
}}
"""

    # ------------------------------------------------------------------ #
    # List component                                                       #
    # ------------------------------------------------------------------ #

    def generate_list_component(self, entity: str, fields: list) -> str:
        lower = _camel(entity)
        # Pick display columns (skip id, skip complex types)
        cols = [
            f for f in fields
            if f.get("name") not in ("id",)
            and not str(f.get("type", "")).startswith("List")
        ][:5]

        headers = "".join(f"<th style={{{{thStyle}}}}>{ _label(c['name'])}</th>" for c in cols)
        cells = "".join(f"<td style={{{{tdStyle}}}}>{{{lower}.{c['name']} ?? '—'}}</td>" for c in cols)

        return f"""import {{ useEffect, useState, useCallback }} from 'react';
import type {{ {entity} }} from '../../types/{entity}';
import type {{ PageResponse }} from '../../types/PageResponse';
import {{ getAll{entity}s, delete{entity} }} from '../../api/{lower}Api';
import {{ useToast }} from '../../context/ToastContext';

interface Props {{
  onEdit: (item: {entity}) => void;
  onNew: () => void;
  refresh: number;
}}

const thStyle: React.CSSProperties = {{
  textAlign: 'left', padding: '8px 12px', borderBottom: '2px solid #e0e0e0',
  background: '#fafafa', fontWeight: 600,
}};
const tdStyle: React.CSSProperties = {{ padding: '8px 12px', borderBottom: '1px solid #f0f0f0' }};

export default function {entity}List({{ onEdit, onNew, refresh }}: Props) {{
  const {{ showToast }} = useToast();
  const [page, setPage] = useState<PageResponse<{entity}> | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback((p: number, s: string) => {{
    setLoading(true);
    getAll{entity}s(p, 20, s)
      .then(setPage)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }}, []);

  useEffect(() => {{ load(currentPage, search); }}, [refresh, currentPage, search, load]);

  const handleDelete = async (id: string) => {{
    if (!window.confirm('¿Eliminar este {lower}?')) return;
    await delete{entity}(id);
    showToast('{entity} eliminado correctamente', 'info');
    load(currentPage, search);
  }};

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {{
    setSearch(e.target.value);
    setCurrentPage(0);
  }};

  return (
    <div>
      <div style={{{{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}}}>
        <h2 style={{{{ margin: 0 }}}}>{{page?.total ?? ''}} {entity}s</h2>
        <div style={{{{ display: 'flex', gap: 8 }}}}>
          <input
            placeholder="Buscar…"
            value={{search}}
            onChange={{handleSearch}}
            style={{{{ padding: '6px 12px', border: '1px solid #ddd', borderRadius: 4, width: 220 }}}}
          />
          <button
            onClick={{onNew}}
            style={{{{ padding: '6px 16px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}}}
          >
            + Nuevo
          </button>
        </div>
      </div>

      {{error && <p style={{{{ color: 'red' }}}}>{{error}}</p>}}
      {{loading && <p style={{{{ color: '#999' }}}}>Cargando…</p>}}

      <table style={{{{ width: '100%', borderCollapse: 'collapse' }}}}>
        <thead>
          <tr>{headers}<th style={{{{thStyle}}}}>Acciones</th></tr>
        </thead>
        <tbody>
          {{(page?.content ?? []).map({lower} => (
            <tr key={{{lower}.id}} style={{{{ background: '#fff' }}}}>
              {cells}
              <td style={{{{tdStyle}}}}>
                <button
                  onClick={{() => onEdit({lower})}}
                  style={{{{ marginRight: 6, padding: '3px 10px', cursor: 'pointer' }}}}
                >Editar</button>
                <button
                  onClick={{() => handleDelete({lower}.id)}}
                  style={{{{ padding: '3px 10px', cursor: 'pointer', color: '#c62828' }}}}
                >Eliminar</button>
              </td>
            </tr>
          ))}}
        </tbody>
      </table>

      {{page && page.totalPages > 1 && (
        <div style={{{{ display: 'flex', gap: 8, marginTop: 16, alignItems: 'center' }}}}>
          <button disabled={{currentPage === 0}} onClick={{() => setCurrentPage(p => p - 1)}}>‹ Anterior</button>
          <span>Página {{currentPage + 1}} de {{page.totalPages}}</span>
          <button disabled={{page.last}} onClick={{() => setCurrentPage(p => p + 1)}}>Siguiente ›</button>
        </div>
      )}}
    </div>
  );
}}
"""

    # ------------------------------------------------------------------ #
    # Form component                                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _input_attrs_for_field(f: dict) -> dict:
        """Returns HTML input type and validation attributes based on Java type."""
        java_type = f.get("type", "String")
        name = f.get("name", "")
        attrs: dict = {}

        if java_type == "LocalDate" or "Date" in name.lower():
            attrs["type"] = "date"
            attrs["required"] = True
        elif java_type == "LocalDateTime" or "DateTime" in java_type:
            attrs["type"] = "datetime-local"
            attrs["required"] = True
        elif any(kw in name.lower() for kw in ("email", "mail")):
            attrs["type"] = "email"
            attrs["required"] = True
            attrs["maxLength"] = 200
        elif java_type in ("int", "Integer", "long", "Long", "double", "Double", "float", "Float"):
            attrs["type"] = "number"
            attrs["step"] = "any"
        elif java_type == "String":
            attrs["type"] = "text"
            attrs["required"] = True
            if any(kw in name.lower() for kw in ("description", "descripcion", "notes", "notas")):
                attrs["maxLength"] = 500
            else:
                attrs["maxLength"] = 100
        elif java_type == "UUID" or java_type.endswith("Id"):
            attrs["type"] = "text"
            attrs["required"] = True
            attrs["pattern"] = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
            attrs["title"] = "UUID válido"
        else:
            # enums, value objects, etc.
            attrs["type"] = "text"
            attrs["required"] = True

        return attrs

    def generate_form_component(self, entity: str, fields: list) -> str:
        lower = _camel(entity)
        # Editable fields (exclude id and list types)
        editable = [
            f for f in fields
            if f.get("name") not in ("id",)
            and not str(f.get("type", "")).startswith("List")
        ]

        state_init = ", ".join(
            f"{f['name']}: item?.{f['name']} ?? ''" for f in editable
        ) if editable else ""

        def _input_el(f):
            attrs = self._input_attrs_for_field(f)
            attr_strs = []
            for k, v in attrs.items():
                if k == "required" and v:
                    attr_strs.append("required")
                elif k == "type":
                    attr_strs.append(f'type="{v}"')
                elif k == "maxLength":
                    attr_strs.append(f"maxLength={{{v}}}")
                elif k == "step":
                    attr_strs.append(f'step="{v}"')
                elif k == "pattern":
                    attr_strs.append(f'pattern="{v}"')
                elif k == "title":
                    attr_strs.append(f'title="{v}"')
            attr_str = " ".join(attr_strs)
            return (
                f"<div>\n"
                f"          <label style={{{{ display: 'block', marginBottom: 4, fontWeight: 500 }}}}>{_label(f['name'])}</label>\n"
                f"          <input\n"
                f"            {attr_str}\n"
                f"            name=\"{f['name']}\"\n"
                f"            value={{form.{f['name']} ?? ''}}\n"
                f"            onChange={{{{e => setForm(prev => ({{ ...prev, {f['name']}: e.target.value }}));}}}}\n"
                f"            style={{{{ width: '100%', padding: '6px 10px', boxSizing: 'border-box', borderRadius: 4, border: '1px solid #ccc' }}}}\n"
                f"          />\n"
                f"        </div>"
            )

        inputs = "\n        ".join(_input_el(f) for f in editable)

        return f"""import {{ useState }} from 'react';
import type {{ {entity} }} from '../../types/{entity}';
import {{ create{entity}, update{entity} }} from '../../api/{lower}Api';
import {{ useToast }} from '../../context/ToastContext';

interface Props {{
  item?: {entity} | null;
  onSaved: () => void;
  onCancel: () => void;
}}

export default function {entity}Form({{ item, onSaved, onCancel }}: Props) {{
  const {{ showToast }} = useToast();
  const [form, setForm] = useState({{ {state_init} }});
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {{
    e.preventDefault();
    setSaving(true);
    setErrors([]);
    try {{
      if (item?.id) {{
        await update{entity}(item.id, form as Partial<{entity}>);
        showToast('{entity} actualizado correctamente');
      }} else {{
        await create{entity}(form as Omit<{entity}, 'id'>);
        showToast('{entity} creado correctamente');
      }}
      onSaved();
    }} catch (err: unknown) {{
      if (err instanceof Response) {{
        const body = await err.json().catch(() => ({{}}));
        const msgs: string[] = body.errors
          ? Object.values(body.errors as Record<string, string>)
          : [body.message ?? 'Error desconocido'];
        setErrors(msgs);
      }} else {{
        setErrors([err instanceof Error ? err.message : 'Error inesperado']);
      }}
    }} finally {{
      setSaving(false);
    }}
  }};

  return (
    <form onSubmit={{handleSubmit}} noValidate style={{{{ display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 480 }}}}>
      <h2 style={{{{ marginBottom: 8 }}}}>{{item ? 'Editar' : 'Nuevo'}} {entity}</h2>
      {inputs}
      {{errors.length > 0 && (
        <ul style={{{{ color: 'red', margin: 0, paddingLeft: 20 }}}}>
          {{errors.map((m, i) => <li key={{i}}>{{m}}</li>)}}
        </ul>
      )}}
      <div style={{{{ display: 'flex', gap: 8 }}}}>
        <button type="submit" disabled={{saving}}
          style={{{{ padding: '8px 20px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}}}>
          {{saving ? 'Guardando…' : 'Guardar'}}
        </button>
        <button type="button" onClick={{onCancel}}
          style={{{{ padding: '8px 20px', borderRadius: 4, cursor: 'pointer' }}}}>
          Cancelar
        </button>
      </div>
    </form>
  );
}}
"""

    # ------------------------------------------------------------------ #
    # Page component (wires list + form together)                          #
    # ------------------------------------------------------------------ #

    def generate_page_component(self, entity: str) -> str:
        lower = _camel(entity)
        return f"""import {{ useState }} from 'react';
import type {{ {entity} }} from '../types/{entity}';
import {entity}List from '../components/{entity}/{entity}List';
import {entity}Form from '../components/{entity}/{entity}Form';

export default function {entity}Page() {{
  const [editing, setEditing] = useState<{entity} | null | undefined>(undefined);
  const [refresh, setRefresh] = useState(0);

  const handleSaved = () => {{
    setEditing(undefined);
    setRefresh(r => r + 1);
  }};

  if (editing !== undefined) {{
    return (
      <{entity}Form
        item={{editing}}
        onSaved={{handleSaved}}
        onCancel={{() => setEditing(undefined)}}
      />
    );
  }}

  return (
    <{entity}List
      onEdit={{item => setEditing(item)}}
      onNew={{() => setEditing(null)}}
      refresh={{refresh}}
    />
  );
}}
"""

    # ------------------------------------------------------------------ #
    # Scaffold files (generated once per project)                          #
    # ------------------------------------------------------------------ #

    def generate_package_json(self, project_name: str) -> str:
        return json.dumps({
            "name": project_name + "-frontend",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "react-router-dom": "^6.23.1",
                "keycloak-js": "^24.0.5",
                "@stomp/stompjs": "^7.0.0",
                "sockjs-client": "^1.6.1"
            },
            "devDependencies": {
                "@types/react": "^18.3.3",
                "@types/react-dom": "^18.3.0",
                "@types/sockjs-client": "^1.5.4",
                "@vitejs/plugin-react": "^4.3.0",
                "typescript": "^5.4.5",
                "vite": "^5.2.12"
            }
        }, indent=2) + "\n"

    def generate_vite_config(self) -> str:
        return """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
"""

    def generate_tsconfig(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}]
        }, indent=2) + "\n"

    def generate_tsconfig_node(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "composite": True,
                "skipLibCheck": True,
                "module": "ESNext",
                "moduleResolution": "bundler",
                "allowSyntheticDefaultImports": True,
                "strict": True
            },
            "include": ["vite.config.ts"]
        }, indent=2) + "\n"

    def generate_index_html(self, project_name: str) -> str:
        title = project_name.replace("-", " ").title()
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

    def generate_main_tsx(self) -> str:
        return """import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './auth/AuthProvider';
import { ToastProvider } from './context/ToastContext';
import { I18nProvider } from './context/I18nContext';
import App from './App';
import './index.css';

// StrictMode omitted intentionally: Keycloak must only be initialized once.
// Future flags suppress React Router v7 upgrade warnings.
ReactDOM.createRoot(document.getElementById('root')!).render(
  <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
    <I18nProvider>
      <AuthProvider>
        <ToastProvider>
          <App />
        </ToastProvider>
      </AuthProvider>
    </I18nProvider>
  </BrowserRouter>
);
"""

    def generate_toast_context_tsx(self) -> str:
        return """import { createContext, useCallback, useContext, useState } from 'react';

export type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  toasts: Toast[];
  showToast: (message: string, type?: ToastType) => void;
  dismiss: (id: number) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let nextId = 1;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const showToast = useCallback((message: string, type: ToastType = 'success') => {
    const id = nextId++;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => dismiss(id), 4000);
  }, [dismiss]);

  return (
    <ToastContext.Provider value={{ toasts, showToast, dismiss }}>
      {children}
      <ToastContainer toasts={toasts} dismiss={dismiss} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be inside ToastProvider');
  return ctx;
}

const BG: Record<ToastType, string> = {
  success: '#2e7d32',
  error: '#c62828',
  info: '#1565c0',
};

function ToastContainer({ toasts, dismiss }: { toasts: Toast[]; dismiss: (id: number) => void }) {
  if (!toasts.length) return null;
  return (
    <div style={{
      position: 'fixed',
      bottom: 24,
      right: 24,
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      zIndex: 9999,
    }}>
      {toasts.map(t => (
        <div key={t.id} style={{
          background: BG[t.type],
          color: '#fff',
          padding: '12px 20px',
          borderRadius: 6,
          boxShadow: '0 4px 12px rgba(0,0,0,.25)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          minWidth: 240,
          maxWidth: 400,
        }}>
          <span style={{ flex: 1 }}>{t.message}</span>
          <button
            onClick={() => dismiss(t.id)}
            style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: 18, lineHeight: 1 }}
          >×</button>
        </div>
      ))}
    </div>
  );
}
"""

    def generate_i18n_context_tsx(self, entities: list[str] | None = None) -> str:
        """
        Generates I18nContext.tsx with ES/EN translations and a useI18n hook.
        Translations cover common UI strings and entity names if provided.
        """
        entity_es = ""
        entity_en = ""
        if entities:
            for e in entities:
                entity_es += f"\n  {e}: '{e}',\n  '{e}s': '{e}s',"
                entity_en += f"\n  {e}: '{e}',\n  '{e}s': '{e}s',"

        return f"""import {{ createContext, useContext, useState, ReactNode }} from 'react';

export type Locale = 'es' | 'en';

const translations = {{
  es: {{
    // Navigation
    dashboard: 'Panel',
    logout: 'Cerrar sesión',
    login: 'Iniciar sesión con Keycloak',
    // Table actions
    new: 'Nuevo',
    edit: 'Editar',
    delete: 'Eliminar',
    save: 'Guardar',
    cancel: 'Cancelar',
    actions: 'Acciones',
    // Table / pagination
    search: 'Buscar...',
    loading: 'Cargando...',
    noResults: 'Sin resultados',
    page: 'Página',
    of: 'de',
    // Export
    exportPdf: 'Exportar PDF',
    exportExcel: 'Exportar Excel',
    // Notifications
    notifications: 'Notificaciones',
    clearAll: 'Limpiar todo',
    noNotifications: 'Sin notificaciones',
    // Feedback
    created: 'creado correctamente',
    updated: 'actualizado correctamente',
    deleted: 'eliminado correctamente',
    errorSaving: 'Error al guardar',
    errorLoading: 'Error al cargar',
    // Confirm
    confirmDelete: '¿Eliminar este registro?',{entity_es}
  }},
  en: {{
    // Navigation
    dashboard: 'Dashboard',
    logout: 'Sign out',
    login: 'Sign in with Keycloak',
    // Table actions
    new: 'New',
    edit: 'Edit',
    delete: 'Delete',
    save: 'Save',
    cancel: 'Cancel',
    actions: 'Actions',
    // Table / pagination
    search: 'Search...',
    loading: 'Loading...',
    noResults: 'No results',
    page: 'Page',
    of: 'of',
    // Export
    exportPdf: 'Export PDF',
    exportExcel: 'Export Excel',
    // Notifications
    notifications: 'Notifications',
    clearAll: 'Clear all',
    noNotifications: 'No notifications',
    // Feedback
    created: 'created successfully',
    updated: 'updated successfully',
    deleted: 'deleted successfully',
    errorSaving: 'Error saving',
    errorLoading: 'Error loading',
    // Confirm
    confirmDelete: 'Delete this record?',{entity_en}
  }},
}};

export type TranslationKey = keyof typeof translations.es;

interface I18nContextValue {{
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: TranslationKey) => string;
}}

const I18nContext = createContext<I18nContextValue>({{
  locale: 'es',
  setLocale: () => {{}},
  t: (key) => key,
}});

export function I18nProvider({{ children }}: {{ children: ReactNode }}) {{
  const [locale, setLocale] = useState<Locale>(() => {{
    return (localStorage.getItem('locale') as Locale) ?? 'es';
  }});

  const handleSetLocale = (l: Locale) => {{
    setLocale(l);
    localStorage.setItem('locale', l);
  }};

  const t = (key: TranslationKey): string =>
    (translations[locale] as Record<string, string>)[key] ?? key;

  return (
    <I18nContext.Provider value={{{{ locale, setLocale: handleSetLocale, t }}}}>
      {{children}}
    </I18nContext.Provider>
  );
}}

export function useI18n() {{
  return useContext(I18nContext);
}}
"""

    def generate_file_upload_tsx(self, api_base_var: str = "API_BASE") -> str:
        """
        Generates FileUpload.tsx — drag & drop file uploader with document list.
        Accepts entityType and entityId props and connects to the DocumentController.
        """
        return f"""import {{ useEffect, useRef, useState }} from 'react';
import {{ {api_base_var} }} from '../config/api';
import {{ apiFetch }} from '../api/apiFetch';

interface DocumentMeta {{
  id: string;
  originalName: string;
  storedName: string;
  contentType: string;
  fileSize: number;
  uploadedBy: string;
  uploadedAt: string;
}}

interface Props {{
  entityType: string;
  entityId: string;
}}

export default function FileUpload({{ entityType, entityId }}: Props) {{
  const [docs, setDocs] = useState<DocumentMeta[]>([]);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = async () => {{
    try {{
      const res = await apiFetch(`${{{{API_BASE}}}}/api/documents/${{{{entityType}}}}/${{{{entityId}}}}`);
      if (res.ok) setDocs(await res.json());
    }} catch {{}}
  }};

  useEffect(() => {{ fetchDocs(); }}, [entityType, entityId]);

  const uploadFile = async (file: File) => {{
    setUploading(true);
    try {{
      const form = new FormData();
      form.append('file', file);
      const res = await apiFetch(
        `${{{{API_BASE}}}}/api/documents/${{{{entityType}}}}/${{{{entityId}}}}`,
        {{ method: 'POST', body: form }}
      );
      if (res.ok) await fetchDocs();
    }} finally {{
      setUploading(false);
    }}
  }};

  const handleDrop = (e: React.DragEvent) => {{
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  }};

  const handleDelete = async (storedName: string) => {{
    if (!confirm('¿Eliminar este archivo?')) return;
    await apiFetch(
      `${{{{API_BASE}}}}/api/documents/${{{{entityType}}}}/${{{{entityId}}}}/${{{{storedName}}}}`,
      {{ method: 'DELETE' }}
    );
    await fetchDocs();
  }};

  const formatSize = (bytes: number) => {{
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }};

  return (
    <div style={{{{ marginTop: 16 }}}}>
      <h4 style={{{{ marginBottom: 8, color: '#555' }}}}>Archivos adjuntos</h4>

      {{/* Drop zone */}}
      <div
        onDragOver={{e => {{ e.preventDefault(); setDragging(true); }}}}
        onDragLeave={{() => setDragging(false)}}
        onDrop={{handleDrop}}
        onClick={{() => inputRef.current?.click()}}
        style={{{{
          border: `2px dashed ${{{{dragging ? '#1976d2' : '#ccc'}}}}`,
          borderRadius: 8, padding: '20px 16px', textAlign: 'center',
          cursor: 'pointer', background: dragging ? '#e3f2fd' : '#fafafa',
          color: '#888', fontSize: 14, transition: 'all .2s',
        }}}}
      >
        {{uploading ? '⏳ Subiendo...' : '📎 Arrastra un archivo aquí o haz clic para seleccionar'}}
        <input ref={{inputRef}} type="file" style={{{{ display: 'none' }}}}
          onChange={{e => {{ const f = e.target.files?.[0]; if (f) uploadFile(f); }}}} />
      </div>

      {{/* Document list */}}
      {{docs.length > 0 && (
        <table style={{{{ width: '100%', marginTop: 12, fontSize: 13 }}}}>
          <thead>
            <tr style={{{{ background: '#f5f5f5' }}}}>
              <th style={{{{ padding: '6px 10px', textAlign: 'left' }}}}>Archivo</th>
              <th style={{{{ padding: '6px 10px', textAlign: 'right' }}}}>Tamaño</th>
              <th style={{{{ padding: '6px 10px', textAlign: 'left' }}}}>Subido por</th>
              <th style={{{{ padding: '6px 10px' }}}}></th>
            </tr>
          </thead>
          <tbody>
            {{docs.map(doc => (
              <tr key={{doc.id}} style={{{{ borderBottom: '1px solid #eee' }}}}>
                <td style={{{{ padding: '6px 10px' }}}}>📄 {{doc.originalName}}</td>
                <td style={{{{ padding: '6px 10px', textAlign: 'right', color: '#888' }}}}>
                  {{formatSize(doc.fileSize)}}
                </td>
                <td style={{{{ padding: '6px 10px', color: '#888' }}}}>{{doc.uploadedBy}}</td>
                <td style={{{{ padding: '6px 10px' }}}}>
                  <button
                    onClick={{() => handleDelete(doc.storedName)}}
                    style={{{{ background: '#f44336', padding: '2px 8px', fontSize: 12 }}}}
                  >Eliminar</button>
                </td>
              </tr>
            ))}}
          </tbody>
        </table>
      )}}
    </div>
  );
}}
"""

    def generate_language_switcher(self) -> str:
        """
        Generates LanguageSwitcher.tsx — ES/EN toggle button for the navbar.
        """
        return """import { useI18n } from '../../context/I18nContext';

export default function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();

  return (
    <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
      <button
        onClick={() => setLocale('es')}
        style={{
          background: locale === 'es' ? 'rgba(255,255,255,0.35)' : 'transparent',
          color: '#fff', border: '1px solid rgba(255,255,255,0.4)',
          borderRadius: 4, padding: '2px 8px', cursor: 'pointer',
          fontWeight: locale === 'es' ? 700 : 400, fontSize: 12,
        }}
      >ES</button>
      <button
        onClick={() => setLocale('en')}
        style={{
          background: locale === 'en' ? 'rgba(255,255,255,0.35)' : 'transparent',
          color: '#fff', border: '1px solid rgba(255,255,255,0.4)',
          borderRadius: 4, padding: '2px 8px', cursor: 'pointer',
          fontWeight: locale === 'en' ? 700 : 400, fontSize: 12,
        }}
      >EN</button>
    </div>
  );
}
"""

    def generate_index_css(self) -> str:
        return """* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: #f9fafb; color: #111827; }
button {
  padding: 6px 14px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}
button[type="button"] { background: #6b7280; }
button:hover { opacity: 0.9; }
input, select, textarea {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
}
table { font-size: 0.875rem; }
th, td { padding: 8px 12px; text-align: left; }
th { background: #f3f4f6; font-weight: 600; }
nav { background: #1e3a5f; padding: 0 24px; }
nav a { color: white; text-decoration: none; display: inline-block; padding: 14px 16px; font-size: 0.9rem; }
nav a:hover { background: rgba(255,255,255,0.1); }
main { padding: 24px; max-width: 1100px; margin: 0 auto; }
"""

    def generate_env_example(self, project_name: str = "") -> str:
        slug = project_name or "app"
        return (
            "VITE_API_URL=http://localhost:8080\n"
            "VITE_KEYCLOAK_URL=http://localhost:8180\n"
            f"VITE_KEYCLOAK_REALM={slug}\n"
            f"VITE_KEYCLOAK_CLIENT_ID={slug}-frontend\n"
        )

    def generate_keycloak_ts(self, project_name: str) -> str:
        slug = project_name or "app"
        return f"""import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({{
  url: import.meta.env.VITE_KEYCLOAK_URL ?? 'http://localhost:8180',
  realm: import.meta.env.VITE_KEYCLOAK_REALM ?? '{slug}',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID ?? '{slug}-frontend',
}});

export default keycloak;
"""

    def generate_auth_provider_tsx(self) -> str:
        return """import { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import keycloak from './keycloak';

interface AuthContextValue {
  authenticated: boolean;
  token: string | undefined;
  username: string | undefined;
  roles: string[];
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  authenticated: false,
  token: undefined,
  username: undefined,
  roles: [],
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authenticated, setAuthenticated] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const initStarted = useRef(false);

  useEffect(() => {
    // Guard against React StrictMode double-invocation
    if (initStarted.current) return;
    initStarted.current = true;

    keycloak
      .init({ onLoad: 'login-required', pkceMethod: 'S256' })
      .then(auth => {
        setAuthenticated(auth);
        setInitialized(true);
        setInterval(() => {
          keycloak.updateToken(60).catch(() => keycloak.logout());
        }, 30_000);
      })
      .catch(err => {
        console.error('Keycloak init failed', err);
        setInitialized(true);
      });
  }, []);

  if (!initialized) return <p style={{ padding: 24 }}>Conectando con Keycloak…</p>;

  const roles: string[] = keycloak.realmAccess?.roles ?? [];

  const value: AuthContextValue = {
    authenticated,
    token: keycloak.token,
    username: keycloak.tokenParsed?.preferred_username,
    roles,
    login: () => keycloak.login(),
    logout: () => keycloak.logout({ redirectUri: window.location.origin }),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
"""

    def generate_api_fetch_ts(self) -> str:
        return """import keycloak from '../auth/keycloak';

/**
 * Wrapper around fetch that automatically attaches the Keycloak Bearer token.
 */
export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  if (keycloak.authenticated) {
    await keycloak.updateToken(30).catch(() => keycloak.logout());
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> ?? {}),
  };

  if (keycloak.token) {
    headers['Authorization'] = `Bearer ${keycloak.token}`;
  }

  return fetch(url, { ...options, headers });
}
"""

    def generate_dashboard_api(self) -> str:
        return """import type { DashboardStats } from '../types/DashboardStats';
import { apiFetch } from './apiFetch';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8080';

export async function getDashboardStats(): Promise<DashboardStats> {
  const res = await apiFetch(`${API_BASE}/dashboard`);
  if (!res.ok) throw new Error('Failed to fetch dashboard stats');
  return res.json();
}
"""

    def generate_dashboard_types(self, entities: list[str]) -> str:
        fields = "\n".join(f"  total{e}s: number;" for e in entities)
        return f"""export interface DashboardStats {{
{fields}
}}
"""

    def generate_dashboard_page(self, entities: list[str]) -> str:
        cards = "\n      ".join(
            f"""<StatCard
        label="{e}s activos"
        value={{stats?.total{e}s ?? '—'}}
        color="#1976d2"
      />""" for e in entities
        )
        return f"""import {{ useEffect, useState }} from 'react';
import type {{ DashboardStats }} from '../types/DashboardStats';
import {{ getDashboardStats }} from '../api/dashboardApi';

interface StatCardProps {{ label: string; value: number | string; color: string; }}

function StatCard({{ label, value, color }}: StatCardProps) {{
  return (
    <div style={{{{
      background: '#fff',
      borderRadius: 8,
      padding: '24px 28px',
      boxShadow: '0 1px 4px rgba(0,0,0,.1)',
      borderTop: `4px solid ${{color}}`,
      minWidth: 180,
      flex: '1 1 180px',
    }}}}>
      <div style={{{{ fontSize: 32, fontWeight: 700, color }}}}>{{{value}}}</div>
      <div style={{{{ color: '#666', marginTop: 4 }}}}>{{{label}}}</div>
    </div>
  );
}}

export default function DashboardPage() {{
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {{
    getDashboardStats()
      .then(setStats)
      .catch(e => setError(e.message));
  }}, []);

  const colors = ['#1976d2','#388e3c','#f57c00','#7b1fa2','#c62828','#00796b','#5d4037'];

  if (error) return <p style={{{{ color: 'red' }}}}>{{error}}</p>;

  return (
    <div>
      <h2 style={{{{ marginBottom: 24 }}}}>Dashboard</h2>
      <div style={{{{ display: 'flex', flexWrap: 'wrap', gap: 16 }}}}>
        {cards}
      </div>
    </div>
  );
}}
"""

    def generate_app_tsx(self, entities: list[str]) -> str:
        imports_pages = "\n".join(
            f"import {e}Page from './pages/{e}Page';" for e in entities
        )
        nav_links = "\n        ".join(
            f'<Link to="/{_camel(e)}s">{e}s</Link>' for e in entities
        )
        routes = "\n          ".join(
            f'<Route path="/{_camel(e)}s" element={{<{e}Page />}} />' for e in entities
        )

        return f"""import {{ Link, Navigate, Route, Routes }} from 'react-router-dom';
import {{ useAuth }} from './auth/AuthProvider';
import {{ useI18n }} from './context/I18nContext';
import DashboardPage from './pages/DashboardPage';
import NotificationBell from './components/Notifications/NotificationBell';
import LanguageSwitcher from './components/LanguageSwitcher';
{imports_pages}

export default function App() {{
  const {{ authenticated, username, roles, login, logout }} = useAuth();
  const {{ t }} = useI18n();

  if (!authenticated) {{
    return (
      <div style={{{{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 120 }}}}>
        <h1>{entities[0] if entities else 'App'} Manager</h1>
        <p>Inicia sesión para continuar</p>
        <button onClick={{login}} style={{{{ padding: '10px 24px', fontSize: 16 }}}}>
          {{t('login')}}
        </button>
      </div>
    );
  }}

  return (
    <>
      <nav style={{{{ display: 'flex', gap: 16, padding: '8px 16px', background: '#1976d2', alignItems: 'center' }}}}>
        <Link to="/" style={{{{ color: '#fff', fontWeight: 700, textDecoration: 'none' }}}}>{{t('dashboard')}}</Link>
        {nav_links}
        <span style={{{{ marginLeft: 'auto', color: '#fff' }}}}>
          {{username}} ({{roles.join(', ')}})
        </span>
        <LanguageSwitcher />
        <NotificationBell />
        <button
          onClick={{logout}}
          style={{{{ background: 'rgba(255,255,255,.15)', color: '#fff', border: 'none', borderRadius: 4, padding: '4px 12px', cursor: 'pointer' }}}}
        >{{t('logout')}}</button>
      </nav>
      <main style={{{{ padding: 24 }}}}>
        <Routes>
          <Route path="/" element={{<DashboardPage />}} />
          {routes}
        </Routes>
      </main>
    </>
  );
}}
"""

    def generate_websocket_hook(self, api_base_var: str = "API_BASE") -> str:
        """
        Generates useWebSocket.ts — connects via STOMP/SockJS to /ws
        and subscribes to /topic/notifications.
        """
        return f"""import {{ useEffect, useState }} from 'react';
import {{ Client }} from '@stomp/stompjs';
import SockJS from 'sockjs-client';
import {{ {api_base_var} }} from '../config/api';

export interface WsNotification {{
  type: 'CREATED' | 'UPDATED' | 'DELETED';
  entityType: string;
  message: string;
  timestamp: string;
}}

export function useWebSocket() {{
  const [notifications, setNotifications] = useState<WsNotification[]>([]);
  const [unread, setUnread] = useState(0);

  useEffect(() => {{
    const client = new Client({{
      webSocketFactory: () => new SockJS(`${{{api_base_var}}}/ws`),
      reconnectDelay: 5000,
      onConnect: () => {{
        client.subscribe('/topic/notifications', (msg) => {{
          const notification: WsNotification = JSON.parse(msg.body);
          setNotifications(prev => [notification, ...prev].slice(0, 50));
          setUnread(prev => prev + 1);
        }});
      }},
    }});
    client.activate();
    return () => {{ client.deactivate(); }};
  }}, []);

  const markAllRead = () => setUnread(0);
  const clearAll = () => {{ setNotifications([]); setUnread(0); }};

  return {{ notifications, unread, markAllRead, clearAll }};
}}
"""

    def generate_notification_bell(self) -> str:
        """
        Generates NotificationBell.tsx — bell icon with unread badge and dropdown panel.
        Color-coded: green=CREATED, blue=UPDATED, red=DELETED.
        """
        return """import { useState } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';

const TYPE_COLOR: Record<string, string> = {
  CREATED: '#2e7d32',
  UPDATED: '#1565c0',
  DELETED: '#c62828',
};

export default function NotificationBell() {
  const { notifications, unread, markAllRead, clearAll } = useWebSocket();
  const [open, setOpen] = useState(false);

  const toggle = () => {
    setOpen(v => !v);
    if (!open) markAllRead();
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={toggle}
        style={{
          background: 'transparent', border: 'none', cursor: 'pointer',
          fontSize: 22, color: '#fff', position: 'relative', padding: '0 4px'
        }}
        title="Notificaciones"
      >
        🔔
        {unread > 0 && (
          <span style={{
            position: 'absolute', top: -4, right: -4,
            background: '#f44336', color: '#fff',
            borderRadius: '50%', fontSize: 10, fontWeight: 700,
            width: 16, height: 16, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
          }}>
            {unread > 9 ? '9+' : unread}
          </span>
        )}
      </button>

      {open && (
        <div style={{
          position: 'absolute', right: 0, top: 36,
          width: 340, maxHeight: 420, overflowY: 'auto',
          background: '#fff', borderRadius: 8,
          boxShadow: '0 4px 20px rgba(0,0,0,.2)', zIndex: 1000,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', borderBottom: '1px solid #eee' }}>
            <strong style={{ color: '#333' }}>Notificaciones</strong>
            {notifications.length > 0 && (
              <button onClick={clearAll} style={{ background: 'none', border: 'none', color: '#999', cursor: 'pointer', fontSize: 12 }}>
                Limpiar todo
              </button>
            )}
          </div>

          {notifications.length === 0 ? (
            <p style={{ padding: 16, color: '#999', textAlign: 'center', margin: 0 }}>Sin notificaciones</p>
          ) : (
            notifications.map((n, i) => (
              <div key={i} style={{ padding: '10px 14px', borderBottom: '1px solid #f5f5f5' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{
                    fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
                    color: TYPE_COLOR[n.type] ?? '#555',
                    background: (TYPE_COLOR[n.type] ?? '#555') + '18',
                    borderRadius: 4, padding: '1px 6px',
                  }}>
                    {n.type}
                  </span>
                  <span style={{ fontSize: 11, color: '#aaa' }}>
                    {new Date(n.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p style={{ margin: '4px 0 0', fontSize: 13, color: '#444' }}>{n.message}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
"""
