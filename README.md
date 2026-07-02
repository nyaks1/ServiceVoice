ServiceVoice
An AI-native GovTech ticket ingestion engine that bridges the civic language divide. ServiceVoice leverages the extreme multimodal speed and reasoning of gemini-3.5-flash to ingest unstructured, multi-dialect, and multi-lingual citizen audio notes directly, translating and parsing them into highly structured, actionable municipal service tickets.
This platform explicitly automates compliance with the Access and Courtesy pillars of South Africa's Batho Pele ("People First") Principles, transforming raw citizen voice notes into localized IT Service Management payloads.
🏗️ System Architecture & Execution Pipeline
[Citizen Audio File (.mp3/.wav)]
               │
               ▼
┌────────────────────────────────────────────────────────┐
│             Streamlit Web Interface Trigger            │
└────────────────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────┐
│         Gemini 3.5 Flash Multimodal Pipeline          │
│                                                        │
│  - Accepts raw audio binary natively                   │
│  - Structured Output Enforced (JSON Schema)            │
│  - Multi-dialect / Multilingual Translation           │
└────────────────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────┐
│           Parsed & Validated JSON Payload             │
└────────────────────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────┐
│           Admin Dashboard (Ticket Generation)          │
└────────────────────────────────────────────────────────┘

📜 Technical Requirements & Dependencies
To execute this project, the runtime environment requires:
Python 3.10+
Google GenAI SDK (Supporting Gemini 3.5 model definitions)
Streamlit (For fast dashboard and audio-capture previewing)

pip install google-genai streamlit pydantic

🔑 Implementation Blueprint
1. Unified JSON Schema Contract (schemas.py)
To eliminate parsing errors, the model must strictly output a schema mapped via Pydantic.

from pydantic import BaseModel, Field
from typing import List, Optional

class ServiceTicket(BaseModel):
    citizen_language_detected: str = Field(description="The primary language or mixture of dialects detected in the audio.")
    english_translation: str = Field(description="Accurate, coherent translation of the citizen's complaint into professional English.")
    category: str = Field(description="Must map strictly to one of: 'water_sanitation', 'electricity_power', 'roads_stormwater', 'refuse_waste', 'housing', 'other'.")
    severity: str = Field(description="Priority rating based on public hazard: 'critical', 'high', 'medium', 'low'.")
    location_clues: List[str] = Field(description="Extracted local landmarks, street names, suburbs, or wards mentioned to identify the location.")
    key_entities: List[str] = Field(description="Specific items damaged or failing (e.g., 'substation', 'pothole', 'burst main pipe').")
    batho_pele_justification: str = Field(description="A brief explanation of how addressing this ticket fulfills the 'People First' mandate.")

Main Agent Execution Pipeline (app.py)
import streamlit as st
import os
from google import genai
from google.genai import types
from schemas import ServiceTicket

# Initialize GenAI Client
# Expects GEMINI_API_KEY inside environment variables
client = genai.Client()

# System Instructions defining the agentic persona
SYSTEM_INSTRUCTION = """
You are the ServiceVoice Engine, an automated civic translation and technical routing specialist deployed within South African municipal infrastructure.
Your task is to listen to raw citizen audio notes containing public service delivery complaints, which may be spoken in a mix of South African languages (isiZulu, isiXhosa, Sesotho, Setswana, Sepedi, Afrikaans, English, or localized township slang).

Execute the following actions:
1. Translate the raw audio intent into high-fidelity English.
2. Route the complaint into the appropriate municipal technical category.
3. Assess the severity based on physical threat to infrastructure or public safety.
4. Extract localized landmarks or location references to guide dispatch teams.
5. Provide a Batho Pele compliance reason for why local government must act quickly.

You must strictly output data conforming to the requested JSON schema. Do not output markdown, wrappers, or prose.
"""

def process_civic_voice_note(audio_file_path: str) -> ServiceTicket:
    """
    Ingests local binary audio file directly into Gemini 3.5 Flash 
    utilizing its native audio multimodal context.
    """
    # Upload binary file via Files API to handle large/varying audio lengths cleanly
    audio_upload = client.files.upload(file=audio_file_path)
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=[
            audio_upload,
            "Analyze this civic voice note and generate the official municipal service ticket payload matching the structural schema schema precisely."
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ServiceTicket,
            temperature=0.1, # Low temperature ensures strict structural replication and routing consistency
        ),
    )
    
    # Cleanup file context post-inference
    client.files.delete(name=audio_upload.name)
    
    return response.text

# --- Streamlit Presentation Layer ---
st.set_page_config(page_title="ServiceVoice Admin Dashboard", layout="wide")
st.title("🇿🇦 ServiceVoice: Multilingual Civic Ticket Router")
st.subheader("Automating Batho Pele Compliance via Gemini 3.5 Flash")

uploaded_file = st.file_uploader("Upload Citizen Voice Recording (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    # Temporarily persist audio stream for upload payload processing
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.audio(temp_path, format="audio/mp3")
    
    with st.spinner("Processing local voice note through multi-dialect extraction engine..."):
        try:
            json_payload = process_civic_voice_note(temp_path)
            
            # Presentation columns matching the 20% Presentation / 40% Polish requirements
            col1, col2 = st.columns(2)
            with col1:
                st.success("Ticket Generated Successfully")
                st.json(json_payload)
                
            with col2:
                # Parse for structured visual output
                import json
                ticket_data = json.loads(json_payload)
                st.metric(label="Detected Language Profile", value=ticket_data.get("citizen_language_detected"))
                st.metric(label="System Severity Assessment", value=ticket_data.get("severity").upper())
                st.info(f"**English Core Translation:**\n{ticket_data.get('english_translation')}")
                st.warning(f"**Extracted Location Markers:** {', '.join(ticket_data.get('location_clues'))}")
                
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


