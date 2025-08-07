export interface NewChatRequest {
  title: string;
  initial_context: string;
  progression_type: number;
  difficulty: number;
  politeness: number;
  friendliness: number;
  rigidity: number;
  detail_orientation: number;
  pacing: number;
  language: number;
}

export interface NewMessageRequest {
  role: 'user';
  content: string;
}
