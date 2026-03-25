# ELYX Frontend

Dashboard UI for the ELYX autonomous AI employee system. Built with Next.js 16, React 19, TypeScript, and Tailwind CSS 4.

## Setup

```bash
npm install
npm run dev
```

Opens at `http://localhost:3000`. Requires the backend APIs running:
- FastAPI on port 8000
- Vault API on port 8080
- Settings API on port 8081

Start all backends with `python run_elyx.py` from the project root.

## Pages

| Route | Page | Description |
|:------|:-----|:------------|
| `/dashboard` | Mission Control | Main overview — tasks, approvals, activity chart, system metrics |
| `/tasks` | Tasks | View and manage pending/completed tasks from the vault |
| `/approvals` | Approvals | Review and approve/reject sensitive actions |
| `/analytics` | Decision Matrix | Analytics dashboard with export and report generation |
| `/users` | Team Directory | Team members and recruitment form |
| `/business` | Business Operations | Odoo-connected business metrics and operations |
| `/comms` | Global Comms | Communication hub — send messages across platforms |
| `/system-monitor` | System Monitor | Live CPU/memory/disk metrics, agent status and toggles |
| `/scheduling` | Task Scheduler | Scheduled task management |
| `/security` | Vault Security | Security audit logs and settings |
| `/settings` | OS Settings | Feature flags, agent config, security toggles |
| `/api-docs` | System Interface | API documentation browser |

## Architecture

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── dashboard/          # Main dashboard
│   ├── tasks/              # Task management
│   ├── approvals/          # Approval workflow
│   ├── analytics/          # Analytics + reports
│   ├── comms/              # Communication hub
│   ├── system-monitor/     # Live system metrics
│   ├── settings/           # Feature flags + config
│   └── ...                 # Other pages
├── components/
│   └── DashboardLayout.tsx # Shared sidebar + header layout
├── lib/
│   ├── api.ts              # All API calls (authFetch wrapper)
│   ├── types.ts            # TypeScript interfaces
│   └── supabase.ts         # Supabase client (inactive, auth removed)
└── public/                 # Static assets
```

## Key Patterns

- **`authFetch()`** — Wrapper around `fetch()` in `lib/api.ts`. All API calls go through this. Gracefully skips auth headers when no session exists (app runs locally without login).
- **`DashboardLayout`** — Shared layout with sidebar navigation, header, and status bar. Every page wraps its content in this component.
- **Real metrics** — System monitor and dashboard pull live CPU/memory/disk from the backend via `psutil`. No mock data when backend is running.
- **Offline detection** — Pages show a warning banner when the backend is unreachable and data falls back to mock values.
- **`react-hot-toast`** — Used for all notifications. Note: no `.info()` method — use `toast("msg", { icon: "..." })` instead.

## Stack

| Package | Version | Role |
|:--------|:--------|:-----|
| Next.js | 16.1.6 | Framework (App Router, Turbopack) |
| React | 19.2.3 | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| Framer Motion | latest | Animations |
| Lucide React | latest | Icons |
| react-hot-toast | latest | Toast notifications |
