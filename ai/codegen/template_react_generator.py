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
import {{ useI18n }} from '../../context/I18nContext';

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
  const {{ t }} = useI18n();
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
    if (!window.confirm(t('confirmDelete'))) return;
    await delete{entity}(id);
    showToast(`${{t('{entity}' as any)}} ${{t('deleted')}}`, 'info');
    load(currentPage, search);
  }};

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {{
    setSearch(e.target.value);
    setCurrentPage(0);
  }};

  return (
    <div>
      <div style={{{{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}}}>
        <h2 style={{{{ margin: 0 }}}}>{{page?.total ?? ''}} {{t('{entity}s' as any)}}</h2>
        <div style={{{{ display: 'flex', gap: 8 }}}}>
          <input
            placeholder={{t('search')}}
            value={{search}}
            onChange={{handleSearch}}
            style={{{{ padding: '6px 12px', border: '1px solid #ddd', borderRadius: 4, width: 220 }}}}
          />
          <button
            onClick={{onNew}}
            style={{{{ padding: '6px 16px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}}}
          >
            + {{t('new')}}
          </button>
        </div>
      </div>

      {{error && <p style={{{{ color: 'red' }}}}>{{error}}</p>}}
      {{loading && <p style={{{{ color: '#999' }}}}>{{t('loading')}}</p>}}

      <table style={{{{ width: '100%', borderCollapse: 'collapse' }}}}>
        <thead>
          <tr>{headers}<th style={{{{thStyle}}}}>{{t('actions')}}</th></tr>
        </thead>
        <tbody>
          {{(page?.content ?? []).map({lower} => (
            <tr key={{{lower}.id}} style={{{{ background: '#fff' }}}}>
              {cells}
              <td style={{{{tdStyle}}}}>
                <button
                  onClick={{() => onEdit({lower})}}
                  style={{{{ marginRight: 6, padding: '3px 10px', cursor: 'pointer' }}}}
                >{{t('edit')}}</button>
                <button
                  onClick={{() => handleDelete({lower}.id)}}
                  style={{{{ padding: '3px 10px', cursor: 'pointer', color: '#c62828' }}}}
                >{{t('delete')}}</button>
              </td>
            </tr>
          ))}}
        </tbody>
      </table>

      {{page && page.totalPages > 1 && (
        <div style={{{{ display: 'flex', gap: 8, marginTop: 16, alignItems: 'center' }}}}>
          <button disabled={{currentPage === 0}} onClick={{() => setCurrentPage(p => p - 1)}}>‹</button>
          <span>{{t('page')}} {{currentPage + 1}} {{t('of')}} {{page.totalPages}}</span>
          <button disabled={{page.last}} onClick={{() => setCurrentPage(p => p + 1)}}>›</button>
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
  define: {
    // sockjs-client uses Node.js 'global' — polyfill for the browser
    global: 'globalThis',
  },
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
      const res = await apiFetch(`${{API_BASE}}/api/documents/${{entityType}}/${{entityId}}`);
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
        `${{API_BASE}}/api/documents/${{entityType}}/${{entityId}}`,
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
      `${{API_BASE}}/api/documents/${{entityType}}/${{entityId}}/${{storedName}}`,
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
          border: `2px dashed ${{dragging ? '#1976d2' : '#ccc'}}`,
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
        return """import { useI18n } from '../context/I18nContext';

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

    def generate_appointment_calendar_tsx(self) -> str:
        """
        Generates AppointmentCalendar.tsx — weekly calendar with CSS grid.
        Mon-Sun columns, time slots 08:00-20:00 in 30min increments.
        Props: appointments array with id, title, start (ISO), end (ISO), color?.
        """
        return """import { useState } from 'react';

interface CalendarAppointment {
  id: string;
  title: string;
  start: string;  // ISO 8601
  end: string;
  color?: string;
}

interface Props {
  appointments: CalendarAppointment[];
  onSlotClick?: (date: Date) => void;
  onAppointmentClick?: (appt: CalendarAppointment) => void;
}

const HOUR_START = 8;
const HOUR_END = 20;
const SLOT_HEIGHT = 40; // px per 30min slot
const DAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
const DAYS_EN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function getWeekDates(base: Date): Date[] {
  const day = base.getDay();
  const diff = (day === 0 ? -6 : 1 - day);
  const monday = new Date(base);
  monday.setDate(base.getDate() + diff);
  monday.setHours(0, 0, 0, 0);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return d;
  });
}

function minutesSinceMidnight(iso: string): number {
  const d = new Date(iso);
  return d.getHours() * 60 + d.getMinutes();
}

function isSameDay(d1: Date, d2: Date): boolean {
  return d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate();
}

export default function AppointmentCalendar({ appointments, onSlotClick, onAppointmentClick }: Props) {
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const weekDates = getWeekDates(currentWeek);

  const slots = Array.from({ length: (HOUR_END - HOUR_START) * 2 }, (_, i) => {
    const h = HOUR_START + Math.floor(i / 2);
    const m = i % 2 === 0 ? '00' : '30';
    return `${String(h).padStart(2, '0')}:${m}`;
  });

  const prevWeek = () => { const d = new Date(currentWeek); d.setDate(d.getDate() - 7); setCurrentWeek(d); };
  const nextWeek = () => { const d = new Date(currentWeek); d.setDate(d.getDate() + 7); setCurrentWeek(d); };
  const today = () => setCurrentWeek(new Date());

  const weekLabel = `${weekDates[0].toLocaleDateString()} – ${weekDates[6].toLocaleDateString()}`;

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif' }}>
      {/* Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <button onClick={prevWeek} style={{ padding: '4px 10px' }}>‹</button>
        <button onClick={today} style={{ padding: '4px 10px', fontSize: 12 }}>Hoy</button>
        <button onClick={nextWeek} style={{ padding: '4px 10px' }}>›</button>
        <span style={{ fontWeight: 600, marginLeft: 8 }}>{weekLabel}</span>
      </div>

      {/* Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '52px repeat(7, 1fr)', border: '1px solid #e0e0e0', borderRadius: 6, overflow: 'hidden' }}>
        {/* Header row */}
        <div style={{ background: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }} />
        {weekDates.map((d, i) => {
          const isToday = isSameDay(d, new Date());
          return (
            <div key={i} style={{
              background: isToday ? '#e3f2fd' : '#f5f5f5',
              borderLeft: '1px solid #e0e0e0',
              borderBottom: '1px solid #e0e0e0',
              padding: '6px 4px',
              textAlign: 'center',
              fontSize: 12,
              fontWeight: isToday ? 700 : 400,
            }}>
              <div>{DAYS[i]}</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: isToday ? '#1976d2' : '#333' }}>
                {d.getDate()}
              </div>
            </div>
          );
        })}

        {/* Time slots */}
        {slots.map((slot, si) => (
          <>
            {/* Time label */}
            <div key={`label-${si}`} style={{
              fontSize: 10, color: '#999', padding: '0 4px',
              height: SLOT_HEIGHT, display: 'flex', alignItems: 'flex-start',
              paddingTop: 2, borderBottom: si % 2 === 1 ? '1px solid #f0f0f0' : undefined,
            }}>
              {si % 2 === 0 ? slot : ''}
            </div>
            {/* Day columns */}
            {weekDates.map((d, di) => {
              const slotStart = new Date(d);
              slotStart.setHours(HOUR_START + Math.floor(si / 2), si % 2 === 0 ? 0 : 30, 0, 0);

              const dayAppts = appointments.filter(a => isSameDay(new Date(a.start), d));

              return (
                <div
                  key={`slot-${si}-${di}`}
                  onClick={() => onSlotClick?.(slotStart)}
                  style={{
                    height: SLOT_HEIGHT,
                    borderLeft: '1px solid #e0e0e0',
                    borderBottom: si % 2 === 1 ? '1px solid #f0f0f0' : '1px dashed #f5f5f5',
                    position: 'relative',
                    cursor: 'pointer',
                    background: si % 2 === 0 ? '#fff' : '#fafafa',
                  }}
                >
                  {si === 0 && dayAppts.map(appt => {
                    const startMin = minutesSinceMidnight(appt.start) - HOUR_START * 60;
                    const endMin = minutesSinceMidnight(appt.end) - HOUR_START * 60;
                    const top = (startMin / 30) * SLOT_HEIGHT;
                    const height = Math.max(((endMin - startMin) / 30) * SLOT_HEIGHT, SLOT_HEIGHT);
                    return (
                      <div
                        key={appt.id}
                        onClick={e => { e.stopPropagation(); onAppointmentClick?.(appt); }}
                        style={{
                          position: 'absolute',
                          top, left: 2, right: 2, height,
                          background: appt.color ?? '#1976d2',
                          color: '#fff', borderRadius: 4,
                          fontSize: 11, padding: '2px 4px',
                          overflow: 'hidden', cursor: 'pointer',
                          zIndex: 1,
                          boxShadow: '0 1px 3px rgba(0,0,0,.2)',
                        }}
                      >
                        {appt.title}
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </>
        ))}
      </div>
    </div>
  );
}
"""

    def generate_odontogram_tsx(self) -> str:
        """
        Generates Odontogram.tsx — interactive SVG odontogram with 32 adult teeth.
        FDI notation. Status map: healthy=white, caries=yellow, treated=blue,
        extracted=red, crown=purple, missing=grey.
        """
        return """import { useState } from 'react';

type ToothStatus = 'healthy' | 'caries' | 'treated' | 'extracted' | 'crown' | 'missing';

const STATUS_COLOR: Record<ToothStatus, string> = {
  healthy: '#ffffff',
  caries: '#ffcc02',
  treated: '#4fc3f7',
  extracted: '#ef9a9a',
  crown: '#ce93d8',
  missing: '#e0e0e0',
};

const STATUS_LABEL: Record<ToothStatus, string> = {
  healthy: 'Sano',
  caries: 'Caries',
  treated: 'Tratado',
  extracted: 'Extraído',
  crown: 'Corona',
  missing: 'Ausente',
};

// FDI notation: upper right 11-18, upper left 21-28, lower left 31-38, lower right 41-48
const UPPER_RIGHT = [18, 17, 16, 15, 14, 13, 12, 11];
const UPPER_LEFT  = [21, 22, 23, 24, 25, 26, 27, 28];
const LOWER_LEFT  = [31, 32, 33, 34, 35, 36, 37, 38];
const LOWER_RIGHT = [48, 47, 46, 45, 44, 43, 42, 41];

interface Props {
  patientId?: string;
  initialState?: Record<number, ToothStatus>;
  onChange?: (toothNum: number, status: ToothStatus) => void;
  readOnly?: boolean;
}

function ToothSVG({ num, status, onClick }: { num: number; status: ToothStatus; onClick: () => void }) {
  const color = STATUS_COLOR[status];
  const isExtracted = status === 'extracted';
  return (
    <div
      onClick={onClick}
      title={`Diente ${num} - ${STATUS_LABEL[status]}`}
      style={{ textAlign: 'center', cursor: 'pointer', width: 36 }}
    >
      <svg width="30" height="36" viewBox="0 0 30 36" style={{ display: 'block', margin: '0 auto' }}>
        {isExtracted ? (
          <line x1="5" y1="5" x2="25" y2="31" stroke="#ef5350" strokeWidth="3" />
        ) : (
          <>
            <rect x="3" y="4" width="24" height="28" rx="5"
              fill={color} stroke="#555" strokeWidth="1.5" />
            {status === 'crown' && (
              <rect x="3" y="4" width="24" height="10" rx="3"
                fill="#ab47bc" stroke="#555" strokeWidth="1" />
            )}
            {status === 'caries' && (
              <circle cx="15" cy="18" r="5" fill="#f57f17" />
            )}
          </>
        )}
      </svg>
      <span style={{ fontSize: 9, color: '#888' }}>{num}</span>
    </div>
  );
}

export default function Odontogram({ patientId, initialState = {}, onChange, readOnly = false }: Props) {
  const [teeth, setTeeth] = useState<Record<number, ToothStatus>>(initialState);
  const [selected, setSelected] = useState<number | null>(null);
  const [legend, setLegend] = useState(false);

  const getStatus = (num: number): ToothStatus => teeth[num] ?? 'healthy';

  const handleClick = (num: number) => {
    if (readOnly) return;
    setSelected(num);
  };

  const applyStatus = (status: ToothStatus) => {
    if (selected === null) return;
    const next = { ...teeth, [selected]: status };
    setTeeth(next);
    onChange?.(selected, status);
    setSelected(null);
  };

  const renderRow = (nums: number[], label: string) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: 2, marginBottom: 4 }}>
      <span style={{ fontSize: 10, color: '#999', width: 60, textAlign: 'right', marginRight: 4 }}>{label}</span>
      {nums.map(n => (
        <div key={n} style={{
          outline: selected === n ? '2px solid #1976d2' : 'none',
          borderRadius: 6,
        }}>
          <ToothSVG num={n} status={getStatus(n)} onClick={() => handleClick(n)} />
        </div>
      ))}
    </div>
  );

  return (
    <div style={{ background: '#fafafa', borderRadius: 8, padding: 16, border: '1px solid #e0e0e0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h4 style={{ margin: 0 }}>Odontograma {patientId ? `— Paciente ${patientId}` : ''}</h4>
        <button onClick={() => setLegend(v => !v)} style={{ fontSize: 12, padding: '2px 8px' }}>
          {legend ? 'Ocultar' : 'Leyenda'}
        </button>
      </div>

      {legend && (
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
          {(Object.keys(STATUS_COLOR) as ToothStatus[]).map(s => (
            <div key={s} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}>
              <div style={{ width: 14, height: 14, background: STATUS_COLOR[s], border: '1px solid #aaa', borderRadius: 3 }} />
              {STATUS_LABEL[s]}
            </div>
          ))}
        </div>
      )}

      <div style={{ overflowX: 'auto' }}>
        {renderRow(UPPER_RIGHT.concat(UPPER_LEFT), 'Superior')}
        <div style={{ borderTop: '1px dashed #ccc', margin: '8px 0 8px 64px' }} />
        {renderRow(LOWER_RIGHT.concat(LOWER_LEFT), 'Inferior')}
      </div>

      {selected !== null && !readOnly && (
        <div style={{ marginTop: 12, padding: 10, background: '#e3f2fd', borderRadius: 6 }}>
          <span style={{ fontSize: 13, marginRight: 8 }}>Diente {selected}:</span>
          {(Object.keys(STATUS_COLOR) as ToothStatus[]).map(s => (
            <button
              key={s}
              onClick={() => applyStatus(s)}
              style={{
                marginRight: 4, padding: '3px 10px', fontSize: 12,
                background: STATUS_COLOR[s], border: '1px solid #aaa',
                borderRadius: 4, cursor: 'pointer',
              }}
            >
              {STATUS_LABEL[s]}
            </button>
          ))}
          <button onClick={() => setSelected(null)} style={{ marginLeft: 8, fontSize: 12, background: '#eee' }}>
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
"""

    def generate_waiting_room_tsx(self) -> str:
        """
        Generates WaitingRoom.tsx — digital waiting room with WebSocket integration.
        Uses STOMP over SockJS. Shows queue with status badges and call-next button.
        """
        return """import { useEffect, useState } from 'react';
import { Client } from '@stomp/stompjs';
import SockJS from 'sockjs-client';
import { API_BASE } from '../config/api';

interface WaitingPatient {
  id: string;
  name: string;
  appointmentTime: string;
  dentist: string;
  status: 'waiting' | 'called' | 'in-progress' | 'done';
}

const STATUS_STYLE: Record<string, React.CSSProperties> = {
  waiting:     { background: '#fff9c4', color: '#f57f17' },
  called:      { background: '#e8f5e9', color: '#2e7d32', fontWeight: 700 },
  'in-progress': { background: '#e3f2fd', color: '#1565c0' },
  done:        { background: '#f5f5f5', color: '#9e9e9e' },
};

const STATUS_LABEL: Record<string, string> = {
  waiting: 'En espera',
  called: '¡Llamado!',
  'in-progress': 'En consulta',
  done: 'Finalizado',
};

export default function WaitingRoom() {
  const [queue, setQueue] = useState<WaitingPatient[]>([]);
  const [client, setClient] = useState<Client | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const c = new Client({
      webSocketFactory: () => new SockJS(`${API_BASE}/ws`),
      reconnectDelay: 5000,
      onConnect: () => {
        setConnected(true);
        c.subscribe('/topic/waiting-room', (msg) => {
          const event = JSON.parse(msg.body);
          if (event.type === 'ADD') {
            setQueue(prev => [...prev, event.patient]);
          } else if (event.type === 'UPDATE') {
            setQueue(prev => prev.map(p => p.id === event.patient.id ? event.patient : p));
          } else if (event.type === 'REMOVE') {
            setQueue(prev => prev.filter(p => p.id !== event.patientId));
          }
        });
      },
      onDisconnect: () => setConnected(false),
    });
    c.activate();
    setClient(c);
    return () => { c.deactivate(); };
  }, []);

  const callNext = () => {
    const next = queue.find(p => p.status === 'waiting');
    if (!next || !client?.connected) return;
    const updated = { ...next, status: 'called' as const };
    client.publish({
      destination: '/app/waiting-room',
      body: JSON.stringify({ type: 'UPDATE', patient: updated }),
    });
  };

  const updateStatus = (id: string, status: WaitingPatient['status']) => {
    if (!client?.connected) return;
    const patient = queue.find(p => p.id === id);
    if (!patient) return;
    client.publish({
      destination: '/app/waiting-room',
      body: JSON.stringify({ type: 'UPDATE', patient: { ...patient, status } }),
    });
  };

  const waiting = queue.filter(p => p.status === 'waiting').length;

  return (
    <div style={{ maxWidth: 720, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0 }}>Sala de espera</h2>
          <span style={{ fontSize: 12, color: connected ? '#2e7d32' : '#c62828' }}>
            {connected ? '● Conectado en tiempo real' : '○ Desconectado'}
          </span>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: 13, color: '#555' }}>{waiting} en espera</span>
          <button
            onClick={callNext}
            disabled={waiting === 0}
            style={{ padding: '8px 16px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: waiting > 0 ? 'pointer' : 'not-allowed' }}
          >
            📢 Llamar siguiente
          </button>
        </div>
      </div>

      {queue.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
          <p style={{ fontSize: 24 }}>🪑</p>
          <p>Sala de espera vacía</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {queue.map((p, i) => (
            <div key={p.id} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '12px 16px', borderRadius: 8,
              border: '1px solid #e0e0e0',
              ...STATUS_STYLE[p.status],
            }}>
              <span style={{ fontSize: 20, fontWeight: 700, color: '#bbb', width: 28 }}>
                {i + 1}
              </span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600 }}>{p.name}</div>
                <div style={{ fontSize: 12, opacity: 0.7 }}>
                  {p.appointmentTime} · Dr/a. {p.dentist}
                </div>
              </div>
              <span style={{
                fontSize: 12, fontWeight: 600, padding: '3px 10px',
                borderRadius: 12, background: 'rgba(0,0,0,0.1)',
              }}>
                {STATUS_LABEL[p.status]}
              </span>
              {p.status === 'called' && (
                <button onClick={() => updateStatus(p.id, 'in-progress')} style={{ fontSize: 12, padding: '3px 10px' }}>
                  En consulta
                </button>
              )}
              {p.status === 'in-progress' && (
                <button onClick={() => updateStatus(p.id, 'done')} style={{ fontSize: 12, padding: '3px 10px', background: '#e8f5e9', color: '#2e7d32' }}>
                  Finalizar
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
"""

    def generate_clinical_timeline_tsx(self) -> str:
        """
        Generates ClinicalTimeline.tsx — patient history timeline.
        Shows appointments, treatments, invoices, documents, notes sorted by date desc.
        """
        return """interface TimelineEvent {
  id: string;
  date: string;
  type: 'appointment' | 'treatment' | 'invoice' | 'document' | 'note';
  title: string;
  description?: string;
  metadata?: Record<string, string>;
}

const TYPE_CONFIG = {
  appointment: { icon: '📅', color: '#1976d2', label: 'Cita' },
  treatment:   { icon: '🦷', color: '#388e3c', label: 'Tratamiento' },
  invoice:     { icon: '💰', color: '#f57c00', label: 'Factura' },
  document:    { icon: '📎', color: '#7b1fa2', label: 'Documento' },
  note:        { icon: '📝', color: '#0288d1', label: 'Nota' },
};

interface Props {
  events: TimelineEvent[];
  patientName?: string;
}

export default function ClinicalTimeline({ events, patientName }: Props) {
  const sorted = [...events].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  if (sorted.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
        <p style={{ fontSize: 24 }}>📋</p>
        <p>Sin historial clínico</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 680 }}>
      {patientName && <h3 style={{ marginBottom: 16 }}>Historia clínica — {patientName}</h3>}
      <div style={{ position: 'relative', paddingLeft: 32 }}>
        {/* vertical line */}
        <div style={{
          position: 'absolute', left: 11, top: 0, bottom: 0,
          width: 2, background: '#e0e0e0',
        }} />

        {sorted.map((ev, i) => {
          const cfg = TYPE_CONFIG[ev.type];
          return (
            <div key={ev.id} style={{ position: 'relative', marginBottom: 24 }}>
              {/* dot */}
              <div style={{
                position: 'absolute', left: -32, top: 2,
                width: 24, height: 24, borderRadius: '50%',
                background: cfg.color, color: '#fff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 12, zIndex: 1,
              }}>
                {cfg.icon}
              </div>

              <div style={{
                background: '#fff', borderRadius: 8,
                border: '1px solid #e8e8e8',
                padding: '10px 14px',
                boxShadow: '0 1px 4px rgba(0,0,0,.06)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <span style={{
                      fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
                      color: cfg.color, background: cfg.color + '18',
                      borderRadius: 4, padding: '1px 6px', marginRight: 8,
                    }}>
                      {cfg.label}
                    </span>
                    <strong style={{ fontSize: 14 }}>{ev.title}</strong>
                  </div>
                  <span style={{ fontSize: 11, color: '#aaa', whiteSpace: 'nowrap', marginLeft: 8 }}>
                    {new Date(ev.date).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })}
                  </span>
                </div>
                {ev.description && (
                  <p style={{ margin: '6px 0 0', fontSize: 13, color: '#555' }}>{ev.description}</p>
                )}
                {ev.metadata && Object.keys(ev.metadata).length > 0 && (
                  <div style={{ marginTop: 6, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    {Object.entries(ev.metadata).map(([k, v]) => (
                      <span key={k} style={{ fontSize: 11, color: '#888' }}>
                        <strong>{k}:</strong> {v}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
"""

    def generate_insurance_form_tsx(self) -> str:
        """
        Generates InsuranceForm.tsx — patient insurance/convenio management form.
        Fields: insuranceCompany, policyNumber, coverageType, validUntil, coveragePercent, notes.
        """
        return """import { useState } from 'react';

interface InsuranceData {
  insuranceCompany: string;
  policyNumber: string;
  coverageType: 'FULL' | 'PARTIAL' | 'DENTAL_ONLY' | 'NONE';
  coveragePercent: number;
  validUntil: string;
  notes: string;
}

const COVERAGE_TYPES = [
  { value: 'FULL', label: 'Cobertura completa' },
  { value: 'PARTIAL', label: 'Cobertura parcial' },
  { value: 'DENTAL_ONLY', label: 'Solo dental' },
  { value: 'NONE', label: 'Sin cobertura' },
];

interface Props {
  patientId: string;
  initial?: InsuranceData;
  onSave?: (data: InsuranceData) => void;
}

export default function InsuranceForm({ patientId, initial, onSave }: Props) {
  const [form, setForm] = useState<InsuranceData>(initial ?? {
    insuranceCompany: '',
    policyNumber: '',
    coverageType: 'NONE',
    coveragePercent: 0,
    validUntil: '',
    notes: '',
  });
  const [saved, setSaved] = useState(false);

  const set = (k: keyof InsuranceData, v: string | number) =>
    setForm(prev => ({ ...prev, [k]: v }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave?.(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 8, padding: 16 }}>
      <h4 style={{ margin: '0 0 16px' }}>Seguro / Convenio</h4>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div>
          <label style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Aseguradora</label>
          <input value={form.insuranceCompany} onChange={e => set('insuranceCompany', e.target.value)}
            placeholder="Ej: Adeslas, Sanitas..." style={{ width: '100%', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 4 }} />
        </div>
        <div>
          <label style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Nº de póliza</label>
          <input value={form.policyNumber} onChange={e => set('policyNumber', e.target.value)}
            placeholder="Número de póliza" style={{ width: '100%', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 4 }} />
        </div>
        <div>
          <label style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Tipo de cobertura</label>
          <select value={form.coverageType} onChange={e => set('coverageType', e.target.value)}
            style={{ width: '100%', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 4 }}>
            {COVERAGE_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Cobertura (%)</label>
          <input type="number" min={0} max={100} value={form.coveragePercent}
            onChange={e => set('coveragePercent', Number(e.target.value))}
            style={{ width: '100%', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 4 }} />
        </div>
        <div>
          <label style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Válido hasta</label>
          <input type="date" value={form.validUntil} onChange={e => set('validUntil', e.target.value)}
            style={{ width: '100%', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 4 }} />
        </div>
        <div>
          <label style={{ fontSize: 12, color: '#555', display: 'block', marginBottom: 4 }}>Notas</label>
          <input value={form.notes} onChange={e => set('notes', e.target.value)}
            placeholder="Observaciones..." style={{ width: '100%', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 4 }} />
        </div>
        <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          {saved && <span style={{ color: '#2e7d32', fontSize: 13, alignSelf: 'center' }}>✓ Guardado</span>}
          <button type="submit" style={{ padding: '8px 20px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
            Guardar seguro
          </button>
        </div>
      </form>
    </div>
  );
}
"""

    def generate_treatment_plan_editor_tsx(self) -> str:
        """
        Generates TreatmentPlanEditor.tsx — itemized treatment plan editor.
        Add/remove items per tooth with procedure, quantity, unit price.
        Shows total, patient share (after insurance), and status selector.
        """
        return """import { useState } from 'react';

interface PlanItem {
  toothNumber: number | '';
  procedureCode: string;
  description: string;
  quantity: number;
  unitPrice: number;
  insuranceCoverage: number;
}

const PROCEDURES = [
  { code: 'EXT001', label: 'Extracción simple' },
  { code: 'EXT002', label: 'Extracción quirúrgica' },
  { code: 'OBT001', label: 'Obturación 1 cara' },
  { code: 'OBT002', label: 'Obturación 2 caras' },
  { code: 'OBT003', label: 'Obturación 3 caras' },
  { code: 'END001', label: 'Endodoncia unirradicular' },
  { code: 'END002', label: 'Endodoncia multirradicular' },
  { code: 'PER001', label: 'Tartrectomía completa' },
  { code: 'PER002', label: 'Raspado y alisado radicular' },
  { code: 'PRO001', label: 'Corona metal-porcelana' },
  { code: 'PRO002', label: 'Corona zirconio' },
  { code: 'IMP001', label: 'Implante dental' },
  { code: 'ORT001', label: 'Ortodoncia mensual' },
  { code: 'BLA001', label: 'Blanqueamiento dental' },
  { code: 'RAD001', label: 'Radiografía periapical' },
  { code: 'RAD002', label: 'Ortopantomografía' },
];

const emptyItem = (): PlanItem => ({
  toothNumber: '',
  procedureCode: PROCEDURES[0].code,
  description: PROCEDURES[0].label,
  quantity: 1,
  unitPrice: 0,
  insuranceCoverage: 0,
});

interface Props {
  patientId: string;
  onSaved?: () => void;
}

export default function TreatmentPlanEditor({ patientId, onSaved }: Props) {
  const [items, setItems] = useState<PlanItem[]>([emptyItem()]);
  const [notes, setNotes] = useState('');
  const [expiresAt, setExpiresAt] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const updateItem = (i: number, field: keyof PlanItem, value: string | number) => {
    setItems(prev => {
      const next = [...prev];
      if (field === 'procedureCode') {
        const proc = PROCEDURES.find(p => p.code === value);
        next[i] = { ...next[i], procedureCode: value as string, description: proc?.label ?? '' };
      } else {
        next[i] = { ...next[i], [field]: value };
      }
      return next;
    });
  };

  const addItem = () => setItems(prev => [...prev, emptyItem()]);
  const removeItem = (i: number) => setItems(prev => prev.filter((_, idx) => idx !== i));

  const total = items.reduce((sum, it) => sum + (it.unitPrice * it.quantity), 0);
  const insurance = items.reduce((sum, it) => sum + it.insuranceCoverage, 0);
  const patientShare = total - insurance;

  const handleSave = async () => {
    setSaving(true);
    try {
      const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8080';
      const res = await fetch(`${API_BASE}/api/treatment-plans`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          patientId,
          expiresAt: expiresAt || null,
          notes,
          items: items.map(it => ({
            toothNumber: it.toothNumber !== '' ? it.toothNumber : null,
            procedureCode: it.procedureCode,
            description: it.description,
            quantity: it.quantity,
            unitPrice: it.unitPrice,
            insuranceCoverage: it.insuranceCoverage,
          })),
        }),
      });
      if (res.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
        onSaved?.();
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 8, padding: 20 }}>
      <h3 style={{ margin: '0 0 16px' }}>Nuevo plan de tratamiento</h3>

      {/* Items table */}
      <div style={{ overflowX: 'auto', marginBottom: 16 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: '#f5f5f5' }}>
              {['Diente', 'Procedimiento', 'Descripción', 'Cant.', 'Precio unit.', 'Seguro cubre', 'Total', ''].map(h => (
                <th key={h} style={{ padding: '8px 10px', textAlign: 'left', fontWeight: 600, whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
                <td style={{ padding: '6px 8px' }}>
                  <input
                    type="number" min={11} max={48} placeholder="—"
                    value={item.toothNumber}
                    onChange={e => updateItem(i, 'toothNumber', e.target.value ? Number(e.target.value) : '')}
                    style={{ width: 52, padding: '4px 6px', border: '1px solid #ddd', borderRadius: 4 }}
                  />
                </td>
                <td style={{ padding: '6px 8px' }}>
                  <select
                    value={item.procedureCode}
                    onChange={e => updateItem(i, 'procedureCode', e.target.value)}
                    style={{ padding: '4px 6px', border: '1px solid #ddd', borderRadius: 4, maxWidth: 200 }}
                  >
                    {PROCEDURES.map(p => <option key={p.code} value={p.code}>{p.label}</option>)}
                  </select>
                </td>
                <td style={{ padding: '6px 8px' }}>
                  <input
                    value={item.description}
                    onChange={e => updateItem(i, 'description', e.target.value)}
                    style={{ width: 180, padding: '4px 6px', border: '1px solid #ddd', borderRadius: 4 }}
                  />
                </td>
                <td style={{ padding: '6px 8px' }}>
                  <input
                    type="number" min={1} value={item.quantity}
                    onChange={e => updateItem(i, 'quantity', Number(e.target.value))}
                    style={{ width: 48, padding: '4px 6px', border: '1px solid #ddd', borderRadius: 4 }}
                  />
                </td>
                <td style={{ padding: '6px 8px' }}>
                  <input
                    type="number" min={0} step="0.01" value={item.unitPrice}
                    onChange={e => updateItem(i, 'unitPrice', Number(e.target.value))}
                    style={{ width: 80, padding: '4px 6px', border: '1px solid #ddd', borderRadius: 4 }}
                  />
                </td>
                <td style={{ padding: '6px 8px' }}>
                  <input
                    type="number" min={0} step="0.01" value={item.insuranceCoverage}
                    onChange={e => updateItem(i, 'insuranceCoverage', Number(e.target.value))}
                    style={{ width: 80, padding: '4px 6px', border: '1px solid #ddd', borderRadius: 4 }}
                  />
                </td>
                <td style={{ padding: '6px 8px', fontWeight: 600, textAlign: 'right', whiteSpace: 'nowrap' }}>
                  {(item.unitPrice * item.quantity).toFixed(2)} €
                </td>
                <td style={{ padding: '6px 8px' }}>
                  <button onClick={() => removeItem(i)} style={{ background: '#ef5350', color: '#fff', border: 'none', borderRadius: 4, padding: '2px 8px', cursor: 'pointer' }}>✕</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button onClick={addItem} style={{ fontSize: 13, padding: '6px 14px', background: '#e3f2fd', color: '#1565c0', border: '1px solid #90caf9', borderRadius: 4, cursor: 'pointer', marginBottom: 16 }}>
        + Añadir procedimiento
      </button>

      {/* Summary */}
      <div style={{ display: 'flex', gap: 24, justifyContent: 'flex-end', marginBottom: 16, fontSize: 14 }}>
        <div>Total bruto: <strong>{total.toFixed(2)} €</strong></div>
        <div style={{ color: '#2e7d32' }}>Cubre seguro: <strong>-{insurance.toFixed(2)} €</strong></div>
        <div style={{ fontSize: 16, fontWeight: 700, color: '#1976d2' }}>Paciente paga: {patientShare.toFixed(2)} €</div>
      </div>

      {/* Metadata */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
        <div>
          <label style={{ fontSize: 12, color: '#666', display: 'block', marginBottom: 4 }}>Válido hasta</label>
          <input type="date" value={expiresAt} onChange={e => setExpiresAt(e.target.value)}
            style={{ width: '100%', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 4 }} />
        </div>
        <div>
          <label style={{ fontSize: 12, color: '#666', display: 'block', marginBottom: 4 }}>Observaciones</label>
          <input value={notes} onChange={e => setNotes(e.target.value)}
            placeholder="Notas para el paciente..."
            style={{ width: '100%', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 4 }} />
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
        {saved && <span style={{ color: '#2e7d32', alignSelf: 'center', fontSize: 13 }}>✓ Plan guardado</span>}
        <button onClick={handleSave} disabled={saving || items.length === 0}
          style={{ padding: '8px 24px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 600 }}>
          {saving ? 'Guardando...' : 'Guardar plan'}
        </button>
      </div>
    </div>
  );
}
"""

    def generate_reports_page_tsx(self) -> str:
        """
        Generates ReportsPage.tsx — production BI dashboard with custom SVG bar charts.
        Shows monthly production, top procedures, cancellations, revenue forecast.
        No external charting library — pure CSS/SVG.
        """
        return """import { useEffect, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8080';

interface MonthlyProduction { month: string; production: number; collected: number; appointments: number; }
interface DentistProduction { dentistName: string; total: number; appointments: number; }
interface ProcedureStats { code: string; name: string; count: number; revenue: number; }
interface CancellationStats { month: string; total: number; cancelled: number; noShow: number; ratePercent: number; }
interface RevenueForecast { pipeline: number; thisMonth: number; nextMonth: number; openPlans: number; }

function BarChart({ data, valueKey, labelKey, color = '#1976d2', unit = '€' }: {
  data: any[]; valueKey: string; labelKey: string; color?: string; unit?: string;
}) {
  if (!data.length) return null;
  const max = Math.max(...data.map(d => d[valueKey]));
  return (
    <div style={{ overflowX: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, minWidth: data.length * 48, height: 140 }}>
        {data.map((d, i) => {
          const pct = max > 0 ? (d[valueKey] / max) * 100 : 0;
          return (
            <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
              <span style={{ fontSize: 9, color: '#999' }}>
                {typeof d[valueKey] === 'number' && d[valueKey] > 999
                  ? (d[valueKey] / 1000).toFixed(1) + 'k'
                  : d[valueKey]}{unit === '€' && d[valueKey] > 0 ? '€' : ''}
              </span>
              <div style={{
                width: '100%', height: `${pct}%`,
                background: color, borderRadius: '3px 3px 0 0', minHeight: 2,
                transition: 'height .3s ease',
              }} title={`${d[labelKey]}: ${d[valueKey]}${unit}`} />
              <span style={{ fontSize: 9, color: '#aaa', textAlign: 'center', lineHeight: 1.2 }}>
                {String(d[labelKey]).slice(-5)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function KpiCard({ label, value, sub, color = '#1976d2' }: { label: string; value: string; sub?: string; color?: string }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 8, padding: '16px 20px', borderTop: `3px solid ${color}` }}>
      <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

function fmt(n: number) {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n);
}

export default function ReportsPage() {
  const [monthly, setMonthly] = useState<MonthlyProduction[]>([]);
  const [byDentist, setByDentist] = useState<DentistProduction[]>([]);
  const [procedures, setProcedures] = useState<ProcedureStats[]>([]);
  const [cancellations, setCancellations] = useState<CancellationStats[]>([]);
  const [forecast, setForecast] = useState<RevenueForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'production' | 'procedures' | 'cancellations' | 'forecast'>('production');

  const today = new Date();
  const fromDate = new Date(today); fromDate.setMonth(fromDate.getMonth() - 3);
  const fromStr = fromDate.toISOString().slice(0, 10);
  const toStr = today.toISOString().slice(0, 10);

  useEffect(() => {
    const headers = { 'Content-Type': 'application/json' };
    const opts = { credentials: 'include' as const };
    Promise.all([
      fetch(`${API_BASE}/api/reports/production/monthly?months=12`, opts).then(r => r.json()),
      fetch(`${API_BASE}/api/reports/production/by-dentist?from=${fromStr}&to=${toStr}`, opts).then(r => r.json()),
      fetch(`${API_BASE}/api/reports/production/top-procedures`, opts).then(r => r.json()),
      fetch(`${API_BASE}/api/reports/cancellations?months=6`, opts).then(r => r.json()),
      fetch(`${API_BASE}/api/reports/revenue-forecast`, opts).then(r => r.json()),
    ]).then(([m, d, p, c, f]) => {
      setMonthly(m); setByDentist(d); setProcedures(p); setCancellations(c); setForecast(f);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <p style={{ padding: 24, color: '#999' }}>Cargando informes...</p>;

  const totalProduction = monthly.reduce((s, m) => s + m.production, 0);
  const totalAppointments = monthly.reduce((s, m) => s + m.appointments, 0);
  const avgCancellationRate = cancellations.length
    ? Math.round(cancellations.reduce((s, c) => s + c.ratePercent, 0) / cancellations.length)
    : 0;

  const TABS = [
    { key: 'production', label: '📈 Producción' },
    { key: 'procedures', label: '🦷 Procedimientos' },
    { key: 'cancellations', label: '❌ Cancelaciones' },
    { key: 'forecast', label: '🔮 Previsión' },
  ] as const;

  return (
    <div>
      <h2 style={{ margin: '0 0 20px' }}>Informes de producción</h2>

      {/* KPI cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
        <KpiCard label="Producción anual" value={fmt(totalProduction)} sub="últimos 12 meses" color="#1976d2" />
        <KpiCard label="Citas realizadas" value={String(totalAppointments)} sub="últimos 12 meses" color="#388e3c" />
        <KpiCard label="Pipeline aceptado" value={forecast ? fmt(forecast.pipeline) : '—'} sub={`${forecast?.openPlans ?? 0} planes abiertos`} color="#f57c00" />
        <KpiCard label="Tasa cancelación" value={`${avgCancellationRate}%`} sub="media últimos 6 meses" color={avgCancellationRate > 15 ? '#c62828' : '#2e7d32'} />
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 16, borderBottom: '2px solid #e0e0e0' }}>
        {TABS.map(tab => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '8px 16px', border: 'none', borderRadius: '4px 4px 0 0',
              background: activeTab === tab.key ? '#1976d2' : '#f5f5f5',
              color: activeTab === tab.key ? '#fff' : '#555',
              cursor: 'pointer', fontWeight: activeTab === tab.key ? 600 : 400,
              marginBottom: -2, borderBottom: activeTab === tab.key ? '2px solid #1976d2' : 'none',
            }}>
            {tab.label}
          </button>
        ))}
      </div>

      <div style={{ background: '#fff', border: '1px solid #e0e0e0', borderRadius: 8, padding: 20 }}>

        {activeTab === 'production' && (
          <div>
            <h3 style={{ margin: '0 0 16px' }}>Producción mensual (12 meses)</h3>
            <BarChart data={monthly} valueKey="production" labelKey="month" color="#1976d2" />
            <div style={{ marginTop: 24 }}>
              <h4 style={{ margin: '0 0 12px' }}>Por dentista (últimos 3 meses)</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead><tr style={{ background: '#f5f5f5' }}>
                  <th style={{ padding: '8px 12px', textAlign: 'left' }}>Dentista</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Producción</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Citas</th>
                  <th style={{ padding: '8px 12px', textAlign: 'right' }}>Media/cita</th>
                </tr></thead>
                <tbody>{byDentist.map((d, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
                    <td style={{ padding: '8px 12px', fontWeight: 600 }}>{d.dentistName}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right' }}>{fmt(d.total)}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right' }}>{d.appointments}</td>
                    <td style={{ padding: '8px 12px', textAlign: 'right', color: '#1976d2' }}>
                      {fmt(d.appointments > 0 ? d.total / d.appointments : 0)}
                    </td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'procedures' && (
          <div>
            <h3 style={{ margin: '0 0 16px' }}>Top procedimientos por ingresos</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead><tr style={{ background: '#f5f5f5' }}>
                <th style={{ padding: '8px 12px', textAlign: 'left' }}>#</th>
                <th style={{ padding: '8px 12px', textAlign: 'left' }}>Procedimiento</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>Uds.</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>Ingresos</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>% del total</th>
              </tr></thead>
              <tbody>
                {(() => {
                  const totalRev = procedures.reduce((s, p) => s + p.revenue, 0);
                  return procedures.map((p, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
                      <td style={{ padding: '8px 12px', color: '#aaa' }}>{i + 1}</td>
                      <td style={{ padding: '8px 12px', fontWeight: 600 }}>{p.name}</td>
                      <td style={{ padding: '8px 12px', textAlign: 'right' }}>{p.count}</td>
                      <td style={{ padding: '8px 12px', textAlign: 'right', color: '#1976d2' }}>{fmt(p.revenue)}</td>
                      <td style={{ padding: '8px 12px', textAlign: 'right' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 6 }}>
                          <div style={{ width: 60, background: '#f0f0f0', borderRadius: 4, height: 8 }}>
                            <div style={{ width: `${totalRev > 0 ? (p.revenue / totalRev * 100) : 0}%`, background: '#1976d2', height: '100%', borderRadius: 4 }} />
                          </div>
                          {totalRev > 0 ? (p.revenue / totalRev * 100).toFixed(1) : 0}%
                        </div>
                      </td>
                    </tr>
                  ));
                })()}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'cancellations' && (
          <div>
            <h3 style={{ margin: '0 0 16px' }}>Análisis de cancelaciones (6 meses)</h3>
            <BarChart data={cancellations} valueKey="ratePercent" labelKey="month" color="#ef5350" unit="%" />
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, marginTop: 20 }}>
              <thead><tr style={{ background: '#f5f5f5' }}>
                {['Mes', 'Total citas', 'Canceladas', 'No presentado', 'Tasa'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: h === 'Mes' ? 'left' : 'right' }}>{h}</th>
                ))}
              </tr></thead>
              <tbody>{cancellations.map((c, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
                  <td style={{ padding: '8px 12px' }}>{c.month}</td>
                  <td style={{ padding: '8px 12px', textAlign: 'right' }}>{c.total}</td>
                  <td style={{ padding: '8px 12px', textAlign: 'right', color: '#f57c00' }}>{c.cancelled}</td>
                  <td style={{ padding: '8px 12px', textAlign: 'right', color: '#c62828' }}>{c.noShow}</td>
                  <td style={{ padding: '8px 12px', textAlign: 'right', fontWeight: 600, color: c.ratePercent > 15 ? '#c62828' : '#2e7d32' }}>
                    {c.ratePercent}%
                  </td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}

        {activeTab === 'forecast' && forecast && (
          <div>
            <h3 style={{ margin: '0 0 20px' }}>Previsión de ingresos</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
              <KpiCard label="Pipeline total" value={fmt(forecast.pipeline)} sub={`${forecast.openPlans} planes aceptados`} color="#1976d2" />
              <KpiCard label="Previsión este mes" value={fmt(forecast.thisMonth)} color="#388e3c" />
              <KpiCard label="Previsión mes siguiente" value={fmt(forecast.nextMonth)} color="#f57c00" />
            </div>
            <div style={{ marginTop: 20, padding: 16, background: '#f9f9f9', borderRadius: 8, fontSize: 13, color: '#666' }}>
              <strong>ℹ️ Metodología:</strong> La previsión se calcula a partir de los planes de tratamiento en estado
              ACCEPTED, ponderados por la tasa histórica de completado mensual de la clínica.
              Conecta el endpoint <code>/api/reports/revenue-forecast</code> con tus datos reales de TreatmentPlan.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
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
