import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Student Knowledge Gap & Score Overview",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add custom CSS
st.markdown("""
<style>
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .card-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #333;
    }
    .card-description {
        color: #666;
        font-size: 14px;
        margin-bottom: 15px;
    }
    .section-title {
        font-weight: 600;
        margin-bottom: 8px;
    }
    .resource-subject {
        font-weight: 600;
        color: #5B21B6;
        margin-top: 12px;
    }
    .resource-link {
        color: #2563EB;
    }
    .resource-type {
        font-size: 12px;
        color: #a0aec0;
    }
    .footer-text {
        color: #666;
        font-size: 12px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Sample student test scores per subject
student_scores = pd.DataFrame([
    {"subject": "Math", "score": 55},
    {"subject": "English", "score": 72},
    {"subject": "Science", "score": 60},
    {"subject": "Art", "score": 85},
    {"subject": "Logic", "score": 65},
    {"subject": "Programming", "score": 40},
    {"subject": "Creative Writing", "score": 78},
])

# Helper: derive abilities from scores
def derive_abilities(scores_df):
    arithmetic = scores_df[scores_df["subject"] == "Math"]["score"].values[0] if not scores_df[scores_df["subject"] == "Math"].empty else 0
    
    art_score = scores_df[scores_df["subject"] == "Art"]["score"].values[0] if not scores_df[scores_df["subject"] == "Art"].empty else 0
    creative_writing_score = scores_df[scores_df["subject"] == "Creative Writing"]["score"].values[0] if not scores_df[scores_df["subject"] == "Creative Writing"].empty else 0
    creativity = (art_score + creative_writing_score) / 2
    
    logic_score = scores_df[scores_df["subject"] == "Logic"]["score"].values[0] if not scores_df[scores_df["subject"] == "Logic"].empty else 0
    programming_score = scores_df[scores_df["subject"] == "Programming"]["score"].values[0] if not scores_df[scores_df["subject"] == "Programming"].empty else 0
    out_of_box = (logic_score + programming_score) / 2
    
    return pd.DataFrame([
        {"ability": "Arithmetic", "value": arithmetic},
        {"ability": "Creativity", "value": creativity},
        {"ability": "Out-of-Box Thinking", "value": out_of_box},
    ])

derived_abilities = derive_abilities(student_scores)

# Resource library
resource_library = {
    "Math": [
        {"title": "Khan Academy Math", "url": "https://www.khanacademy.org/math", "type": "Video Course"},
        {"title": "Brilliant.org Math", "url": "https://brilliant.org/courses/", "type": "Interactive"},
    ],
    "English": [
        {"title": "BBC Learning English", "url": "https://www.bbc.co.uk/learningenglish", "type": "Website"}
    ],
    "Science": [
        {"title": "Crash Course Science Videos", "url": "https://www.youtube.com/c/crashcourse", "type": "YouTube"}
    ],
    "Art": [
        {"title": "Draw with Jazza", "url": "https://www.youtube.com/user/DrawWithJazza", "type": "YouTube"}
    ],
    "Logic": [
        {"title": "LSAT Logic Games", "url": "https://7sage.com/logic-games/", "type": "Practice"}
    ],
    "Programming": [
        {"title": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "type": "Interactive"},
        {"title": "Codecademy Programming", "url": "https://www.codecademy.com/", "type": "Interactive"},
    ],
    "Creative Writing": [
        {"title": "Reedsy: Creative Writing Prompts", "url": "https://blog.reedsy.com/creative-writing-prompts/", "type": "Prompts"},
        {"title": "Coursera Creative Writing", "url": "https://www.coursera.org/specializations/creative-writing", "type": "Video Course"},
    ],
}

# Get recommendations based on low scores
def get_recommendations(scores_df):
    recommendations = []
    for _, row in scores_df[scores_df["score"] < 65].iterrows():
        subject = row["subject"]
        if subject in resource_library:
            recommendations.append({
                "subject": subject,
                "resources": resource_library[subject]
            })
    return recommendations

recommendations = get_recommendations(student_scores)

# Create the bar chart
def create_score_chart(scores_df):
    fig = px.bar(
        scores_df,
        x="subject",
        y="score",
        color_discrete_sequence=["#9b87f5"],
        labels={"subject": "Subject", "score": "Score"},
        height=300,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis_range=[0, 100],
    )
    fig.update_traces(marker_line_width=0, marker_line_color="#9b87f5", selector=dict(type="bar"))
    
    return fig

# Create the radar chart
def create_abilities_radar(abilities_df):
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=abilities_df["value"],
        theta=abilities_df["ability"],
        fill='toself',
        name='Abilities',
        line_color='#7E69AB',
        fillcolor='rgba(126, 105, 171, 0.5)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
    )
    
    return fig

# Main application
def main():
    # First Card - Score Overview
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown('<div class="card-title">📊 Student Knowledge Gap & Score Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-description">Review your results and discover how to level up! Below is a visual of your scores, your strengths, and personalized resource recommendations.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">Subject Scores</div>', unsafe_allow_html=True)
        st.plotly_chart(create_score_chart(student_scores), use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<div class="section-title">⭐ Abilities Radar</div>', unsafe_allow_html=True)
        st.plotly_chart(create_abilities_radar(derived_abilities), use_container_width=True, config={'displayModeBar': False})
        st.markdown('<div style="font-size: 12px; color: #666;">Abilities derived from your scores in relevant subjects.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Second Card - Resources
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📚 Targeted Resources to Improve</div>', unsafe_allow_html=True)
    
    if not recommendations:
        st.markdown('<div style="color: #10B981; font-weight: 600;">Great job! No big gaps detected. Keep it up!</div>', unsafe_allow_html=True)
    else:
        for rec in recommendations:
            st.markdown(f'<div class="resource-subject">{rec["subject"]} (score &lt; 65)</div>', unsafe_allow_html=True)
            for resource in rec['resources']:
                st.markdown(f'• <a href="{resource["url"]}" target="_blank" class="resource-link">{resource["title"]}</a> <span class="resource-type">[{resource["type"]}]</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer-text">Resources are recommended for subjects where your score was less than 65.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()