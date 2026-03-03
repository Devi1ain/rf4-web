import streamlit as st
from supabase import create_client, Client
import requests

# --- НАСТРОЙКИ ---
SUPABASE_URL = "https://bjxvmbttkspbakjolmke.supabase.co"
SUPABASE_KEY = "sb_publishable_XUAIfY1ERJ_IqLozzUx0FQ_o8PHdHs9"
TG_TOKEN = "ТОКЕН_ТВОЕГО_БОТА"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="РР4: Заказы на водоемах", layout="wide")

# Функция получения живой ссылки на фото из Telegram
def get_tg_url(file_id):
    if not file_id: return None
    res = requests.get(f"https://api.telegram.org{TG_TOKEN}/getFile?file_id={file_id}").json()
    if res.get('ok'):
        return f"https://api.telegram.org{TG_TOKEN}/{res['result']['file_path']}"
    return None

st.title("🔎 Мониторинг заказов Русская Рыбалка 4")

# Загружаем данные из базы
response = supabase.table("fishing_orders").select("*").execute()
data = response.data

if not data:
    st.info("Данные еще не поступили. Запустите скрипт на ПК.")
else:
    # Боковое меню со списком водоемов
    names = [item['wood_name'] for item in data]
    selected_wood = st.sidebar.radio("Выберите водоем:", names)

    # Находим данные по выбранному водоему
    current_data = next(item for item in data if item['wood_name'] == selected_wood)
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Скриншот")
        img_url = get_tg_url(current_data['tg_file_id'])
        if img_url:
            st.image(img_url, use_container_width=True)
        else:
            st.warning("Изображение недоступно")

    with col2:
        st.subheader("Список заказов")
        orders = current_data['json_data'] # Это наш список из 8 заказов
        
        for order in orders:
            with st.expander(f"🐟 {order['fish']}", expanded=True):
                c1, c2 = st.columns(2)
                c1.metric("Кол-во", f"{order['count']} шт.")
                c2.metric("Истекает", order['date'])

    st.caption(f"Последнее обновление базы: {current_data['updated_at']}")
