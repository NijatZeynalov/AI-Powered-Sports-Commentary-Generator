# AI-Powered Sports Commentary Generator

A sophisticated real-time sports commentary system that combines live game statistics with AI-powered natural language generation and voice synthesis to create engaging sports commentary.

## Features

- **Real-time Game Analysis**
  - Integration with live sports data APIs
  - Advanced game state analysis
  - Momentum and performance tracking

- **AI Commentary Generation**
  - Natural language generation using Groq API
  - Multiple commentary styles (excited, neutral, analytical)
  - Context-aware commentary based on game situations

- **Voice Synthesis**
  - High-quality text-to-speech using Azure Cognitive Services
  - Multiple voice profiles for different commentary styles
  - Customizable speech parameters

## Technology Stack

- Python 3.9+
- Groq AI API for natural language generation
- Azure Cognitive Services for speech synthesis
- Real-time sports data API integration
- Type hints and data validation throughout

## Installation

1. Clone the repository:


2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

Update the `.env` file with your API credentials and preferences. Required settings include:
- `GROQ_API_KEY`: Your Groq API key
- `AZURE_SPEECH_KEY`: Azure Cognitive Services key
- `AZURE_SPEECH_REGION`: Azure service region
- `GAME_STATS_API_KEY`: Sports data API key

## Usage

1. Start the commentary system:
```bash
python -m src.main
```

2. Monitor the output:
- Generated commentary will be saved to the specified output directory
- Logs will be available in the `logs` directory
