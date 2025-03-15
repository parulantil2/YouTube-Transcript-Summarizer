import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set page configuration (MUST BE THE FIRST STREAMLIT COMMAND)
st.set_page_config(
    page_title="YouTube Transcript Summarizer",
    page_icon="📝",
    layout="centered"
)

# In-memory user database (for demonstration purposes)
users = {}

# Function to extract transcript details
def extract_transcript_details(youtube_video_url):
    try:
        # Extract video ID from URL
        if "youtube.com" in youtube_video_url:
            video_id = youtube_video_url.split("=")[1]
        elif "youtu.be" in youtube_video_url:
            video_id = youtube_video_url.split("/")[-1]
        else:
            raise ValueError("Invalid YouTube URL")

        # Fetch transcript
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Convert transcript list to a single string
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript

    except TranscriptsDisabled:
        st.error("🚫 Transcripts are disabled for this video.")
        return None
    except NoTranscriptFound:
        st.error("🚫 No transcript found for this video.")
        return None
    except Exception as e:
        st.error(f"🚫 An error occurred: {e}")
        return None

# Function to generate summary using Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Custom CSS for dark/light mode
def load_css():
    st.markdown("""
        <style>
            /* General styles */
            body {
                font-family: 'Arial', sans-serif;
                transition: background-color 0.3s, color 0.3s;
            }
            .stButton button {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                width: 100%;
            }
            .stButton button:hover {
                background-color: #45a049;
            }
            .stTextInput input {
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            .stMarkdown h1 {
                color: #4CAF50;
            }
            .stMarkdown h2 {
                color: #2E86C1;
            }
            /* Navbar styles */
            .navbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .navbar a {
                color: white;
                text-decoration: none;
                margin: 0 10px;
            }
            .navbar a:hover {
                text-decoration: underline;
            }
            /* Card styles */
            .card {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            /* Footer styles */
            .footer {
                text-align: center;
                padding: 20px;
                margin-top: 20px;
                background-color: #f1f1f1;
                border-top: 1px solid #ddd;
            }
            .footer a {
                color: #4CAF50;
                text-decoration: none;
            }
            .footer a:hover {
                text-decoration: underline;
            }
            /* Dark mode styles */
            .dark-mode {
                background-color: #121212;
                color: #ffffff;
            }
            .dark-mode .stButton button {
                background-color: #333;
                color: #ffffff;
            }
            .dark-mode .stTextInput input {
                background-color: #333;
                color: #ffffff;
                border: 1px solid #555;
            }
            .dark-mode .card {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            .dark-mode .footer {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

# JavaScript to toggle dark/light mode
def toggle_dark_mode():
    st.markdown("""
        <script>
            function toggleTheme() {
                const body = document.body;
                body.classList.toggle('dark-mode');
                const isDarkMode = body.classList.contains('dark-mode');
                localStorage.setItem('darkMode', isDarkMode);
            }
            // Apply saved theme preference
            const savedDarkMode = localStorage.getItem('darkMode') === 'true';
            if (savedDarkMode) {
                document.body.classList.add('dark-mode');
            }
        </script>
    """, unsafe_allow_html=True)

# Streamlit app
def main():
    # Load custom CSS
    load_css()

    # Initialize session state for login and theme
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    # Navbar
    st.markdown("""
        <div class="navbar">
            <div>YouTube Transcript Summarizer</div>
            <div>
                <a href="#">Home</a>
                <a href="#">About</a>
                <a href="#">Contact</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Dark/Light mode toggle
    if st.sidebar.button("Toggle Dark/Light Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        toggle_dark_mode()

    # Login/Sign-Up form
    if not st.session_state.logged_in:
        st.title("Welcome to the YouTube Transcript Summarizer")
        choice = st.radio("Select an option:", ["Login", "Sign Up"])

        if choice == "Login":
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.button("Login")

            if login_button:
                if username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Invalid username or password")

        elif choice == "Sign Up":
            st.subheader("Sign Up")
            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            signup_button = st.button("Sign Up")

            if signup_button:
                if new_username in users:
                    st.error("Username already exists. Please choose another.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    users[new_username] = new_password
                    st.success("Account created successfully! Please log in.")
        return

    # Logout button
    if st.session_state.logged_in:
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.clear()  # Clear all session state
            st.rerun()  # Rerun the app to show the login form

    # Main app content (only visible if logged in)
    st.title("📝 YouTube Transcript to Detailed Notes Converter")
    st.markdown(f"Welcome, {st.session_state.username}!")
    st.markdown("""
        This app converts the transcript of a YouTube video into detailed notes using Google's Gemini Pro AI model.
        Simply paste the YouTube video link below and click **Get Detailed Notes**.
    """)

    # Sidebar for additional options
    with st.sidebar:
        st.header("⚙️ Settings")
        summary_length = st.slider("Summary Length (words)", 100, 500, 250)
        st.markdown("---")
        st.markdown("### 📌 Tips")
        st.markdown("- Ensure the YouTube video has captions enabled.")
        st.markdown("- Use full YouTube links (e.g., `https://www.youtube.com/watch?v=...`).")

    # Input for YouTube link
    youtube_link = st.text_input("Enter YouTube Video Link:", placeholder="https://www.youtube.com/watch?v=...")

    if youtube_link:
        # Extract video ID for thumbnail
        if "youtube.com" in youtube_link:
            video_id = youtube_link.split("=")[1]
        elif "youtu.be" in youtube_link:
            video_id = youtube_link.split("/")[-1]
        else:
            st.error("Invalid YouTube URL")
            st.stop()

        # Display video thumbnail
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

    # Button to generate notes
    if st.button("Get Detailed Notes"):
        if not youtube_link:
            st.warning("Please enter a valid YouTube video link.")
        else:
            with st.spinner("Fetching transcript and generating notes..."):
                progress_bar = st.progress(0)
                transcript_text = extract_transcript_details(youtube_link)
                progress_bar.progress(50)

                if transcript_text:
                    # Update the prompt with the selected summary length
                    prompt = f"""You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in bullet points
within {summary_length} words. Please provide the summary of the text given here in the following format:
- Point 1
- Point 2
- Point 3
..."""

                    summary = generate_gemini_content(transcript_text, prompt)
                    progress_bar.progress(100)

                    st.session_state.transcript_text = transcript_text
                    st.session_state.summary = summary

                    st.markdown("## 📄 Detailed Notes:")
                    st.write(summary)

                    # Expandable section for raw transcript
                    with st.expander("📜 View Raw Transcript"):
                        st.write(transcript_text)
                else:
                    st.warning("No transcript available for this video. Please try another video with captions enabled.")

    # Copy-to-clipboard button (outside the main button block)
    if st.session_state.get("summary"):
        if st.button("📋 Copy Summary to Clipboard"):
            st.session_state.summary = st.session_state.summary
            st.success("Summary copied to clipboard!")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div class="footer">
            <p>Made with ❤️ by <a href="https://github.com/yourusername" target="_blank">Your Name</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()