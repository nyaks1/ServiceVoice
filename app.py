import streamlit as st
import os
import json
from google import genai
from google.genai import types
from schemas import ServiceTicket
from dotenv import load_dotenv

# Try loading from a local .env file
load_dotenv()

# Set up page configurations
st.set_page_config(
    page_title="ServiceVoice Admin Dashboard",
    page_icon="🇿🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich South African Civic branding and modern aesthetics
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Custom Header styling */
.header-container {
    background: linear-gradient(135deg, #007A4B 0%, #1C3B57 50%, #D4AF37 100%);
    padding: 24px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.main-title {
    color: #FFFFFF !important;
    font-weight: 700;
    font-size: 2.8rem;
    margin: 0;
    letter-spacing: -0.02em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.subtitle {
    font-size: 1.1rem;
    color: #E2E8F0 !important;
    margin-top: 8px;
    margin-bottom: 0;
    font-weight: 300;
}

/* Ticket Card styling */
.ticket-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

.ticket-card:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 122, 75, 0.4);
    box-shadow: 0 6px 24px rgba(0, 122, 75, 0.15);
}

/* Badge component styles */
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-critical {
    background: linear-gradient(135deg, #E63946 0%, #D62828 100%);
    color: white;
    box-shadow: 0 0 10px rgba(230, 57, 70, 0.4);
}

.badge-high {
    background: linear-gradient(135deg, #F77F00 0%, #FCBF49 100%);
    color: white;
}

.badge-medium {
    background: linear-gradient(135deg, #0077B6 0%, #0096C7 100%);
    color: white;
}

.badge-low {
    background: linear-gradient(135deg, #2A9D8F 0%, #264653 100%);
    color: white;
}

/* Detail items */
.detail-label {
    font-weight: 600;
    color: #D4AF37;
    margin-top: 15px;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.detail-value {
    color: #E2E8F0;
    font-size: 1.05rem;
    margin-bottom: 12px;
    line-height: 1.5;
}

.tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
    margin-bottom: 12px;
}

.tag-item {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #CBD5E0;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
}

.batho-pele-container {
    background: rgba(0, 122, 75, 0.1);
    border-left: 4px solid #007A4B;
    padding: 14px 18px;
    border-radius: 0 8px 8px 0;
    margin-top: 20px;
}

.batho-pele-title {
    color: #48BB78;
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🇿🇦 ServiceVoice Dashboard</h1>
    <p class="subtitle">AI-Native Civic Ticket Ingestion Engine | Batho Pele Compliance Platform</p>
</div>
""", unsafe_allow_html=True)

# API Key Discovery Setup
api_key = os.environ.get("GEMINI_API_KEY")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/af/Flag_of_South_Africa.svg", width=80)
st.sidebar.markdown("### System Settings")

if not api_key:
    st.sidebar.warning("🔑 GEMINI_API_KEY environment variable not detected.")
    api_key_input = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    if api_key_input:
        api_key = api_key_input
else:
    st.sidebar.success("🔑 API Key configured from system environment.")

# Initialize Client
client = None
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
    try:
        client = genai.Client()
    except Exception as e:
        st.sidebar.error(f"Client Init Failed: {e}")
else:
    st.sidebar.info("Please provide an API key in the field above or set the GEMINI_API_KEY environment variable to test the extraction engine.")

# System prompt defining the parsing & translation criteria
SYSTEM_INSTRUCTION = """
You are the ServiceVoice Engine, an automated civic translation and technical routing specialist deployed within South African municipal infrastructure.
Your task is to analyze raw citizen inputs (audio files or text messages) containing public service delivery complaints, which may be spoken or written in a mix of South African languages (isiZulu, isiXhosa, Sesotho, Setswana, Sepedi, Afrikaans, English, or localized township slang like Tsotsitaal).

Execute the following actions:
1. Identify and translate the raw civic intent into high-fidelity English.
2. Route the complaint into the appropriate municipal technical category.
3. Assess the severity based on physical threat to infrastructure or public safety.
4. Extract localized landmarks or location references to guide dispatch teams.
5. Identify specific key entities or items damaged or failing.
6. Provide a Batho Pele compliance reason for why local government must act quickly.

You must strictly output data conforming to the requested JSON schema. Do not output markdown, wrappers, or prose.
"""

def process_civic_voice_note(audio_file_path: str) -> str:
    """
    Uploads voice note via Files API, processes it with Gemini 3.5 Flash, and cleans it up.
    """
    if not client:
        raise ValueError("Google GenAI client is not initialized.")
        
    audio_upload = client.files.upload(file=audio_file_path)
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[
                audio_upload,
                "Analyze this civic voice note and generate the official municipal service ticket payload matching the structural schema precisely."
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=ServiceTicket,
                temperature=0.1,
            ),
        )
        return response.text
    finally:
        client.files.delete(name=audio_upload.name)

def process_civic_text_note(text_content: str) -> str:
    """
    Processes plain text civic note directly with Gemini 3.5 Flash.
    """
    if not client:
        raise ValueError("Google GenAI client is not initialized.")
        
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=[
            text_content,
            "Analyze this civic text note and generate the official municipal service ticket payload matching the structural schema precisely."
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ServiceTicket,
            temperature=0.1,
        ),
    )
    return response.text

CATEGORY_MAP = {
    'water_sanitation': '💧 Water & Sanitation',
    'electricity_power': '⚡ Electricity & Power',
    'roads_stormwater': '🛣️ Roads & Stormwater',
    'refuse_waste': '🗑️ Refuse & Waste',
    'housing': '🏠 Housing',
    'other': '⚙️ Other'
}

# Ingestion Interface Tabs
tab1, tab2 = st.tabs(["🎙️ Ingest Voice Note", "✍️ Ingest Text Complaint"])

with tab1:
    st.markdown("### Upload Audio Recording")
    st.write("Submit a voice recording of the service issue. The engine handles multilingual/multi-dialect South African speech profiles.")
    
    uploaded_file = st.file_uploader(
        "Upload Citizen Voice Recording (.mp3, .wav, .m4a)", 
        type=["mp3", "wav", "m4a"], 
        key="voice_uploader"
    )
    
    if uploaded_file is not None:
        # Sanitize filename by keeping only basename to prevent traversal issues
        safe_filename = os.path.basename(uploaded_file.name)
        temp_path = f"temp_{safe_filename}"
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.audio(temp_path, format="audio/mp3")
        
        if st.button("Analyze Voice Note", type="primary", key="btn_process_audio"):
            if not client:
                st.error("Please configure the Gemini API Key first.")
            else:
                with st.spinner("Uploading and analyzing voice note with Gemini 3.5 Flash..."):
                    try:
                        json_payload = process_civic_voice_note(temp_path)
                        st.session_state["result_payload"] = json_payload
                        st.success("Analysis Complete!")
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

with tab2:
    st.markdown("### Submit Text Complaint")
    st.write("Type a complaint or select one of the typical multilingual examples below:")
    
    sample_options = [
        "None (Write custom text)",
        "Sample 1 (isiZulu/English mix - Water Leak): Ngicela usizo, there is a big water leak in my street at corner of Gwigwi Mrwebi. Amanzi ayachitheka everywhere since yesterday morning.",
        "Sample 2 (Afrikaans/English mix - Potholes): Die potholes op Main Road is heeltemal buite beheer. Multi car tires broken. Near the Shell garage.",
        "Sample 3 (Sesotho/Tsotsitaal mix - Electricity): Geen lights in Ward 4 since Thursday. I think the transformer or substation e qhumile. Re kopa help fast."
    ]
    
    selected_sample = st.selectbox(
        "Load a sample complaint:", 
        sample_options, 
        key="sample_selector"
    )
    
    default_text = ""
    if selected_sample != "None (Write custom text)":
        default_text = selected_sample.split(": ", 1)[1]
        
    text_content = st.text_area(
        "Complaint text:", 
        value=default_text, 
        height=120, 
        key="text_input_area"
    )
    
    if st.button("Analyze Text Complaint", type="primary", key="btn_process_text"):
        if not text_content.strip():
            st.warning("Please input complaint text first.")
        elif not client:
            st.error("Please configure the Gemini API Key first.")
        else:
            with st.spinner("Analyzing text complaint with Gemini 3.5 Flash..."):
                try:
                    json_payload = process_civic_text_note(text_content)
                    st.session_state["result_payload"] = json_payload
                    st.success("Analysis Complete!")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# Display Analysis Output
if "result_payload" in st.session_state:
    st.markdown("---")
    
    try:
        payload_data = json.loads(st.session_state["result_payload"])
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📋 Municipal Service Ticket Details")
            
            # Severity color styling
            sev = payload_data.get("severity", "medium").lower()
            badge_class = f"badge-{sev}" if sev in ["critical", "high", "medium", "low"] else "badge-medium"
            
            category_val = payload_data.get("category", "other")
            category_display = CATEGORY_MAP.get(category_val, f"⚙️ {category_val.title()}")
            
            location_items = payload_data.get('location_clues', [])
            entity_items = payload_data.get('key_entities', [])
            
            st.markdown(f"""
            <div class="ticket-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <span style="font-size: 1.3rem; font-weight: 700; color: #E2E8F0;">{category_display}</span>
                    <span class="badge {badge_class}">{sev}</span>
                </div>
                
                <div class="detail-label">Detected Language Profile</div>
                <div class="detail-value">{payload_data.get('citizen_language_detected')}</div>
                
                <div class="detail-label">English Core Translation</div>
                <div class="detail-value" style="font-style: italic; background: rgba(0,0,0,0.25); padding: 12px; border-radius: 8px; border-left: 3px solid #D4AF37;">
                    "{payload_data.get('english_translation')}"
                </div>
                
                <div class="detail-label">Extracted Location Markers</div>
                <div class="tag-list">
                    {" ".join([f'<span class="tag-item">📍 {item}</span>' for item in location_items]) if location_items else '<span class="tag-item">None detected</span>'}
                </div>
                
                <div class="detail-label">Key Damaged/Failing Entities</div>
                <div class="tag-list">
                    {" ".join([f'<span class="tag-item">🔧 {item}</span>' for item in entity_items]) if entity_items else '<span class="tag-item">None detected</span>'}
                </div>
                
                <div class="batho-pele-container">
                    <div class="batho-pele-title">Batho Pele Compliance Pillar</div>
                    <div style="color: #CBD5E0; font-size: 0.95rem; line-height: 1.4;">{payload_data.get('batho_pele_justification')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("🚀 Dispatch Municipal Field Team", use_container_width=True, key="btn_dispatch"):
                    st.toast("Field dispatch notification triggered!", icon="🚀")
            with action_col2:
                if st.button("💬 Send Citizen SMS Notification", use_container_width=True, key="btn_sms"):
                    st.toast("SMS status update notification queued for citizen!", icon="💬")
                    
        with col2:
            st.markdown("### 🛠️ Raw JSON Payload")
            st.write("This structured payload complies with the municipal IT Service Management (ITSM) systems integration schema:")
            st.json(payload_data)
            
    except Exception as parse_err:
        st.error(f"Error parsing payload JSON: {parse_err}")
        st.code(st.session_state["result_payload"])
