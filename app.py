import streamlit as st
import PyPDF2
import requests
import json

# 1. Access Control
st.title("Secure AI Document Extractor")
password = st.text_input("Enter App Password", type="password")

if password != "mysecret123":
    st.warning("Please enter the correct password to continue.")
    st.stop()

# 2. Secure API Key Input
api_key = st.text_input("Enter your Groq API Key", type="password")
if not api_key:
    st.info("API Key required to run the AI.")
    st.stop()

# 3. File Uploader (Accepts MULTIPLE files)
uploaded_files = st.file_uploader("Upload your PDFs here", type="pdf", accept_multiple_files=True)

if uploaded_files and st.button("Analyze Documents"):
    
    # 4. Loop through every single file uploaded
    for uploaded_file in uploaded_files:
        st.write(f"### 📄 Results for: {uploaded_file.name}")
        
        with st.spinner(f"Reading {uploaded_file.name}..."):
            # Extract PDF text
            reader = PyPDF2.PdfReader(uploaded_file)
            document_text = ""
            for page in reader.pages:
                if page.extract_text():
                    document_text += page.extract_text()
            
            # Send to Groq
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "Extract customer_name, property_owner, property_address, papers_required, and documents_received into a flat JSON object. If a field is missing, output null."},
                    {"role": "user", "content": document_text}
                ]
            }
            
            try:
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                result = response.json()
                
                # Display Results
                ai_data = json.loads(result["choices"][0]["message"]["content"])
                st.success("Extraction Complete!")
                st.json(ai_data)
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")
        
        st.divider()
