import streamlit as st

import pandas as pd

import time

import re

import json

import os

from datetime import datetime



# ==========================================

# CONSTANTS & CONFIGURATION

# ==========================================



st.set_page_config(

    page_title="The Business Level-Up Challenge",

    page_icon="🎮",

    layout="centered"

)



# Custom CSS to match the "Mountain Monk" branding

st.markdown("""

    <style>

    .stApp {

        background-color: #f8fafc;

        font-family: 'Inter', sans-serif;

    }

    .brand-header {

        color: #f05a37;

        font-weight: 800;

        text-align: center;

        text-transform: uppercase;

        letter-spacing: 0.1em;

    }

    .big-title {

        color: #1e293b;

        font-weight: 900;

        text-align: center;

        margin-bottom: 1rem;

    }

    .stButton>button {

        background-color: #f05a37;

        color: white;

        border-radius: 0.5rem;

        border: none;

        padding: 0.5rem 1rem;

        font-weight: 600;

        width: 100%;

        transition: all 0.3s;

    }

    .stButton>button:hover {

        background-color: #d64d2e;

        color: white;

        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);

    }

    .card {

        background-color: white;

        padding: 1.5rem;

        border-radius: 1rem;

        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);

        border: 1px solid #e2e8f0;

        margin-bottom: 1rem;

    }

    .timer-box {

        font-family: monospace;

        font-weight: bold;

        color: #f05a37;

        font-size: 1.2rem;

        text-align: right;

    }

    </style>

""", unsafe_allow_html=True)



QUESTIONS = {

  "Level 1: The Stats": [

      {

        "question": "The Squad Size: How big is the team right now?",

        "options": ["Small & Agile (5–20 people)", "Scaling Up (20–80 people)", "Large Army (80+ people)"],

      },

      {

        "question": "The Scoreboard (Annual Revenue): What league is the business currently playing in financially?",

        "options": ["The Challenger League (Below ₹20 Cr)", "The Professional League (₹20–100 Cr)", "The Premier League (₹100+ Cr)"],

      }

  ],

  "Level 2: The Gameplay": [

     {

       "question": "The Decision Matrix: It’s Tuesday morning. A big decision needs to be made. What happens?",

       "options": ["Everyone looks at me. I make the call.", "My leaders debate it, but they eventually text me for the final 'Yes/No.'", "My leaders handle it using our governance framework."],

     },

     {

       "question": "The Blueprint (Org Structure): If a stranger looked at your Org Chart, what would they see?",

       "options": ["What chart? We just wear multiple hats.", "It exists on paper, but lines are blurry.", "A clear map where everyone knows ownership."],

     },

     {

       "question": "The Playbook (Processes): If you went on a silent retreat for 2 weeks, how does work get done?",

       "options": ["Tribal knowledge—people just 'know'.", "We have SOPs, but people ignore them.", "Like a Swiss watch—processes are followed."],

     },

     {

       "question": "The Boss Battle (Primary Challenge): What is the one monster keeping you awake at night?",

       "options": ["Survival Mode: Cash flow & chaos.", "Growing Pains: Hiring & communication.", "Velocity: Breaking silos to move faster."],

     }

  ],

  "Level 3: The Engine": [

     {

       "question": "The Captain’s Chair (Dependency): If you stepped away for a month, what happens to the ship?",

       "options": ["It sinks. I am the engine.", "It floats, but goes in circles.", "It sails fine, but might miss a turn."],

     },

     {

       "question": "The Radar (Data): How do you know if you’re winning or losing right now?",

       "options": ["Gut feeling and bank balance.", "I get reports, but they are messy/late.", "Real-time dashboards and reviews."],

     },

     {

       "question": "The Fuel (Sales Rhythm): Describe your sales engine.",

       "options": ["Feast or Famine.", "Team exists, but unpredictable.", "Predictable machine needing margins."],

     }

  ],

  "Level 4: The Vibe": [

      {

        "question": "The Squad (Culture): How much 'babysitting' does the team need?",

        "options": ["A lot. Work slows without me.", "Leaders try, but ownership varies.", "High ownership everywhere."],

      },

      {

        "question": "The Horizon (Vision): Where are your eyes focused right now?",

        "options": ["Next week. Keeping lights on.", "Next year. New cities/products.", "Next decade. Domination & legacy."],

      },

      {

        "question": "Your Avatar (Current Role): Be honest, what is your actual job title?",

        "options": ["Chief Firefighter.", "The Referee.", "The Architect."],

      }

  ],

}



QUESTION_TIME = 15



# ==========================================

# STATE MANAGEMENT

# ==========================================



if 'page' not in st.session_state:

    st.session_state.page = 'home'

if 'user' not in st.session_state:

    st.session_state.user = {}

if 'score' not in st.session_state:

    st.session_state.score = 0

if 'asked_questions' not in st.session_state:

    st.session_state.asked_questions = {cat: [] for cat in QUESTIONS.keys()}

if 'user_answers' not in st.session_state:

    st.session_state.user_answers = []

if 'current_question_data' not in st.session_state:

    # holds {category, question_obj, start_time}

    st.session_state.current_question_data = None 



# ==========================================

# HELPERS

# ==========================================



def reset_game():

    st.session_state.page = 'home'

    st.session_state.user = {}

    st.session_state.score = 0

    st.session_state.asked_questions = {cat: [] for cat in QUESTIONS.keys()}

    st.session_state.user_answers = []

    st.session_state.current_question_data = None



def get_leaderboard():

    if os.path.exists('leaderboard.json'):

        with open('leaderboard.json', 'r') as f:

            return json.load(f)

    return []



def save_score(user, score):

    data = get_leaderboard()

    data.append({

        "name": user['name'],

        "score": score,

        "industry": user['industry'],

        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    })

    # Sort and keep top 50

    data = sorted(data, key=lambda x: x['score'], reverse=True)[:50]

    with open('leaderboard.json', 'w') as f:

        json.dump(data, f)



# ==========================================

# SCREENS

# ==========================================



def render_home():

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("<div class='brand-header'>Mountain Monk Consulting</div>", unsafe_allow_html=True)

    st.markdown("<h1 class='big-title'>The Business Level-Up Challenge 🎮</h1>", unsafe_allow_html=True)

    

    st.markdown("""

    <div style='text-align: center; max-width: 600px; margin: 0 auto; color: #475569;'>

        Every business is playing a game, but the rules change as you scale. 

        <br><br>

        Answer rapid-fire questions to discover your "Player Class" and unlock cheat codes for your next peak.

    </div>

    <br><br>

    """, unsafe_allow_html=True)

    

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        if st.button("CLICK TO ENTER", use_container_width=True):

            st.session_state.page = 'form'

            st.rerun()



def render_form():

    st.markdown("<h2 style='text-align:center'>Player Registration</h2>", unsafe_allow_html=True)

    

    with st.form("user_form"):

        name = st.text_input("Full Name")

        mobile = st.text_input("Mobile No (10 digits)")

        business_name = st.text_input("Business Name")

        website = st.text_input("Business Website (Optional)")

        industry = st.text_input("Industry")

        email = st.text_input("Business Email")

        

        submitted = st.form_submit_button("Start Challenge")

        

        if submitted:

            # Validation

            if not (name and mobile and business_name and industry and email):

                st.error("Please fill in all mandatory fields.")

            elif not re.match(r'^\d{10}$', mobile.strip()):

                st.error("Mobile number must be exactly 10 digits.")

            else:

                st.session_state.user = {

                    "name": name,

                    "mobile": mobile,

                    "businessName": business_name,

                    "businessWebsite": website,

                    "industry": industry,

                    "email": email

                }

                st.session_state.page = 'game'

                st.rerun()



def render_game():

    # Progress Calculation

    total_q = sum(len(q) for q in QUESTIONS.values())

    asked_q_count = sum(len(q) for q in st.session_state.asked_questions.values())

    

    # Auto-redirect to results if done

    if total_q > 0 and asked_q_count == total_q:

        st.session_state.page = 'result'

        st.rerun()

        return



    # Header

    col1, col2 = st.columns([2, 1])

    with col1:

        st.markdown(f"**XP Score:** {st.session_state.score:,}")

    with col2:

        progress = asked_q_count / total_q

        st.progress(progress, text=f"Progress {int(progress*100)}%")



    st.markdown("### Choose Your Battle")

    

    categories = list(QUESTIONS.keys())

    

    # Render Category Cards

    for idx, category in enumerate(categories):

        # Logic for locking/exhausting levels

        cat_questions = QUESTIONS[category]

        asked_in_cat = st.session_state.asked_questions[category]

        remaining = len(cat_questions) - len(asked_in_cat)

        

        is_exhausted = remaining == 0

        is_locked = False

        if idx > 0:

            prev_cat = categories[idx - 1]

            if len(st.session_state.asked_questions[prev_cat]) < len(QUESTIONS[prev_cat]):

                is_locked = True

        

        # UI for Card

        card_style = "opacity: 0.5; background: #f1f5f9;" if is_locked or is_exhausted else "border-left: 5px solid #f05a37;"

        status_icon = "✅" if is_exhausted else "🔒" if is_locked else "⚔️"

        

        st.markdown(f"""

        <div class="card" style="{card_style}">

            <div style="display:flex; justify-content:space-between; align-items:center;">

                <h4 style="margin:0; color: #334155;">{status_icon} {category}</h4>

                <span style="font-size:0.8rem; color: #64748b;">

                    { 'Completed' if is_exhausted else 'Locked' if is_locked else f'{remaining} Challenges'}

                </span>

            </div>

        </div>

        """, unsafe_allow_html=True)

        

        if not is_locked and not is_exhausted:

            if st.button(f"Enter {category}", key=f"btn_{category}"):

                # Pick next question

                next_q = [q for q in cat_questions if q not in asked_in_cat][0]

                st.session_state.current_question_data = {

                    "category": category,

                    "question": next_q,

                    "start_time": time.time()

                }

                st.session_state.page = 'question'

                st.rerun()



def render_question():

    q_data = st.session_state.current_question_data

    if not q_data:

        st.session_state.page = 'game'

        st.rerun()

        return



    category = q_data['category']

    question_obj = q_data['question']

    

    # Timer Logic (Visual mainly, logic handled on submit)

    elapsed = time.time() - q_data['start_time']

    time_left = max(0, QUESTION_TIME - elapsed)

    

    # Visual Header

    col1, col2 = st.columns([3, 1])

    with col1:

        st.caption(f"SECTOR: {category}")

    with col2:

        color = "red" if time_left < 5 else "#f05a37"

        st.markdown(f"<div class='timer-box' style='color:{color}'>⏱️ {int(time_left)}s</div>", unsafe_allow_html=True)



    st.markdown(f"### {question_obj['question']}")

    

    # Options

    # We use a placeholder for the form to recreate it if needed

    with st.form("answer_form"):

        selection = st.radio("Select the best match:", question_obj['options'], index=None)

        

        submitted = st.form_submit_button("Confirm Decision")

        

        if submitted:

            # Score Calculation

            final_elapsed = time.time() - q_data['start_time']

            

            # 0 points if time ran out (with 2s grace period for UI latency)

            if final_elapsed > (QUESTION_TIME + 2):

                points = 0

                chosen = "Timed Out"

                st.error("Time ran out!")

                time.sleep(1)

            elif selection:

                idx = question_obj['options'].index(selection)

                # Option A=1000, B=2000, C=3000 logic from React app

                points = (idx + 1) * 1000 

                chosen = selection

            else:

                points = 0

                chosen = "Skipped"



            # Save Answer

            st.session_state.score += points

            st.session_state.user_answers.append({

                "category": category,

                "question": question_obj['question'],

                "answer": chosen,

                "points": points

            })

            

            # Mark as asked

            st.session_state.asked_questions[category].append(question_obj)

            

            # Clear current question and go back

            st.session_state.current_question_data = None

            st.session_state.page = 'game'

            st.rerun()



    # Auto-refresh for timer visualization (rough approx)

    if time_left > 0:

        time.sleep(1)

        st.rerun()

    elif time_left <= 0:

        # Force a timeout submit via rerunning if user hasn't acted

        # (Limitations of Streamlit prevent auto-submitting form easily without js hack)

        # We will just show timeout message in real implementation or let them submit for 0 points.

        pass



def render_result():

    user = st.session_state.user

    score = st.session_state.score

    

    # Save score once

    if 'score_saved' not in st.session_state:

        save_score(user, score)

        st.session_state.score_saved = True



    st.markdown("<div class='brand-header'>MISSION COMPLETE</div>", unsafe_allow_html=True)

    

    st.markdown(f"""

    <div style='background-color:#1e293b; color:white; padding:2rem; border-radius:1rem; text-align:center; margin: 2rem 0;'>

        <h3>Total Score</h3>

        <h1 style='font-size:3rem; color:#f05a37'>{score:,}</h1>

        <p>Well done, {user.get('name', 'Player')}!</p>

    </div>

    """, unsafe_allow_html=True)

    

    # Leaderboard

    st.subheader("🏆 Leaderboard")

    lb_data = get_leaderboard()

    df = pd.DataFrame(lb_data)

    if not df.empty:

        st.dataframe(

            df[['name', 'score', 'industry']].rename(columns=str.title), 

            hide_index=True, 

            use_container_width=True

        )



    # CSV Generation

    csv_data = []

    # User Details

    base_row = {

        "Name": user.get('name'),

        "Mobile": user.get('mobile'),

        "Business": user.get('businessName'),

        "Email": user.get('email'),

        "Industry": user.get('industry'),

        "Score": score

    }

    # Flatten answers

    row = base_row.copy()

    for ans in st.session_state.user_answers:

        # Simplified header: Category - Question

        key = f"{ans['category']} - Question"

        row[key] = ans['answer']

        

    csv_df = pd.DataFrame([row])

    csv = csv_df.to_csv(index=False).encode('utf-8')

    

    st.download_button(

        "Download Report (CSV)",

        csv,

        "results.csv",

        "text/csv",

        key='download-csv'

    )

    

    if st.button("Play Again"):

        if 'score_saved' in st.session_state:

            del st.session_state.score_saved

        reset_game()

        st.rerun()



# ==========================================

# MAIN APP ROUTER

# ==========================================



def main():

    if st.session_state.page == 'home':

        render_home()

    elif st.session_state.page == 'form':

        render_form()

    elif st.session_state.page == 'game':

        render_game()

    elif st.session_state.page == 'question':

        render_question()

    elif st.session_state.page == 'result':

        render_result()



if __name__ == "__main__":

    main()
