export interface ShortChatResponse {
  id: number;
  title: string;
  is_archived: boolean;
  updated_at: string; // обычно для дат используют строку в ISO формате
}

export interface MessageResponse {
  id: number;
  role: string;
  content: string;
  created_at: string;
}
export interface EventResponse {
  id: number;
  content: string;
}

export interface ChatResponse extends ShortChatResponse {
  total_count_request_tokens: number;
  total_count_response_tokens: number;
  current_count_request_tokens: number;
  current_event_chance: 0;
  created_at: string;
  queue_position: number;
  messages: MessageResponse[];
  events: EventResponse[];
}

export interface PaginatedResponseModel<T> {
  items: T[];
  page: number;
  per_page: number;
  total_items: number;
  total_pages: number;
}

export type PaginatedChatsResponse = PaginatedResponseModel<ShortChatResponse>;
