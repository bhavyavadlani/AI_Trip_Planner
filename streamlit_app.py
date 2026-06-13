import streamlit as st
import requests
import datetime
import os
import glob

BASE_URL = "http://localhost:8000"  # Backend endpoint
OUTPUT_DIR = "./output"

# Set up page configurations
st.set_page_config(
    page_title="🌍 AI Travel Agent & Expense Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom premium styling using CSS injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* App Title Header Gradient */
    .title-gradient {
        background: linear-gradient(135deg, #FF6B6B 10%, #FF8E53 30%, #4ECDC4 60%, #45B6FE 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar Headers */
    .sidebar-header {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 1.2rem;
        color: #4ECDC4;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Cards and Containers styling (Glassmorphism inspired) */
    .plan-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        margin-bottom: 20px;
    }
    
    /* Button Hover Micro-animations */
    div.stButton > button {
        background: linear-gradient(135deg, #4ECDC4 0%, #45B6FE 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        text-align: left !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(78, 205, 196, 0.3) !important;
        border: none !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to search for saved travel plans
def get_saved_plans():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        return []
    files = glob.glob(os.path.join(OUTPUT_DIR, "*.md"))
    # Sort files by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    return files

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_plan" not in st.session_state:
    st.session_state.selected_plan = None
if "selected_plan_content" not in st.session_state:
    st.session_state.selected_plan_content = None

# Sidebar Content
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    
    # Model selection
    model_provider = st.selectbox(
        "Choose LLM Engine:",
        ["groq", "openai"],
        index=0,
        help="Groq uses DeepSeek (Llama), OpenAI uses GPT-4o-mini"
    )
    
    st.markdown("---")
    
    # Quick start templates
    st.markdown('<div class="sidebar-header">💡 Destination Ideas</div>', unsafe_allow_html=True)
    st.caption("Click any idea to load it as your query:")
    
    ideas = [
        "Plan a trip to Goa for 5 days with a budget-friendly expense breakdown",
        "Create a 7-day itinerary for Tokyo showcasing tech spots and local food",
        "Design a 3-day romantic weekend getaway in Paris with boutique hotels",
        "Plan a 4-day trip to Jaipur & Udaipur with currency conversions USD to INR"
    ]
    
    for idx, idea in enumerate(ideas):
        if st.button(idea[:38] + "...", help=idea, key=f"idea_{idx}"):
            st.session_state.preset_prompt = idea

    st.markdown("---")
    
    # Saved Travel Plans List
    st.markdown('<div class="sidebar-header">📂 Saved Trip Plans</div>', unsafe_allow_html=True)
    saved_plans = get_saved_plans()
    if saved_plans:
        for filepath in saved_plans:
            filename = os.path.basename(filepath)
            display_name = filename.replace("AI_Trip_Planner_", "").replace(".md", "").replace("_", " ")
            if st.button(f"📄 {display_name[:25]}", key=filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    st.session_state.selected_plan_content = f.read()
                st.session_state.selected_plan = filepath
    else:
        st.info("No saved plans yet. Generate one to see it here!")

# Main Application Layout
st.markdown('<h1 class="title-gradient">🌍 AI Travel Agent & Expense Planner</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #888;'>Your intelligent companion for creating perfect itineraries, estimating expenses, checking weather conditions, and converting currencies in real-time.</p>", unsafe_allow_html=True)

# Create two columns: Chat interface and Plan Viewer
col_chat, col_viewer = st.columns([1, 1.2])

with col_chat:
    st.subheader("💬 Chat with Travel Agent")
    
    # Display message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Determine the default value for input if a preset prompt was clicked
    input_placeholder = "e.g., Plan a 5-day trip to Goa with cost estimation"
    default_input = ""
    if "preset_prompt" in st.session_state and st.session_state.preset_prompt:
        default_input = st.session_state.preset_prompt
        # Clear the preset prompt after loading
        st.session_state.preset_prompt = None
        
    # User Input box using st.chat_input
    user_query = st.chat_input(placeholder=input_placeholder)
    
    # Alternatively, if default_input is set, we automatically submit it
    if default_input:
        user_query = default_input

    if user_query:
        # Show user message in chat
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
            
        # Call backend
        with st.spinner("🤖 Agent is planning your journey, calculating expenses, and gathering weather..."):
            try:
                payload = {
                    "question": user_query,
                    "model_provider": model_provider
                }
                response = requests.post(f"{BASE_URL}/query", json=payload, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer returned.")
                    saved_file = data.get("saved_file")
                    
                    # Add agent response to history
                    st.session_state.messages.append({"role": "assistant", "content": "Here is your generated travel plan! Check the viewer on the right side for the full layout."})
                    with st.chat_message("assistant"):
                        st.write("Here is your generated travel plan! Check the viewer on the right side for the full layout.")
                        
                    # Put contents directly into the Plan Viewer
                    st.session_state.selected_plan_content = answer
                    if saved_file:
                        st.session_state.selected_plan = saved_file
                    else:
                        st.session_state.selected_plan = "unsaved_temp.md"
                        
                    # Rerun to refresh the UI and show content in viewer
                    st.rerun()
                else:
                    st.error(f"Error from Backend (Status {response.status_code}): {response.text}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {response.text}"})
            except Exception as e:
                st.error(f"Could not connect to FastAPI server at {BASE_URL}. Please ensure the backend server is running. (Error: {e})")

with col_viewer:
    st.subheader("📋 Travel Plan Viewer")
    
    if st.session_state.selected_plan_content:
        # Display Plan Metadata if saved
        if st.session_state.selected_plan:
            filename = os.path.basename(st.session_state.selected_plan)
            st.caption(f"Viewing: **{filename}**")
            
            # Download button
            st.download_button(
                label="📥 Download Travel Plan (.md)",
                data=st.session_state.selected_plan_content,
                file_name=filename,
                mime="text/markdown"
            )
            
        st.markdown('---')
        
        # Display Markdown Content in a premium card style container
        st.markdown(
            f'<div class="plan-card">\n\n{st.session_state.selected_plan_content}\n\n</div>', 
            unsafe_allow_html=True
        )
    else:
        st.info("Your detailed travel plan will appear here. Start chatting or select an idea to begin!")