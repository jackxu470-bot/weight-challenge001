import streamlit as st
from supabase import create_client, Client
import hashlib
from datetime import date

st.set_page_config(page_title='减肥挑战赛', page_icon='🏆', layout='centered')

# ── Supabase ──────────────────────────────────────────────
SUPABASE_URL = "https://zvdhaafykxwtnouourwr.supabase.co"
SUPABASE_KEY = "sb_publishable_zQz_dX-zhrYoqldhAt6ddQ_PWIaaJdM"
ADMIN_PASSWORD = '0123456'

@st.cache_resource
def get_sb():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

sb: Client = get_sb()

# ── Custom CSS ────────────────────────────────────────────
st.markdown('''
<style>
    .stApp { background: linear-gradient(170deg, #fef5f5 0%, #fce4ec 35%, #f3e5f5 100%); }
    .block-container { padding: 2rem 1rem 1.5rem 1rem !important; }
    .stButton button {
        border-radius: 12px !important; font-weight: 550 !important;
        border: none !important; background: #fdf0ed !important;
        padding: 5px 0 !important; font-size: 13px !important;
        letter-spacing: 0.5px !important; transition: all 0.15s ease !important;
        width: 100% !important; color: #c0978e !important;
    }
    .stButton button:hover { background: #f9e2dc !important; color: #b07e74 !important; }
    .stButton button:active { transform: scale(0.97) !important; }
</style>
''', unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────
COLORS = ['#F8A4A4', '#A8E6CF', '#FFD3B6', '#D5AAFF', '#87CEEB', '#FFB7B2', '#B5EAD7', '#C7CEEA']
TITLES = ['至尊瘦皇 👑', '亚军达人 🥈', '季军新星 🥉', '减重勇士 💪', '减重勇士 💪', '减重勇士 💪']

def get_prize():
    r = sb.table('config').select('value').eq('key', 'prize_pool').execute()
    return float(r.data[0]['value']) if r.data else 1000

def set_prize(v):
    sb.table('config').upsert({'key': 'prize_pool', 'value': str(v)}, on_conflict='key').execute()

def check_admin(pw):
    return hashlib.sha256(pw.encode()).hexdigest() == hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()

def get_rankings():
    rows = sb.table('profiles').select('*').order('id').execute().data
    results = []
    for r in rows:
        pid, name, initial, color = r['id'], r['name'], r['initial_weight'], r['avatar_color']
        wlogs = sb.table('weight_logs').select('weight').eq('user_id', pid).order('logged_date', desc=True).limit(1).execute().data
        latest = wlogs[0]['weight'] if wlogs else None
        loss_pct = ((initial - latest) / initial * 100) if latest else 0
        results.append({'id': pid, 'name': name, 'initial': initial, 'color': color, 'latest': latest, 'loss_pct': loss_pct})
    results.sort(key=lambda x: x['loss_pct'], reverse=True)
    return results

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
            </div>''', unsafe_allow_html=True)
        with col_rec:
            if st.button('记录', key=f'rec_{r["id"]}', use_container_width=True):
                st.session_state.record_target = r['id']; st.session_state.record_name = r['name']
                st.session_state.record_color = r['color']; st.session_state.record_initial = r['initial']
                st.session_state.page = 'record'; st.rerun()
        with col_view:
            if st.button('查看', key=f'vw_{r["id"]}', use_container_width=True):
                st.session_state.view_target = r['id']; st.session_state.view_name = r['name']
                st.session_state.view_color = r['color']; st.session_state.view_initial = r['initial']
                st.session_state.page = 'view'; st.rerun()

    st.markdown('---')
    c1, c2 = st.columns(2)
    with c1:
        if st.button('📊 排行榜', use_container_width=True):
            st.session_state.page = 'leaderboard'; st.rerun()
    with c2:
        if st.button('⚙️ 管理', use_container_width=True):
            st.session_state.page = 'admin'; st.session_state.admin_verified = False; st.rerun()

# ── RECORD ────────────────────────────────────────────────
elif st.session_state.page == 'record':
    tid = st.session_state.get('record_target')
    name = st.session_state.get('record_name', '')
    color = st.session_state.get('record_color', '#F8A4A4')
    initial = st.session_state.get('record_initial', 0)

    st.markdown(f'<div style="text-align:center"><div style="width:56px;height:56px;border-radius:50%;background:{color};display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:24px;margin-bottom:8px">{name[0]}</div><h3>{name}</h3>', unsafe_allow_html=True)

    wlogs = sb.table('weight_logs').select('weight').eq('user_id', tid).order('logged_date', desc=True).limit(1).execute().data
    if wlogs:
        lw = wlogs[0]['weight']
        loss_pct = (initial - lw) / initial * 100
        lc = '#81C784' if loss_pct > 0 else '#e57373'
        a = '↓' if loss_pct > 0 else ('↑' if loss_pct < 0 else '—')
        st.markdown(f'<p style="text-align:center;color:#b0a0a0">初始 {initial}kg · 当前 {lw}kg · <span style="color:{lc};font-weight:600">{a}{abs(loss_pct):.1f}%</span></p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="text-align:center;color:#b0a0a0">初始 {initial}kg · 暂无记录</p>', unsafe_allow_html=True)

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
                sb.table('weight_logs').upsert({
                    'user_id': tid, 'weight': weight, 'logged_date': str(log_date)
                }, on_conflict='user_id,logged_date').execute()
                st.success('记录成功！')

    # History
    logs = sb.table('weight_logs').select('*').eq('user_id', tid).order('logged_date', desc=True).limit(50).execute().data
    st.markdown('##### 📋 历史记录')
    if not logs:
        st.info('还没有记录')
    else:
        for l in logs:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f0e8e8;font-size:14px"><span style="color:#b0a0a0">{l["logged_date"]}</span><span style="font-weight:600">{l["weight"]} kg</span></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button('← 返回首页', use_container_width=True):
            st.session_state.page = 'home'; st.rerun()
    with c2:
        if st.button('📊 排行榜', use_container_width=True):
            st.session_state.page = 'leaderboard'; st.rerun()

# ── VIEW ─────────────────────────────────────────────────
elif st.session_state.page == 'view':
    tid = st.session_state.get('view_target')
    name = st.session_state.get('view_name', '')
    color = st.session_state.get('view_color', '#F8A4A4')
    initial = st.session_state.get('view_initial', 0)

    st.markdown(f'<div style="text-align:center"><div style="width:56px;height:56px;border-radius:50%;background:{color};display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:24px;margin-bottom:8px">{name[0]}</div><h3>{name}</h3>', unsafe_allow_html=True)

    logs = sb.table('weight_logs').select('*').eq('user_id', tid).order('logged_date', desc=True).execute().data
    if logs:
        lw = logs[0]['weight']
        loss_pct = (initial - lw) / initial * 100
        lc = '#81C784' if loss_pct > 0 else '#e57373'
        a = '↓' if loss_pct > 0 else ('↑' if loss_pct < 0 else '—')
        st.markdown(f'<p style="text-align:center;color:#b0a0a0">初始 {initial}kg · 当前 {lw}kg · <span style="color:{lc};font-weight:600">{a}{abs(loss_pct):.1f}%</span></p>', unsafe_allow_html=True)

    st.markdown('---')
    st.markdown('##### 📋 体重记录')
    if not logs:
        st.info('还没有记录')
    else:
        for l in logs:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f0e8e8;font-size:14px"><span style="color:#b0a0a0">{l["logged_date"]}</span><span style="font-weight:600">{l["weight"]} kg</span></div>', unsafe_allow_html=True)

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
    prize = get_prize()

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
        c1, c2 = st.columns(2)
        with c1:
            if st.button('验证', use_container_width=True):
                if check_admin(admin_pw):
                    st.session_state.admin_verified = True; st.rerun()
                else:
                    st.error('密码错误')
        with c2:
            if st.button('← 返回', use_container_width=True):
                st.session_state.page = 'home'; st.rerun()
    else:
        st.markdown('<h2 style="text-align:center">⚙️ 管理面板</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#b0a0a0">管理参赛者和比赛设置</p>', unsafe_allow_html=True)

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
                    count = len(sb.table('profiles').select('id').execute().data)
                    color = COLORS[count % len(COLORS)]
                    try:
                        sb.table('profiles').insert({
                            'name': new_name.strip(), 'initial_weight': new_iw, 'avatar_color': color
                        }).execute()
                        st.success(f'{new_name} 添加成功！')
                    except Exception as e:
                        st.error('名字已存在，请换一个')

        st.markdown('---')
        st.markdown('##### 💰 奖金池设置')
        prize = get_prize()
        new_prize = st.number_input('总奖金 (元)', value=float(prize), step=100.0, key='pp')
        if st.button('保存设置'):
            set_prize(new_prize)
            st.success('奖金池已更新')

        st.markdown('---')
        profiles = sb.table('profiles').select('*').execute().data
        if profiles:
            st.markdown(f'##### 👥 参赛者 ({len(profiles)})')
            for p in profiles:
                c1, c2 = st.columns([0.85, 0.15])
                with c1:
                    st.markdown(f'<div style="display:flex;align-items:center;gap:10px"><div style="width:36px;height:36px;border-radius:50%;background:{p["avatar_color"]};display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:15px">{p["name"][0]}</div><div><div style="font-weight:600">{p["name"]}</div><div style="font-size:12px;color:#b0a0a0">初始 {p["initial_weight"]}kg</div></div></div>', unsafe_allow_html=True)
                with c2:
                    if st.button('移除', key=f'del_{p["id"]}'):
                        sb.table('weight_logs').delete().eq('user_id', p['id']).execute()
                        sb.table('profiles').delete().eq('id', p['id']).execute()
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
            ca, cb = st.columns(2)
            with ca:
                if st.button('确认重置', use_container_width=True):
                    sb.table('weight_logs').delete().neq('id', 0).execute()
                    sb.table('profiles').delete().neq('id', 0).execute()
                    st.session_state.confirm_reset = False
                    st.success('已全部重置')
                    st.rerun()
            with cb:
                if st.button('取消', use_container_width=True):
                    st.session_state.confirm_reset = False; st.rerun()
