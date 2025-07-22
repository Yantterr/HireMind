export interface ShortChatResponse {
  id: number;
  title: string;
  is_archived: boolean;
  count_request_tokens: number;
  count_response_tokens: number;
  created_at: string;
  updated_at: string;
}

export interface MessageResponse {
  id: number;
  role: string;
  content: string;
  created_at: string;
}

export interface ChatResponse extends ShortChatResponse {
  messages: MessageResponse[];
}
