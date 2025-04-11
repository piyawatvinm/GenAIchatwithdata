import streamlit as st
import pandas as pd
import google.generativeai as genai

# ===== 1. Setup Layout =====
st.title("🐧 My Chatbot and Data Analysis App")
st.subheader("Upload your CSV and get AI insights!")

# ===== 2. Load Gemini API Key =====
try:
    key = st.secrets["gemini_api_key"]
    genai.configure(api_key=key)
    model = genai.GenerativeModel("models/gemini-2.0-flash-lite")
    st.success("✅ Gemini API Key configured successfully.")
except Exception as e:
    model = None
    st.error(f"❌ Error setting up Gemini model: {e}")

# ===== 3. Initialize session state =====
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# ===== 4. Section 1: Upload Main Dataset =====
st.header("📁 Section 1: Upload Main Dataset (CSV)")
uploaded_file = st.file_uploader("Choose your main data CSV file", type=["csv"], key="main_data")

if uploaded_file is not None:
    try:
        st.session_state.uploaded_data = pd.read_csv(uploaded_file)
        st.success("✅ Main data uploaded successfully.")
        st.write("### 🔍 Data Preview")
        st.dataframe(st.session_state.uploaded_data.head())
    except Exception as e:
        st.error(f"Error reading main dataset: {e}")

# ===== 5. Section 2: Upload Data Dictionary (Optional) =====
st.header("📖 Section 2: Upload Data Dictionary (Optional)")
data_dict_file = st.file_uploader("Upload a data dictionary CSV (optional)", type=["csv"], key="data_dict_file")

if data_dict_file is not None:
    try:
        data_dict_df = pd.read_csv(data_dict_file)
        st.session_state.data_dict = data_dict_df
        st.success("✅ Data dictionary uploaded.")
        st.write("### 📘 Data Dictionary Preview")
        st.dataframe(data_dict_df)
    except Exception as e:
        st.error(f"Error reading data dictionary: {e}")

# ===== 6. Enable Analysis =====
analyze_data_checkbox = st.checkbox("📊 Analyze CSV with AI")

# ===== 7. Chat Input =====
if user_input := st.chat_input("💬 Type your question here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:

                # ========== Build Prompt ========== #
                data_description = st.session_state.uploaded_data.describe().to_string()
                data_sample = st.session_state.uploaded_data.head(5).to_string()

                if "data_dict" in st.session_state and st.session_state.data_dict is not None:
                    data_dict_description = st.session_state.data_dict.to_string(index=False)
                    prompt = (
                        f"I uploaded a dataset. Here's a statistical summary:\n\n{data_description}\n\n"
                        f"Sample rows from the dataset:\n\n{data_sample}\n\n"
                        f"Column descriptions from the data dictionary:\n\n{data_dict_description}\n\n"
                        f"Please analyze the dataset and provide key insights, trends, anomalies, or important summaries."
                    )
                else:
                    prompt = (
                        f"I uploaded a dataset. Here's a statistical summary:\n\n{data_description}\n\n"
                        f"Sample rows from the dataset:\n\n{data_sample}\n\n"
                        f"Please analyze the dataset and provide insights or summaries based on these values."
                    )

                # ========== Generate Response ========== #
                response = model.generate_content(prompt)
                bot_response = response.text

            elif not analyze_data_checkbox:
                bot_response = "📌 Please enable 'Analyze CSV with AI' to allow me to help with data insights."
            else:
                bot_response = "⚠️ Please upload a CSV file first."

            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)

        except Exception as e:
            st.error(f"Error generating AI response: {e}")
    else:
        st.warning("⚠️ Gemini model is not configured yet.")
