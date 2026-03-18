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
    return JAVA_TO_TS.get(java_type, java_type)


def _camel(name: str) -> str:
    return name[0].lower() + name[1:] if name else name


def _label(name: str) -> str:
    """'firstName' → 'First Name'"""
    import re
    s = re.sub(r"([A-Z])", r" \1", name).strip()
    return s[0].upper() + s[1:]


class TemplateReactGenerator:

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

const {base_url_var} = import.meta.env.VITE_API_URL ?? 'http://localhost:8080';
const ENDPOINT = `${{{base_url_var}}}/{lower}s`;

export async function getAll{entity}s(): Promise<{entity}[]> {{
  const res = await fetch(ENDPOINT);
  if (!res.ok) throw new Error('Failed to fetch {lower}s');
  return res.json();
}}

export async function get{entity}ById(id: string): Promise<{entity}> {{
  const res = await fetch(`${{ENDPOINT}}/${{id}}`);
  if (!res.ok) throw new Error(`{entity} ${{id}} not found`);
  return res.json();
}}

export async function create{entity}(data: Omit<{entity}, 'id'>): Promise<{entity}> {{
  const res = await fetch(ENDPOINT, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(data),
  }});
  if (!res.ok) throw new Error('Failed to create {lower}');
  return res.json();
}}

export async function update{entity}(id: string, data: Partial<{entity}>): Promise<{entity}> {{
  const res = await fetch(`${{ENDPOINT}}/${{id}}`, {{
    method: 'PUT',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(data),
  }});
  if (!res.ok) throw new Error(`Failed to update {lower} ${{id}}`);
  return res.json();
}}

export async function delete{entity}(id: string): Promise<void> {{
  const res = await fetch(`${{ENDPOINT}}/${{id}}`, {{ method: 'DELETE' }});
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

        headers = "".join(f"<th>{_label(c['name'])}</th>" for c in cols)
        cells = "".join(f"<td>{{String({lower}.{c['name']})}}</td>" for c in cols)

        return f"""import {{ useEffect, useState }} from 'react';
import type {{ {entity} }} from '../../types/{entity}';
import {{ getAll{entity}s, delete{entity} }} from '../../api/{lower}Api';

interface Props {{
  onEdit: (item: {entity}) => void;
  onNew: () => void;
  refresh: number;
}}

export default function {entity}List({{ onEdit, onNew, refresh }}: Props) {{
  const [{lower}s, set{entity}s] = useState<{entity}[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {{
    setLoading(true);
    getAll{entity}s()
      .then(set{entity}s)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }}, [refresh]);

  const handleDelete = async (id: string) => {{
    if (!window.confirm('Delete this {lower}?')) return;
    await delete{entity}(id);
    set{entity}s(prev => prev.filter(x => x.id !== id));
  }};

  if (loading) return <p>Loading…</p>;
  if (error) return <p style={{{{ color: 'red' }}}}>{{error}}</p>;

  return (
    <div>
      <div style={{{{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}}}>
        <h2>{entity}s</h2>
        <button onClick={{onNew}}>+ New {entity}</button>
      </div>
      <table style={{{{ width: '100%', borderCollapse: 'collapse' }}}}>
        <thead>
          <tr>{headers}<th>Actions</th></tr>
        </thead>
        <tbody>
          {{{lower}s.map({lower} => (
            <tr key={{{lower}.id}} style={{{{ borderBottom: '1px solid #eee' }}}}>
              {cells}
              <td>
                <button onClick={{() => onEdit({lower})}}>Edit</button>
                {{' '}}
                <button onClick={{() => handleDelete({lower}.id)}}>Delete</button>
              </td>
            </tr>
          ))}}
        </tbody>
      </table>
    </div>
  );
}}
"""

    # ------------------------------------------------------------------ #
    # Form component                                                       #
    # ------------------------------------------------------------------ #

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

        inputs = "\n        ".join(
            f"""<div>
          <label>{_label(f['name'])}</label>
          <input
            name="{f['name']}"
            value={{form.{f['name']} ?? ''}}
            onChange={{e => setForm(prev => ({{ ...prev, {f['name']}: e.target.value }}))}}
          />
        </div>"""
            for f in editable
        )

        return f"""import {{ useState }} from 'react';
import type {{ {entity} }} from '../../types/{entity}';
import {{ create{entity}, update{entity} }} from '../../api/{lower}Api';

interface Props {{
  item?: {entity} | null;
  onSaved: () => void;
  onCancel: () => void;
}}

export default function {entity}Form({{ item, onSaved, onCancel }}: Props) {{
  const [form, setForm] = useState({{ {state_init} }});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {{
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {{
      if (item?.id) {{
        await update{entity}(item.id, form as Partial<{entity}>);
      }} else {{
        await create{entity}(form as Omit<{entity}, 'id'>);
      }}
      onSaved();
    }} catch (err: unknown) {{
      setError(err instanceof Error ? err.message : 'Unexpected error');
    }} finally {{
      setSaving(false);
    }}
  }};

  return (
    <form onSubmit={{handleSubmit}} style={{{{ display: 'flex', flexDirection: 'column', gap: 12 }}}}>
      <h2>{{item ? 'Edit' : 'New'}} {entity}</h2>
      {inputs}
      {{error && <p style={{{{ color: 'red' }}}}>{{error}}</p>}}
      <div style={{{{ display: 'flex', gap: 8 }}}}>
        <button type="submit" disabled={{saving}}>{{saving ? 'Saving…' : 'Save'}}</button>
        <button type="button" onClick={{onCancel}}>Cancel</button>
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
                "react-router-dom": "^6.23.1"
            },
            "devDependencies": {
                "@types/react": "^18.3.3",
                "@types/react-dom": "^18.3.0",
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
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8080', changeOrigin: true },
    },
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
        return """import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
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

    def generate_env_example(self) -> str:
        return "VITE_API_URL=http://localhost:8080\n"

    def generate_app_tsx(self, entities: list[str]) -> str:
        imports_pages = "\n".join(
            f"import {e}Page from './pages/{e}Page';" for e in entities
        )
        nav_links = "\n          ".join(
            f'<Link to="/{_camel(e)}s">{e}s</Link>' for e in entities
        )
        routes = "\n          ".join(
            f'<Route path="/{_camel(e)}s" element={{<{e}Page />}} />' for e in entities
        )
        first = _camel(entities[0]) + "s" if entities else ""

        return f"""import {{ Link, Navigate, Route, Routes }} from 'react-router-dom';
{imports_pages}

export default function App() {{
  return (
    <>
      <nav>
        {nav_links}
      </nav>
      <main>
        <Routes>
          <Route path="/" element={{<Navigate to="/{first}" replace />}} />
          {routes}
        </Routes>
      </main>
    </>
  );
}}
"""
