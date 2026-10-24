export interface AgentInfo {
  name: string
  description: string
  model: string
  tools: string[]
  handoffs: string[]
}

export interface GuardrailResult {
  name: string
  passed: boolean
  reasoning: string | null
}

export interface AgentEvent {
  type: 'handoff' | 'tool_call' | 'tool_output'
  agent: string
  content: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  agent?: string
}
