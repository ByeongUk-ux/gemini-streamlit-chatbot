
import streamlit as st
from google import genai
from google.genai import types

# 1. 웹사이트 기본 설정
st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖")
st.title("🤖 My Gemini Chatbot")

# 2. Gemini API 연결
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL = "gemini-3.5-flash-lite"

# 3. 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 기존 대화 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요"):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. Gemini API에 전달할 대화 기록 변환
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=m["content"])]
        )
        for m in st.session_state.messages
    ]

    # 7. Gemini 응답을 실시간으로 받아오는 함수
    def generate_response():
        stream = client.models.generate_content_stream(
            model=MODEL,
            contents=contents
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text

    # 8. 답변 출력 및 저장
    with st.chat_message("assistant"):
        try:
            response = st.write_stream(generate_response())
        except Exception as e:
            st.error(f"API 호출 실패: {e}")
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

