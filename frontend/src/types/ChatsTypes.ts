export type MessageRoles = 'user' | 'assistant' | 'system';

export interface Message {
  id: number;
  content: string;
  role: MessageRoles;
  createdAt: string;
}

export interface IEvent {
  id: number;
  content: string;
}

export interface IChat {
  id: number;
  title: string;
  messages: Message[];
  events: Event[];
  queue_position: number;
  created_at: string;
  updated_at: string;
}

export type TChats = Array<Omit<IChat, 'messages' | 'events'>>;

export interface ICreateChat {
  title: string;
  initial_context?: string;
  progression_type: number;
  difficulty: number;
  politeness: number;
  friendliness: number;
  rigidity: number;
  detail_orientation: number;
  pacing: number;
  language: number;
}
