import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from streamlit_chat import message

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import controllers and config
from myApp.controllers.class_controller import ClassController
from myApp.controllers.localStatistics_controller import StatisticsController
from myApp.controllers.globalStatistics_controller import GlobalStatisticsController
from myApp.controllers.room_controller import RoomController
from myApp.controllers.auth_controller import AuthController
from config.environment import get_database_url  # Changed this line
from myApp.chatbot import Chatbot
from myApp.models.chatbot_model import ChatbotService

# Initialize controllers
db_url = get_database_url()  # Changed this line
class_controller = ClassController(db_url=db_url)
local_controller = StatisticsController(db_url=db_url)
global_controller = GlobalStatisticsController(db_url=db_url)
room_controller = RoomController(db_url=db_url)
auth_controller = AuthController()

# Configure requests for Ollama
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy, pool_maxsize=10)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Initialize chatbot
chatbot = Chatbot()  # Remove timeout parameter if Chatbot class can't be modified

# Configure requests timeout globally
requests.adapters.DEFAULT_TIMEOUT = 15  # Set default timeout for all requests

# Set page configuration
st.set_page_config(page_title="RUMADv2.0", layout="wide", page_icon="🎓")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.auth_token = None
    st.session_state.messages = []
    st.session_state.last_question = ""
    st.session_state.chat_history = []

# Custom CSS for additional styling
st.markdown("""
    <style>
    .stApp {
        color: inherit;
    }
    .stButton>button {
        border-radius: 5px;
        background-color: #FF6B6B !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF8E8E !important;
        transform: translateY(-2px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stSelectbox>div>div>select {
        border-radius: 5px;
    }
    .stHeader {
        padding: 1rem;
        border-radius: 5px;
    }
    /* Chat container styles */
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 20px;
        background: rgba(0,0,0,0.05);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* Chat message styles */
    .chat-message {
        padding: 12px 16px;
        border-radius: 15px;
        margin: 8px 0;
        max-width: 75%;
        word-wrap: break-word;
    }
    
    .user-message {
        background: #2196F3;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }
    
    .bot-message {
        background: #4CAF50;
        color: white;
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }
    
    .message-timestamp {
        font-size: 0.7em;
        opacity: 0.7;
        margin-top: 4px;
    }
    
    /* Input area styles */
    .chat-input {
        background: white;
        border: 1px solid #ddd;
        border-radius: 20px;
        padding: 10px 20px;
        margin-top: 10px;
    }
    /* Updated chat styles */
    .chat-container {
        height: 600px;
        overflow-y: auto;
        padding: 20px;
        background: #4F4F4F;  /* Darker background color */
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column-reverse;
    }
    
    .message-group {
        padding: 20px;
        margin: 10px 0;
        width: 100%;
    }
    
    .user-message-group {
        background: #2F2F2F;  /* Darker background for user messages */
    }
    
    .bot-message-group {
        background: #3F3F3F;  /* Darker background for bot messages */
    }
    
    .chat-message {
        padding: 8px 12px;
        margin: 4px 0;
        max-width: 90%;
        line-height: 1.4;
        color: #FFFFFF;  /* White text for better contrast */
    }
    
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 20px;
        background: #2F2F2F;  /* Darker background for input area */
        border-top: 1px solid #555;
        z-index: 100;
    }
    
    .send-button {
        position: absolute;
        right: 30px;
        bottom: 30px;
        background: #FF6B6B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Authentication functions
def login(username, password):
    try:
        auth_response = auth_controller.authenticate_user(username, password)
        st.session_state.logged_in = True
        st.session_state.username = auth_response["username"]
        st.session_state.auth_token = auth_response["token"]
        st.success("Login successful!")
        st.rerun()
    except ValueError as ve:
        st.error(str(ve))
    except Exception as e:
        st.error(f"An error occurred during login: {str(e)}")

def register(username, password):
    try:
        register_response = auth_controller.register_user(username, password)
        if register_response.get("success"):
            st.success(f"Welcome {register_response['user']['username']}! Registration successful.")
            # Automatically log in the user after registration
            login(username, password)
        else:
            st.error("Registration failed. Please try again.")
    except ValueError as ve:
        st.error(str(ve))
    except Exception as e:
        st.error(f"An error occurred during registration: {str(e)}")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.auth_token = None
    st.info("You have been logged out.")
    st.rerun()

# Helper functions
def send_chat_request(question: str, user_id: str = "anonymous") -> dict:
    try:
        response = chatbot.process_question(question, user_id)
        if isinstance(response, str):
            return {"answer": response}
        return response
    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "error": "Sorry, I'm having trouble processing your request.",
            "fallback": True
        }

def add_to_knowledge_base(content: str, auth_token: str, file_content: str = None) -> bool:
    try:
        if not auth_token:
            raise ValueError("No auth token provided")
            
        # Validate token directly
        user_info = auth_controller.validate_token(token=auth_token)
        user_id = user_info["user_id"]
        
        # Combine text content and file content if both exist
        if file_content:
            content = f"{content}\n\n{file_content}" if content else file_content
            
        result = chatbot.store_knowledge(content, user_id)
        if result and "id" in result:
            print(f"Successfully stored knowledge with ID: {result['id']}")
            return True
        return False
    except Exception as e:
        print(f"Error adding to knowledge base: {e}")
        return False

def process_uploaded_file(uploaded_file) -> str:
    try:
        if uploaded_file.type == "application/pdf":
            # Add PyPDF2 import at the top of the file
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join(page.extract_text() for page in pdf_reader.pages)
            
        elif uploaded_file.type == "text/plain":
            return uploaded_file.getvalue().decode("utf-8")
            
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            return df.to_string()
            
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.type}")
            
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

def process_chat_input(question: str):
    if not question.strip():
        return
        
    with st.spinner("VIC is thinking..."):
        try:
            user_id = st.session_state.get("username", "anonymous")
            response = send_chat_request(question, user_id)
            
            if isinstance(response, dict):
                if "error" in response:
                    if response.get("fallback", False):
                        st.error(response["error"])
                        return
                    content = response["error"]
                else:
                    content = response.get("answer", "No answer available")
            else:
                content = str(response)
            
            # Create new messages
            new_messages = [
                {"role": "user", "content": question},
                {"role": "assistant", "content": content}
            ]
            
            # Add to current session messages
            st.session_state.messages.extend(new_messages)
            
            # Add to chat history with timestamp
            chat_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": new_messages.copy(),
                "user_id": user_id
            }
            st.session_state.chat_history.append(chat_entry)
            
            st.rerun()
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            print(f"Chat error: {e}")

# UI Components
def render_auth_page():
    st.title("Welcome to RUMADv2.0 🎓✨")
    st.image("./myApp/nprlogo.png", use_container_width=True)
    
    auth_type = st.radio("Choose action:", ("Login", "Sign Up"))
    
    username = st.text_input("Username", key="auth_username")
    password = st.text_input("Password", type="password", key="auth_password")
    
    if auth_type == "Login":
        if st.button("Login", key="login_button"):
            login(username, password)
    else:
        if st.button("Sign Up", key="signup_button"):
            register(username, password)

def render_home_page():
    st.title("Welcome to RUMADv2.0 🏫")
    st.image("./myApp/nprlogo.png", use_container_width=False)
    st.markdown(
        """
        <h1 style='text-align: center;'>Welcome to RUMADv2.0</h1>
        <p style='text-align: center;'>Your personalized academic assistant to guide you through your academic journey.</p>
        """,
        unsafe_allow_html=True,
    )

    st.header("Course Catalog 📚")
    
    # Fetch courses from the database
    courses = class_controller.get_all_classes()

    if courses:
        # Convert the courses into a DataFrame
        course_data = [
            {
                "Course Name": course["cname"],
                "Course Code": course["ccode"],
                "Description": course["cdesc"],
                "Credits": course["cred"],
                "Term Offered": course["term"],
                "Years Offered": course["years"],
                "Syllabus": course["csyllabus"]
            }
            for course in courses
        ]
        df = pd.DataFrame(course_data)

        # Display courses in an interactive table
        st.dataframe(df)

        # Download Button for CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Course List as CSV",
            data=csv,
            file_name="course_catalog.csv",
            mime="text/csv",
        )
    else:
        st.write("No courses available in the catalog.")

def render_local_statistics():
    st.header("Local Statistics 📊")

    rooms = room_controller.get_all_rooms()
    building_options = pd.DataFrame(rooms)["building"].unique()

    # Local Statistics: Room Capacity
    try:
        building = st.selectbox("Select a Building for Room Statistics:", options=building_options)
        if building:
            st.subheader(f"Top 3 Rooms by Capacity in Building {building}")
            rooms = local_controller.room_capacity(building)
            if rooms:
                room_data = pd.DataFrame(rooms)
                room_data.columns = ["Room ID", "Room Number", "Capacity"]  # Rename columns for clarity
                st.table(room_data)

                # Ensure data is sorted
                room_data = room_data.sort_values(by="Capacity", ascending=True)

                # Plot room capacity using Streamlit
                st.bar_chart(
                    data=room_data.set_index("Room ID")["Capacity"],
                    use_container_width=True,
                )
            else:
                st.warning("No data found for selected building.")
    except Exception as e:
        st.error(f"Error fetching room capacity data: {e}")

    # Local Statistics: Sections by Student-to-Capacity Ratio
    try:
        st.subheader(f"Top 3 Sections by Student-to-Capacity Ratio in Building {building}")
        sections_ratio = local_controller.room_ratio(building)
        if sections_ratio:
            ratio_data = pd.DataFrame(sections_ratio)
            ratio_data.columns = ["Section ID", "Semester", "Ratio (%)", "Room Number"]  # Rename columns for clarity
            st.table(ratio_data)

            # Ensure data is sorted
            ratio_data = ratio_data.sort_values(by="Ratio (%)", ascending=True)

            # Plot ratio using Streamlit
            st.bar_chart(
                data=ratio_data.set_index("Section ID")["Ratio (%)"],
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"Error fetching room ratio data: {e}")

    # Local Statistics: Classes per Room
    try:
        room_id = st.text_input("Enter Room ID for Top Classes:", value="1")
        if room_id:
            st.subheader(f"Top 3 Most Taught Classes in Room {room_id}")
            room_classes = local_controller.room_classes(room_id)
            if room_classes:
                class_data = pd.DataFrame(room_classes)
                class_data.columns = ["Class ID", "Class Name", "Class Code", "Number of Semesters Taught"]
                st.table(class_data)

                # Plot number of semesters taught using Streamlit
                st.bar_chart(
                    data=class_data.set_index("Class ID")["Number of Semesters Taught"],
                    use_container_width=True,
                )
    except Exception as e:
        st.error(f"Error fetching classes per room data: {e}")

    # Local Statistics: Top Classes Per Semester
    try:
        year = st.number_input("Enter Year for Semester Statistics:", min_value=2000, max_value=2100, value=2024)
        semester = st.selectbox("Select Semester for Top Classes:", options=["Fall", "Spring", "Summer"])
        if year and semester:
            st.subheader(f"Top 3 Most Taught Classes in {semester} {year}")
            semester_classes = local_controller.classes_by_semester(year, semester)
            if semester_classes:
                semester_data = pd.DataFrame(semester_classes)
                semester_data.columns = ["Class ID", "Class Name", "Number of Sections"]
                st.table(semester_data)

                # Plot number of sections using Streamlit
                st.bar_chart(
                    data=semester_data.set_index("Class ID")["Number of Sections"],
                    use_container_width=True,
                )
    except Exception as e:
        st.error(f"Error fetching classes per semester data: {e}")

def render_global_statistics():
    st.header("Global Statistics 🌐")

    # Global Statistics: Total Sections Per Year
    try:
        st.subheader("Total Sections Per Year")
        total_sections_data = global_controller.total_sections_per_year()
        if total_sections_data:
            # Convert to DataFrame for easier visualization
            total_sections_df = pd.DataFrame(total_sections_data)
            total_sections_df.columns = ["Year", "Total Sections"]  # Rename columns for clarity
            st.line_chart(
                total_sections_df.set_index("Year")["Total Sections"],
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Error fetching total sections per year: {e}")

    # Global Statistics: Top Meetings by Section Count
    try:
        st.subheader("Top 5 Meetings with the Most Sections")
        top_meetings = global_controller.top_meetings_with_most_sections()
        if top_meetings:
            meetings_df = pd.DataFrame(top_meetings)
            meetings_df.columns = [
                "Meeting ID", "Course Code", "Start Time", "End Time", "Days", "Number of Sections"
            ]
            st.table(meetings_df)

            # Plot number of sections
            st.bar_chart(meetings_df.set_index("Meeting ID")["Number of Sections"], use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching top meetings data: {e}")

    # Global Statistics: Top Classes Most Prerequisites
    try:
        st.subheader("Top 3 Classes with the Most Prerequisites")
        most_prerequisites = global_controller.top_classes_most_prerequisites()
        if most_prerequisites:
            prerequisites_df = pd.DataFrame(most_prerequisites)
            prerequisites_df.columns = ["Class ID", "Class Name", "Class Code", "Number of Prerequisites"]
            st.table(prerequisites_df)

            # Plot number of prerequisites
            st.bar_chart(prerequisites_df.set_index("Class ID")["Number of Prerequisites"], use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching classes with the most prerequisites: {e}")

    # Global Statistics: Top Classes Least Offered
    try:
        st.subheader("Top 3 Classes Offered the Least")
        least_offered = global_controller.top_classes_least_offered()
        if least_offered:
            least_offered_df = pd.DataFrame(least_offered)
            least_offered_df.columns = ["Class ID", "Class Name", "Class Code", "Number of Times Offered"]
            st.table(least_offered_df)

            # Plot number of times offered
            st.bar_chart(least_offered_df.set_index("Class ID")["Number of Times Offered"], use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching least offered classes: {e}")

def render_vic_interface():
    st.title("Ask VIC! 🤖💡")
    
    chat_col, info_col = st.columns([3, 1])
    
    with chat_col:
        # Define tabs first
        chat_tab, knowledge_tab = st.tabs(["💬 Chat with VIC", "🧠 Knowledge Base Management"])
        
        with chat_tab:
            st.markdown("""
            <style>
            .stChatMessage {
                padding: 10px;
                border-radius: 15px;
                margin-bottom: 10px;
            }
            .stChatMessage.user {
                background-color: #E6F3FF;
                border: 1px solid #B3D9FF;
            }
            .stChatMessage.assistant {
                background-color: #F0F0F0;
                border: 1px solid #D3D3D3;
            }
            .chat-container {
                height: 400px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Add example buttons
            st.write("Try these examples:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📚 What are the requisites for CIIC 3015?"):
                    process_chat_input("What are the requisites for CIIC 3015?")
                if st.button("📊 How are grades divided in CIIC 4060?"):
                    process_chat_input("How are grades divided in CIIC 4060?")
            with col2:
                if st.button("📖 What textbooks are used in CIIC 4030?"):
                    process_chat_input("What textbooks are used in CIIC 4030?")
                if st.button("🎯 List topics in CIIC 4020"):
                    process_chat_input("List topics in CIIC 4020")

            # Chat container with messages
            with st.container():
                for i, msg in enumerate(st.session_state.messages):
                    message(msg["content"], is_user=msg["role"] == "user", key=f"{i}_{msg['role']}")
            
            # User input and send button
            with st.container():
                col1, col2 = st.columns([6,1])
                with col1:
                    user_input = st.text_input(
                        "Ask VIC:",
                        key="chat_input_field",
                        value="",
                        placeholder="Type your question here...",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    send_pressed = st.button("🚀", key="send_button")
                
                if send_pressed and user_input:
                    process_chat_input(user_input)

        with knowledge_tab:
            st.subheader("Knowledge Base Management 📚")
            if "auth_token" not in st.session_state:
                st.warning("Please log in to manage the knowledge base")
            else:
                # Add Knowledge section
                st.subheader("Add New Knowledge Entry")
                uploaded_file = st.file_uploader(
                    "Upload File (PDF, TXT, CSV)", 
                    type=["pdf", "txt", "csv"],
                    help="Upload a file to add to the knowledge base"
                )
                
                content = st.text_area(
                    "Content", 
                    height=150,
                    placeholder="Enter your knowledge here...",
                    help="Enter the content you want to add to the knowledge base"
                )
                
                col1, col2 = st.columns([3,1])
                with col1:
                    tags = st.multiselect(
                        "Tags",
                        options=["Course Info", "Prerequisites", "Policies", "Schedule", "Other"],
                        default=None,
                        help="Select relevant tags for this knowledge entry"
                    )
                with col2:
                    priority = st.selectbox(
                        "Priority",
                        options=["Low", "Medium", "High"],
                        index=1
                    )
                
                if st.button("Add to Knowledge Base", use_container_width=True):
                    try:
                        file_content = None
                        if uploaded_file:
                            with st.spinner("Processing file..."):
                                file_content = process_uploaded_file(uploaded_file)
                        
                        if not content.strip() and not file_content:
                            st.error("Please provide content or upload a file!")
                        else:
                            with st.spinner("Adding to knowledge base..."):
                                combined_content = content
                                if file_content:
                                    combined_content = f"{content}\n\n{file_content}" if content.strip() else file_content
                                
                                if add_to_knowledge_base(combined_content, st.session_state.auth_token, file_content):
                                    st.success("✅ Knowledge added successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to add knowledge")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with info_col:
        st.subheader("VIC Info")
        st.info("""
        VIC is your Virtual Institutional Counselor. 
        Ask about:
        - Course information
        - Prerequisites
        - Schedules
        - Academic policies
        """)
        
        # Clear buttons side by side
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("🗑️ Clear History", key="clear_history"):
                st.session_state.chat_history = []
                st.rerun()

        # Add Chat History section
        st.subheader("Chat History 📜")
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💭 Chat {chat.get('timestamp', 'Unknown time')}", expanded=False):
                if chat.get('messages'):
                    st.markdown("**Preview:**")
                    preview_msg = chat['messages'][0]['content']
                    st.markdown(f"{preview_msg[:100]}...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👀 View", key=f"view_{idx}"):
                        for msg in chat['messages']:
                            st.write(f"**{'You' if msg['role'] == 'user' else 'VIC'}:** {msg['content']}")
                with col2:
                    if st.button("📂 Load", key=f"load_{idx}"):
                        st.session_state.messages = chat['messages'].copy()
                        st.success("Chat loaded! ✅")
                        st.rerun()

# Main app logic
def main():
    if not st.session_state.logged_in:
        render_auth_page()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username} 👋")
        if st.sidebar.button("🚪 Logout"):
            logout()

        menu = st.sidebar.radio("Navigate 🧭", ["🏠 Home", "📊 Local Statistics", "🌐 Global Statistics", "🤖 Virtual Institutional Counselor"])

        if menu == "🏠 Home":
            render_home_page()
        elif menu == "📊 Local Statistics":
            render_local_statistics()
        elif menu == "🌐 Global Statistics":
            render_global_statistics()
        elif menu == "🤖 Virtual Institutional Counselor":
            render_vic_interface()

    st.markdown(
        """
        <hr>
        <footer style="text-align: center;">
            <p>&copy; 2024 RUMADv2.0 - Virtual Institutional Counselor</p>
        </footer>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()