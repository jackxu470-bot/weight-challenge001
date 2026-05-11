import { useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { storage } from '../lib/storage';

export default function LoginPage() {
  const { userId } = useParams<{ userId: string }>();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const profile = storage.getProfileById(userId!);
  if (!profile) {
    return (
      <div>
        <Link to="/" className="back-link">← 返回</Link>
        <div className="card empty-state">
          <p>找不到该参赛者</p>
        </div>
      </div>
    );
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const result = storage.verifyLogin(profile.name, password);
    if (result) {
      navigate(`/dashboard/${result.id}`);
    } else {
      setError('密码错误');
    }
  };

  return (
    <div>
      <Link to="/" className="back-link">← 返回</Link>
      <h1 className="page-title">🔐</h1>
      <p className="page-subtitle" style={{ marginBottom: 8 }}>你好，{profile.name}</p>

      <div className="card" style={{ marginTop: 16 }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">输入密码</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setError(''); }}
              placeholder="请输入密码"
              autoFocus
            />
            {error && <p style={{ color: '#e57373', fontSize: 13, marginTop: 6 }}>{error}</p>}
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: 8 }}>
            进入我的记录
          </button>
        </form>
      </div>
    </div>
  );
}
