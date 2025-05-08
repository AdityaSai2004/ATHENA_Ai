import streamlit as st
from utils.gemini_utils import upload_and_cache_topic, ask_question, get_summary, generate_quiz, generate_flashcards_from_cache
import os
import json
import math
import random
import base64

# Page configuration with custom theme colors
st.set_page_config(
    page_title="Nova AI",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🚀"
)

# Load custom CSS
with open("utils/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to load local images
def get_image_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Get logo as base64
logo_base64 = get_image_base64("logo 2.svg")

# Colorful header with animation effect and logo
st.markdown(
    f"""
    <div class='header-container'>
        <div class='logo-container'>
            <img src="data:image/svg+xml;base64,{logo_base64}" class="logo-image"/>
            <h1>✨ Nova AI</h1>
        </div>
        <p class='subtitle'>Your magical learning adventure!</p>
    </div>
    """, 
    unsafe_allow_html=True
)

DATA_DIR = "books"
pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]
topic_files = {os.path.splitext(f)[0].capitalize(): os.path.join(DATA_DIR, f) for f in pdf_files}

# Session state for selected topic
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "cache_id" not in st.session_state:
    st.session_state.cache_id = None

# Topic selection with colorful design
st.markdown("<div class='section-header'>📚 Choose Your Adventure</div>", unsafe_allow_html=True)
topic = st.selectbox("Select a topic to learn about", ["Select..."] + list(topic_files.keys()))

#display utils
def display_flashcards_grid(flashcards):
    questions = flashcards.get("Question", [])
    answers = flashcards.get("Answer", [])

    num_flashcards = min(len(questions), len(answers))
    num_per_row = 3
    
    # Fun emoji list for flashcards
    card_emojis = ["🌟", "🚀", "🦄", "🐳", "🦋", "🌈", "🌻", "🐢", "🦁", "🐘", "🦊", "🐬"]

    for i in range(0, num_flashcards, num_per_row):
        cols = st.columns(num_per_row)

        for j in range(num_per_row):
            idx = i + j
            if idx < num_flashcards:
                # Get a random emoji for each card
                emoji = random.choice(card_emojis)
                
                with cols[j]:
                    with st.expander(f"{emoji} {questions[idx]}", expanded=False):
                        st.markdown(f"<div class='flashcard-answer'>**Answer:** {answers[idx]}</div>", unsafe_allow_html=True)

if topic != "Select..." and topic != st.session_state.selected_topic:
    with st.spinner("🔍 Loading your adventure..."):
        st.session_state.selected_topic = topic
        st.session_state.cache_id = upload_and_cache_topic(
            path=topic_files[topic],
            system_instruction="You are a kids learning assistant. Be fun, simple and clear."
        )
        st.success(f"🎉 {topic} is ready for exploration!")

# Interaction Modes with fun icons
if st.session_state.cache_id:
    st.markdown("<div class='section-header'>🎮 Choose Your Learning Mode</div>", unsafe_allow_html=True)
    
    mode = st.radio(
        "",
        ["Ask Questions", "Quiz Mode", "Revision Mode", "Flashcard Mode"],
        format_func=lambda x: {
            "Ask Questions": "🙋 Ask Questions",
            "Quiz Mode": "🎯 Quiz Mode",
            "Revision Mode": "📝 Revision Mode",
            "Flashcard Mode": "🃏 Flashcard Mode"
        }[x]
    )

    if mode == "Ask Questions":
        st.markdown(f"<div class='mode-description'>Ask anything about <span class='highlight'>{topic}</span> and I'll help you understand!</div>", unsafe_allow_html=True)
        
        user_q = st.text_input("💭 What would you like to know?", placeholder=f"Example: What is {topic} about?")
        
        if st.button("🔍 Find Answer") and user_q:
            print(f"User question: {user_q}")
            with st.spinner("🧠 Thinking..."):
                answer = ask_question(st.session_state.cache_id, user_q)

            st.markdown("<div class='answer-box'>", unsafe_allow_html=True)
            st.markdown(f"**Answer:** {answer}")
            st.markdown("</div>", unsafe_allow_html=True)

    elif mode == "Quiz Mode":
        st.markdown(f"<div class='mode-description'>Test your knowledge about <span class='highlight'>{topic}</span> with a fun quiz!</div>", unsafe_allow_html=True)
        
        if st.button("🎮 Start Quiz Challenge"):
            with st.spinner("🎲 Creating your quiz challenge..."):
                quiz = generate_quiz(st.session_state.cache_id)
            
            st.markdown("<div class='quiz-container'>", unsafe_allow_html=True)
            st.markdown(quiz)
            st.markdown("</div>", unsafe_allow_html=True)

    elif mode == "Revision Mode":
        st.markdown(f"<div class='mode-description'>Review the key points about <span class='highlight'>{topic}</span> in a fun way!</div>", unsafe_allow_html=True)
        
        if st.button("📚 Create Fun Summary"):
            with st.spinner("✨ Creating your magical summary..."):
                summary = get_summary(st.session_state.cache_id)
            
            st.markdown("<div class='summary-container'>", unsafe_allow_html=True)
            st.markdown(summary)
            st.markdown("</div>", unsafe_allow_html=True)

    elif mode == "Flashcard Mode":
        st.markdown(f"<div class='mode-description'>Practice with colorful flashcards about <span class='highlight'>{topic}</span>!</div>", unsafe_allow_html=True)
        
        if st.button("🃏 Create Flashcards"):
            with st.spinner("✂️ Creating your flashcards..."):
                # Generate flashcards from the cached content
                flashcards = generate_flashcards_from_cache(st.session_state.cache_id)
                if flashcards:
                    st.success("🎉 Your flashcards are ready! Click on each card to see the answer.")
                    
                    # Add some fun animations to the flashcards display
                    st.markdown("<div class='flashcards-container'>", unsafe_allow_html=True)
                    display_flashcards_grid(flashcards)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("😕 Oops! We couldn't create flashcards. Please try again.")
