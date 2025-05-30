# Deploying Salescoach to Replit

Follow these steps to deploy your Salescoach application to Replit:

## 🚀 Quick Setup Steps

### 1. Create a New Replit Project

1. Go to [replit.com](https://replit.com)
2. Click **"Create Repl"**
3. Choose **"Import from GitHub"** or **"Upload files"**
4. If uploading files, select **"Python"** as the template

### 2. Upload Your Files

Upload all these files to your Replit project:

- `main.py` - Entry point for Replit
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `.replit` - Replit configuration
- `replit.nix` - System dependencies
- `templates/index.html` - Web interface
- `sample_transcript.txt` - Example transcript
- `README.md` - Documentation

### 3. Set Environment Variables

⚠️ **IMPORTANT**: You need to set your OpenAI API key as an environment variable.

1. In your Replit project, click on **"Secrets"** tab (🔐 icon in sidebar)
2. Add a new secret:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: Your actual OpenAI API key (starts with `sk-`)

Optional:
- **Key**: `SECRET_KEY`
- **Value**: A random string for Flask sessions (optional, will auto-generate if not set)

### 4. Install Dependencies

Replit should automatically install dependencies from `requirements.txt`. If not, run:

```bash
pip install -r requirements.txt
```

### 5. Run the Application

1. Click the **"Run"** button in Replit
2. Your app will start on port 8080
3. Replit will provide a URL like: `https://your-repl-name.your-username.repl.co`

## 🌐 Accessing Your App

Once running, you can:
- Access the app through the Replit preview window
- Share the public URL with others
- Use all Salescoach features (transcript analysis, coaching chat, etc.)

## 🔧 Configuration

### Dependencies (requirements.txt)
```
flask==2.3.3
openai>=1.40.0
python-dotenv==1.0.0
werkzeug==2.3.7
gunicorn==21.2.0
httpx>=0.27.0,<0.28.0
```

### Environment Variables Required
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `SECRET_KEY` - Flask secret key (optional)

## 🐛 Troubleshooting

### Common Issues

1. **"OpenAI API key not configured" error**
   - Make sure you've added `OPENAI_API_KEY` to Replit Secrets
   - Restart your Repl after adding the secret

2. **Dependencies not installing**
   - Run `pip install -r requirements.txt` in the console
   - Check that `requirements.txt` is in the root directory

3. **App not starting**
   - Check the console for error messages
   - Make sure `main.py` is in the root directory
   - Verify `.replit` configuration file exists

4. **502 Bad Gateway errors**
   - Restart the Repl
   - Check if the app is running on port 8080
   - Look for Python errors in the console

### Console Commands

If you need to run commands in Replit console:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app manually
python main.py

# Check Python version
python --version

# List installed packages
pip list
```

## 🚀 Deployment Tips

1. **Keep your API key secure** - Never commit it to code, always use Replit Secrets
2. **Monitor usage** - Watch your OpenAI API usage to manage costs
3. **Test thoroughly** - Try all features (upload, analysis, chat) after deployment
4. **Share safely** - The public URL can be shared with others to use the app

## 📱 Features Available

Your deployed app will have all the original features:
- ✅ Transcript upload (drag & drop or paste)
- ✅ AI-powered sales coaching analysis
- ✅ Annotated transcripts with inline coaching notes
- ✅ Interactive chat for follow-up questions
- ✅ Beautiful, responsive web interface
- ✅ Session management for context retention

## 🔗 Next Steps

1. Test your deployed app with the sample transcript
2. Share the URL with your team
3. Consider upgrading your OpenAI plan if you need higher rate limits
4. Customize the coaching prompts in `app.py` if needed

Happy coaching! 🎯 