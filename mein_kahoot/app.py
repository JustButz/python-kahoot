import streamlit as st
from streamlit_autorefresh import st_autorefresh

# --- SETUP & DESIGN ---
st.set_page_config(page_title="Python Kahoot Pro", layout="wide")

# Alle 2 Sekunden aktualisieren, damit Handy & Host synchron sind
st_autorefresh(interval=2000, key="global_refresh")

# --- GEMEINSAMER SPEICHER (Für alle Nutzer) ---
@st.cache_resource
def get_global_state():
    return {
        "current_question": -1, 
        "players": {}, # Speichert {Name: Punkte}
        "active": False
    }

global_data = get_global_state()

# --- FRAGENKATALOG ---
QUESTIONS = [
    {"q": "Was ist die Hauptstadt von Frankreich?", "a": ["Berlin", "Madrid", "Paris", "Rom"], "correct": "Paris"},
    {"q": "Welche Programmiersprache nutzen wir hier?", "a": ["Java", "C++", "Python", "PHP"], "correct": "Python"},
    {"q": "Was ist 12 * 12?", "a": ["122", "144", "148", "164"], "correct": "144"},
    {"q": "Wie viele Kontinente gibt es?", "a": ["5", "6", "7", "8"], "correct": "7"},
    {"q": "Welches Element hat das Symbol 'O'?", "a": ["Gold", "Sauerstoff", "Eisen", "Silber"], "correct": "Sauerstoff"},
    {"q": "Wer hat die Relativitätstheorie aufgestellt?", "a": ["Newton", "Tesla", "Einstein", "Hawking"], "correct": "Einstein"}
]

# --- SIDEBAR ---
role = st.sidebar.radio("Rolle wählen:", ["Spieler (Handy)", "Host (Beamer)"])

# --- HOST LOGIK ---
if role == "Host (Beamer)":
    st.title("📺 Kahoot Host Monitor")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Nächste Frage ➡️", use_container_width=True):
            global_data["current_question"] += 1
            # Reset der Antwort-Sperre für alle Spieler (simuliert)
            st.rerun()
    with col2:
        if st.button("Spiel Neustarten 🔄", use_container_width=True):
            global_data["current_question"] = -1
            global_data["players"] = {}
            st.rerun()

    curr_q = global_data["current_question"]
    
    if curr_q == -1:
        st.subheader("Warten auf Spieler...")
        st.write("Aktuelle Teilnehmer:", ", ".join(global_data["players"].keys()) if global_data["players"] else "Keiner")
    elif curr_q < len(QUESTIONS):
        st.header(f"Frage {curr_q + 1}: {QUESTIONS[curr_q]['q']}")
        st.info("Schau auf dein Handy zum Antworten!")
        # Leaderboard live anzeigen
        st.write("---")
        st.subheader("Punktestand:")
        st.json(global_data["players"])
    else:
        st.balloons()
        st.header("🏆 Endergebnis")
        # Sortiertes Leaderboard
        sorted_players = dict(sorted(global_data["players"].items(), key=lambda item: item[1], reverse=True))
        for i, (name, score) in enumerate(sorted_players.items()):
            st.subheader(f"{i+1}. {name}: {score} Punkte")

# --- SPIELER LOGIK ---
else:
    st.title("📱 Dein Controller")
    
    # 1. Login
    if "my_name" not in st.session_state:
        name = st.text_input("Dein Nickname:")
        if st.button("Beitreten"):
            if name:
                st.session_state.my_name = name
                if name not in global_data["players"]:
                    global_data["players"][name] = 0
                st.rerun()
    else:
        name = st.session_state.my_name
        curr_q = global_data["current_question"]
        
        # Zeige Punkte immer oben an
        st.sidebar.write(f"Spieler: **{name}**")
        st.sidebar.write(f"Deine Punkte: **{global_data['players'].get(name, 0)}**")

        if curr_q == -1:
            st.warning("Warte, bis der Host das Spiel startet...")
        elif curr_q < len(QUESTIONS):
            q_data = QUESTIONS[curr_q]
            
            # Verhindern, dass man mehrfach antwortet (pro Frage)
            # Wir speichern die letzte beantwortete Frage im lokalen session_state
            if "last_answered" not in st.session_state:
                st.session_state.last_answered = -1
            
            if st.session_state.last_answered < curr_q:
                st.subheader("Wähle die richtige Antwort:")
                
                # Button-Grid
                for option in q_data["a"]:
                    if st.button(option, use_container_width=True):
                        st.session_state.last_answered = curr_q
                        if option == q_data["correct"]:
                            global_data["players"][name] += 1
                            st.session_state.last_result = "RICHTIG! ✅"
                        else:
                            st.session_state.last_result = f"FALSCH! ❌ (Richtig war: {q_data['correct']})"
                        st.rerun()
            else:
                # Feedback nach der Antwort
                st.info(st.session_state.get("last_result", "Antwort gespeichert!"))
                st.write("Warte auf die nächste Frage vom Host...")
        else:
            st.success("Spiel beendet! Schau auf das Leaderboard.")
