// Interfaces para la aplicación MiMapa

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  oauth_provider: string;
  created_at: string;
  last_login: string;
}

export interface Marker {
  id: string;
  user_email: string;
  location_name: string;
  latitude: number;
  longitude: number;
  image_url?: string;
  description?: string;
  created_at: string;
}

export interface MarkerCreate {
  location_name: string;
  description?: string;
}

export interface UserMapResponse {
  user_email: string;
  user_name: string;
  markers: Marker[];
}

export interface AuthCallbackParams {
  token?: string;
  error?: string;
}

export interface Visit {
  id: string;
  visited_user_email: string;
  visitor_email: string;
  visitor_oauth_id: string;
  visited_at: string;
}
