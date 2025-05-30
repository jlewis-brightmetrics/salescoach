from flask import Flask, render_template, request, jsonify, session, make_response
import anthropic
import os
from dotenv import load_dotenv
import json
from werkzeug.utils import secure_filename
import uuid
import tempfile
import pickle
from pdf_generator import SalesCoachPDFGenerator

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'salescoach-secret-key-' + str(uuid.uuid4()))

# Configure Anthropic
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'md'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Simple in-memory session storage to avoid large cookies
SESSION_STORE = {}

def get_session_id():
    """Get or create a session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_session_data(key, default=None):
    """Get data from session store"""
    session_id = get_session_id()
    return SESSION_STORE.get(session_id, {}).get(key, default)

def set_session_data(key, value):
    """Set data in session store"""
    session_id = get_session_id()
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {}
    SESSION_STORE[session_id][key] = value

def clear_session_data():
    """Clear session data"""
    session_id = get_session_id()
    if session_id in SESSION_STORE:
        del SESSION_STORE[session_id]
    session.clear()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SalescoachAnalyzer:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        # Using Claude Sonnet 4 - the latest model
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def analyze_transcript(self, transcript):
        """Analyze the sales call transcript and provide coaching feedback"""
        prompt = f"""
        You are an expert sales coach analyzing a sales call transcript. Please provide a comprehensive analysis with the following sections:

        1. **Overall Performance Summary**: Brief overview of how the call went
        2. **What the Representative Did Well**: Specific positive behaviors and techniques
        3. **Areas for Improvement**: Specific areas where the rep could improve
        4. **Key Coaching Points**: 3-5 actionable recommendations
        5. **Call Outcome Assessment**: Likely success/next steps

        Here's the transcript to analyze:

        {transcript}

        Please provide detailed, actionable feedback that would help this sales representative improve their performance.
        """
        
        try:
            model_name = "claude-sonnet-4-20250514"
            print(f"🤖 Using model: {model_name} with max_tokens: 20000")
            
            message = self.client.messages.create(
                model=model_name,
                max_tokens=20000,
                temperature=0.7,
                system="You are an expert sales coach with 20+ years of experience training top sales representatives.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Create result with token usage
            result = {
                'content': message.content[0].text,
                'token_usage': {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens,
                    'total_tokens': message.usage.input_tokens + message.usage.output_tokens,
                    'max_tokens_limit': 20000
                }
            }
            return result, prompt
        except Exception as e:
            return f"Error analyzing transcript: {str(e)}", prompt
    
    def annotate_transcript(self, transcript):
        """Add coaching annotations throughout the transcript"""
        prompt = f"""
        You are a sales coach reviewing a call transcript. Your task is to provide the COMPLETE original transcript with coaching annotations inserted throughout.
        
        CRITICAL INSTRUCTIONS:
        1. You MUST include the ENTIRE transcript from beginning to end
        2. Do NOT summarize, truncate, or skip any part of the conversation
        3. Continue annotating until you reach the very end of the transcript
        4. If you approach token limits, prioritize including the complete transcript over detailed annotations
        
        Format: Insert coaching feedback in [COACH: ...] format after key moments, but ensure you reproduce the complete original transcript word-for-word.
        
        Add coaching notes for:
        - Opening techniques
        - Rapport building
        - Discovery questions
        - Objection handling
        - Closing attempts
        - Missed opportunities
        
        Transcript to annotate:
        {transcript}
        
        IMPORTANT: Output the full transcript with annotations. Continue until you have covered the entire conversation from start to finish. Do not stop early.
        """
        
        try:
            print(f"🔄 Annotating transcript with model: claude-sonnet-4-20250514, max_tokens: 20000")
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=20000,
                temperature=0.7,
                system="You are a sales coach providing inline feedback on a sales call transcript.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            print(f"📊 Annotation tokens - Input: {message.usage.input_tokens}, Output: {message.usage.output_tokens}, Total: {message.usage.input_tokens + message.usage.output_tokens}")
            result = message.content[0].text
            print(f"📝 Annotation result length: {len(result)} characters")
            return result, prompt
        except Exception as e:
            return f"Error annotating transcript: {str(e)}", prompt
    
    def chat_about_analysis(self, question, transcript, previous_analysis):
        """Handle conversational questions about the transcript or analysis"""
        prompt = f"""
        You are a sales coach discussing a sales call transcript analysis. The user has a question about either the transcript or the coaching analysis.
        
        Original Transcript:
        {transcript}
        
        Previous Analysis:
        {previous_analysis}
        
        User Question: {question}
        
        Please provide a helpful, detailed response based on the transcript and analysis.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=20000,
                temperature=0.7,
                system="You are an expert sales coach answering questions about a sales call analysis.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text, prompt
        except Exception as e:
            return f"Error processing question: {str(e)}", prompt

# Initialize the analyzer (with error handling)
try:
    analyzer = SalescoachAnalyzer()
    print("✅ Salescoach initialized successfully with Claude API")
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    analyzer = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if not analyzer:
            return jsonify({'error': 'Claude API key not configured. Please set ANTHROPIC_API_KEY environment variable.'}), 500
            
        data = request.get_json()
        transcript = data.get('transcript', '').strip()
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400
        
        # Check transcript length and truncate if too long
        max_length = 50000  # Increased limit for Claude Sonnet 4 - roughly 12,500 tokens
        if len(transcript) > max_length:
            transcript = transcript[:max_length] + "\n\n[Note: Transcript truncated due to length]"
        
        # Store transcript in session store (not browser cookies)
        set_session_data('transcript', transcript)
        
        # Analyze the transcript
        print("🔄 Analyzing transcript...")
        analysis_result, analysis_prompt = analyzer.analyze_transcript(transcript)
        annotated_transcript, annotation_prompt = analyzer.annotate_transcript(transcript)
        
        # Handle the new return format with token usage
        if isinstance(analysis_result, dict) and 'content' in analysis_result:
            analysis_content = analysis_result['content']
            token_usage = analysis_result.get('token_usage', {})
        else:
            analysis_content = str(analysis_result)
            token_usage = {}
        
        # Store analysis and prompts in session store
        set_session_data('analysis', analysis_content)
        set_session_data('annotated_transcript', annotated_transcript)
        set_session_data('analysis_prompt', analysis_prompt)
        set_session_data('annotation_prompt', annotation_prompt)
        
        print("✅ Analysis completed successfully")
        print(f"📤 Sending annotated transcript length: {len(annotated_transcript)} characters")
        print(f"📄 Last 100 chars of annotated transcript: {annotated_transcript[-100:]}")
        
        return jsonify({
            'analysis': analysis_content,
            'annotated_transcript': annotated_transcript,
            'token_usage': token_usage,
            'prompts': {
                'analysis': analysis_prompt,
                'annotation': annotation_prompt
            }
        })
    
    except Exception as e:
        print(f"❌ Error in analyze: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add unique identifier to filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Read the file content
            with open(filepath, 'r', encoding='utf-8') as f:
                transcript = f.read()
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return jsonify({'transcript': transcript})
        
        return jsonify({'error': 'Invalid file type. Please upload .txt, .csv, or .md files'}), 400
    
    except Exception as e:
        print(f"❌ Error in upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not analyzer:
            return jsonify({'error': 'Claude API key not configured. Please set ANTHROPIC_API_KEY environment variable.'}), 500
            
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        transcript = get_session_data('transcript', '')
        analysis = get_session_data('analysis', '')
        
        if not transcript or not analysis:
            return jsonify({'error': 'No previous analysis found. Please analyze a transcript first.'}), 400
        
        print(f"🔄 Processing chat question: {question[:50]}...")
        response, chat_prompt = analyzer.chat_about_analysis(question, transcript, analysis)
        
        # Store the chat prompt in session for the Prompts tab
        set_session_data('last_chat_prompt', chat_prompt)
        
        return jsonify({
            'response': response,
            'chat_prompt': chat_prompt
        })
    
    except Exception as e:
        print(f"❌ Error in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/update-analysis', methods=['POST'])
def update_analysis():
    """Update the analysis results in session"""
    try:
        data = request.get_json()
        updated_analysis = data.get('analysis', '').strip()
        
        if not updated_analysis:
            return jsonify({'error': 'No analysis content provided'}), 400
        
        # Update analysis in session store
        set_session_data('analysis', updated_analysis)
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Error updating analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_session():
    clear_session_data()
    return jsonify({'success': True})

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    """Export analysis results and annotated transcript as PDF"""
    try:
        # Get analysis data from session
        analysis = get_session_data('analysis')
        annotated_transcript = get_session_data('annotated_transcript')
        original_transcript = get_session_data('transcript')
        
        if not analysis or not annotated_transcript:
            return jsonify({'error': 'No analysis data found. Please analyze a transcript first.'}), 400
        
        # Generate PDF
        pdf_generator = SalesCoachPDFGenerator()
        pdf_data = pdf_generator.generate_pdf_report(
            analysis_content=analysis,
            annotated_transcript=annotated_transcript,
            transcript_original=original_transcript or ""
        )
        
        # Create response with PDF data
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        from datetime import datetime
        response.headers['Content-Disposition'] = f'attachment; filename="sales_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        return response
        
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        return jsonify({'error': f'Failed to generate PDF: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Replit"""
    return jsonify({
        'status': 'healthy',
        'analyzer_ready': analyzer is not None,
        'api_configured': bool(os.getenv('ANTHROPIC_API_KEY'))
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"🚀 Starting Salescoach on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 