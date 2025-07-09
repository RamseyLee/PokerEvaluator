# Poker Hand Evaluator

A terminal-based Python script designed to evaluate Texas Hold'em poker hands using Google AI Studio's Gemini 2.5 Pro model. The tool processes structured and unstructured inputs (e.g., shorthand "AS," verbose "Ace of Spades," typos), provides beginner-friendly feedback, and promotes responsible gambling.

## Project Overview

This tool allows users to input poker hand details (player's cards, community cards, context) via the terminal. It leverages advanced prompt engineering with Gemini 2.5 Pro for flexible input normalization and Python for robust validation, ensuring accurate evaluations even with incomplete or ambiguous inputs. Feedback includes what was done well, mistakes, an improvement tip, and a responsible gambling message ("Play responsibly within your limits").

## Setup

1. **Install Python 3.8+**:
   
   brew install python
   
2. **Install Dependencies**:
   
   pip install google-generativeai python-dotenv
   
3. **Configure API Key**:
   - Obtain a Google AI Studio API key.
   - Create a `.env` file in the project root:
     
     echo "GOOGLE_AI_API_KEY=your_api_key_here" > .env
     
   - The `.env` file is excluded from Git via `.gitignore` for security.
4. **Ensure Required Files**:
   - `PokerEvaluator.py`: Main script.
   - `prompt.txt`: Prompt for Gemini model.
   - Place both in the project directory (`~/Desktop/PokerEvaluator`).

## Usage

1. Navigate to the project directory:
   
   cd ~/Desktop/PokerEvaluator
   
2. Run the script:
   
   python3 PokerEvaluator.py
   
3. Enter poker hand details when prompted:
   - **Player's cards**: e.g., "AS, KH" or "Ace Spades, King Hearts".
   - **Community cards**: e.g., "Qd, 10c, 5s" or "Queen Diamonds, 10 Clubs, 5 Spades" (0-5 cards).
   - **Context**: e.g., "Early position, bet half the pot".
4. Review feedback, provide clarifications if prompted, and choose to evaluate another hand (`y/n`).
5. Check logs:
   - `outputs.txt`: Session inputs, outputs, and errors.
   - `poker_evaluator.log`: Debugging information.

### Example

**Input**:

Player's cards: AS, KH
Community cards: Qd, 10c, 5s
Context: Early position, bet half pot

**Output**:

Evaluation:
Nice work with Ace-King! Your half-pot bet builds value. In early position, it might reveal your strength. Tip: Try a smaller bet to disguise your hand. Play responsibly within your limits.

## Features

- **Continuous Evaluation**: Loops to evaluate multiple hands until the user exits.
- **Flexible Input Handling**: Normalizes shorthand (e.g., "AS"), verbose (e.g., "Ace of Spades"), typos (e.g., "Ace Spade"), and mixed formats via Gemini 1.5 Flash.
- **Robust Validation**: Python ensures exactly two player cards; Gemini validates ranks (2-10, J, Q, K, A) and suits (Spades, Hearts, Diamonds, Clubs).
- **Dynamic Clarification**: Prompts for specific corrections (e.g., invalid suits, vague context).
- **Logging**: Saves inputs/outputs to `outputs.txt` and debug info to `poker_evaluator.log`.
- **Cost-Efficient**: Minimizes API calls with local validation.
- **Responsible Gambling**: Includes "Play responsibly within your limits" in all feedback.

## Notes

- **API Key Security**: The `GOOGLE_AI_API_KEY` is stored in `.env`, which is excluded from Git via `.gitignore`. Reviewers must provide their own API key.
- **Sample Outputs**: See `outputs.txt` for example sessions and `poker_evaluator.log` for debugging logs.
- **Prompt Engineering**: The `prompt.txt` file leverages Gemini’s NLP for flexible input parsing, showcasing advanced AI integration for PokerStars’ engagement.

## License

MIT License. See `LICENSE` for details (if included).