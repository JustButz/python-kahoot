import streamlit as st

# --- SETUP ---
st.set_page_config(page_title="Python Kahoot Pro", layout="wide")

# Gemeinsamer Speicher für alle
@st.cache_resource
def get_global_state():
    return {"current_question": -1, "players": {}}

global_state = get_global_state()

QUESTIONS = [
    {"q": "Was ist 10 + 10?", "a": ["15", "20", "25", "30"], "correct": "20"},
    {"q": "Welches Tier bellt?", "a": ["Katze", "Hund", "Vogel", "Fisch"], "correct": "Hund"}
]

# --- REFRESH TRICK ---
# Das hier lässt die App alle 3 Sekunden neu laden, damit das Handy reagiert!
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=3000, key="datarefresh")

# --- UI ---
st.sidebar.title("🎮 Menü")
role = st.sidebar.radio("Rolle:", ["Spieler", "Host"])

if role == "Host":
    st.title("📺 Host-Monitor")
    if st.button("Nächste Frage ➡️"):
        global_state["current_question"] += 1
    if st.button("Reset 🔄"):
        global_state["current_question"] = -1
        global_state["players"] = {}
    
    curr_q = global_state["current_question"]
    if curr_q == -1:
        st.write("Warten auf Spieler... Dabei sind:", list(global_state["players"].keys()))
    elif curr_q < len(QUESTIONS):
        st.header(QUESTIONS[curr_q]["q"])
        st.write(f"Antworten erhalten: {len(global_state['players'])}")
    else:
        st.table(global_state["players"])

else:
    st.title("📱 Handy")
    if "name" not in st.session_state:
        n = st.text_input("Name:")
        if st.button("Los"):
            st.session_state.name = n
            global_state["players"][n] = 0
    else:
        curr_q = global_state["current_question"]
        if curr_q == -1:
            st.info("Warte bis der Host startet...")
        elif curr_q < len(QUESTIONS):
            st.subheader("Wähle:")
            for ans in QUESTIONS[curr_q]["a"]:
                if st.button(ans, use_container_width=True):
                    if ans == QUESTIONS[curr_q]["correct"]:
                        global_state["players"][st.session_state.name] += 1
                    st.success("Gespeichert!")
        else:
            st.write("Spiel vorbei!")
