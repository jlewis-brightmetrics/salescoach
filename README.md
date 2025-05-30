# Salescoach - AI-Powered Sales Call Analysis

Salescoach is a Python web application that analyzes sales call transcripts using ChatGPT to provide detailed coaching feedback and insights. It helps sales representatives improve their performance by identifying strengths, areas for improvement, and providing actionable coaching recommendations.

## Features

### 🎯 Core Functionality
- **Transcript Analysis**: Upload or paste sales call transcripts for AI-powered analysis
- **Coaching Feedback**: Detailed breakdown of what went well and areas for improvement
- **Annotated Transcripts**: Line-by-line coaching annotations throughout the conversation
- **Conversational Interface**: Ask follow-up questions about the analysis or get additional coaching advice

### 🚀 User Experience
- **Modern Web Interface**: Beautiful, responsive design with Bootstrap 5
- **File Upload**: Drag-and-drop or click to upload transcript files (.txt, .csv, .md)
- **Copy/Paste Support**: Directly paste transcript text for quick analysis
- **Real-time Chat**: Interactive coaching assistant for follow-up questions
- **Session Management**: Maintains context throughout your coaching session

### 🤖 AI-Powered Analysis
- **Comprehensive Reports**: 5-section analysis including performance summary, strengths, improvements, coaching points, and outcome assessment
- **Contextual Annotations**: Smart coaching notes inserted at relevant points in the transcript
- **Follow-up Support**: Conversational AI that can answer questions about the analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Setup Steps

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd Salescoach
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `env_example.txt` to `.env`
   - Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:5000`
   - Start analyzing your sales calls!

## Usage Guide

### 1. Upload or Paste Transcript
- **File Upload**: Drag and drop a transcript file or click to browse
- **Direct Input**: Paste your transcript text directly into the text area
- Supported formats: .txt, .csv, .md files

### 2. Analyze Transcript
- Click "Analyze Transcript" to start the AI analysis
- Wait for the comprehensive analysis to complete
- Review the detailed coaching feedback

### 3. Review Results
The analysis provides:
- **Overall Performance Summary**: High-level assessment of the call
- **What the Representative Did Well**: Specific positive behaviors identified
- **Areas for Improvement**: Actionable improvement opportunities
- **Key Coaching Points**: 3-5 prioritized recommendations
- **Call Outcome Assessment**: Evaluation of likely success and next steps

### 4. Examine Annotated Transcript
- View your original transcript with coaching annotations
- Coaching notes appear as highlighted sections with specific feedback
- Identify missed opportunities and successful techniques in context

### 5. Ask Follow-up Questions
- Switch to the "Ask Questions" tab
- Chat with the AI coach about specific aspects of the call
- Get clarification on coaching recommendations
- Explore alternative approaches and strategies

## Example Analysis Output

```
**Overall Performance Summary**
The representative demonstrated strong product knowledge and maintained a professional tone throughout the call. However, there were missed opportunities for deeper discovery and relationship building.

**What the Representative Did Well**
- Opened with a clear agenda and purpose
- Demonstrated excellent product knowledge
- Handled initial objections professionally
- Maintained enthusiasm throughout

**Areas for Improvement**
- Limited discovery questions about pain points
- Missed opportunities to build rapport
- Could have been more consultative in approach
- Rushed through closing without confirming understanding

**Key Coaching Points**
1. Develop deeper discovery questions to uncover true business needs
2. Practice active listening and pause for responses
3. Build more personal connections early in the conversation
4. Use trial closes throughout to gauge interest
5. Slow down the closing process and confirm understanding

**Call Outcome Assessment**
Moderate success probability. Follow-up recommended with focus on addressing specific concerns raised about implementation timeline.
```

## API Endpoints

- `GET /` - Main application interface
- `POST /analyze` - Analyze transcript content
- `POST /upload` - Handle file uploads
- `POST /chat` - Process conversational questions
- `POST /clear` - Clear session data

## Technical Details

### Architecture
- **Backend**: Flask web framework
- **AI Integration**: OpenAI GPT-4 API
- **Frontend**: Bootstrap 5 with vanilla JavaScript
- **Session Management**: Flask sessions for maintaining context

### File Structure
```
Salescoach/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── uploads/              # Temporary file storage
├── requirements.txt      # Python dependencies
├── env_example.txt      # Environment variables template
└── README.md            # This file
```

### Security Features
- File type validation
- File size limits (16MB max)
- Secure filename handling
- Temporary file cleanup
- Session-based data isolation

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Application Settings
- Maximum file size: 16MB
- Supported file types: .txt, .csv, .md
- Session timeout: Browser session
- API model: GPT-4

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure you have access to GPT-4

2. **File Upload Issues**
   - Check file format is supported (.txt, .csv, .md)
   - Ensure file size is under 16MB
   - Verify file encoding is UTF-8

3. **Analysis Takes Too Long**
   - Large transcripts may take 30-60 seconds to analyze
   - Check your internet connection
   - OpenAI API may have temporary delays

### Getting Help
- Check the browser console for JavaScript errors
- Review the Flask application logs
- Ensure all dependencies are installed correctly

## Contributing

This is a personal project, but suggestions and improvements are welcome! Feel free to:
- Report bugs or issues
- Suggest new features
- Submit pull requests with improvements

## License

This project is for educational and personal use. Please ensure compliance with OpenAI's usage policies when using their API.

## Acknowledgments

- Built with Flask and OpenAI's GPT-4
- UI powered by Bootstrap 5 and Font Awesome
- Designed for sales professionals and coaching teams 