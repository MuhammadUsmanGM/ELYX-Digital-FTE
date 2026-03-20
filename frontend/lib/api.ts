import { DashboardData, SystemState, ScenarioStatus, Task, ApprovalRequest, Communication, Transaction, KPI, BusinessWorkflow, SystemHistory, Scenario, WorkflowTask } from "./types";
import { supabase } from "./supabase";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// lib/api.ts

/**
 * Authenticated fetch wrapper — attaches Supabase JWT as Bearer token
 * when a session is available. Falls back to unauthenticated fetch otherwise.
 */
async function authFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers);
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      headers.set("Authorization", `Bearer ${session.access_token}`);
    }
  } catch {
    // No session available — proceed without auth header
  }
  return fetch(input, { ...init, headers });
}

// Fallback Mock Data as required by the ELYX platform for seamless UI experience
const MOCK_FALLBACKS = {
  systemHistory: Array.from({ length: 24 }, (_, i) => ({
    timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
    stability: 85 + Math.random() * 10,
    performance: 0.8 + Math.random() * 0.15,
    attention: 0.7 + Math.random() * 0.25
  })),
  scenarios: [
    { id: "S1", name: "Global Market Expansion", type: "strategic", probability: 0.65, status: "simulating", impact_score: 92, process_links: 1422, description: "Analyzing the impact of entering the EU market.", last_calculation: new Date().toISOString() },
    { id: "S2", name: "Standard Growth Path", type: "strategic", probability: 0.88, status: "anchored", impact_score: 15, process_links: 450, description: "Baseline projection with minimal risk.", last_calculation: new Date().toISOString() }
  ],
  kpis: [
    { label: "Monthly Revenue", value: "$45,210", change: 12.5, trend: "up" },
    { label: "Operating Efficiency", value: "94.2%", change: -2.1, trend: "down" },
    { label: "New Leads", value: "142", change: 8.4, trend: "up" },
    { label: "Churn Rate", value: "0.8%", change: 0, trend: "neutral" }
  ],
  businessWorkflows: [
    { id: "WF1", name: "Invoicing Optimization", status: "active", efficiency: 94, steps_completed: 4, total_steps: 6, last_run: new Date().toISOString() },
    { id: "WF2", name: "Lead Generation Relay", status: "active", efficiency: 88, steps_completed: 2, total_steps: 5, last_run: new Date().toISOString() },
    { id: "WF3", name: "Expense Reconciliation", status: "completed", efficiency: 99, steps_completed: 8, total_steps: 8, last_run: new Date().toISOString() }
  ]
};

/**
 * Derive system state from the real /dashboard/status endpoint.
 * No backend route exists for /system/state — this uses the existing health check instead.
 */
export async function fetchSystemState(entityId: string = "system_core"): Promise<SystemState> {
  try {
    const response = await authFetch(`${API_BASE_URL}/dashboard/status`);
    if (!response.ok) throw new Error("Backend offline");
    const status = await response.json();

    return {
      id: "system_core",
      entity_id: entityId,
      entity_type: "ai_system",
      state_type: status.status === "active" ? "active" : "degraded",
      attention_focus: { current: "System Core" },
      stability_level: status.status === "active" ? 0.95 : 0.7,
      introspection_depth: 0.85,
      emotional_state: { mood: "focused" },
      load_level: status.active_agents ?? 0,
      creativity_level: 0.8,
      memory_integration_status: "stable",
      coherence_level: 0.95,
      model_accuracy: 0.99,
      stability_score: status.status === "active" ? 98.4 : 75.0,
      updated_at: status.last_update || new Date().toISOString()
    };
  } catch (error) {
    console.warn("Backend offline — using default system state");
    return {
      id: "offline",
      entity_id: entityId,
      entity_type: "ai_system",
      state_type: "active",
      attention_focus: { current: "System Core" },
      stability_level: 0.92,
      introspection_depth: 0.85,
      emotional_state: { mood: "focused" },
      load_level: 0,
      creativity_level: 0.8,
      memory_integration_status: "stable",
      coherence_level: 0.95,
      model_accuracy: 0.99,
      stability_score: 98.4,
      updated_at: new Date().toISOString()
    };
  }
}

/**
 * Derive scenario status from the real /health endpoint.
 * No backend route exists for /scenario/status — this uses the existing health check.
 */
export async function fetchScenarioStatus(domain: string = "primary"): Promise<ScenarioStatus> {
  try {
    const response = await authFetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();

    const isHealthy = data.status === "healthy";
    return {
      domain,
      stability_score: isHealthy ? 99.9 : 70.0,
      stability_index: isHealthy ? 99.4 : 65.0,
      anchoring_strength: isHealthy ? 95.2 : 60.0,
      integrity_score: isHealthy ? 98.7 : 55.0,
      current_status: isHealthy ? "stable" : "degraded",
      next_check_due: new Date(Date.now() + 60000).toISOString()
    };
  } catch (error) {
    return {
      domain,
      stability_score: 0,
      stability_index: 0,
      anchoring_strength: 0,
      integrity_score: 0,
      current_status: "offline",
      next_check_due: new Date().toISOString()
    };
  }
}

/**
 * Fetch real system metrics from /health endpoint (FI3 fix).
 * Returns CPU, memory, disk, uptime, and health status from the backend.
 */
export async function fetchSystemMetrics(): Promise<{
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_watchers: number;
  tasks_processed: number;
  uptime_hours: number;
  last_sync: string;
  health_status: 'healthy' | 'degraded' | 'critical';
}> {
  try {
    const [healthRes, statusRes] = await Promise.all([
      authFetch(`${API_BASE_URL}/health`),
      authFetch(`${API_BASE_URL}/dashboard/status`)
    ]);

    const health = healthRes.ok ? await healthRes.json() : null;
    const dashStatus = statusRes.ok ? await statusRes.json() : null;

    return {
      cpu_usage: health?.metrics?.cpu_usage ?? 0,
      memory_usage: health?.metrics?.memory_usage ?? 0,
      disk_usage: health?.metrics?.disk_usage ?? 0,
      active_watchers: dashStatus?.active_agents ?? 0,
      tasks_processed: dashStatus?.tasks_processed_today ?? 0,
      uptime_hours: (health?.metrics?.uptime_seconds ?? 0) / 3600,
      last_sync: health?.timestamp ?? new Date().toISOString(),
      health_status: health?.status === "healthy" ? "healthy" : "degraded"
    };
  } catch {
    return {
      cpu_usage: 0, memory_usage: 0, disk_usage: 0,
      active_watchers: 0, tasks_processed: 0, uptime_hours: 0,
      last_sync: new Date().toISOString(), health_status: "critical"
    };
  }
}

export async function fetchDashboardData(): Promise<DashboardData> {
  try {
    const [vaultSummary, statusRes, system, scenarios] = await Promise.all([
      fetchVaultSummary(),
      authFetch(`${API_BASE_URL}/dashboard/status`).then(r => {
        if (!r.ok) throw new Error("Backend offline");
        return r.json();
      }).catch(() => null),
      fetchSystemState(),
      fetchScenarioStatus()
    ]);

    // If the main API didn't respond, this is mock data
    const isLive = statusRes !== null;
    const status = statusRes ?? {};

    const pendingApprovals = vaultSummary?.pending_approvals ?? status.pending_approvals ?? 0;
    const pendingTasks = vaultSummary?.pending_tasks ?? status.pending_tasks ?? 0;

    return {
      system,
      scenarios,
      tasks: {
        pending_count: pendingApprovals + pendingTasks,
        pending_approvals: pendingApprovals,
        completed_today: vaultSummary?.completed_tasks ?? status.tasks_processed_today ?? 0,
        active_chains: status.active_agents ?? 0
      },
      health: {
        status: isLive && status.status === "active" ? "healthy" : "warning",
        uptime: status.system_uptime || "0m",
        version: "System v2.0"
      },
      dataSource: isLive ? "live" : "mock"
    };
  } catch (error) {
    const vaultSummary = await fetchVaultSummary();
    return {
      system: await fetchSystemState(),
      scenarios: await fetchScenarioStatus(),
      tasks: {
        pending_count: (vaultSummary?.pending_approvals ?? 0) + (vaultSummary?.pending_tasks ?? 0),
        pending_approvals: vaultSummary?.pending_approvals ?? 0,
        completed_today: vaultSummary?.completed_tasks ?? 0,
        active_chains: 0
      },
      health: { status: "warning", uptime: "0m", version: "System v2.0" },
      dataSource: "mock"
    };
  }
}

export async function fetchTasks(): Promise<Task[]> {
  try {
    const response = await authFetch(`${API_BASE_URL}/dashboard/tasks`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();
    
    return data.recent_tasks.map((t: any) => ({
      id: t.id,
      type: t.category,
      from: t.task_metadata?.source || "System",
      priority: t.priority === "high" ? "high" : "medium",
      status: t.status,
      created: t.created_at,
      subject: t.title,
      content: t.description,
      suggested_actions: ["Analyze", "Execute", "Archive"]
    }));
  } catch (error) {
    return [
      { id: "EMAIL_123", type: "email", from: "investor@example.com", priority: "high", status: "pending", created: new Date().toISOString(), subject: "Investment Opportunity", content: "Discussing System rollout.", suggested_actions: ["Draft reply"] }
    ] as Task[];
  }
}

export async function fetchApprovals(): Promise<ApprovalRequest[]> {
  try {
    const response = await authFetch(`${API_BASE_URL}/approvals/pending`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();
    
    return data.map((a: any) => ({
      id: a.id,
      type: "approval_request",
      action: a.title,
      recipient: a.task_metadata?.recipient || "N/A",
      reason: a.description,
      created: a.created_at,
      expires: new Date(Date.now() + 86400000).toISOString(),
      status: "pending",
      details: a.task_metadata?.details || "No details provided."
    }));
  } catch (error) {
    return [] as ApprovalRequest[];
  }
}

export async function fetchActivityLog(limit: number = 20): Promise<any[]> {
  try {
    const response = await authFetch(`${API_BASE_URL}/dashboard/activity?limit=${encodeURIComponent(String(limit))}`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();
    return (data.activities || []) as any[];
  } catch (error) {
    return [] as any[];
  }
}

export async function fetchCommunications(): Promise<Communication[]> {
  try {
    const response = await authFetch(`${API_BASE_URL}/communication/conversations`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();

    return (data.conversations || []).map((conv: any) => {
      const channelRaw = (conv.original_channel || "").toLowerCase();
      const platformMap: Record<string, Communication["platform"]> = {
        email: "email",
        whatsapp: "whatsapp",
        twitter: "twitter",
        slack: "slack",
        linkedin: "linkedin",
        facebook: "facebook",
        instagram: "instagram",
      };
      const platform = platformMap[channelRaw] || "email";

      const responses: any[] = conv.responses || [];
      const lastResp = responses[responses.length - 1];

      const history: Message[] = responses.map((r: any, idx: number) => ({
        id: r.id || `msg_${idx}`,
        sender: r.sender || "Unknown",
        content: r.content || "",
        timestamp: r.timestamp || conv.last_activity,
        is_ai: (r.sender || "").toUpperCase() === "ELYX",
      }));

      return {
        id: conv.id,
        platform,
        contact_name: conv.original_sender || "Unknown",
        contact_identifier: conv.original_sender || "",
        last_message: lastResp?.content || conv.context_summary || "No messages yet",
        last_timestamp: conv.last_activity || conv.created_at,
        unread_count: 0,
        sentiment_score: 0,
        status: conv.active ? "active" : "archived",
        history,
      } as Communication;
    });
  } catch (error) {
    console.warn("Using mock communications");
    return [
      { id: "COM_1", platform: "email", contact_name: "John Doe", contact_identifier: "john@example.com", last_message: "The proposal looks solid.", last_timestamp: new Date().toISOString(), unread_count: 0, sentiment_score: 0.85, status: "active", history: [] }
    ] as Communication[];
  }
}

export async function sendMessage(
  conversationId: string,
  platform: string,
  recipient: string,
  content: string,
  subject?: string,
): Promise<{ success: boolean; error?: string }> {
  const channelMap: Record<string, string> = {
    email: "EMAIL",
    whatsapp: "WHATSAPP",
    twitter: "TWITTER",
    slack: "EMAIL",
    linkedin: "LINKEDIN",
    facebook: "FACEBOOK",
    instagram: "INSTAGRAM",
  };

  try {
    const apiKey = process.env.NEXT_PUBLIC_ELYX_API_KEY || "";
    const response = await authFetch(`${API_BASE_URL}/communication/send-response`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({
        original_message_id: conversationId,
        channel: channelMap[platform] || "EMAIL",
        recipient_identifier: recipient,
        content,
        response_type: "INFORMATIONAL",
        priority: "MEDIUM",
        requires_approval: false,
        ...(subject ? { subject } : {}),
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      return { success: false, error: err.detail || `Send failed (${response.status})` };
    }

    return { success: true };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

export async function fetchTransactions(): Promise<Transaction[]> {
  try {
    const response = await authFetch(`${API_BASE_URL}/finance/transactions?limit=25&include_expenses=true`);
    if (!response.ok) throw new Error("Finance API offline");
    const data = await response.json();
    return (data.transactions || []) as Transaction[];
  } catch (error) {
    console.warn("Using mock transactions");
    return [
      { id: "T1", type: "income", amount: 4500.00, category: "Services", merchant: "Client A", date: new Date().toISOString(), status: "completed" }
    ] as Transaction[];
  }
}

export async function fetchKPIs(): Promise<KPI[]> {
  try {
    const response = await authFetch(`${API_BASE_URL}/finance/kpis`);
    if (!response.ok) throw new Error("Finance API offline");
    const data = await response.json();
    return (data.kpis || []) as KPI[];
  } catch (error) {
    console.warn("Using mock KPIs");
    return MOCK_FALLBACKS.kpis as KPI[];
  }
}

export async function fetchWorkflows(): Promise<BusinessWorkflow[]> {
  return MOCK_FALLBACKS.businessWorkflows as BusinessWorkflow[];
}


export async function fetchSystemHistory(): Promise<SystemHistory[]> {
  return MOCK_FALLBACKS.systemHistory as SystemHistory[];
}

export async function fetchScenarios(): Promise<Scenario[]> {
  return MOCK_FALLBACKS.scenarios as Scenario[];
}

export async function fetchWorkflowTasks(): Promise<WorkflowTask[]> {
  return [
    { id: "TT1", title: "Quarterly Financial Analysis Sync", scheduled_time: new Date(Date.now() + 3600000).toISOString(), workflow: "primary", priority: "high", status: "scheduled", impact_coefficient: 0.88 }
  ] as WorkflowTask[];
}

export async function fetchUserPreferences(): Promise<any[]> {
  try {
    const response = await authFetch(`${API_BASE_URL}/dashboard/preferences`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();
    return data.preferences;
  } catch (error) {
    console.warn("Using mock preferences");
    return [
      { preference_key: "communication_whatsapp", preference_value: "true", preference_type: "communication" },
      { preference_key: "workflow_verification", preference_value: "true", preference_type: "operational" },
      { preference_key: "system_projection", preference_value: "true", preference_type: "behavioral" }
    ];
  }
}

export async function updateUserPreference(key: string, value: any, type: string = "operational"): Promise<void> {
  try {
    const response = await authFetch(`${API_BASE_URL}/dashboard/preferences`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: "demo_user@example.com",
        preference_key: key,
        preference_value: value,
        preference_type: type
      })
    });
    if (!response.ok) throw new Error("Failed to update preference");
  } catch (error) {
    console.error("Error updating preference:", error);
    throw error;
  }
}

export async function fetchAnalytics(timeframe: string = "week"): Promise<any> {
  try {
    const response = await authFetch(`${API_BASE_URL}/dashboard/analytics?timeframe=${timeframe}`);
    if (!response.ok) throw new Error("Backend offline");
    return await response.json();
  } catch (error) {
    console.warn("Using mock analytics data");
    return {
      timeframe: timeframe,
      metrics: {
        tasks_processed: 1422,
        approvals_granted: 88,
        average_response_time: 12.5,
        success_rate: 98.2,
        user_satisfaction: 94.5,
        task_completion_by_category: {
          email: 450,
          file: 280,
          calendar: 150,
          crm: 320,
          custom: 222
        },
        communication_stats: {
          whatsapp: 850,
          linkedin: 420,
          email: 1200,
          internal: 300
        },
        engagement_by_hour: Array.from({ length: 24 }, (_, i) => ({
          hour: i,
          engagement: 20 + Math.random() * 80
        }))
      },
      trends: {
        improving: true,
        percentage_change: 12.5
      }
    };
  }
}

export async function fetchTeamMembers(): Promise<any[]> {
  try {
    const response = await authFetch(`${API_BASE_URL}/users`);
    if (!response.ok) throw new Error("Backend offline");
    return await response.json();
  } catch (error) {
    console.warn("Using mock team data", error);
    return [
      {
        id: "1",
        name: "Usman Mustafa",
        email: "usman@elyx.ai",
        role: "System Architect",
        status: "active",
        last_active: new Date().toISOString(),
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Usman",
        permissions: ["admin", "system_core_access", "data_integrity_check"]
      },
      {
        id: "2",
        name: "Sarah Chen",
        email: "sarah@elyx.ai",
        role: "Workflow Operator",
        status: "active",
        last_active: new Date().toISOString(),
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        permissions: ["task_management", "audit_log"]
      }
    ];
  }
}

export async function deleteTeamMember(id: string): Promise<boolean> {
  try {
    const response = await authFetch(`${API_BASE_URL}/users/${id}`, { method: 'DELETE' });
    return response.ok;
  } catch (error) {
    return false;
  }
}

export async function saveOnboardingData(data: {
  user_id: string;
  anthropic_key?: string;
  selected_channels: string[];
}): Promise<boolean> {
  try {
    const response = await authFetch(`${API_BASE_URL}/settings/onboard`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.ok;
  } catch (error) {
    console.error("Onboarding save failed", error);
    return false;
  }
}

export async function fetchOnboardingStatus(userId: string): Promise<boolean> {
  try {
    const response = await authFetch(`${API_BASE_URL}/settings/status/${userId}`);
    if (!response.ok) return false;
    const data = await response.json();
    return data.onboarded;
  } catch (error) {
    return true; // Fallback to true if backend is down to avoid blocking user
  }
}

// Vault API Functions (for Tasks and Approvals pages)
const VAULT_API_BASE = "http://localhost:8080/api/vault";

export async function fetchVaultSummary(): Promise<{ pending_tasks: number; pending_approvals: number; completed_tasks: number } | null> {
  try {
    const response = await authFetch(`${VAULT_API_BASE}/summary`);
    if (!response.ok) return null;
    const data = await response.json();
    return {
      pending_tasks: data.pending_tasks ?? 0,
      pending_approvals: data.pending_approvals ?? 0,
      completed_tasks: data.completed_tasks ?? 0
    };
  } catch {
    return null;
  }
}

export async function fetchVaultTasks(folder: string = "Needs_Action"): Promise<Task[]> {
  try {
    const response = await authFetch(`${VAULT_API_BASE}/tasks?folder=${folder}`);
    if (!response.ok) throw new Error("Vault API offline");
    const data = await response.json();
    
    return (data.tasks || []).map((t: any) => ({
      id: t.id,
      filename: t.filename,
      type: t.type || "unknown",
      from: t.from || "Unknown",
      priority: t.priority || "medium",
      status: t.status || "pending",
      created: t.created || t.frontmatter?.created,
      subject: t.subject || "No Subject",
      content: t.content || "",
      suggested_actions: ["View Details"]
    }));
  } catch (error) {
    console.warn("Using mock vault tasks");
    return [] as Task[];
  }
}

export async function approveVaultTask(filename: string): Promise<boolean> {
  try {
    const response = await authFetch(`${VAULT_API_BASE}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename })
    });
    const data = await response.json();
    return data.success === true;
  } catch (error) {
    console.error("Approve task failed:", error);
    return false;
  }
}

export async function rejectVaultTask(filename: string): Promise<boolean> {
  try {
    const response = await authFetch(`${VAULT_API_BASE}/reject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename })
    });
    const data = await response.json();
    return data.success === true;
  } catch (error) {
    console.error("Reject task failed:", error);
    return false;
  }
}

export async function completeVaultTask(filename: string): Promise<boolean> {
  try {
    const response = await authFetch(`${VAULT_API_BASE}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename })
    });
    const data = await response.json();
    return data.success === true;
  } catch (error) {
    console.error("Complete task failed:", error);
    return false;
  }
}

export async function fetchVaultApprovals(): Promise<ApprovalRequest[]> {
  try {
    const response = await authFetch(`${VAULT_API_BASE}/approvals`);
    if (!response.ok) throw new Error("Vault API offline");
    const data = await response.json();
    
    return (data.approvals || []).map((a: any) => ({
      id: a.id,
      type: "approval_request",
      action: a.frontmatter?.action === "process_task" ? "Process task" : (a.frontmatter?.action || "Action Required"),
      recipient: a.from || a.frontmatter?.recipient || "N/A",
      reason: a.frontmatter?.reason || a.content?.slice?.(0, 200) || "Review required",
      created: a.created || a.frontmatter?.created,
      expires: new Date(Date.now() + 86400000).toISOString(),
      status: "pending",
      details: a.content,
      filename: a.filename
    }));
  } catch (error) {
    console.warn("Using mock vault approvals");
    return [] as ApprovalRequest[];
  }
}

// Settings API Functions (Feature Flags)
const SETTINGS_API_BASE = "http://localhost:8081/api/settings";

export interface FeatureFlag {
  name: string;
  value: boolean;
  default: boolean;
  type: string;
  description: string;
  category: string;
}

export async function fetchFeatureFlags(): Promise<FeatureFlag[]> {
  try {
    const response = await authFetch(`${SETTINGS_API_BASE}/flags`);
    if (!response.ok) throw new Error("Settings API offline");
    const data = await response.json();
    return data.flags || [];
  } catch (error) {
    console.warn("Using mock feature flags");
    return [
      { name: "ENABLE_ANALYTICS", value: true, default: true, type: "boolean", description: "Enable analytics", category: "features" },
      { name: "ENABLE_LEARNING", value: true, default: true, type: "boolean", description: "Enable learning", category: "features" },
      { name: "ENABLE_CALENDAR_INTEGRATION", value: false, default: false, type: "boolean", description: "Enable calendar", category: "integrations" },
      { name: "ENABLE_AUDIT_LOGGING", value: true, default: true, type: "boolean", description: "Enable audit logging", category: "security" },
      { name: "ENABLE_ACTION_SIGNING", value: true, default: true, type: "boolean", description: "Enable action signing", category: "security" }
    ] as FeatureFlag[];
  }
}

export async function updateFeatureFlag(flag: string, value: boolean): Promise<boolean> {
  try {
    const response = await authFetch(`${SETTINGS_API_BASE}/flags`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ flag, value })
    });
    const data = await response.json();
    return data.success === true;
  } catch (error) {
    console.error("Update flag failed:", error);
    return false;
  }
}

export async function fetchAllSettings(): Promise<any> {
  try {
    const response = await authFetch(`${SETTINGS_API_BASE}/all`);
    if (!response.ok) throw new Error("Settings API offline");
    return await response.json();
  } catch (error) {
    console.warn("Using mock settings");
    return {};
  }
}
