import streamlit as st
import pandas as pd
import google.generativeai as genai

# Set up the Streamlit app layout
st.title("🐧 My Chatbot and Data Analysis App")
st.subheader("Conversation and Data Analysis")

# Capture Gemini API Key
gemini_api_key = st.text_input("Gemini API Key: ", placeholder="Type your API Key here...", type="password")

# Initialize the Gemini Model
model = None
if gemini_api_key:
    try:
        # Configure Gemini with the provided API Key
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("models/gemini-1.5-flash-lite")
        st.success("Gemini API Key successfully configured.")
    except Exception as e:
        st.error(f"An error occurred while setting up the Gemini model: {e}")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None
# No need to define st.session_state.data_dict here to avoid key conflict

# Display chat history
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# ========= Section 1: Upload Main Data =========
st.header("📁 Section 1: Upload Main Dataset (CSV)")
uploaded_file = st.file_uploader("Choose your main data CSV file", type=["csv"], key="main_data")

if uploaded_file is not None:
    try:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.success("✅ Main data file uploaded successfully.")
        st.write("### 🔍 Preview of Main Dataset")
        st.dataframe(st.session_state.uploaded_data.head())
    except Exception as e:
        st.error(f"An error occurred while reading the main data file: {e}")

# ========= Section 2: Upload Data Dictionary (Optional) =========
st.header("📖 Section 2: Upload Data Dictionary (Optional)")
data_dict_file = st.file_uploader("Upload a Data Dictionary CSV (optional)", type=["csv"], key="data_dict_file")

if data_dict_file is not None:
    try:
        data_dict_df = pd.read_csv(data_dict_file)
        st.session_state.data_dict = data_dict_df  # Save to session state
        st.success("✅ Data dictionary loaded successfully.")
        st.write("### 📘 Preview of Data Dictionary")
        st.dataframe(data_dict_df)
    except Exception as e:
        st.error(f"An error occurred while reading the data dictionary: {e}")

# Checkbox to enable analysis
analyze_data_checkbox = st.checkbox("Analyze CSV Data with AI")

# Chat Input
if user_input := st.chat_input("Type your message here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:
                if "analyze" in user_input.lower() or "insight" in user_input.lower():
                    data_description = st.session_state.uploaded_data.describe().to_string()

                    if "data_dict" in st.session_state and st.session_state.data_dict is not None:
                        data_dict_description = st.session_state.data_dict.to_string(index=False)
                        prompt = (
                            f"I have the following dataset:\n\n{data_description}\n\n"
                            f"And here is a data dictionary that describes the dataset:\n\n{data_dict_description}\n\n"
                            f"Please analyze the dataset and provide insights considering both the dataset and dictionary."
                        )
                    else:
                        prompt = (
                            f"Analyze the following dataset and provide insights:\n\n{data_description}"
                        )

                    response = model.generate_content(prompt)
                    bot_response = response.text
                else:
                    response = model.generate_content(user_input)
                    bot_response = response.text
            elif not analyze_data_checkbox:
                bot_response = "Data analysis is disabled. Please select the 'Analyze CSV Data with AI' checkbox to enable analysis."
            else:
                bot_response = "Please upload a CSV file first, then ask me to analyze it."

            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)

        except Exception as e:
            st.error(f"An error occurred while generating the response: {e}")
    else:
        st.warning("Please configure the Gemini API Key to enable chat responses.")
