import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('请在 .env 文件中配置 VITE_SUPABASE_URL 和 VITE_SUPABASE_ANON_KEY');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export type Profile = {
  id: string;
  name: string;
  initial_weight: number;
  avatar_color: string;
  is_admin: boolean;
  created_at: string;
};

export type WeightLog = {
  id: number;
  user_id: string;
  weight: number;
  logged_date: string;
  created_at: string;
};

export type Config = {
  key: string;
  value: string;
};
