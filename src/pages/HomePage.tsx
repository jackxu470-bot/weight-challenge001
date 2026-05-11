import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { storage } from '../lib/storage';
import type { Profile } from '../lib/storage';
import Leaderboard from '../components/Leaderboard';

export default function HomePage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [showLB, setShowLB] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setProfiles(storage.getProfiles());
  }, []);

  const handleClick = (p: Profile) => {
    navigate(`/login/${p.id}`);
  };

  const latestWeights = storage.getAllLatestWeights();

  return (
    <div>
      <h1 className="page-title">减肥挑战赛 🏆</h1>
      <p className="page-subtitle">点击你的名字开始记录</p>

      {profiles.length === 0 ? (
        <div className="card empty-state" style={{ marginTop: 24 }}>
          <p style={{ fontSize: 40, marginBottom: 12 }}>🍽️</p>
          <p>还没有参赛者</p>
          <p style={{ fontSize: 13, marginTop: 4 }}>点击下方「管理」添加</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 8 }}>
          {profiles.map((p) => {
            const latest = latestWeights.get(p.id);
            const loss = latest
              ? ((p.initialWeight - latest.weight) / p.initialWeight * 100).toFixed(1)
              : null;

            return (
              <div
                key={p.id}
                className="card participant-card"
                onClick={() => handleClick(p)}
              >
                <div className="avatar" style={{ background: p.avatarColor }}>
                  {p.name.charAt(0)}
                </div>
                <div className="participant-info">
                  <div className="participant-name">{p.name}</div>
                  <div className="participant-stats">
                    初始 {p.initialWeight}kg
                    {latest && (
                      <> · 当前 {latest.weight}kg · <span style={{ color: loss && parseFloat(loss) > 0 ? '#81C784' : '#e57373' }}>{loss && parseFloat(loss) > 0 ? '↓' : '↑'}{Math.abs(parseFloat(loss || '0'))}%</span></>
                    )}
                  </div>
                </div>
                <div style={{ color: '#d0c0c0', fontSize: 18 }}>›</div>
              </div>
            );
          })}
        </div>
      )}

      <div style={{ display: 'flex', gap: 12, marginTop: 24, justifyContent: 'center' }}>
        <button className="btn btn-primary" onClick={() => setShowLB(true)}>
          📊 排行榜
        </button>
        <button className="btn btn-secondary" onClick={() => navigate('/admin')}>
          ⚙️ 管理
        </button>
      </div>

      {showLB && <Leaderboard onClose={() => setShowLB(false)} />}
    </div>
  );
}
