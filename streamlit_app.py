import streamlit as st
import requests
from PIL import Image
import io
import base64
import pandas as pd

API_URL = "http://localhost:8000"


QUESTIONS = [
    {"key": "age", "question": "What is your age?", "type": "string"},
    {"key": "income", "question": "What is your monthly income (in INR)?", "type": "string"},
    {"key": "employmentType", "question": "What is your employment type?", "type": "select", "options": ["salaried", "self-employed"]},
    {"key": "spending", "question": "How much do you spend monthly on your preferred category (e.g., fuel, shopping, travel, etc.)?", "type": "string"},
]

st.set_page_config(page_title="Credit Card Chatbot", page_icon="💳", layout="centered")
st.title("💳 Credit Card Recommendation Chatbot")

if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "structured_input" not in st.session_state:
    st.session_state.structured_input = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
if "compare" not in st.session_state:
    st.session_state.compare = set()
if "show_summary" not in st.session_state:
    st.session_state.show_summary = False


def reset_all():
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.structured_input = None
    st.session_state.recommendations = None
    st.session_state.compare = set()
    st.session_state.show_summary = False


def ask_question():
    step = st.session_state.step
    if step < len(QUESTIONS):
        q = QUESTIONS[step]
        if q["type"] == "number":
            value = st.number_input(q["question"], min_value=0, key=q["key"])
        elif q["type"] == "select":
            value = st.selectbox(q["question"], q["options"], key=q["key"])
        else:
            value = st.text_input(q["question"], key=q["key"])
        if st.button("Next", key=f"next_{step}"):
            st.session_state.answers[q["key"]] = value
            st.session_state.step += 1
            st.rerun()
    else:
        # All questions answered, show summary and call API
        st.write("\nGreat! Let's process your answers...")
        if st.button("Submit", key="submit_all"):
            process_answers()

def process_answers():
    # Call /parse-input
    try:
        resp = requests.post(f"{API_URL}/parse-input", json=st.session_state.answers)
        resp.raise_for_status()
        st.session_state.structured_input = resp.json()["structured_input"]
    except Exception as e:
        st.error(f"Failed to parse input: {e}")
        return
    # Call /recommend
    try:
        rec = requests.post(f"{API_URL}/recommend", json=st.session_state.structured_input)
        rec.raise_for_status()
        st.session_state.recommendations = rec.json()
        st.session_state.show_summary = True
        st.rerun()
    except Exception as e:
        st.error(f"Failed to get recommendations: {e}")
        return

def show_summary():
    recs = st.session_state.recommendations
    if not recs:
        st.error("No recommendations found.")
        return
    st.header("Recommended Cards for You")
    cards = recs["cards"]
    reasons = recs.get("reasons", "")
    for idx, card in enumerate(cards):
        with st.container():
            cols = st.columns([1, 2])
            # Card image
            with cols[0]:
                if card.get("cardImage"):
                    try:
                        img_bytes = base64.b64decode(card["cardImage"])
                        st.image(img_bytes, width=120)
                    except Exception:
                        st.write("[Image not available]")
            # Card details
            with cols[1]:
                st.subheader(card["cardName"])
                st.write(f"**Reward Type:** {card.get('rewardType', '-')}")
                st.write(f"**Reward Rate:** {' to '.join([str(i) for i in card.get('rewardRate', '-')])}%")
                st.write(f"**Joining Fee:** ₹{card.get('joiningFee', '-')}")
                st.write(f"**Annual Fee:** ₹{card.get('annualFee', '-')}")
                st.write(f"**Eligibility:** {card.get('eligibility', '-')}")
                st.write(f"**Features:** {card.get('features', '-')}")
                #print(card.get('spending'))
                if card.get('spending'):
                    reward_sim = card.get('spending') * max(card.get('rewardRate')) // 100
                    st.write(f"**You could earn ₹{reward_sim}/month on {card.get('rewardType', '-')}**")
                st.checkbox("Compare", key=f"compare_{idx}", on_change=lambda i=idx: st.session_state.compare.add(i))
    if reasons:
        st.markdown("---")
        st.write("**Why these cards?**")
        # Convert reasons list to a pandas DataFrame for better display
        reasons_df = pd.DataFrame(reasons)
        # Assuming each reason is a dict with card name as key and reason as value
        reasons_table = pd.DataFrame({
            'Card': [list(r.keys())[0] for r in reasons],
            'Reason': [list(r.values())[0] for r in reasons]
        })
        st.table(reasons_table)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Compare Selected Cards"):
            show_comparison()
    with col2:
        if st.button("Restart"):
            reset_all()
            st.rerun()

def show_comparison():
    recs = st.session_state.recommendations
    cards = recs["cards"]
    selected = [cards[i] for i in st.session_state.compare]
    if not selected:
        st.warning("Select cards to compare.")
        return
    st.header("Compare Cards")
    for card in selected:
        st.subheader(card["cardName"])
        st.write(f"**Reward Type:** {card.get('rewardType', '-')}")
        st.write(f"**Reward Rate:** {card.get('rewardRate', '-')}")
        st.write(f"**Joining Fee:** ₹{card.get('joiningFee', '-')}")
        st.write(f"**Annual Fee:** ₹{card.get('annualFee', '-')}")
        st.write(f"**Eligibility:** {card.get('eligibility', '-')}")
        st.write(f"**Features:** {card.get('features', '-')}")
        st.markdown("---")
    if st.button("Back to Recommendations"):
        st.session_state.show_summary = True
        st.rerun()

# Main app logic
if not st.session_state.show_summary:
    ask_question()
else:
    show_summary()
