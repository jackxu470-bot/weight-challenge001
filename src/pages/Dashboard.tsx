import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { storage } from '../lib/storage';
import type { Profile, WeightLog } from '../lib/storage';
import WeightChart from '../components/WeightChart';

export default function Dashboard() {
  const { userId } = useParams<{ userId: string }>();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [logs, setLogs] = useState<WeightLog[]>([]);
  const [weight, setWeight] = useState('');
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [msg, setMsg] = useState('');

  useEffect(() => {
    const p = storage.getProfileById(userId!);
    setProfile(p || null);
    if (p) setLogs(storage.getLogsByUser(p.id));
  }, [userId]);

  if (!profile) {
    return (
      <div>
        <Link to="/" className="back-link">← 返回</Link>
        <div className="card empty-state"><p>找不到参赛者</p></div>
      </div>
    );
  }

  const latest = logs[0];
  const lossPct = latest
    ? ((profile.initialWeight - latest.weight) / profile.initialWeight * 100).toFixed(1)
    : null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const w = parseFloat(weight);
    if (!w || w <= 0) { setMsg('请输入有效体重'); return; }
    storage.addWeightLog(profile.id, w, date);
    setLogs(storage.getLogsByUser(profile.id));
    setWeight('');
    setMsg('记录成功！');
    setTimeout(() => setMsg(''), 2000);
  };

  return (
    <div>
      <Link to="/" className="back-link">← 返回首页</Link>

      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <div className="avatar" style={{ background: profile.avatarColor, margin: '0 auto 12px', width: 56, height: 56, fontSize: 24 }}>
          {profile.name.charAt(0)}
        </div>
        <h1 className="page-title" style={{ marginBottom: 4 }}>{profile.name}</h1>
        <p className="page-subtitle" style={{ marginBottom: 0 }}>
          初始体重 {profile.initialWeight}kg
          {lossPct && <> · 变化 <span style={{ color: parseFloat(lossPct) > 0 ? '#81C784' : '#e57373', fontWeight: 600 }}>{parseFloat(lossPct) > 0 ? '↓' : '↑'}{Math.abs(parseFloat(lossPct))}%</span></>}
        </p>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
            <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
              <label className="form-label">体重 (kg)</label>
              <input
                type="number"
                className="form-input"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
                placeholder="如 70.5"
                step="0.1"
                min="0"
              />
            </div>
            <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
              <label className="form-label">日期</label>
              <input
                type="date"
                className="form-input"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ padding: '12px 20px' }}>
              记录
            </button>
          </div>
          {msg && <p style={{ textAlign: 'center', marginTop: 10, fontSize: 13, color: msg.includes('成功') ? '#81C784' : '#e57373' }}>{msg}</p>}
        </form>
      </div>

      {logs.length > 1 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: '#888' }}>📈 体重趋势</h3>
          <WeightChart logs={logs} initialWeight={profile.initialWeight} />
        </div>
      )}

      <div className="card">
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: '#888' }}>📋 历史记录</h3>
        {logs.length === 0 ? (
          <p className="empty-state" style={{ padding: '20px 0' }}>还没有记录，开始记录你的体重吧</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {logs.map((l) => (
              <div key={l.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f5f0f0', fontSize: 14 }}>
                <span style={{ color: '#b0a0a0' }}>{l.loggedDate}</span>
                <span style={{ fontWeight: 600 }}>{l.weight} kg</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
