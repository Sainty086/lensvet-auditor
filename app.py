import streamlit as st
import google.generativeai as genai
import tempfile
import os

# ==========================================
# 1. НАСТРОЙКИ БЕЗОПАСНОСТИ И ДОСТУПА
# ==========================================
# Вставь сюда свой реальный API-ключ внутри кавычек
MY_API_KEY = st.secrets["GEMINI_API_KEY"] 

# Придумай пароль для коллег
APP_PASSWORD = "MartiniMartini" 


# ==========================================
# 2. ИНТЕРФЕЙС И ПРОВЕРКА ПАРОЛЯ
# ==========================================
# ИЗМЕНЕНИЕ 1: Убрали layout="wide". Теперь страница центрирована и ограничена ~730px (как ширина чата)
st.set_page_config(page_title="Аудитор Ленсвет", page_icon="💡", layout="centered")
st.title("🕵️‍♂️ ИИ-Аудитор паспортов светильников")

# ИЗМЕНЕНИЕ 2: Создаем колонки. Левая (input_col) займет 2/3 от 730px (примерно 480px).
input_col, empty_col = st.columns([2, 1])

with input_col:
    # Кладем поле пароля в узкую колонку
    user_password = st.text_input("🔒 Введите пароль для доступа:", type="password")

# Шлагбаум пароля
if user_password != APP_PASSWORD:
    st.warning("Пожалуйста, введите верный пароль для начала работы.")
    st.stop() 

st.success("Доступ разрешен!")
st.write("Загрузите паспорт в формате PDF, и система проверит его на соответствие требованиям СПб ГБУ «Ленсвет».")


# ==========================================
# 3. НАСТРОЙКА API И ПРОМПТ
# ==========================================
genai.configure(api_key=MY_API_KEY)

system_prompt = """
[СЮДА ВСТАВЬ ПОЛНЫЙ ТЕКСТ НАШЕГО ИТОГОВОГО ПРОМПТА ИЗ ПРЕДЫДУЩЕГО ШАГА]
"""


# ==========================================
# 4. ЛОГИКА ЗАГРУЗКИ И ПРОВЕРКИ
# ==========================================
with input_col:
    # Кладем загрузчик файла и кнопку тоже в узкую колонку
    uploaded_file = st.file_uploader("Загрузите паспорт (только PDF)", type=["pdf"])
    start_button = st.button("🚀 Начать проверку", use_container_width=True)

if uploaded_file is not None:
    if start_button:
        with st.spinner("Изучаю ГОСТы и анализирую документ..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                    
                uploaded_pdf = genai.upload_file(path=tmp_path, mime_type="application/pdf")
                
                response = model.generate_content([system_prompt, uploaded_pdf])
                
                # Вывод ответа (таблицы) идет вне узкой колонки, 
                # поэтому он займет всю доступную ширину по центру (те самые комфортные ~730px)
                st.markdown("---")
                st.markdown(response.text)
                
                os.remove(tmp_path)
                
            except Exception as e:
                st.error(f"Произошла ошибка при обращении к API: {e}")
