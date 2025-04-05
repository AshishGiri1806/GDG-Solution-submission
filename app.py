import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pandas as pd

# Configure Gemini API
genai.configure(api_key="AIzaSyCF5Y4pskDJYIeV5o0-RlYiI5haeB9nD_g")
model = genai.GenerativeModel("gemini-1.5-flash")

# Sample recycler data (in a real app, this would come from a database)
RECYCLERS_DATA = {
    'Name': ['EcoRecycle Solutions', 'GreenTech Recycling', 'E-Waste Management Inc'],
    'Location': ['Mumbai', 'Delhi', 'Bangalore'],
    'Contact': ['+91 9876543210', '+91 9876543211', '+91 9876543212'],
    'Types Accepted': ['All Electronics', 'Computers & Phones', 'Large Appliances'],
    'Rating': [4.5, 4.2, 4.7]
}

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit UI
st.set_page_config(page_title="♻️ E-Waste Segregation Chatbot", layout="wide")
st.title("♻️ E-Waste Segregation Chatbot")

# Add some custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
    }
    .recycler-section {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
    }
    .divider {
        border-top: 2px solid #e0e0e0;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Create two columns with different background colors
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 Chat with E-Waste Assistant")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "image" in message:
                st.image(message["image"], caption="Uploaded E-Waste", use_container_width=True)

    # File Uploader and Text Input in the chat input area
    uploaded_file = st.file_uploader("Upload an e-waste image", type=["jpg", "png", "jpeg"])
    user_input = st.chat_input("Ask about e-waste or describe an item...")

with col2:
    st.markdown("### 🔍 Find Recyclers")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="recycler-section">', unsafe_allow_html=True)
        location = st.selectbox("Select your location", ['Mumbai', 'Delhi', 'Bangalore', 'Other'])
        waste_type = st.selectbox("Type of e-waste", ['All Electronics', 'Computers & Phones', 'Large Appliances', 'Other'])
        
        # Filter and display recyclers
        df = pd.DataFrame(RECYCLERS_DATA)
        filtered_recyclers = df[
            (df['Location'] == location) & 
            (df['Types Accepted'].str.contains(waste_type))
        ]
        
        if not filtered_recyclers.empty:
            st.write("### Available Recyclers")
            for _, recycler in filtered_recyclers.iterrows():
                with st.expander(f"🌟 {recycler['Name']} ({recycler['Rating']}⭐)"):
                    st.write(f"📍 Location: {recycler['Location']}")
                    st.write(f"📱 Contact: {recycler['Contact']}")
                    st.write(f"♻️ Types Accepted: {recycler['Types Accepted']}")
        else:
            st.info("No recyclers found for your criteria. Try different filters.")
        st.markdown('</div>', unsafe_allow_html=True)

# Function to classify waste
def classify_waste(image=None, text_query=None):
    prompt = """
    Classify the e-waste item into 1 of the following categories:
    - **Recyclable**
    - **Non-Recyclable**
    - **Reusable**
    
    Also provide a brief explanation for the classification.
    """
    
    input_data = [prompt]
    
    if image:
        input_data.append(image)
    if text_query:
        input_data.append(text_query)
    
    response = model.generate_content(input_data)
    return response.text

# Handle user input
if user_input or uploaded_file:
    # Add user message to chat
    user_message = {"role": "user", "content": user_input if user_input else ""}
    if uploaded_file:
        user_message["image"] = uploaded_file
        image = Image.open(uploaded_file)
    st.session_state.messages.append(user_message)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if uploaded_file:
                response = classify_waste(image=image, text_query=user_input)
            else:
                response = classify_waste(text_query=user_input)
            st.write(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
