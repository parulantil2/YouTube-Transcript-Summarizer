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

# Custom CSS for styling
def load_css():
    st.markdown("""
        <style>
            /* General styles */
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f5f5f5;
                color: #333;
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
        </style>
    """, unsafe_allow_html=True)

# Streamlit app
def main():
    # Load custom CSS
    load_css()

    # Title and description
    st.title("📝 YouTube Transcript to Detailed Notes Converter")
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