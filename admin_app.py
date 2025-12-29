import streamlit as st
import requests
import os
import pandas as pd
import time

# 백엔드 API 주소 (로컬 개발용 기본값)
# Docker Compose에서는 'backend' 호스트명을 쓰지만, 로컬에서 실행할 경우 localhost
# Streamlit이 Docker 내부에서 돌면 'http://backend:8000', 로컬이면 'http://localhost:8000'
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE_URL = f"{BACKEND_URL}/api/v1"

st.set_page_config(page_title="RAG Admin Console", layout="wide", page_icon="🛡️")

# --- Session State 초기화 ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# --- Helper Functions ---
def login(email, password):
    try:
        res = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": email, "password": password}
        )
        if res.status_code == 200:
            data = res.json()
            st.session_state.token = data["access_token"]
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error(f"로그인 실패: {res.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"서버 연결 오류: {str(e)}")

def logout():
    st.session_state.token = None
    st.session_state.user_email = None
    st.rerun()

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# --- Login Page ---
if not st.session_state.token:
    st.title("🔒 Enterprise RAG Admin Login")
    
    # 서버 상태 체크
    try:
        health = requests.get(f"{BACKEND_URL}/")
        if health.status_code == 200:
            st.success("✅ Backend System Online")
        else:
            st.warning("⚠️ Backend System Unstable")
    except:
        st.error("❌ Backend System Offline (Cannot connect to server)")
        st.stop()

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="admin@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not email or not password:
                st.warning("이메일과 비밀번호를 입력해주세요.")
            else:
                login(email, password)
    
    st.info("💡 초기 관리자 계정: `admin@example.com` / `admin123`")
    st.stop()  # 로그인 전에는 아래 내용 렌더링 안 함

# --- Main Admin Dashboard ---
st.sidebar.title("🛡️ Admin Console")
st.sidebar.info(f"User: **{st.session_state.user_email}**")
if st.sidebar.button("Logout"):
    logout()

st.title("📂 문서 관리 및 모니터링")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📤 문서 업로드", "📋 문서 목록", "🤖 RAG 테스트"])

# --- Tab 1: 문서 업로드 (비동기) ---
with tab1:
    st.header("Upload New Documents")
    uploaded_files = st.file_uploader(
        "지원 포맷: PDF, HWP, DOCX, XLSX, TXT", 
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button(f"🚀 파일 {len(uploaded_files)}개 업로드 시작"):
            progress_bar = st.progress(0)
            status_area = st.empty()
            
            success_count = 0
            
            for i, file in enumerate(uploaded_files):
                status_area.text(f"Uploading: {file.name}...")
                try:
                    files = {"file": (file.name, file.getvalue(), file.type)}
                    # 인증 헤더 추가
                    response = requests.post(
                        f"{API_BASE_URL}/documents/upload", 
                        files=files,
                        headers=get_headers()
                    )
                    
                    if response.status_code == 202:
                        data = response.json()
                        st.toast(f"✅ {file.name} 업로드 완료! (Task ID: {data.get('task_id')})")
                        success_count += 1
                    else:
                        st.error(f"❌ 실패 {file.name}: {response.text}")
                except Exception as e:
                    st.error(f"❌ 오류 {file.name}: {str(e)}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            if success_count > 0:
                st.success(f"총 {success_count}개 파일이 백그라운드 처리 큐에 등록되었습니다.")
                time.sleep(1)
                st.rerun()

# --- Tab 2: 문서 목록 ---
with tab2:
    st.header("Registered Documents")
    
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🔄 목록 새로고침"):
            st.rerun()

    try:
        # 인증 헤더 추가 (목록 조회는 public일 수도 있지만, 보안상 잠그는 게 좋음)
        # 현재 API 문서상 GET /documents/ 는 잠기지 않았을 수 있음 (확인 필요)
        # 하지만 우리는 안전하게 헤더를 보낸다.
        res = requests.get(f"{API_BASE_URL}/documents/", params={"limit": 50}, headers=get_headers())
        
        if res.status_code == 200:
            docs = res.json()
            if docs:
                df = pd.DataFrame(docs)
                
                # 데이터 가공
                if 'file_size' in df.columns:
                    df['file_size'] = df['file_size'].apply(lambda x: f"{x/1024:.1f} KB" if x else "0 KB")
                
                # 삭제 버튼 구현을 위한 컬럼 설정
                st.dataframe(
                    df[['id', 'filename', 'status', 'file_size', 'created_at']],
                    use_container_width=True,
                    column_config={
                        "id": "Document ID",
                        "created_at": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm")
                    }
                )
                
                # 문서 삭제 기능
                st.divider()
                st.subheader("🗑️ 문서 삭제")
                del_id = st.text_input("삭제할 Document ID (UUID) 입력")
                if st.button("영구 삭제") and del_id:
                    with st.spinner("삭제 중..."):
                        del_res = requests.delete(f"{API_BASE_URL}/documents/{del_id}", headers=get_headers())
                        if del_res.status_code == 200:
                            st.success("문서가 삭제되었습니다.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"삭제 실패: {del_res.text}")
            else:
                st.info("등록된 문서가 없습니다.")
        else:
            st.error(f"데이터 조회 실패: {res.status_code}")
    except Exception as e:
        st.error(f"연결 오류: {str(e)}")

# --- Tab 3: RAG 테스트 ---
with tab3:
    st.header("🤖 RAG Quality Test")
    
    query = st.text_input("테스트할 질문을 입력하세요:", placeholder="예: 재택 근무 규정이 어떻게 되나요?")
    top_k = st.slider("검색할 문서 수 (Top K)", 1, 10, 4)
    
    if st.button("질문하기") and query:
        with st.spinner("AI가 답변을 생성하고 있습니다..."):
            try:
                # 채팅은 현재 Public API로 열려 있을 수 있음 (하지만 추후 잠길 수 있으니 헤더 포함 가능)
                # 현재 API 명세: POST /chat/query
                payload = {"query": query, "top_k": top_k}
                res = requests.post(f"{API_BASE_URL}/chat/query", json=payload) # 채팅은 보통 Public
                
                if res.status_code == 200:
                    result = res.json()
                    
                    st.markdown("### 💡 답변")
                    st.info(result.get("answer", "답변을 찾을 수 없습니다."))
                    
                    st.markdown("### 📚 참고 문서 (Sources)")
                    sources = result.get("sources", [])
                    if sources:
                        for idx, src in enumerate(sources):
                            with st.expander(f"[{idx+1}] {src.get('filename', 'Unknown')} (Score: {src.get('relevance_score', 0):.4f})"):
                                st.markdown(src.get('content', ''))
                    else:
                        st.warning("참고할 문서를 찾지 못했습니다.")
                        
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Request Error: {e}")
