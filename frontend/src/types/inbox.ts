export interface InboxItem {
  id: number;
  event_type: string;
  site: string;
  asset_id: number | null;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface InboxResponse {
  unread_count: number;
  items: InboxItem[];
}
