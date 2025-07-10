# Prompt OPT

A powerful prompt optimization tool that uses Google's Gemini AI to enhance and refine prompts for better AI model performance.

## Features

- **Streamlit Web Interface**: User-friendly web application for prompt optimization
- **Gemini AI Integration**: Leverages Google's Gemini AI for intelligent prompt enhancement
- **Multiple Optimization Modes**: Different approaches to prompt optimization
- **Real-time Results**: Instant feedback and suggestions
- **Export Capabilities**: Save optimized prompts for later use

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RohitMudili/prompt-opt.git
cd prompt-opt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Gemini API key:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root and add:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

### Web Interface (Recommended)

Run the Streamlit application:
```bash
streamlit run streamlit_prompt_optimizer.py
```

This will open a web interface where you can:
- Input your original prompt
- Choose optimization strategies
- Get real-time suggestions
- Export optimized prompts

### Command Line Usage

For quick optimization:
```bash
python quick_optimize.py "Your prompt here"
```

For more detailed optimization:
```bash
python gemini_prompt_optimizer.py
```

### Example Usage

See `example_usage.py` for detailed examples of how to use the optimization functions programmatically.

## Project Structure

- `streamlit_prompt_optimizer.py` - Main web application
- `gemini_prompt_optimizer.py` - Core optimization logic
- `quick_optimize.py` - Command-line interface
- `example_usage.py` - Usage examples
- `requirements.txt` - Python dependencies

## Dependencies

- streamlit>=1.28.0
- google-generativeai>=0.3.0
- python-dotenv>=0.19.0
- pandas>=1.3.0
- plotly>=5.15.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub. 