import streamlit as st
import pandas as pd
import sqlite3
import os
import hashlib
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 기본 설정 ---
st.set_page_config(page_title="Sales Budget & Performance System", layout="wide")

DB_PATH = "db/sales_data.db"
if not os.path.exists('db'): os.makedirs('db')

EXCHANGE_RATES = {"USD": 1.0, "KRW": 1350.0, "SAR": 3.75}
BIZ_UNITS = ["FF", "CL"]
CUST_GROUPS = ["SC", "LG"]
MODES = ["Sea", "Air", "CL", "Rail"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MONTH_MAP = {name: i+1 for i, name in enumerate(MONTH_NAMES)}
MONTH_MAP_REV = {i+1: name for i, name in enumerate(MONTH_NAMES)}

# --- 보안 및 메일 함수 ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_approval_request_email(user_name, user_email, role):
    """관리자에게 가입 승인 요청 메일 발송"""
    try:
        if "smtp" not in st.secrets:
            return False # Secrets 설정 안되어 있으면 무시
            
        sender = st.secrets["smtp"]["user"]
        password = st.secrets["smtp"]["password"]
        admin_email = st.secrets["smtp"].get("admin_email", "taewon.seo@lxpantos.com")

        msg = MIMEText(f"신규 사용자 가입 요청이 있습니다.\n\n이름: {user_name}\n이메일: {user_email}\n권한요청: {role}\n\n시스템 관리자 페이지에 로그인하여 가입을 승인해주세요.")
        msg['Subject'] = "[시스템] 신규 사용자 가입 승인 요청"
        msg['From'] = sender
        msg['To'] = admin_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"메일 전송 실패: {e}")
        return False

# --- 데이터베이스 초기화 ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 사용자 테이블 (role 컬럼 추가)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    ''')
    try: c.execute("ALTER TABLE users ADD COLUMN role TEXT")
    except: pass
    
    # 기존 테이블들...
    c.execute('''CREATE TABLE IF NOT EXISTS plans (id INTEGER PRIMARY KEY AUTOINCREMENT, budget_plan_no TEXT, customer TEXT, sales_person TEXT, biz_unit TEXT, cust_group TEXT, mode TEXT, year INTEGER, month INTEGER, teu REAL, revenue REAL, gp REAL, revision INTEGER, is_dropped BOOLEAN, drop_reason TEXT, updated_at TEXT)''')
    try: c.execute("ALTER TABLE plans ADD COLUMN drop_reason TEXT")
    except: pass
    c.execute('''CREATE TABLE IF NOT EXISTS actuals (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, sales_person TEXT, biz_unit TEXT, mode TEXT, year INTEGER, month INTEGER, teu REAL, revenue REAL, gp REAL, updated_at TEXT, UNIQUE(customer, biz_unit, mode, year, month))''')
    try: c.execute("ALTER TABLE actuals ADD COLUMN sales_person TEXT")
    except: pass
    c.execute('''CREATE TABLE IF NOT EXISTS incentive_params (year INTEGER, month INTEGER, sales_person TEXT, base_salary REAL, fixed_allow REAL, fuel_cost REAL, trip_cost REAL, other_cost REAL, updated_at TEXT, UNIQUE(year, month, sales_person))''')
    c.execute('''CREATE TABLE IF NOT EXISTS customer_status (sales_person TEXT, customer TEXT, status TEXT, updated_at TEXT, UNIQUE(sales_person, customer))''')
    conn.commit()
    conn.close()

def get_metadata_lists():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT DISTINCT p.customer, p.sales_person FROM plans p WHERE p.is_dropped = 0", conn)
        return sorted(df['customer'].dropna().unique().tolist()), sorted(df['sales_person'].dropna().unique().tolist())
    except: return [], []
    finally: conn.close()

# --- 인증 및 관리자 DB 함수 ---
def register_user(name, email, password, role):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # 관리자 본인 계정은 가입 즉시 승인 처리
        status = 'approved' if email == "taewon.seo@lxpantos.com" else 'pending'
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO users (name, email, password, role, status, created_at) VALUES (?, ?, ?, ?, ?, ?)", 
                  (name, email, hash_password(password), role, status, ts))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # 이미 존재하는 이메일
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, status, role FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user # (name, status, role) or None

def get_pending_users():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT id, name, email, role, created_at FROM users WHERE status='pending'", conn)
    conn.close()
    return df

def approve_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET status='approved' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# 기존 로직 함수들 
def get_next_revision(budget_plan_no):
    conn = sqlite3.connect(DB_PATH)
    try: max_val = pd.read_sql("SELECT MAX(revision) as max_rev FROM plans WHERE budget_plan_no=?", conn, params=(budget_plan_no,)).iloc[0]['max_rev']; return int(max_val)+1 if pd.notna(max_val) and max_val!="" else 1
    except: return 1
    finally: conn.close()
def load_plan_summary(year, customer=None, sales_person=None, biz_unit=None, mode=None, show_dropped=False):
    conn = sqlite3.connect(DB_PATH)
    q = f"SELECT p.budget_plan_no, p.customer, p.sales_person, p.biz_unit, p.cust_group, p.mode, p.year, p.revision as current_ver, SUM(p.revenue) as total_rev, SUM(p.gp) as total_gp, MAX(p.drop_reason) as drop_reason, MAX(p.updated_at) as last_update FROM plans p INNER JOIN (SELECT budget_plan_no, MAX(revision) as max_rev FROM plans WHERE year = {year} GROUP BY budget_plan_no) latest ON p.budget_plan_no = latest.budget_plan_no AND p.revision = latest.max_rev WHERE p.year = {year} AND p.is_dropped = {1 if show_dropped else 0}"
    p = []; 
    if customer: q += " AND p.customer LIKE ?"; p.append(f"%{customer}%")
    if sales_person: q += " AND p.sales_person LIKE ?"; p.append(f"%{sales_person}%")
    if biz_unit and biz_unit != "All": q += " AND p.biz_unit = ?"; p.append(biz_unit)
    if mode and mode != "All": q += " AND p.mode = ?"; p.append(mode)
    df = pd.read_sql(q + " GROUP BY p.budget_plan_no, p.customer, p.sales_person, p.biz_unit, p.cust_group, p.mode, p.year, p.revision", conn, params=p); conn.close(); return df
def load_plan_details(budget_plan_no, revision):
    conn = sqlite3.connect(DB_PATH); df = pd.read_sql("SELECT * FROM plans WHERE budget_plan_no = ? AND revision = ? ORDER BY month ASC", conn, params=(budget_plan_no, revision)); conn.close(); return df
def save_plan_revision(data_list):
    conn = sqlite3.connect(DB_PATH); conn.cursor().executemany('''INSERT INTO plans (budget_plan_no, customer, sales_person, biz_unit, cust_group, mode, year, month, teu, revenue, gp, revision, is_dropped, drop_reason, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data_list); conn.commit(); conn.close()
def update_plan_metadata_batch(edited_df):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    for _, row in edited_df.iterrows():
        c.execute('''UPDATE plans SET customer=?, sales_person=?, biz_unit=?, mode=?, cust_group=?, drop_reason=? WHERE budget_plan_no=? AND revision=?''', (row['customer'], row['sales_person'], row['biz_unit'], row['mode'], row.get('cust_group'), row.get('drop_reason'), row['budget_plan_no'], row['current_ver']))
    conn.commit(); conn.close()
def save_actuals(data_list):
    conn = sqlite3.connect(DB_PATH); conn.cursor().executemany('''INSERT OR REPLACE INTO actuals (customer, sales_person, biz_unit, mode, year, month, teu, revenue, gp, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data_list); conn.commit(); conn.close()
def load_actuals_comparison(year, customer, biz_unit, mode):
    conn = sqlite3.connect(DB_PATH)
    pq = "SELECT month, MAX(sales_person) as plan_sales_person, SUM(teu) as plan_teu, SUM(revenue) as plan_rev, SUM(gp) as plan_gp, MAX(revision) as plan_rev_no FROM plans p INNER JOIN (SELECT budget_plan_no, MAX(revision) as max_rev FROM plans GROUP BY budget_plan_no) latest ON p.budget_plan_no = latest.budget_plan_no AND p.revision = latest.max_rev WHERE p.year = ? AND p.customer = ? AND p.is_dropped = 0"
    pp = [year, customer]
    if biz_unit != "All": pq += " AND p.biz_unit = ?"; pp.append(biz_unit)
    if mode != "All": pq += " AND p.mode = ?"; pp.append(mode)
    df_plan = pd.read_sql(pq + " GROUP BY month", conn, params=pp)
    aq = "SELECT month, sales_person as act_sales_person, revenue as act_rev, gp as act_gp, teu as act_teu FROM actuals WHERE year = ? AND customer = ?"
    ap = [year, customer]
    if biz_unit != "All": aq += " AND biz_unit = ?"; ap.append(biz_unit)
    if mode != "All": aq += " AND mode = ?"; ap.append(mode)
    df_act = pd.read_sql(aq, conn, params=ap); conn.close()
    df_merged = pd.merge(pd.DataFrame({'month': range(1, 13)}), df_plan, on='month', how='left')
    if not df_act.empty: df_merged = pd.merge(df_merged, df_act.groupby('month').agg({'act_rev': 'sum', 'act_gp': 'sum', 'act_teu': 'sum', 'act_sales_person': 'first'}).reset_index(), on='month', how='left')
    else: df_merged['act_rev'] = 0.0; df_merged['act_gp'] = 0.0; df_merged['act_teu'] = 0.0; df_merged['act_sales_person'] = None
    df_merged['final_sales_person'] = df_merged['act_sales_person'].fillna(df_merged['plan_sales_person']).fillna("").replace(0, "")
    return df_merged.fillna(0)
def save_incentive_params(year, month, sp, base, fixed, fuel, trip, other):
    conn = sqlite3.connect(DB_PATH); conn.cursor().execute('''INSERT OR REPLACE INTO incentive_params (year, month, sales_person, base_salary, fixed_allow, fuel_cost, trip_cost, other_cost, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (year, month, sp, base, fixed, fuel, trip, other, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))); conn.commit(); conn.close()
def load_incentive_params(year, month, sp):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor(); c.execute("SELECT * FROM incentive_params WHERE year=? AND month=? AND sales_person=?", (year, month, sp)); r = c.fetchone(); conn.close(); return r
def save_customer_status(sp, cust, status):
    conn = sqlite3.connect(DB_PATH); conn.cursor().execute('''INSERT OR REPLACE INTO customer_status (sales_person, customer, status, updated_at) VALUES (?, ?, ?, ?)''', (sp, cust, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))); conn.commit(); conn.close()
def get_customer_status_map(sp):
    conn = sqlite3.connect(DB_PATH); df = pd.read_sql("SELECT customer, status FROM customer_status WHERE sales_person=?", conn, params=(sp,)); conn.close(); return {} if df.empty else dict(zip(df.customer, df.status))
def load_sales_person_performance(year, month_idx, sp):
    conn = sqlite3.connect(DB_PATH); df = pd.read_sql("SELECT a.customer, SUM(a.revenue) as revenue, SUM(a.gp) as gp FROM actuals a LEFT JOIN (SELECT DISTINCT customer, sales_person FROM plans WHERE is_dropped = 0) p ON a.customer = p.customer WHERE a.year = ? AND a.month = ? AND p.sales_person = ? GROUP BY a.customer", conn, params=(year, month_idx, sp)); conn.close(); return df

init_db()

# --- 세션 상태 초기화 (로그인) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_name'] = ""
    st.session_state['role'] = ""
    st.session_state['is_admin'] = False

# ==========================================
# 로그인 및 회원가입 화면
# ==========================================
if not st.session_state['logged_in']:
    st.title("🔒 Sales Budget & Performance System")
    st.markdown("이 시스템은 인가된 사용자만 접근할 수 있습니다.")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 로그인 (Login)", "📝 회원가입 (Register)"])
    
    with auth_tab1:
        with st.form("login_form"):
            l_email = st.text_input("Email")
            l_pwd = st.text_input("Password", type="password")
            if st.form_submit_button("로그인"):
                user = login_user(l_email, l_pwd)
                if user:
                    name, status, role = user
                    if status == 'approved':
                        st.session_state['logged_in'] = True
                        st.session_state['user_name'] = name
                        st.session_state['role'] = role
                        st.session_state['is_admin'] = (role == 'Admin' or l_email == "taewon.seo@lxpantos.com")
                        st.success(f"환영합니다, {name}님! ({role})")
                        st.rerun()
                    else:
                        st.warning("⏳ 관리자 승인 대기 중입니다. 승인 후 이용 가능합니다.")
                else:
                    st.error("❌ 이메일 또는 비밀번호가 일치하지 않습니다.")

    with auth_tab2:
        st.subheader("계정 생성")
        # 폼(form) 바깥으로 빼서 드롭다운이 즉각 반응하도록 구성
        r_role = st.radio("권한 (Role)", ["Sales", "Admin"], horizontal=True)
        
        if r_role == "Sales":
            _, reps_list = get_metadata_lists()
            if reps_list:
                r_name = st.selectbox("영업사원 선택 (Select Sales Person)", reps_list, help="DB에 등록된 영업담당자 이름이 표시됩니다.")
            else:
                r_name = st.text_input("영업사원 이름 (DB에 등록된 직원이 없습니다. 직접 입력하세요)")
        else:
            r_name = st.text_input("이름 (Name)")
            
        r_email = st.text_input("이메일 (Company Email)")
        r_pwd = st.text_input("비밀번호 (Password)", type="password", key="reg_pwd1")
        r_pwd_chk = st.text_input("비밀번호 확인", type="password", key="reg_pwd2")
        
        if st.button("회원가입 요청"):
            if not r_name or not r_email or not r_pwd:
                st.error("모든 항목을 입력해주세요.")
            elif r_pwd != r_pwd_chk:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                success = register_user(r_name, r_email, r_pwd, r_role)
                if success:
                    st.success("✅ 가입 요청이 완료되었습니다. 관리자 승인 후 로그인 가능합니다.")
                    send_approval_request_email(r_name, r_email, r_role)
                else:
                    st.error("이미 가입된 이메일입니다.")
    
    st.stop() # 로그인 전에는 아래 앱 코드가 실행 안됨

# ==========================================
# 메인 앱 (로그인 성공 후)
# ==========================================
c_head1, c_head2 = st.columns([8, 1])
c_head1.title("📊 Sales Budget & Performance System")
if c_head2.button("🚪 Logout"):
    st.session_state['logged_in'] = False
    st.rerun()

# 관리자(Admin) 승인 패널
if st.session_state.get('is_admin', False):
    with st.expander("👑 관리자 패널 (가입 승인)", expanded=True):
        pending_users = get_pending_users()
        if pending_users.empty:
            st.info("대기 중인 가입 요청이 없습니다.")
        else:
            st.warning(f"현재 {len(pending_users)}명의 가입 대기자가 있습니다.")
            for _, u_row in pending_users.iterrows():
                col_u1, col_u2, col_u3, col_u4, col_u5 = st.columns([1.5, 2, 1, 2, 1.5])
                col_u1.write(f"**{u_row['name']}**")
                col_u2.write(u_row['email'])
                col_u3.write(f"({u_row['role']})")
                col_u4.write(u_row['created_at'])
                if col_u5.button(f"✅ 승인", key=f"app_{u_row['id']}"):
                    approve_user(u_row['id'])
                    st.success(f"{u_row['name']}님 가입 승인 완료!")
                    st.rerun()

st.markdown("---")

if 'editor_key' not in st.session_state: st.session_state['editor_key'] = 0
if 'edit_mode' not in st.session_state: st.session_state['edit_mode'] = False
if 'selected_plan' not in st.session_state: st.session_state['selected_plan'] = None
if 'drop_confirm_mode' not in st.session_state: st.session_state['drop_confirm_mode'] = False

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Budget Planning", "📝 Actuals Input", "📈 Gap Analysis", "📊 Dashboard", "💰 Incentive Calc"])

# 1. Budget Planning
with tab1:
    if not st.session_state['edit_mode']:
        st.subheader("📁 Budget Plan List")
        c1, c2, c3, c4 = st.columns(4)
        with c1: s_year = st.number_input("Year", 2025, 2030, 2026)
        with c2: s_cust = st.text_input("Customer Name", placeholder="Search...")
        with c3: s_bu = st.selectbox("Biz Unit", ["All"] + BIZ_UNITS)
        with c4: s_mode = st.selectbox("Transport Mode", ["All"] + MODES)
        status_filter = st.radio("Status:", ["Active Plans", "Dropped Plans"], horizontal=True); show_dropped = (status_filter == "Dropped Plans")

        if st.button("🔍 Search Plans"):
            st.session_state['search_results'] = load_plan_summary(s_year, s_cust, None, s_bu, s_mode, show_dropped)
        
        if 'search_results' in st.session_state:
            if st.session_state['search_results'].empty: st.info("No plans found.")
            else:
                disp_cols = ['budget_plan_no', 'customer', 'sales_person', 'biz_unit', 'cust_group', 'mode', 'current_ver', 'total_rev', 'total_gp', 'last_update']
                if show_dropped: disp_cols.append('drop_reason')
                
                st.info("💡 You can edit **Customer**, **Sales Person**, **Biz Unit**, **Group** directly in the list below. Click **'Save List Changes'** to apply.")
                
                edited_list_df = st.data_editor(
                    st.session_state['search_results'][disp_cols],
                    column_config={
                        "budget_plan_no": st.column_config.TextColumn(disabled=True),
                        "current_ver": st.column_config.NumberColumn(disabled=True),
                        "total_rev": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                        "total_gp": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                        "last_update": st.column_config.TextColumn(disabled=True),
                        "biz_unit": st.column_config.SelectboxColumn(options=BIZ_UNITS),
                        "cust_group": st.column_config.SelectboxColumn(options=CUST_GROUPS),
                        "mode": st.column_config.SelectboxColumn(options=MODES),
                    },
                    use_container_width=True,
                    hide_index=True,
                    key="plan_list_editor"
                )
                
                if st.button("💾 Save List Changes"):
                    try:
                        update_plan_metadata_batch(edited_list_df)
                        st.success("✅ Plan details updated successfully!")
                        st.session_state['search_results'] = load_plan_summary(s_year, s_cust, None, s_bu, s_mode, show_dropped)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating plans: {e}")

                st.divider()
                st.markdown("##### ✏️ Detailed Edit (Monthly Revenue/GP)")
                
                plan_options = st.session_state['search_results']['budget_plan_no'].tolist()
                selected_no = st.selectbox("Select 'Budget Plan No' to Edit/View Details", plan_options)
                
                if st.button("Go to Detail View"):
                    row = st.session_state['search_results'][st.session_state['search_results']['budget_plan_no'] == selected_no].iloc[0]
                    st.session_state['selected_plan'] = row
                    detail_df = load_plan_details(row['budget_plan_no'], row['current_ver'])
                    editor_data = []
                    for i, m_name in enumerate(MONTH_NAMES):
                        m_idx = i + 1
                        match = detail_df[detail_df['month'] == m_idx]
                        if not match.empty:
                            rev = match.iloc[0]['revenue']; gp = match.iloc[0]['gp']; teu = match.iloc[0]['teu']; margin = (gp / rev * 100) if rev != 0 else 0.0
                            editor_data.append({"Month": m_name, "TEU": teu, "Revenue ($)": rev, "GP ($)": gp, "GP Margin (%)": margin})
                        else:
                            editor_data.append({"Month": m_name, "TEU": 0.0, "Revenue ($)": 0.0, "GP ($)": 0.0, "GP Margin (%)": 0.0})
                    st.session_state['editor_data'] = pd.DataFrame(editor_data)
                    st.session_state['editor_key'] += 1; st.session_state['drop_confirm_mode'] = False; st.session_state['edit_mode'] = True; st.rerun()

        st.markdown("---")
        if not show_dropped and st.button("➕ Create New Plan"):
            st.session_state['selected_plan'] = None
            st.session_state['editor_data'] = pd.DataFrame({"Month": MONTH_NAMES, "TEU": [0.0]*12, "Revenue ($)": [0.0]*12, "GP ($)": [0.0]*12, "GP Margin (%)": [0.0]*12})
            st.session_state['editor_key'] += 1; st.session_state['drop_confirm_mode'] = False; st.session_state['edit_mode'] = True; st.rerun()

    else:
        plan_info = st.session_state['selected_plan']; is_new = plan_info is None
        if is_new: st.subheader("📝 New Budget Plan")
        else: st.subheader(f"✏️ Edit Budget Plan {'(Dropped)' if plan_info.get('drop_reason') else ''}")
        col1, col2, col3, col4 = st.columns(4)
        with col1: year_input = st.number_input("Year", 2025, 2030, int(plan_info['year']) if not is_new else 2026, disabled=not is_new)
        with col2: customer = st.text_input("Customer Name", value=plan_info['customer'], disabled=True) if not is_new else st.text_input("Customer Name").upper()
        with col3: sales_person = st.text_input("Sales Person", value=plan_info['sales_person'] if not is_new else "")
        with col4: 
            if not is_new: st.metric("Budget Plan No", plan_info['budget_plan_no'])
        col5, col6, col7 = st.columns(3)
        with col5: biz_unit = st.selectbox("Biz Unit", BIZ_UNITS, index=BIZ_UNITS.index(plan_info['biz_unit']) if not is_new else 0, disabled=not is_new)
        with col6: cust_group = st.selectbox("Customer Group", CUST_GROUPS, index=CUST_GROUPS.index(plan_info['cust_group']) if not is_new and plan_info['cust_group'] in CUST_GROUPS else 0)
        with col7: mode = st.selectbox("Mode", MODES, index=MODES.index(plan_info['mode']) if not is_new else 0, disabled=not is_new)
        budget_plan_no = plan_info['budget_plan_no'] if not is_new else f"{customer}_{mode}_{year_input}"
        next_rev = get_next_revision(budget_plan_no)
        if not is_new and not plan_info.get('drop_reason'): st.info(f"Editing Active Plan. Saving will create **Revision {next_rev}**.")
        elif not is_new and plan_info.get('drop_reason'): st.error(f"This plan is DROPPED. Reason: {plan_info['drop_reason']}")
        edited_df = st.data_editor(st.session_state['editor_data'], key=f"plan_editor_{st.session_state['editor_key']}", column_config={"Month": st.column_config.TextColumn(disabled=True), "GP Margin (%)": st.column_config.NumberColumn(format="%.2f %%", min_value=0, max_value=100), "Revenue ($)": st.column_config.NumberColumn(format="%.0f"), "GP ($)": st.column_config.NumberColumn(format="%.0f")}, use_container_width=True, hide_index=True, num_rows="fixed", height=500, disabled=(True if not is_new and plan_info.get('drop_reason') else False))
        st.markdown("---")
        if st.session_state['drop_confirm_mode']:
            with st.container():
                st.error("⚠️ You are about to DROP this business plan.")
                drop_reason_input = st.text_area("Reason for dropping:", placeholder="e.g. Lost bidding...")
                d_c1, d_c2 = st.columns([1, 5])
                with d_c1:
                    if st.button("✅ Confirm Drop"):
                        if not drop_reason_input: st.warning("Reason required.")
                        else:
                            save_data = []
                            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            for _, row in edited_df.iterrows():
                                save_data.append((budget_plan_no, customer, sales_person, biz_unit, cust_group, mode, year_input, MONTH_MAP[row["Month"]], row["TEU"], row["Revenue ($)"], row["GP ($)"], next_rev, True, drop_reason_input, ts))
                            save_plan_revision(save_data); st.success("Dropped Successfully."); st.session_state['edit_mode'] = False; st.rerun()
                with d_c2:
                    if st.button("↩️ Cancel"): st.session_state['drop_confirm_mode'] = False; st.rerun()
        else:
            b_c1, b_c2, b_c3 = st.columns([1, 1, 4])
            with b_c1:
                if (is_new or not plan_info.get('drop_reason')):
                    if st.button("💾 Update / Save"):
                        if not customer or not sales_person: st.error("Missing fields.")
                        else:
                            save_data = []; updated_ui = []; ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            for _, row in edited_df.iterrows():
                                rev = float(row["Revenue ($)"]); gp = float(row["GP ($)"]); margin = float(row["GP Margin (%)"]); teu = float(row["TEU"])
                                if rev != 0:
                                    if gp != 0: margin = (gp / rev) * 100
                                    elif gp == 0 and margin != 0: gp = rev * (margin / 100)
                                else: gp = 0.0; margin = 0.0
                                save_data.append((budget_plan_no, customer, sales_person, biz_unit, cust_group, mode, year_input, MONTH_MAP[row["Month"]], teu, rev, gp, next_rev, False, None, ts))
                                updated_ui.append({"Month": row["Month"], "TEU": teu, "Revenue ($)": rev, "GP ($)": gp, "GP Margin (%)": margin})
                            save_plan_revision(save_data); st.session_state['editor_data'] = pd.DataFrame(updated_ui); st.session_state['editor_key'] += 1
                            if is_new: st.session_state['selected_plan'] = {'budget_plan_no': budget_plan_no, 'customer': customer, 'sales_person': sales_person, 'biz_unit': biz_unit, 'cust_group': cust_group, 'mode': mode, 'year': year_input, 'is_dropped': False, 'current_ver': next_rev}
                            else: st.session_state['selected_plan']['current_ver'] = next_rev
                            st.success(f"Saved Revision {next_rev}"); st.rerun()
            with b_c2:
                if not is_new and not plan_info.get('drop_reason'):
                    if st.button("🗑️ Drop Plan"): st.session_state['drop_confirm_mode'] = True; st.rerun()
            with b_c3:
                if st.button("Back to List"): st.session_state['edit_mode'] = False; st.session_state['drop_confirm_mode'] = False; del st.session_state['editor_data']; st.rerun()

# 2. Actuals Input
with tab2:
    st.subheader("📝 Actuals Input")
    col1, col2, col3, col4 = st.columns(4)
    with col1: a_year = st.number_input("Year", 2025, 2030, 2026, key='act_year_inp')
    with col2: cust_list, _ = get_metadata_lists(); a_cust = st.selectbox("Customer", cust_list if cust_list else [])
    with col3: a_bu = st.selectbox("Biz Unit", ["All"] + BIZ_UNITS, key='act_bu')
    with col4: a_mode = st.selectbox("Mode", ["All"] + MODES, key='act_mode')

    if a_cust:
        if a_bu == "All" or a_mode == "All":
            st.warning("⚠️ Please select a specific **Biz Unit** and **Mode** to input Actuals.")
            comp_df = load_actuals_comparison(a_year, a_cust, a_bu, a_mode)
            comp_df['Month'] = comp_df['month'].map(MONTH_MAP_REV)
            
            disp_df = comp_df[['Month', 'final_sales_person', 'plan_teu', 'plan_rev', 'plan_gp', 'act_teu', 'act_rev', 'act_gp']].copy()
            disp_df.columns = ['Month', 'Sales Person', 'Plan TEU', 'Plan Rev', 'Plan GP', 'Act TEU', 'Act Revenue', 'Act GP']
            st.dataframe(disp_df.style.format({"Plan TEU": "{:,.0f}", "Plan Rev": "{:,.0f}", "Plan GP": "{:,.0f}", "Act TEU": "{:,.0f}", "Act Revenue": "{:,.0f}", "Act GP": "{:,.0f}"}), use_container_width=True)
        else:
            comp_df = load_actuals_comparison(a_year, a_cust, a_bu, a_mode)
            comp_df['Month'] = comp_df['month'].map(MONTH_MAP_REV)
            
            disp_df = comp_df[['Month', 'final_sales_person', 'plan_teu', 'plan_rev', 'plan_gp', 'act_teu', 'act_rev', 'act_gp']].copy()
            disp_df.columns = ['Month', 'Sales Person', 'Plan TEU', 'Plan Rev', 'Plan GP', 'Act TEU', 'Act Revenue', 'Act GP']
            
            st.info(f"💡 Input Actuals for **{a_cust}** - **{a_bu}** / **{a_mode}**")
            
            edited_act = st.data_editor(
                disp_df, 
                column_config={
                    "Month": st.column_config.TextColumn(disabled=True), 
                    "Sales Person": st.column_config.TextColumn(required=True, help="Edit Sales Person if needed"),
                    "Plan TEU": st.column_config.NumberColumn(disabled=True, format="%.0f"), 
                    "Plan Rev": st.column_config.NumberColumn(disabled=True, format="%.0f"), 
                    "Plan GP": st.column_config.NumberColumn(disabled=True, format="%.0f"), 
                    "Act TEU": st.column_config.NumberColumn(required=True, format="%.0f"), 
                    "Act Revenue": st.column_config.NumberColumn(required=True, format="%.0f"), 
                    "Act GP": st.column_config.NumberColumn(required=True, format="%.0f")
                }, 
                use_container_width=True, hide_index=True, num_rows="fixed", height=500
            )
            
            if st.button("💾 Save Actuals"):
                save_list = []; ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for _, row in edited_act.iterrows():
                    if row['Act Revenue']!=0 or row['Act GP']!=0 or row['Act TEU']!=0:
                        save_list.append((a_cust, row['Sales Person'], a_bu, a_mode, a_year, MONTH_MAP[row['Month']], row['Act TEU'], row['Act Revenue'], row['Act GP'], ts))
                save_actuals(save_list); st.success("Saved!")

# 3. Gap Analysis
with tab3:
    st.subheader("📈 Gap Analysis")
    c1, c2, c3 = st.columns(3)
    with c1: r_year = st.selectbox("Year", [2025, 2026], key='gap_year')
    with c2: period = st.slider("Period", 1, 12, (1, 12), key='gap_period')
    with c3: currency = st.radio("Currency", ["USD", "KRW", "SAR"], horizontal=True, key='gap_curr')
    with st.expander("Filter Options", expanded=False):
        f1, f2, f3, f4, f5 = st.columns(5)
        with f1: f_cust = st.multiselect("Customer", cust_list)
        with f2: _, rep_list = get_metadata_lists(); f_rep = st.multiselect("Sales Rep", rep_list)
        with f3: f_bu = st.multiselect("Biz Unit", BIZ_UNITS); 
        with f4: f_grp = st.multiselect("Cust Group", CUST_GROUPS); 
        with f5: f_mode = st.multiselect("Mode", MODES)
    conn = sqlite3.connect(DB_PATH)
    p_query = f"""SELECT p.* FROM plans p INNER JOIN (SELECT budget_plan_no, MAX(revision) as max_rev FROM plans GROUP BY budget_plan_no) lat ON p.budget_plan_no = lat.budget_plan_no AND p.revision = lat.max_rev WHERE year = {r_year} AND is_dropped = 0 AND month BETWEEN {period[0]} AND {period[1]}"""
    plans = pd.read_sql(p_query, conn)
    a_query = f"SELECT * FROM actuals WHERE year = {r_year} AND month BETWEEN {period[0]} AND {period[1]}"
    actuals = pd.read_sql(a_query, conn)
    conn.close()
    rate = EXCHANGE_RATES[currency]
    if plans.empty: st.warning("No active plan data.")
    else:
        if f_cust: plans=plans[plans['customer'].isin(f_cust)]; actuals=actuals[actuals['customer'].isin(f_cust)]
        if f_rep: plans=plans[plans['sales_person'].isin(f_rep)]
        if f_bu: plans=plans[plans['biz_unit'].isin(f_bu)]; actuals=actuals[actuals['biz_unit'].isin(f_bu)]
        if f_grp: plans=plans[plans['cust_group'].isin(f_grp)]
        if f_mode: plans=plans[plans['mode'].isin(f_mode)]; actuals=actuals[actuals['mode'].isin(f_mode)]
        group_cols = [c for c, f in [('customer', f_cust), ('sales_person', f_rep), ('biz_unit', f_bu), ('cust_group', f_grp), ('mode', f_mode)] if not f] or ['customer']
        p_agg = plans.groupby(group_cols)[['revenue', 'gp']].sum().reset_index()
        meta_df = plans[['customer', 'biz_unit', 'mode', 'sales_person', 'cust_group']].drop_duplicates()
        
        if 'sales_person' in actuals.columns:
            a_merged = pd.merge(actuals, meta_df, on=['customer', 'biz_unit', 'mode'], how='left', suffixes=('', '_plan'))
            a_merged['sales_person'] = a_merged['sales_person'].fillna(a_merged['sales_person_plan'])
        else:
            a_merged = pd.merge(actuals, meta_df, on=['customer', 'biz_unit', 'mode'], how='left')
            
        a_agg = a_merged.groupby(group_cols)[['revenue', 'gp']].sum().reset_index()
        final = pd.merge(p_agg, a_agg, on=group_cols, how='left', suffixes=('_plan', '_act')).fillna(0)
        final['Plan Rev'] = final['revenue_plan']*rate; final['Act Rev'] = final['revenue_act']*rate; final['Gap Rev'] = final['Plan Rev'] - final['Act Rev']
        final['Plan GP'] = final['gp_plan']*rate; final['Act GP'] = final['gp_act']*rate; final['Gap GP'] = final['Plan GP'] - final['Act GP']
        final['Achv Rev(%)'] = (final['Act Rev'] / final['Plan Rev'].replace(0, 1)) * 100
        final['Achv GP(%)'] = (final['Act GP'] / final['Plan GP'].replace(0, 1)) * 100
        
        show_cols = group_cols + ['Plan Rev', 'Act Rev', 'Gap Rev', 'Achv Rev(%)', 'Plan GP', 'Act GP', 'Gap GP', 'Achv GP(%)']
        final_disp = final[show_cols]
        
        st.dataframe(final_disp.style.format({'Plan Rev': '{:,.0f}', 'Act Rev': '{:,.0f}', 'Gap Rev': '{:,.0f}', 'Achv Rev(%)': '{:.1f}%', 'Plan GP': '{:,.0f}', 'Act GP': '{:,.0f}', 'Gap GP': '{:,.0f}', 'Achv GP(%)': '{:.1f}%'}).background_gradient(subset=['Achv GP(%)', 'Achv Rev(%)'], cmap="RdYlGn", vmin=50, vmax=120), use_container_width=True)

# 4. Dashboard
with tab4:
    st.subheader("📊 Dashboard")
    conn = sqlite3.connect(DB_PATH)
    plans_all = pd.read_sql(f"""SELECT p.* FROM plans p INNER JOIN (SELECT budget_plan_no, MAX(revision) m FROM plans GROUP BY budget_plan_no) k ON p.budget_plan_no=k.budget_plan_no AND p.revision=k.m WHERE year={r_year} AND is_dropped=0""", conn)
    actuals_all = pd.read_sql(f"SELECT * FROM actuals WHERE year={r_year}", conn)
    conn.close()
    if plans_all.empty: st.warning("No data.")
    else:
        st.markdown("### 1. Monthly Trend")
        p_trend = plans_all.groupby(['month', 'biz_unit'])[['revenue', 'gp']].sum().reset_index()
        a_trend = actuals_all.groupby(['month', 'biz_unit'])[['revenue', 'gp']].sum().reset_index()
        p_trend['Month'] = p_trend['month'].map(MONTH_MAP_REV); a_trend['Month'] = a_trend['month'].map(MONTH_MAP_REV)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        p_ff = p_trend[p_trend['biz_unit']=='FF']; fig.add_trace(go.Bar(x=p_ff['Month'], y=p_ff['revenue'], name="Plan(FF)", marker_color='lightblue', opacity=0.6), secondary_y=False)
        p_cl = p_trend[p_trend['biz_unit']=='CL']; fig.add_trace(go.Bar(x=p_cl['Month'], y=p_cl['revenue'], name="Plan(CL)", marker_color='blue', opacity=0.6), secondary_y=False)
        a_ff = a_trend[a_trend['biz_unit']=='FF']; fig.add_trace(go.Bar(x=a_ff['Month'], y=a_ff['revenue'], name="Act(FF)", marker_color='lightgreen', opacity=0.8), secondary_y=False)
        a_cl = a_trend[a_trend['biz_unit']=='CL']; fig.add_trace(go.Bar(x=a_cl['Month'], y=a_cl['revenue'], name="Act(CL)", marker_color='green', opacity=0.8), secondary_y=False)
        p_gp = plans_all.groupby('month')['gp'].sum().reset_index(); p_gp['Month'] = p_gp['month'].map(MONTH_MAP_REV)
        a_gp = actuals_all.groupby('month')['gp'].sum().reset_index(); a_gp['Month'] = a_gp['month'].map(MONTH_MAP_REV)
        fig.add_trace(go.Scatter(x=p_gp['Month'], y=p_gp['gp'], name="Plan GP", mode='lines+markers', line=dict(color='red')), secondary_y=True)
        fig.add_trace(go.Scatter(x=a_gp['Month'], y=a_gp['gp'], name="Act GP", mode='lines+markers', line=dict(color='orange')), secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### 2. Rev Contribution")
        c_tabs = st.tabs(["Customer", "Rep", "Biz", "Group", "Mode"])
        def pie(t, c): 
            with t: st.plotly_chart(px.pie(plans_all.groupby(c)['revenue'].sum().reset_index(), values='revenue', names=c), use_container_width=True)
        pie(c_tabs[0],'customer'); pie(c_tabs[1],'sales_person'); pie(c_tabs[2],'biz_unit'); pie(c_tabs[3],'cust_group'); pie(c_tabs[4],'mode')
        st.markdown("### 3. Plan vs Actual")
        dim = st.selectbox("Dimension", ['customer', 'sales_person', 'biz_unit', 'cust_group', 'mode'])
        meta = plans_all[['customer', 'biz_unit', 'mode', 'sales_person', 'cust_group']].drop_duplicates()
        
        if 'sales_person' in actuals_all.columns:
            a_mg = pd.merge(actuals_all, meta, on=['customer', 'biz_unit', 'mode'], how='left', suffixes=('', '_plan'))
            a_mg['sales_person'] = a_mg['sales_person'].fillna(a_mg['sales_person_plan'])
        else:
            a_mg = pd.merge(actuals_all, meta, on=['customer', 'biz_unit', 'mode'], how='left')
            
        p_d = plans_all.groupby(dim)[['revenue', 'gp']].sum().reset_index()
        a_d = a_mg.groupby(dim)[['revenue', 'gp']].sum().reset_index()
        comp = pd.merge(p_d, a_d, on=dim, suffixes=('_P', '_A')).fillna(0)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=comp[dim], y=comp['revenue_P'], name='Plan Rev'))
        fig2.add_trace(go.Bar(x=comp[dim], y=comp['revenue_A'], name='Act Rev'))
        st.plotly_chart(fig2, use_container_width=True)

# 5. Incentive Calculation
with tab5:
    st.subheader("💰 Incentive Calculation")
    st.markdown("Calculate monthly incentive based on **Total GP vs Cost Target**.")

    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1: i_year = st.number_input("Year", 2025, 2030, 2026, key='inc_year')
    with col_i2: i_month_name = st.selectbox("Month", MONTH_NAMES, key='inc_month')
    _, reps_list = get_metadata_lists()
    with col_i3: i_person = st.selectbox("Sales Person", reps_list, key='inc_person')
    i_month = MONTH_MAP[i_month_name]
    st.divider()

    st.markdown("#### 1. Input Salary & Expenses")
    saved_params = load_incentive_params(i_year, i_month, i_person)
    def_base = saved_params[3] if saved_params else 0.0
    def_fix  = saved_params[4] if saved_params else 0.0
    def_fuel = saved_params[5] if saved_params else 0.0
    def_trip = saved_params[6] if saved_params else 0.0
    def_other= saved_params[7] if saved_params else 0.0
    def secure_input(label, val):
        val_str = st.text_input(label, value=str(int(val)) if val else "0", type="password", help=f"현재 값: {val:,.0f}")
        try: return float(val_str)
        except: return 0.0
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: base_salary = secure_input("Base Salary", def_base)
    with c2: fixed_allow = secure_input("Fixed Allowance", def_fix)
    with c3: fuel_cost = secure_input("Fuel Cost", def_fuel)
    with c4: trip_cost = secure_input("Biz Trip Cost", def_trip)
    with c5: other_cost = secure_input("Other Cost", def_other)
    if st.button("💾 Save Salary & Expenses"):
        save_incentive_params(i_year, i_month, i_person, base_salary, fixed_allow, fuel_cost, trip_cost, other_cost)
        st.success("Salary & Expenses Saved!")
    total_cost = base_salary + fixed_allow + fuel_cost + trip_cost + other_cost
    target_gp = total_cost * 3
    st.info(f"🎯 **Target GP (Cost x 3):** {target_gp:,.0f} (Based on masked input costs)")
    st.divider()

    st.markdown("#### 2. Classify Customers (New/Existing)")
    if st.button("🔄 Load Performance Data"):
        perf_df = load_sales_person_performance(i_year, i_month, i_person)
        if perf_df.empty:
            st.warning("No performance data found for this sales person/month.")
            st.session_state['inc_data'] = pd.DataFrame()
        else:
            status_map = get_customer_status_map(i_person)
            perf_df['Type'] = perf_df['customer'].map(status_map).fillna("Existing")
            st.session_state['inc_data'] = perf_df

    if 'inc_data' in st.session_state and not st.session_state['inc_data'].empty:
        edited_inc_df = st.data_editor(st.session_state['inc_data'], column_config={"customer": st.column_config.TextColumn("Customer", disabled=True), "revenue": st.column_config.NumberColumn("Revenue", format="%.0f", disabled=True), "gp": st.column_config.NumberColumn("GP", format="%.0f", disabled=True), "Type": st.column_config.SelectboxColumn("Customer Type", options=["Existing", "New"], required=True)}, hide_index=True, use_container_width=True)
        if st.button("💰 Calculate Incentive & Save Classifications"):
            for _, row in edited_inc_df.iterrows():
                save_customer_status(i_person, row['customer'], row['Type'])
            st.toast("Customer Classifications Saved!", icon="✅")
            total_act_gp = edited_inc_df['gp'].sum()
            excess_gp = total_act_gp - target_gp
            st.markdown("#### 3. Calculation Result")
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("Total Actual GP", f"{total_act_gp:,.0f}")
            res_col2.metric("Target GP", f"{target_gp:,.0f}")
            res_col3.metric("Excess GP (Over Target)", f"{excess_gp:,.0f}", delta_color="normal")
            if excess_gp <= 0: st.error("📉 **No Incentive.** (Total GP did not exceed Target)")
            else:
                gp_new = edited_inc_df[edited_inc_df['Type']=="New"]['gp'].sum()
                gp_old = edited_inc_df[edited_inc_df['Type']=="Existing"]['gp'].sum()
                if total_act_gp == 0: ratio_new = 0; ratio_old = 0
                else: ratio_new = gp_new / total_act_gp; ratio_old = gp_old / total_act_gp
                inc_new_part = excess_gp * ratio_new * 0.20
                inc_old_part = excess_gp * ratio_old * 0.10
                total_incentive = inc_new_part + inc_old_part
                st.success(f"🎉 **Total Incentive:** {total_incentive:,.0f}")
                with st.expander("Show Calculation Details"):
                    st.write(f"- **New Customer GP:** {gp_new:,.0f} ({ratio_new*100:.1f}%) → Incentive Part: {inc_new_part:,.0f} (20% rate)")
                    st.write(f"- **Existing Customer GP:** {gp_old:,.0f} ({ratio_old*100:.1f}%) → Incentive Part: {inc_old_part:,.0f} (10% rate)")
                    st.write(f"- **Formula:** ({excess_gp:,.0f} * {ratio_new:.2f} * 0.2) + ({excess_gp:,.0f} * {ratio_old:.2f} * 0.1)")
