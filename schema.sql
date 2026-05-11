-- 减肥挑战赛 Supabase 数据库建表 SQL
-- 在 Supabase SQL Editor 中执行此文件

-- 1. 参赛者资料表
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  initial_weight NUMERIC NOT NULL CHECK (initial_weight > 0),
  avatar_color TEXT NOT NULL DEFAULT '#F8A4A4',
  is_admin BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. 体重记录表
CREATE TABLE weight_logs (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  weight NUMERIC NOT NULL CHECK (weight > 0),
  logged_date DATE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(user_id, logged_date)
);

-- 3. 比赛配置表
CREATE TABLE config (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT INTO config (key, value) VALUES ('prize_pool', '1000');
INSERT INTO config (key, value) VALUES ('start_date', '');

-- 4. 开启 RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE weight_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE config ENABLE ROW LEVEL SECURITY;

-- 5. RLS 策略：profiles 所有人可读，管理员可写
CREATE POLICY "profiles_read_all" ON profiles FOR SELECT USING (true);
CREATE POLICY "profiles_insert_admin" ON profiles FOR INSERT WITH CHECK (is_admin = true OR (SELECT COUNT(*) FROM profiles) = 0);
CREATE POLICY "profiles_update_admin" ON profiles FOR UPDATE USING (is_admin = true);
CREATE POLICY "profiles_delete_admin" ON profiles FOR DELETE USING (is_admin = true);

-- 6. RLS 策略：weight_logs 所有人可读，每人只能改自己的
CREATE POLICY "logs_read_all" ON weight_logs FOR SELECT USING (true);
CREATE POLICY "logs_insert_own" ON weight_logs FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "logs_update_own" ON weight_logs FOR UPDATE USING (user_id = auth.uid());

-- 7. RLS 策略：config 所有人可读，管理员可改
CREATE POLICY "config_read_all" ON config FOR SELECT USING (true);
CREATE POLICY "config_write_admin" ON config FOR UPDATE USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_admin = true));

-- 8. 示例参赛者（可选）
-- INSERT INTO profiles (name, initial_weight, avatar_color) VALUES ('小明', 80.0, '#F8A4A4');
-- INSERT INTO profiles (name, initial_weight, avatar_color) VALUES ('小红', 65.0, '#A8E6CF');
-- INSERT INTO profiles (name, initial_weight, avatar_color) VALUES ('小刚', 90.0, '#FFD3B6');
