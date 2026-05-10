import streamlit as st
import sqlite3
import hashlib
from datetime import date

st.set_page_config(page_title='减肥挑战赛', page_icon='🏆', layout='centered')

# ── Custom CSS ────────────────────────────────────────────
st.markdown('''
<style>
    .stApp {
        background: linear-gradient(170deg, #fef5f5 0%, #fce4ec 35%, #f3e5f5 100%);
    }
    .block-container {
        padding: 2rem 1rem 1.5rem 1rem !important;
    }
    .stButton button {
        border-radius: 12px !important;
        font-weight: 550 !important;
        border: none !important;
        background: #fdf0ed !important;
        padding: 5px 0 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
        color: #c0978e !important;
    }
    .stButton button:hover {
        background: #f9e2dc !important;
        color: #b07e74 !important;
    }
    .stButton button:active {
        transform: scale(0.97) !important;
    }
</style>
''', unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────
COLORS = ['#F8A4A4', '#A8E6CF', '#FFD3B6', '#D5AAFF', '#87CEEB', '#FFB7B2', '#B5EAD7', '#C7CEEA']
TITLES = ['至尊瘦皇 👑', '亚军达人 🥈', '季军新星 🥉', '减重勇士 💪', '减重勇士 💪', '减重勇士 💪']
ADMIN_PASSWORD = '0123456'

import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weight_challenge.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        initial_weight REAL NOT NULL,
        avatar_color TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS weight_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES profiles(id),
        weight REAL NOT NULL,
        logged_date TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        UNIQUE(user_id, logged_date)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')
    conn.execute("INSERT OR IGNORE INTO config VALUES ('prize_pool', '1000')")
    conn.execute("INSERT OR REPLACE INTO config VALUES ('admin_password', ?)", (hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),))
    conn.commit()

if 'db_initialized' not in st.session_state:
    st.session_state.conn = get_conn()
    init_db(st.session_state.conn)
    st.session_state.db_initialized = True

conn = st.session_state.conn

# ── Helpers ───────────────────────────────────────────────
def get_rankings():
    rows = conn.execute('SELECT * FROM profiles').fetchall()
    results = []
    for r in rows:
        pid, name, initial, color = r[0], r[1], r[2], r[3]
        latest_row = conn.execute(
            'SELECT weight FROM weight_logs WHERE user_id=? ORDER BY logged_date DESC LIMIT 1',
            (pid,)
        ).fetchone()
        latest = latest_row[0] if latest_row else None
        loss_pct = ((initial - latest) / initial * 100) if latest else 0
        results.append({
            'id': pid, 'name': name, 'initial': initial,
            'color': color, 'latest': latest, 'loss_pct': loss_pct
        })
    results.sort(key=lambda x: x['loss_pct'], reverse=True)
    return results

def get_logs_html(user_id):
    logs = conn.execute(
        'SELECT * FROM weight_logs WHERE user_id=? ORDER BY logged_date DESC',
        (user_id,)
    ).fetchall()
    if not logs:
        return '<p style="color:#b0a0a0;text-align:center;padding:20px">还没有记录</p>'
    html = ''
    for l in logs:
        html += f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f0e8e8;font-size:14px"><span style="color:#b0a0a0">{l[3]}</span><span style="font-weight:600">{l[2]} kg</span></div>'
    return html

def check_admin_password(pw):
    stored = conn.execute("SELECT value FROM config WHERE key='admin_password'").fetchone()[0]
    return hashlib.sha256(pw.encode()).hexdigest() == stored

# ── Page State ────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ── HOME ──────────────────────────────────────────────────
if st.session_state.page == 'home':
    st.markdown('<h2 style="text-align:center">🏆 减肥挑战赛</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#b0a0a0">记录每日体重，一起变瘦</p>', unsafe_allow_html=True)

    rankings = get_rankings()

    if not rankings:
        st.info('还没有参赛者，点击下方「管理」添加')

    for r in rankings:
        latest_str = f'{r["latest"]}kg' if r['latest'] else '未记录'
        lc = '#81C784' if r['loss_pct'] > 0 else '#e57373'
        arrow = '↓' if r['loss_pct'] > 0 else ('↑' if r['loss_pct'] < 0 else '—')

        col_left, col_rec, col_view = st.columns([0.6, 0.2, 0.2], gap='small')

        with col_left:
            st.markdown(f'''
            <div style="display:flex;align-items:center;gap:10px">
                <div style="width:40px;height:40px;border-radius:50%;background:{r["color"]};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:17px;flex-shrink:0">{r["name"][0]}</div>
                <div style="min-width:0">
                    <div style="font-weight:650;font-size:14px;color:#3a3a3a;line-height:1.3">{r["name"]}</div>
                    <div style="font-size:11px;color:#b0a0a0;line-height:1.3">初始{r["initial"]}kg · {latest_str} <span style="color:{lc}">{arrow}{abs(r["loss_pct"]):.1f}%</span></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with col_rec:
            if st.button('记录', key=f'rec_{r["id"]}', use_container_width=True):
                st.session_state.record_target = r['id']
                st.session_state.record_name = r['name']
                st.session_state.record_color = r['color']
                st.session_state.record_initial = r['initial']
                st.session_state.page = 'record'; st.rerun()

        with col_view:
            if st.button('查看', key=f'vw_{r["id"]}', use_container_width=True):
                st.session_state.view_target = r['id']
                st.session_state.view_name = r['name']
                st.session_state.view_color = r['color']
                st.session_state.view_initial = r['initial']
                st.session_state.page = 'view'; st.rerun()

    st.markdown('---')
    c1, c2 = st.columns(2)
    with c1:
        if st.button('📊 排行榜', use_container_width=True):
            st.session_state.page = 'leaderboard'
            st.rerun()
    with c2:
        if st.button('⚙️ 管理', use_container_width=True):
            st.session_state.page = 'admin'
            st.session_state.admin_verified = False
            st.rerun()

# ── RECORD (输入体重) ─────────────────────────────────────
elif st.session_state.page == 'record':
    target_id = st.session_state.get('record_target')
    name = st.session_state.get('record_name', '')
    color = st.session_state.get('record_color', '#F8A4A4')
    initial = st.session_state.get('record_initial', 0)

    st.markdown(f'<div style="text-align:center"><div style="width:56px;height:56px;border-radius:50%;background:{color};display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:24px;margin-bottom:8px">{name[0]}</div><h3>{name}</h3>', unsafe_allow_html=True)

    latest_row = conn.execute(
        'SELECT weight FROM weight_logs WHERE user_id=? ORDER BY logged_date DESC LIMIT 1',
        (target_id,)
    ).fetchone()
    if latest_row:
        loss_pct = (initial - latest_row[0]) / initial * 100
        lc = '#81C784' if loss_pct > 0 else '#e57373'
        a = '↓' if loss_pct > 0 else ('↑' if loss_pct < 0 else '—')
        st.markdown(f'<p style="text-align:center;color:#b0a0a0">初始 {initial}kg · 当前 {latest_row[0]}kg · <span style="color:{lc};font-weight:600">{a}{abs(loss_pct):.1f}%</span></p>', unsafe_allow_html=True)

    st.markdown('---')
    c1, c2, c3 = st.columns([1, 1, 0.8])
    with c1:
        weight = st.number_input('体重 (kg)', min_value=0.0, max_value=300.0, step=0.1, format='%.1f', key='rw')
    with c2:
        log_date = st.date_input('日期', value=date.today(), key='rd')
    with c3:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button('保存', use_container_width=True):
            if weight > 0:
                conn.execute(
                    'INSERT OR REPLACE INTO weight_logs (user_id, weight, logged_date) VALUES (?,?,?)',
                    (target_id, weight, str(log_date))
                )
                conn.commit()
                st.success('记录成功！')

    st.markdown('##### 📋 历史记录')
    st.markdown(get_logs_html(target_id), unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button('← 返回首页', use_container_width=True):
            st.session_state.page = 'home'; st.rerun()
    with c2:
        if st.button('📊 排行榜', use_container_width=True):
            st.session_state.page = 'leaderboard'; st.rerun()

# ── VIEW (查看他人) ───────────────────────────────────────
elif st.session_state.page == 'view':
    target_id = st.session_state.get('view_target')
    name = st.session_state.get('view_name', '')
    color = st.session_state.get('view_color', '#F8A4A4')
    initial = st.session_state.get('view_initial', 0)

    st.markdown(f'<div style="text-align:center"><div style="width:56px;height:56px;border-radius:50%;background:{color};display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:24px;margin-bottom:8px">{name[0]}</div><h3>{name}</h3>', unsafe_allow_html=True)

    logs = conn.execute(
        'SELECT * FROM weight_logs WHERE user_id=? ORDER BY logged_date DESC',
        (target_id,)
    ).fetchall()

    latest_row = logs[0] if logs else None
    if latest_row:
        loss_pct = (initial - latest_row[2]) / initial * 100
        lc = '#81C784' if loss_pct > 0 else '#e57373'
        a = '↓' if loss_pct > 0 else ('↑' if loss_pct < 0 else '—')
        st.markdown(f'<p style="text-align:center;color:#b0a0a0">初始 {initial}kg · 当前 {latest_row[2]}kg · <span style="color:{lc};font-weight:600">{a}{abs(loss_pct):.1f}%</span></p>', unsafe_allow_html=True)

    # Simple chart
    if len(logs) >= 2:
        sorted_logs = sorted(logs, key=lambda x: x[3])
        all_weights = [initial] + [l[2] for l in sorted_logs]
        min_w, max_w = min(all_weights) - 1, max(all_weights) + 1
        rng = max_w - min_w or 1
        labels = ['初始'] + [l[3][5:] for l in sorted_logs]
        points_html = ''
        for i, v in enumerate(all_weights):
            x = 40 + (i / max(1, len(all_weights) - 1)) * 240
            y = 20 + ((max_w - v) / rng) * 100
            points_html += f'<circle cx="{x}" cy="{y}" r="3" fill="#F8A4A4"/>'
        line_html = ''
        for i in range(len(all_weights) - 1):
            x1 = 40 + (i / max(1, len(all_weights) - 1)) * 240
            y1 = 20 + ((max_w - all_weights[i]) / rng) * 100
            x2 = 40 + ((i + 1) / max(1, len(all_weights) - 1)) * 240
            y2 = 20 + ((max_w - all_weights[i + 1]) / rng) * 100
            line_html += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#F8A4A4" stroke-width="2"/>'
        labels_html = ''
        for i, lbl in enumerate(labels):
            if i == 0 or i == len(labels) - 1 or i % max(1, len(labels) // 4) == 0:
                x = 40 + (i / max(1, len(all_weights) - 1)) * 240
                labels_html += f'<text x="{x}" y="145" text-anchor="middle" font-size="9" fill="#b0a0a0">{lbl}</text>'

        st.markdown(f'''
        <svg viewBox="0 0 300 155" style="width:100%;max-width:400px;display:block;margin:0 auto">
            <text x="5" y="25" font-size="9" fill="#c0b0b0">{max_w:.0f}</text>
            <text x="5" y="75" font-size="9" fill="#c0b0b0">{(min_w+max_w)/2:.0f}</text>
            <text x="5" y="125" font-size="9" fill="#c0b0b0">{min_w:.0f}</text>
            <line x1="35" y1="20" x2="35" y2="125" stroke="#f0e8e8" stroke-width="1"/>
            <line x1="35" y1="125" x2="290" y2="125" stroke="#f0e8e8" stroke-width="1"/>
            {line_html}
            {points_html}
            {labels_html}
        </svg>
        ''', unsafe_allow_html=True)

    st.markdown('---')
    st.markdown('##### 📋 体重记录')
    st.markdown(get_logs_html(target_id), unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button('← 返回首页', use_container_width=True):
            st.session_state.page = 'home'; st.rerun()
    with c2:
        if st.button('📊 排行榜', use_container_width=True):
            st.session_state.page = 'leaderboard'; st.rerun()

# ── LEADERBOARD ───────────────────────────────────────────
elif st.session_state.page == 'leaderboard':
    st.markdown('<h2 style="text-align:center">📊 排行榜</h2>', unsafe_allow_html=True)
    rankings = get_rankings()
    prize = float(conn.execute("SELECT value FROM config WHERE key='prize_pool'").fetchone()[0])

    if not rankings:
        st.info('暂无参赛者')
    else:
        total_loss = sum(max(0, r['loss_pct']) for r in rankings)
        for i, r in enumerate(rankings):
            bg = 'linear-gradient(135deg, #fff9e6, #fff3cd)' if i == 0 else '#faf8f8'
            rank_color = ['#f0c040', '#c0c0c0', '#cd7f32'][i] if i < 3 else '#ccc'
            st.markdown(f'''
            <div style="display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:16px;background:{bg};margin-bottom:8px">
                <div style="font-size:22px;font-weight:700;color:{rank_color};width:32px;text-align:center">{i+1}</div>
                <div style="width:40px;height:40px;border-radius:50%;background:{r['color']};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:16px">{r["name"][0]}</div>
                <div style="flex:1"><div style="font-weight:600">{r["name"]}</div><div style="font-size:12px;color:#b0a0a0">{r['latest'] or '未记录'}kg · 初始{r['initial']}kg</div></div>
                <div style="text-align:right"><div style="font-size:18px;font-weight:700;color:#81C784">{'↓' if r['loss_pct'] >= 0 else '↑'}{abs(r['loss_pct']):.1f}%</div><div style="font-size:11px;color:#b0a0a0">{TITLES[i] if i < len(TITLES) else TITLES[-1]}</div></div>
            </div>''', unsafe_allow_html=True)

        st.markdown('---')
        st.markdown(f'##### 💰 奖金分配 · 总奖金池 ¥{prize:.0f}')
        if total_loss > 0:
            for r in rankings:
                share = (max(0, r['loss_pct']) / total_loss * prize) if r['loss_pct'] > 0 else 0
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0e8e8;font-size:14px"><span>{r["name"]}</span><span style="font-weight:600;color:#F08080">¥{share:.0f}</span></div>', unsafe_allow_html=True)
        else:
            st.info('还没有人减重，暂无可分配奖金')

    if st.button('← 返回'):
        st.session_state.page = 'home'; st.rerun()

# ── ADMIN ─────────────────────────────────────────────────
elif st.session_state.page == 'admin':
    if not st.session_state.get('admin_verified'):
        st.markdown('<h2 style="text-align:center">🔐 管理员验证</h2>', unsafe_allow_html=True)
        admin_pw = st.text_input('请输入管理密码', type='password')
        if st.button('验证', use_container_width=True):
            if check_admin_password(admin_pw):
                st.session_state.admin_verified = True
                st.rerun()
            else:
                st.error('密码错误')
        if st.button('← 返回'):
            st.session_state.page = 'home'; st.rerun()
    else:
        st.markdown('<h2 style="text-align:center">⚙️ 管理面板</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#b0a0a0">管理参赛者和比赛设置</p>', unsafe_allow_html=True)

        # Add participant (no password)
        st.markdown('##### ➕ 添加参赛者')
        with st.form('add_form', clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input('姓名')
            with c2:
                new_iw = st.number_input('初始体重 (kg)', min_value=1.0, max_value=300.0, step=0.1, value=70.0)
            if st.form_submit_button('添加参赛者', use_container_width=True):
                if not new_name:
                    st.error('请填写姓名')
                elif new_iw <= 0:
                    st.error('请输入有效体重')
                else:
                    try:
                        count = conn.execute('SELECT COUNT(*) FROM profiles').fetchone()[0]
                        color = COLORS[count % len(COLORS)]
                        conn.execute(
                            'INSERT INTO profiles (name, initial_weight, avatar_color) VALUES (?,?,?)',
                            (new_name.strip(), new_iw, color)
                        )
                        conn.commit()
                        st.success(f'{new_name} 添加成功！')
                    except sqlite3.IntegrityError:
                        st.error('名字已存在，请换一个')

        # Prize pool
        st.markdown('---')
        st.markdown('##### 💰 奖金池设置')
        prize = float(conn.execute("SELECT value FROM config WHERE key='prize_pool'").fetchone()[0])
        new_prize = st.number_input('总奖金 (元)', value=prize, step=100.0, key='pp')
        if st.button('保存设置'):
            conn.execute("UPDATE config SET value=? WHERE key='prize_pool'", (str(new_prize),))
            conn.commit()
            st.success('奖金池已更新')

        # Participant list
        st.markdown('---')
        profiles = conn.execute('SELECT * FROM profiles').fetchall()
        if profiles:
            st.markdown(f'##### 👥 参赛者 ({len(profiles)})')
            for p in profiles:
                c1, c2 = st.columns([0.85, 0.15])
                with c1:
                    st.markdown(f'<div style="display:flex;align-items:center;gap:10px"><div style="width:36px;height:36px;border-radius:50%;background:{p[3]};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:15px">{p[1][0]}</div><div><div style="font-weight:600">{p[1]}</div><div style="font-size:12px;color:#b0a0a0">初始 {p[2]}kg</div></div></div>', unsafe_allow_html=True)
                with c2:
                    if st.button('移除', key=f'del_{p[0]}'):
                        conn.execute('DELETE FROM weight_logs WHERE user_id=?', (p[0],))
                        conn.execute('DELETE FROM profiles WHERE id=?', (p[0],))
                        conn.commit()
                        st.rerun()

        st.markdown('---')
        c1, c2 = st.columns(2)
        with c1:
            if st.button('🔄 重置比赛', use_container_width=True):
                st.session_state.confirm_reset = True
        with c2:
            if st.button('← 返回首页', use_container_width=True):
                st.session_state.page = 'home'; st.rerun()

        if st.session_state.get('confirm_reset'):
            st.error('⚠️ 确定要删除所有数据？不可恢复！')
            c1, c2 = st.columns(2)
            with c1:
                if st.button('确认重置', use_container_width=True):
                    conn.execute('DELETE FROM weight_logs')
                    conn.execute('DELETE FROM profiles')
                    conn.commit()
                    st.session_state.confirm_reset = False
                    st.success('已全部重置')
                    st.rerun()
            with c2:
                if st.button('取消', use_container_width=True):
                    st.session_state.confirm_reset = False
                    st.rerun()
