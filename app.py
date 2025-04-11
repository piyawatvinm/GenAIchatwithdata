import streamlit as st
import pandas as pd
import google.generativeai as genai

# ===== 1. Setup Layout =====
st.title("🐧 Gemini Chatbot + Data Analyzer")
st.subheader("Upload your CSV and get AI insights!")

# ===== 2. Load Gemini API Key =====
try:
    key = st.secrets["gemini_api_key"]
    genai.configure(api_key=key)
    model = genai.GenerativeModel("models/gemini-2.0-flash-lite")
    st.success("✅ Gemini API Key successfully configured.")
except Exception as e:
    model = None
    st.error(f"❌ Error setting up Gemini model: {e}")

# ===== 3. Initialize session state =====
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# ===== 4. Display chat history =====
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# ===== 5. Upload Main Dataset =====
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

# ===== 6. Upload Data Dictionary (Optional) =====
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

# ===== 7. Enable AI Analysis =====
analyze_data_checkbox = st.checkbox("📊 Analyze CSV with AI")

# ===== 8. Chat Input and AI Response =====
if user_input := st.chat_input("💬 Type your question here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:

                # สร้าง Prompt ให้ AI วิเคราะห์ข้อมูล
                data_description = st.session_state.uploaded_data.describe().to_string()
                data_sample = st.session_state.uploaded_data.head(5).to_string()

                if "data_dict" in st.session_state and st.session_state.data_dict is not None:
                    data_dict_description = st.session_state.data_dict.to_string(index=False)
                    prompt = (
                        f"I uploaded a dataset. Here's a statistical summary:\n\n{data_description}\n\n"
                        f"Sample rows from the dataset:\n\n{data_sample}\n\n"
                        f"Column descriptions from the data dictionary:\n\n{data_dict_description}\n\n"
                        f"Please analyze the dataset and provide key insights in bullet points."
                    )
                else:
                    prompt = (
                        f"I uploaded a dataset. Here's a statistical summary:\n\n{data_description}\n\n"
                        f"Sample rows from the dataset:\n\n{data_sample}\n\n"
                        f"Please analyze the dataset and provide insights or summaries in bullet points."
                    )

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

# ===== 9. Auto Plot Section =====
if st.session_state.uploaded_data is not None:
    st.subheader("📈 Section: Auto Plotting")
    column_options = st.session_state.uploaded_data.columns.tolist()
    selected_column = st.selectbox("Choose a column to plot", column_options)
    chart_type = st.radio("Chart Type", ["Histogram", "Line Chart", "Bar Chart"])

    try:
        if chart_type == "Histogram":
            st.bar_chart(st.session_state.uploaded_data[selected_column].value_counts())
        elif chart_type == "Line Chart":
            st.line_chart(st.session_state.uploaded_data[selected_column])
        elif chart_type == "Bar Chart":
            st.bar_chart(st.session_state.uploaded_data[selected_column].value_counts())
    except Exception as e:
        st.error(f"Unable to plot chart: {e}")

# ===== 10. AI Chart Suggestions =====
if model and st.session_state.uploaded_data is not None:
    st.subheader("🤖 Section: AI Suggested Charts")
    try:
        columns_info = st.session_state.uploaded_data.dtypes.astype(str).to_string()
        sample_data = st.session_state.uploaded_data.head(5).to_string()

        plot_prompt = (
            f"This is a dataset with the following columns and types:\n{columns_info}\n\n"
            f"Here are some sample rows:\n{sample_data}\n\n"
            f"Based on this, please recommend which columns to visualize and what chart types to use. "
            f"For each chart, mention the column(s) and the chart type (bar, line, histogram, scatter, etc.) "
            f"Format your answer in bullet points."
        )

        plot_response = model.generate_content(plot_prompt)
        plot_suggestions = plot_response.text

        st.markdown("### 🧠 Gemini Suggestions for Charts")
        st.markdown(plot_suggestions)

    except Exception as e:
        st.error(f"Error while generating chart recommendations: {e}")
