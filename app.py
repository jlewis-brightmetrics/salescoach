import streamlit as st
import os
from sales_analyzer import SalesAnalyzer
import tempfile

# Page configuration
st.set_page_config(
    page_title="Sales Coach - Transcript Analyzer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the sales analyzer
@st.cache_resource
def get_analyzer():
    return SalesAnalyzer()

def main():
    st.title("💼 Sales Coach - Transcript Analyzer")
    st.markdown("---")
    
    # Sidebar for API key configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            st.error("⚠️ OpenAI API Key not found in environment variables")
            st.info("Please configure OPENAI_API_KEY in your environment")
            return
        else:
            st.success("✅ OpenAI API Key configured")
        
        st.markdown("---")
        st.header("About")
        st.markdown("""
        This application analyzes sales call transcripts to provide:
        - **Key insights** and conversation summary
        - **Customer sentiment** analysis
        - **Objections** and concerns identification
        - **Action items** and next steps
        - **Performance metrics** and recommendations
        """)

    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 Upload Transcript")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a transcript file",
            type=['txt', 'doc', 'docx', 'pdf'],
            help="Upload your sales call transcript in TXT, DOC, DOCX, or PDF format"
        )
        
        # Text input as alternative
        st.markdown("**Or paste transcript directly:**")
        transcript_text = st.text_area(
            "Paste your transcript here",
            height=300,
            placeholder="Paste the sales call transcript here..."
        )
        
        # Analysis button
        analyze_button = st.button(
            "🔍 Analyze Transcript",
            type="primary",
            use_container_width=True,
            disabled=not (uploaded_file or transcript_text.strip())
        )

    with col2:
        st.header("📊 Analysis Results")
        
        if analyze_button:
            try:
                analyzer = get_analyzer()
                
                # Get transcript content
                if uploaded_file:
                    # Handle file upload
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        content = analyzer.extract_text_from_file(tmp_file_path)
                    finally:
                        os.unlink(tmp_file_path)  # Clean up temp file
                else:
                    content = transcript_text.strip()
                
                if not content:
                    st.error("❌ No content found in the transcript")
                    return
                
                # Show loading spinner
                with st.spinner("🤖 Analyzing transcript with AI..."):
                    analysis_result = analyzer.analyze_transcript(content)
                
                if analysis_result:
                    # Display results in tabs
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📋 Summary", 
                        "😊 Sentiment", 
                        "❗ Objections", 
                        "✅ Action Items", 
                        "📈 Performance"
                    ])
                    
                    with tab1:
                        st.subheader("Key Insights")
                        st.write(analysis_result.get('summary', 'No summary available'))
                        
                        st.subheader("Main Topics Discussed")
                        topics = analysis_result.get('topics', [])
                        if topics:
                            for i, topic in enumerate(topics, 1):
                                st.write(f"{i}. {topic}")
                        else:
                            st.write("No specific topics identified")
                    
                    with tab2:
                        sentiment = analysis_result.get('sentiment', {})
                        
                        col_sent1, col_sent2 = st.columns(2)
                        with col_sent1:
                            st.metric(
                                "Overall Sentiment",
                                sentiment.get('overall', 'Neutral'),
                                help="Customer's overall sentiment during the call"
                            )
                        
                        with col_sent2:
                            confidence = sentiment.get('confidence', 0.5)
                            st.metric(
                                "Confidence Score",
                                f"{confidence:.1%}",
                                help="AI confidence in sentiment analysis"
                            )
                        
                        st.subheader("Sentiment Analysis")
                        st.write(sentiment.get('explanation', 'No detailed sentiment analysis available'))
                    
                    with tab3:
                        objections = analysis_result.get('objections', [])
                        
                        if objections:
                            st.subheader("Identified Objections")
                            for i, objection in enumerate(objections, 1):
                                with st.expander(f"Objection {i}: {objection.get('type', 'Unknown')}"):
                                    st.write("**Customer Concern:**")
                                    st.write(objection.get('concern', 'No details available'))
                                    st.write("**Suggested Response:**")
                                    st.write(objection.get('response', 'No response suggested'))
                        else:
                            st.info("✅ No major objections identified in this transcript")
                    
                    with tab4:
                        action_items = analysis_result.get('action_items', [])
                        
                        if action_items:
                            st.subheader("Next Steps")
                            for i, action in enumerate(action_items, 1):
                                st.write(f"**{i}. {action.get('task', 'Unknown task')}**")
                                st.write(f"   - Priority: {action.get('priority', 'Medium')}")
                                st.write(f"   - Timeline: {action.get('timeline', 'Not specified')}")
                                st.write("")
                        else:
                            st.info("No specific action items identified")
                    
                    with tab5:
                        performance = analysis_result.get('performance', {})
                        
                        # Performance metrics
                        col_perf1, col_perf2, col_perf3 = st.columns(3)
                        
                        with col_perf1:
                            st.metric(
                                "Talk Ratio",
                                performance.get('talk_ratio', 'Unknown'),
                                help="Sales rep vs customer talk time"
                            )
                        
                        with col_perf2:
                            st.metric(
                                "Question Quality",
                                performance.get('question_quality', 'Unknown'),
                                help="Quality of questions asked"
                            )
                        
                        with col_perf3:
                            st.metric(
                                "Overall Score",
                                performance.get('overall_score', 'Unknown'),
                                help="Overall call performance rating"
                            )
                        
                        st.subheader("Performance Insights")
                        st.write(performance.get('insights', 'No performance insights available'))
                        
                        st.subheader("Recommendations")
                        recommendations = performance.get('recommendations', [])
                        if recommendations:
                            for rec in recommendations:
                                st.write(f"• {rec}")
                        else:
                            st.write("No specific recommendations available")
                
                else:
                    st.error("❌ Failed to analyze transcript. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Error analyzing transcript: {str(e)}")
                st.info("Please check your transcript content and try again.")
        
        elif not (uploaded_file or transcript_text.strip()):
            st.info("👆 Upload a file or paste transcript text to begin analysis")
        
        else:
            st.info("👆 Click 'Analyze Transcript' to start the analysis")

if __name__ == "__main__":
    main()
