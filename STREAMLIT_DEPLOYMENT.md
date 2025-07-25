# Streamlit Cloud Deployment Guide

## Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Gemini API Key**: Get your API key from [Google AI Studio](https://aistudio.google.com/)

## Deployment Steps

### 1. Push Your Code to GitHub

Make sure all your files are committed and pushed to GitHub:

```bash
git add .
git commit -m "Add Streamlit interface for Gemini VEO3 Assistant"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set the path to your Streamlit app: `gemini_streamlit_interface.py`
6. Click "Deploy!"

### 3. Configure API Key (IMPORTANT!)

After deployment, you need to add your Gemini API key:

1. Go to your deployed app
2. Click the hamburger menu (☰) in the top right
3. Select "Settings"
4. Scroll down to "Secrets"
5. Add your API key in this format:

```toml
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

6. Click "Save"
7. Your app will automatically redeploy

## File Structure for Deployment

Make sure your repository has these files:

```
your-repo/
├── gemini_streamlit_interface.py
├── veo3-assistant-system-prompt.md
├── requirements.txt
├── README.md
└── .gitignore
```

## Troubleshooting

### "System prompt file not found"
- The app will use a fallback system prompt if the file isn't found
- Make sure `veo3-assistant-system-prompt.md` is in your repository

### "GEMINI_API_KEY not found"
- Check that you added the secret correctly in Streamlit Cloud
- The secret name must be exactly `GEMINI_API_KEY`
- Wait a few minutes for the app to redeploy after adding secrets

### App not loading
- Check the deployment logs in Streamlit Cloud
- Make sure all dependencies are in `requirements.txt`
- Verify the file path in the deployment settings

## Local Testing

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Run locally
streamlit run gemini_streamlit_interface.py
```

## Security Notes

- Never commit your API key to GitHub
- Use Streamlit secrets for production deployments
- The `.env` file should be in your `.gitignore`

## Support

If you encounter issues:
1. Check the deployment logs in Streamlit Cloud
2. Verify your API key is working
3. Test the app locally first
4. Check that all files are properly committed to GitHub 