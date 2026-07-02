ServiceVoice Deployment & Execution Guide
This document contains step-by-step instructions on setting up, configuring, and launching the ServiceVoice multi-dialect civic ingestion engine.

🛠️ 1. Environment Prerequisites
Ensure you have Python 3.10 or higher installed on your Linux, macOS, or WSL subsystem environment.

Core Dependencies
Streamlit: Controls the web-based administrative reporting dashboard and audio playback components.

Google GenAI SDK: Interfaces directly with the native multimodal pipeline of the gemini-3.5-flash model.

Pydantic: Enforces strict structural boundaries and data serialization contracts for JSON output.

# 🚀 2. Quick-Start Setup
Follow these commands in your terminal to initialize and execute the application locally:

Step 1: Clone or Enter the Project Directory
Bash
cd servicevoice-govtech
Step 2: Initialize a Python Virtual Environment
Bash
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
Step 3: Install Required Packages
Bash
pip install --upgrade pip
pip install google-genai streamlit pydantic
🔑 3. Authentication & API Configuration
The application utilizes the modern Google GenAI Client wrapper, which implicitly searches the operating system environment for authentication tokens.

Export your Gemini API Key directly into your current terminal session:

Bash
export GEMINI_API_KEY="your_actual_gemini_api_key_here"
⚠️ Security Warning: Never hardcode your API key into app.py or commit it to your GitHub repository. The runtime will fail gracefully if GEMINI_API_KEY is not present in the system environment.

🖥️ 4. Running the Application
Launch the localized Streamlit dashboard server by running the following command:

Bash
streamlit run app.py
Network Access URLs
Upon successful initialization, your terminal will output the local networking boundaries:

Local URL: http://localhost:8501

Network URL: http://192.168.x.x:8501 (Use this to test the live system from a mobile device on the same Wi-Fi network during demonstrations)

🎯 5. Step-by-Step Live Demo Verification
To demonstrate the ServiceVoice system processing multi-lingual audio under the 90-second constraint:

Open http://localhost:8501 in any modern web browser.

Drag and drop or upload a sample civic recording (.mp3, .wav, or .m4a).

The dashboard will instantly render an inline audio preview controller.

The system will dispatch the raw audio binary directly to Gemini 3.5 Flash context windows.

Watch the dashboard dynamically parse the response text into real-time metrics, translation blocks, and structured municipal database payload arrays.