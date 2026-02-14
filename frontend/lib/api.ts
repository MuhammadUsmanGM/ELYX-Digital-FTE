import { DashboardData, ConsciousnessState, RealityStatus, Task, ApprovalRequest, Communication, Transaction, KPI, BusinessWorkflow, ConsciousnessHistory, RealityScenario, TemporalTask } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// lib/api.ts

// Fallback Mock Data as required by the ELYX platform for seamless UI experience
const MOCK_FALLBACKS = {
  consciousnessHistory: Array.from({ length: 24 }, (_, i) => ({
    timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
    phi: 85 + Math.random() * 10,
    self_awareness: 0.8 + Math.random() * 0.15,
    attention: 0.7 + Math.random() * 0.25
  })),
  realityScenarios: [
    { id: "S1", name: "Global Market Expansion", type: "strategic", probability: 0.65, status: "simulating", impact_score: 92, causal_links: 1422, description: "Analyzing the impact of entering the EU market.", last_calculation: new Date().toISOString() },
    { id: "S2", name: "Standard Growth Path", type: "strategic", probability: 0.88, status: "anchored", impact_score: 15, causal_links: 450, description: "Baseline projection with minimal risk.", last_calculation: new Date().toISOString() }
  ],
  kpis: [
    { label: "Monthly Revenue", value: "$45,210", change: 12.5, trend: "up" },
    { label: "Operating Efficiency", value: "94.2%", change: -2.1, trend: "down" },
    { label: "New Leads", value: "142", change: 8.4, trend: "up" },
    { label: "Churn Rate", value: "0.8%", change: 0, trend: "neutral" }
  ]
};

export async function fetchConsciousnessState(entityId: string = "system_core"): Promise<ConsciousnessState> {
  try {
    const response = await fetch(`${API_BASE_URL}/consciousness/state/${entityId}`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();
    const state = data.consciousness_state;
    
    return {
      id: state.id || "system_core",
      entity_id: state.entity_id || entityId,
      entity_type: state.entity_type || "ai_system",
      state_type: state.state_type || "active",
      attention_focus: state.attention_focus || { current: "System Core" },
      self_awareness_level: state.self_awareness_level || 0.85,
      introspection_depth: state.introspection_depth || 0.7,
      emotional_state: state.emotional_state || { mood: "neutral" },
      cognitive_load: state.cognitive_load || 2.4,
      creativity_level: state.creativity_level || 0.6,
      memory_integration_status: state.memory_integration_status || "stable",
      attention_coherence: state.attention_coherence || 0.9,
      self_model_accuracy: state.self_model_accuracy || 0.95,
      phi: (data.consciousness_integrity_score || 9.8) * 10,
      updated_at: data.timestamp || new Date().toISOString()
    };
  } catch (error) {
    console.warn("Using mock consciousness state");
    return {
      id: "mock_id",
      entity_id: entityId,
      entity_type: "ai_system",
      state_type: "active",
      attention_focus: { current: "Market Volatility" },
      self_awareness_level: 0.92,
      introspection_depth: 0.85,
      emotional_state: { mood: "focused" },
      cognitive_load: 2.4,
      creativity_level: 0.8,
      memory_integration_status: "stable",
      attention_coherence: 0.95,
      self_model_accuracy: 0.99,
      phi: 98.4,
      updated_at: new Date().toISOString()
    };
  }
}

export async function fetchRealityStatus(domain: string = "primary"): Promise<RealityStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/reality/status/${domain}`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();
    
    return {
      domain: data.reality_domain || domain,
      current_score: (data.reality_coherence_score || 9.9) * 10,
      stability_index: (data.reality_stability_index || 9.9) * 10,
      anchoring_strength: (data.reality_anchoring_strength || 9.5) * 10,
      boundary_integrity: (data.boundary_integrity || 9.8) * 10,
      current_status: data.reality_status?.status || "stable",
      next_check_due: data.timestamp || new Date().toISOString()
    };
  } catch (error) {
    return {
      domain: domain,
      current_score: 99.98,
      stability_index: 99.4,
      anchoring_strength: 95.2,
      boundary_integrity: 98.7,
      current_status: "stable",
      next_check_due: new Date().toISOString()
    };
  }
}

export async function fetchDashboardData(): Promise<DashboardData> {
  try {
    const [statusRes, consciousness, reality] = await Promise.all([
      fetch(`${API_BASE_URL}/dashboard/status`).then(r => r.json()),
      fetchConsciousnessState(),
      fetchRealityStatus()
    ]);
    
    return {
      consciousness,
      reality,
      tasks: {
        pending_count: statusRes.pending_approvals || 0,
        completed_today: statusRes.tasks_processed_today || 0,
        active_chains: statusRes.active_agents || 0
      },
      health: {
        status: statusRes.status === "active" ? "healthy" : "warning",
        uptime: statusRes.system_uptime || "0m",
        version: "Neural v2.0"
      }
    };
  } catch (error) {
    // Fallback to full mock if backend is down
    return {
      consciousness: await fetchConsciousnessState(),
      reality: await fetchRealityStatus(),
      tasks: { pending_count: 3, completed_today: 14, active_chains: 5 },
      health: { status: "healthy", uptime: "14d 6h 22m", version: "Neural v2.0" }
    };
  }
}

export async function fetchTasks(): Promise<Task[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/dashboard/tasks`);
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
      { id: "EMAIL_123", type: "email", from: "investor@example.com", priority: "high", status: "pending", created: new Date().toISOString(), subject: "Investment Opportunity", content: "Discussing Neural Network rollout.", suggested_actions: ["Draft reply"] }
    ] as Task[];
  }
}

export async function fetchApprovals(): Promise<ApprovalRequest[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/approvals/pending`);
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

export async function fetchCommunications(): Promise<Communication[]> {
  // In a real system, this would fetch from /comms or /dashboard/interactions
  return [
    { id: "COM_1", platform: "email", contact_name: "John Doe", contact_identifier: "john@example.com", last_message: "The proposal looks solid.", last_timestamp: new Date().toISOString(), unread_count: 0, sentiment_score: 0.85, status: "active", history: [] }
  ] as Communication[];
}

export async function fetchTransactions(): Promise<Transaction[]> {
  return [
    { id: "T1", type: "income", amount: 4500.00, category: "Services", merchant: "Client A", date: new Date().toISOString(), status: "completed" }
  ] as Transaction[];
}

export async function fetchKPIs(): Promise<KPI[]> {
  return MOCK_FALLBACKS.kpis as KPI[];
}


export async function fetchConsciousnessHistory(): Promise<ConsciousnessHistory[]> {
  return MOCK_FALLBACKS.consciousnessHistory as ConsciousnessHistory[];
}

export async function fetchRealityScenarios(): Promise<RealityScenario[]> {
  return MOCK_FALLBACKS.realityScenarios as RealityScenario[];
}

export async function fetchTemporalTasks(): Promise<TemporalTask[]> {
  return [
    { id: "TT1", title: "Quarterly Financial Prophet Sync", scheduled_time: new Date(Date.now() + 3600000).toISOString(), timeline: "primary", priority: "high", status: "scheduled", impact_coefficient: 0.88 }
  ] as TemporalTask[];
}

export async function fetchUserPreferences(): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/dashboard/preferences`);
    if (!response.ok) throw new Error("Backend offline");
    const data = await response.json();
    return data.preferences;
  } catch (error) {
    console.warn("Using mock preferences");
    return [
      { preference_key: "communication_whatsapp", preference_value: "true", preference_type: "communication" },
      { preference_key: "workflow_causal_verification", preference_value: "true", preference_type: "operational" },
      { preference_key: "ai_temporal_projection", preference_value: "true", preference_type: "behavioral" }
    ];
  }
}

export async function updateUserPreference(key: string, value: any, type: string = "operational"): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/dashboard/preferences`, {
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
    const response = await fetch(`${API_BASE_URL}/dashboard/analytics?timeframe=${timeframe}`);
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
    const response = await fetch(`${API_BASE_URL}/users`);
    if (!response.ok) throw new Error("Backend offline");
    return await response.json();
  } catch (error) {
    console.warn("Using mock team data", error);
    return [
      {
        id: "1",
        name: "Usman Mustafa",
        email: "usman@elyx.ai",
        role: "Neural Architect",
        status: "active",
        last_active: new Date().toISOString(),
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Usman",
        permissions: ["admin", "neural_core_access", "reality_manipulation"]
      },
      {
        id: "2",
        name: "Sarah Chen",
        email: "sarah@elyx.ai",
        role: "Logic Operator",
        status: "active",
        last_active: new Date().toISOString(),
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        permissions: ["task_management", "temporal_audit"]
      }
    ];
  }
}

export async function deleteTeamMember(id: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${id}`, { method: 'DELETE' });
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
    const response = await fetch(`${API_BASE_URL}/settings/onboard`, {
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
    const response = await fetch(`${API_BASE_URL}/settings/status/${userId}`);
    if (!response.ok) return false;
    const data = await response.json();
    return data.onboarded;
  } catch (error) {
    return true; // Fallback to true if backend is down to avoid blocking user
  }
}
