import { storage } from '../lib/storage';
import PrizeDisplay from './PrizeDisplay';

type Props = { onClose: () => void };

const TITLES = ['至尊瘦皇 👑', '亚军达人 🥈', '季军新星 🥉', '减重勇士 💪', '减重勇士 💪', '减重勇士 💪'];

export default function Leaderboard({ onClose }: Props) {
  const profiles = storage.getProfiles();
  const latestWeights = storage.getAllLatestWeights();
  const config = storage.getConfig();

  const ranked = profiles
    .map((p) => {
      const latest = latestWeights.get(p.id);
      const lossPct = latest
        ? ((p.initialWeight - latest.weight) / p.initialWeight * 100)
        : 0;
      return { ...p, latestWeight: latest?.weight ?? null, lossPct };
    })
    .sort((a, b) => b.lossPct - a.lossPct);

  return (
    <div className="overlay" onClick={onClose}>
      <div className="overlay-card" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>📊 排行榜</h2>
          <button className="btn btn-secondary btn-small" onClick={onClose}>关闭</button>
        </div>

        {ranked.length === 0 ? (
          <div className="empty-state"><p>暂无参赛者</p></div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
            {ranked.map((p, i) => (
              <div key={p.id} style={{
                display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px',
                borderRadius: 16, background: i === 0 ? 'linear-gradient(135deg, #fff9e6, #fff3cd)' : '#faf8f8'
              }}>
                <div style={{ fontSize: 22, fontWeight: 700, color: i < 3 ? ['#f0c040', '#c0c0c0', '#cd7f32'][i] : '#ccc', width: 32, textAlign: 'center' }}>
                  {i + 1}
                </div>
                <div className="avatar" style={{ background: p.avatarColor, width: 40, height: 40, fontSize: 16 }}>
                  {p.name.charAt(0)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 15, fontWeight: 600 }}>{p.name}</div>
                  <div style={{ fontSize: 12, color: '#b0a0a0' }}>
                    {p.latestWeight ? `${p.latestWeight}kg` : '未记录'} ·
                    初始 {p.initialWeight}kg
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: p.lossPct > 0 ? '#81C784' : '#e57373' }}>
                    {p.lossPct > 0 ? '↓' : p.lossPct < 0 ? '↑' : '—'}{Math.abs(p.lossPct).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: 11, color: '#b0a0a0' }}>{TITLES[i] || TITLES[TITLES.length - 1]}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        <PrizeDisplay ranked={ranked} prizePool={config.prizePool} />
      </div>
    </div>
  );
}
