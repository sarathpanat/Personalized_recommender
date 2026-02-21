import streamlit as st
import requests
import json
import os
import pandas as pd

st.set_page_config(page_title="Course Recommender")

API_URL = os.environ.get("BACKEND_URL", "http://localhost:8000") + "/recommend"
PROFILES_PATH = os.path.join(os.path.dirname(__file__), "profiles.json")


def load_profiles():
    if os.path.exists(PROFILES_PATH):
        with open(PROFILES_PATH) as f:
            return json.load(f)
    return {}


def save_profiles(profiles):
    with open(PROFILES_PATH, "w") as f:
        json.dump(profiles, f, indent=2)


# ── Page 1: Enter Name ──────────────────────────────────────────────────────
if "name" not in st.session_state:
    st.session_state.name = ""

if not st.session_state.name:
    st.title("Course Recommender")
    name = st.text_input("Enter your name")
    if st.button("Continue") and name.strip():
        profiles = load_profiles()
        if name not in profiles:
            profiles[name] = {"viewed_content_ids": []}
            save_profiles(profiles)
        st.session_state.name = name
        st.rerun()
    st.stop()


# ── Page 2: Preferences + Recommendations ───────────────────────────────────
name = st.session_state.name
profiles = load_profiles()
viewed = profiles.get(name, {}).get("viewed_content_ids", [])

st.title(f"Hi {name}!")

if viewed:
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_data.csv')
    course_df = pd.read_csv(DATA_PATH)
    id_to_title = dict(zip(course_df['id'], course_df['title']))
    viewed_titles = [f"{id_to_title.get(cid, f'ID {cid}')}" for cid in viewed]
    st.info("Previously viewed:\n" + "\n".join(f"• {t}" for t in viewed_titles))

st.divider()
st.subheader("What do you want to learn?")

# Topic is mandatory
topic = st.text_input("Topic *", placeholder="e.g. Docker for machine learning")

# Optional filters — map directly to CSV columns
col1, col2, col3 = st.columns(3)
with col1:
    difficulty = st.selectbox("Difficulty", ["", "Beginner", "Intermediate", "Advanced"])
with col2:
    #time_per_day = st.number_input("Time per Day (mins)", min_value=0, max_value=240, value=0, step=15)
    time_per_day = st.selectbox(
        "Time per Day (mins)",
        options=[None, 15, 30, 45, 60, 90, 120],
        format_func=lambda x: "No preference" if x is None else f"{x} mins"
    )
with col3:
    learning_style = st.selectbox("Learning Style", ["", "video", "article", "blog"])

if "recs" not in st.session_state:
    st.session_state["recs"] = None  # None = not clicked yet, [] = clicked but no results

if st.button("Get Recommendations", use_container_width=True, key="get_recs_btn"):
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Finding best courses..."):
            payload = {
                "name": name,
                "topic": topic,
                "difficulty": difficulty or None,
                "time_per_day_minutes": time_per_day,
                "learning_style": learning_style or None,
                "viewed_content_ids": viewed
            }
            resp = requests.post(API_URL, json=payload, timeout=120)
            resp.raise_for_status()
            st.session_state["recs"] = resp.json()  # will be [] if no results

# ── Results ──────────────────────────────────────────────────────────────────
recs = st.session_state.get("recs", None)

if recs is None:
    pass  # button not clicked yet, show nothing
elif not recs:
    st.warning("No relevant courses found. Try a topic within 'Kubernetes', 'Machine Learning', 'Docker'.")
else:
    profiles = load_profiles()
    viewed = profiles[name]["viewed_content_ids"]
    st.subheader("Top Recommendations")
    for i, rec in enumerate(recs):
        with st.container(border=True):
            col_text, col_action = st.columns([4, 1])
            with col_text:
                st.markdown(f"**{i+1}. {rec['title']}**")
                st.caption(
                    f"`{rec.get('format', '').upper()}` | "
                    f"{rec.get('difficulty')} | "
                    f"⏱ {rec.get('duration_minutes')} mins"
                )
                st.write(rec.get("explanation", ""))
                if rec.get("url"):
                    st.markdown(f"[Open Course ↗]({rec['url']})")
            with col_action:
                rec_id = rec["id"]
                if rec_id in viewed:
                    st.success("✅ Viewed")
                elif st.button("Mark Viewed", key=f"v_{rec_id}"):
                    profiles[name]["viewed_content_ids"].append(rec_id)
                    save_profiles(profiles)
                    st.session_state["recs"] = None
                    st.rerun()

st.divider()
if st.button("← Switch User"):
    st.session_state.name = ""
    st.session_state["recs"] = []
    st.rerun()