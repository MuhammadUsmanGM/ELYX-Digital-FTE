export interface SystemState {
  id: string;
  entity_id: string;
  entity_type: string;
  state_type: string;
  attention_focus: Record<string, any>;
  stability_level: number;
  introspection_depth: number;
  emotional_state: Record<string, any>;
  load_level: number;
  creativity_level: number;
  memory_integration_status: string;
  coherence_level: number;
  model_accuracy: number;
  stability_score: number;
  updated_at: string;
}

export interface ScenarioStatus {
  domain: string;
  stability_score: number;
  stability_index: number;
  anchoring_strength: number;
  integrity_score: number;
  current_status: string;
  next_check_due: string;
}

export interface TaskStatus {
  pending_count: number;
  completed_today: number;
  active_chains: number;
}

export interface SystemHistory {
  timestamp: string;
  stability: number;
  performance: number;
  attention: number;
}

export interface DashboardData {
  system: SystemState;
  scenarios: ScenarioStatus;
  tasks: TaskStatus;
  health: {
    status: string;
    uptime: string;
    version: string;
  };
  /** Indicates whether data came from a live API or from fallback mocks */
  dataSource: "live" | "mock";
}

export interface Task {
  id: string;
  type: 'email' | 'whatsapp' | 'file_drop' | 'finance' | 'general';
  from: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  created: string;
  subject?: string;
  content: string;
  suggested_actions?: string[];
}

export interface ApprovalRequest {
  id: string;
  type: 'approval_request';
  action: string;
  amount?: number;
  recipient?: string;
  reason: string;
  created: string;
  expires: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  details: string;
}

export interface Message {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
  is_ai: boolean;
}

export interface Communication {
  id: string;
  platform: 'email' | 'whatsapp' | 'slack' | 'twitter' | 'linkedin' | 'facebook' | 'instagram';
  contact_name: string;
  contact_identifier: string;
  last_message: string;
  last_timestamp: string;
  unread_count: number;
  sentiment_score: number;
  status: 'active' | 'archived' | 'needs_reply';
  history: Message[];
}

export interface Transaction {
  id: string;
  type: 'income' | 'expense';
  amount: number;
  category: string;
  merchant: string;
  date: string;
  status: 'completed' | 'pending' | 'flagged';
}

export interface KPI {
  label: string;
  value: string;
  change: number;
  trend: 'up' | 'down' | 'neutral';
}

export interface BusinessWorkflow {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'completed';
  efficiency: number;
  steps_completed: number;
  total_steps: number;
  last_run: string;
}

export interface Scenario {
  id: string;
  name: string;
  type: 'business' | 'personal' | 'strategic' | 'financial';
  probability: number;
  status: 'simulating' | 'stable' | 'diverged' | 'anchored';
  impact_score: number;
  process_links: number;
  description: string;
  last_calculation: string;
}

export interface WorkflowTask {
  id: string;
  title: string;
  scheduled_time: string;
  workflow: 'primary' | 'simulated' | 'historical';
  priority: 'low' | 'medium' | 'high';
  status: 'scheduled' | 'running' | 'completed' | 'failed';
  impact_coefficient: number;
}
