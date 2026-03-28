import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Эко-трекер Борисов", page_icon="🌳", layout="wide")

st.markdown("""
    <style>
    .stButton>button { background-color: #22c55e; color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "eco_diary.csv"

# --- РЕАЛЬНЫЙ СПИСОК ШКОЛ БОРИСОВА ---
borisov_schools = [
    "Гимназия № 1 г. Борисова", "Гимназия № 3 г. Борисова", 
    "Средняя школа № 2 г. Борисова", "Средняя школа № 3 г. Борисова", 
    "Средняя школа № 7 г. Борисова", "Средняя школа № 8 г. Борисова", 
    "Средняя школа № 9 г. Борисова", "Средняя школа № 10 г. Борисова", 
    "Средняя школа № 11 г. Борисова", "Средняя школа № 12 г. Борисова", 
    "Средняя школа № 13 г. Борисова", "Средняя школа № 16 г. Борисова", 
    "Средняя школа № 17 г. Борисова", "Средняя школа № 18 г. Борисова", 
    "Средняя школа № 20 г. Борисова", "Средняя школа № 22 г. Борисова", 
    "Средняя школа № 23 г. Борисова", "Средняя школа № 24 г. Борисова", 
    "Лошницкая гимназия", "Лошницкая средняя школа", "Зембинская средняя школа", 
    "Большеухолодская средняя школа", "Велятичская средняя школа", 
    "Ганцевичская средняя школа", "Метченская средняя школа", "Другое учебное заведение"
]

# --- БОКОВАЯ ПАНЕЛЬ (Профиль) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Coat_of_Arms_of_Barysa%C5%AD.svg/992px-Coat_of_Arms_of_Barysa%C5%AD.svg.png", width=100)
st.sidebar.title("Профиль Активиста")
user_name = st.sidebar.text_input("Твое имя", "Ученик")
school_name = st.sidebar.selectbox("Учебное заведение", borisov_schools)

st.sidebar.divider()
st.sidebar.info(f"📍 Локация: г. Борисов\n📅 Дата: {datetime.date.today()}")

# --- ОСНОВНОЙ ЭКРАН ---
st.title("🌱 Мой CO2-след: Адаптация к климату")
st.write(f"Привет, {user_name} из {school_name}! Давай посчитаем твой углеродный след за сегодняшний школьный день.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Дорога в школу")
    transport_type = st.radio(
        "Как ты сегодня добирался?",
        ["Пешком / Велосипед", "Электробус / Трамвай", "Автобус (ДВС)", "Легковой автомобиль"]
    )
    km = st.slider("Сколько километров преодолел?", 0.0, 30.0, 3.0, step=0.5)

    coeff_transport = {"Пешком / Велосипед": 0.0, "Электробус / Трамвай": 0.02, "Автобус (ДВС)": 0.1, "Легковой автомобиль": 0.2}
    co2_transport = km * coeff_transport[transport_type]

with col2:
    st.subheader("🍱 Школьный обед")
    diet = st.selectbox("Что было на обед?", ["Каша / Овощи (Вегетарианский)", "Птица / Рыба (Смешанный)", "Мясо / Сосиска (Мясной)"])
    waste = st.checkbox("Я сегодня отсортировал(а) свой мусор ♻️")
    
    diet_map = {"Каша / Овощи (Вегетарианский)": 0.5, "Птица / Рыба (Смешанный)": 1.0, "Мясо / Сосиска (Мясной)": 1.8}
    co2_food = diet_map[diet]
    if waste: co2_food = max(0.1, co2_food - 0.3)

# --- РАСЧЕТЫ И ГРАФИКИ ---
total_co2 = co2_transport + co2_food
st.divider()

res_col1, res_col2 = st.columns([1, 1.5])

with res_col1:
    st.metric(label="Твой углеродный след (кг CO2)", value=f"{total_co2:.2f}")
    trees_needed = total_co2 / 0.06 
    st.info(f"🔬 Биологический факт: Чтобы переработать этот CO2 через фотосинтез, нужно {int(trees_needed) + 1} взрослых деревьев!")
    
    # Блок уровней
    if total_co2 < 1.0:
        st.success("✅ Уровень: Климатический Герой!")
    elif total_co2 < 2.0:
        st.warning("⚠️ Уровень: Обычный горожанин.")
    else:
        st.error("🆘 Уровень: Высокий след.")

with res_col2:
    data = pd.DataFrame({'Категория': ['Транспорт', 'Питание'], 'Выбросы (кг)': [co2_transport, co2_food]})
    fig = px.pie(data, values='Выбросы (кг)', names='Категория', title='Структура твоего следа', hole=.4, color_discrete_sequence=['#3b82f6', '#10b981'])
    st.plotly_chart(fig, use_container_width=True)
# --- СОХРАНЕНИЕ ---
st.divider()

if st.button("Сохранить результат в базу данных"):
    # 1. ЗАЩИТА ОТ "ЛЕВЫХ" ДАННЫХ
    if user_name.strip() == "" or user_name.strip() == "Ученик":
        st.error("🛑 Ошибка: Пожалуйста, введи свое реальное имя в профиле слева перед сохранением!")
    else:
        # Уникальный слепок текущих данных
        current_entry = f"{user_name}_{school_name}_{total_co2}"
        
        # 2. ЗАЩИТА ОТ ДУБЛИКАТОВ И ОБНОВЛЕНИЯ СТРАНИЦЫ (F5)
        if "last_saved" in st.session_state and st.session_state.last_saved == current_entry:
            st.warning("⚠️ Эти данные уже сохранены! Если хочешь добавить новую запись, измени показатели.")
        else:
            new_data = pd.DataFrame([{
                "Дата": datetime.date.today(), "Имя": user_name, "Школа": school_name,
                "Транспорт (кг)": round(co2_transport, 2), "Еда (кг)": round(co2_food, 2), "Итог (кг CO2)": round(total_co2, 2)
            }])
            
            if os.path.exists(DB_FILE):
                new_data.to_csv(DB_FILE, mode='a', header=False, index=False)
            else:
                new_data.to_csv(DB_FILE, mode='w', header=True, index=False)
                
            # Запоминаем, что мы только что сохранили, чтобы не дублировать
            st.session_state.last_saved = current_entry
            
            if "data_editor" in st.session_state:
                del st.session_state["data_editor"]
                
            st.success(f"Отлично, {user_name}! Твои данные успешно добавлены в рейтинг.")
            st.balloons()

# --- АНАЛИТИКА И РЕДАКТИРОВАНИЕ (ВКЛАДКИ) ---
st.subheader("📊 Аналитика и База данных")

tab1, tab2 = st.tabs(["💾 Управление данными (Редактор)", "🏆 Рейтинг школ (Средний след)"])

with tab1:
    st.write("Здесь хранятся все записи. Ты можешь изменить любую цифру или удалить ошибочную строку (выдели строку слева и нажми Delete).")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="data_editor")
        
        if st.button("💾 Сохранить изменения в таблице"):
            edited_df.to_csv(DB_FILE, index=False)
            st.success("Изменения успешно применены к базе данных!")
    else:
        st.info("База данных пока пуста.")

with tab2:
    st.write("Соревнование школ! Чем МЕНЬШЕ средний углеродный след учеников, тем выше школа в рейтинге.")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if not df.empty:
            school_rating = df.groupby("Школа")["Итог (кг CO2)"].mean().reset_index()
            school_rating = school_rating.sort_values(by="Итог (кг CO2)", ascending=True)
            school_rating.columns = ["Учебное заведение", "Средний след (кг CO2)"]
            
            fig_rating = px.bar(
                school_rating, x="Учебное заведение", y="Средний след (кг CO2)", 
                title="Эко-рейтинг школ Борисова (Лидеры слева)",
                color="Средний след (кг CO2)", color_continuous_scale="Greens_r" 
            )
            st.plotly_chart(fig_rating, use_container_width=True)
            st.dataframe(school_rating, use_container_width=True, hide_index=True)
        else:
            st.info("Добавьте данные, чтобы увидеть рейтинг.")
    else:
        st.info("База данных пока пуста.")

st.caption("Разработано для конкурса экоактивистов г. Борисов.")