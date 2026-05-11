import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { storage } from '../lib/storage';
import type { Profile } from '../lib/storage';

export default function AdminPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [initialWeight, setInitialWeight] = useState('');
  const [prizePool, setPrizePool] = useState('');
  const [msg, setMsg] = useState('');

  const config = storage.getConfig();

  useEffect(() => {
    setProfiles(storage.getProfiles());
    setPrizePool(String(config.prizePool));
  }, []);

  const addProfile = (e: React.FormEvent) => {
    e.preventDefault();
    const w = parseFloat(initialWeight);
    if (!name.trim() || !password.trim() || !w || w <= 0) {
      setMsg('请填写完整信息');
      return;
    }
    try {
      storage.createProfile(name.trim(), password.trim(), w);
      setProfiles(storage.getProfiles());
      setName('');
      setPassword('');
      setInitialWeight('');
      setMsg('添加成功！');
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : '添加失败');
    }
    setTimeout(() => setMsg(''), 2000);
  };

  const removeProfile = (id: string) => {
    storage.removeProfile(id);
    setProfiles(storage.getProfiles());
  };

  const updatePrize = () => {
    const v = parseFloat(prizePool);
    if (v >= 0) {
      storage.updateConfig({ prizePool: v });
      setMsg('奖金池已更新');
      setTimeout(() => setMsg(''), 2000);
    }
  };

  const resetAll = () => {
    if (confirm('确定要重置所有数据？此操作不可恢复！')) {
      storage.resetAll();
      setProfiles([]);
      setPrizePool('1000');
      setMsg('已全部重置');
      setTimeout(() => setMsg(''), 2000);
    }
  };

  return (
    <div>
      <Link to="/" className="back-link">← 返回首页</Link>
      <h1 className="page-title">⚙️ 管理面板</h1>
      <p className="page-subtitle">管理参赛者和比赛设置</p>

      {/* add participant */}
      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: '#888' }}>➕ 添加参赛者</h3>
        <form onSubmit={addProfile}>
          <div className="form-group">
            <label className="form-label">姓名</label>
            <input className="form-input" value={name} onChange={(e) => setName(e.target.value)} placeholder="昵称" />
          </div>
          <div className="form-group">
            <label className="form-label">密码</label>
            <input className="form-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="登录密码" />
          </div>
          <div className="form-group">
            <label className="form-label">初始体重 (kg)</label>
            <input className="form-input" type="number" value={initialWeight} onChange={(e) => setInitialWeight(e.target.value)} placeholder="如 80" step="0.1" />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>添加参赛者</button>
        </form>
        {msg && <p style={{ textAlign: 'center', marginTop: 10, fontSize: 13, color: msg.includes('成功') ? '#81C784' : '#e57373' }}>{msg}</p>}
      </div>

      {/* prize pool */}
      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: '#888' }}>💰 奖金池设置</h3>
        <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <label className="form-label">总奖金 (元)</label>
            <input className="form-input" type="number" value={prizePool} onChange={(e) => setPrizePool(e.target.value)} placeholder="如 1000" />
          </div>
          <button className="btn btn-primary btn-small" onClick={updatePrize}>保存</button>
        </div>
        <p style={{ fontSize: 12, color: '#c0b0b0', marginTop: 8 }}>虚拟金额，仅用于计算分配比例</p>
      </div>

      {/* participant list */}
      {profiles.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: '#888' }}>👥 参赛者 ({profiles.length})</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {profiles.map((p) => (
              <div key={p.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f5f0f0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div className="avatar" style={{ background: p.avatarColor, width: 36, height: 36, fontSize: 15 }}>{p.name.charAt(0)}</div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600 }}>{p.name}</div>
                    <div style={{ fontSize: 12, color: '#b0a0a0' }}>初始 {p.initialWeight}kg</div>
                  </div>
                </div>
                <button className="btn btn-danger btn-small" onClick={() => removeProfile(p.id)}>移除</button>
              </div>
            ))}
          </div>
        </div>
      )}

      <button className="btn btn-danger" style={{ width: '100%' }} onClick={resetAll}>
        🔄 重置比赛
      </button>
    </div>
  );
}
