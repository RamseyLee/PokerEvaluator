import os
from dotenv import load_dotenv
import google.generativeai as genai
import re
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename="PokerEvaluator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Load API key from .env
load_dotenv()
api_key = os.getenv("GOOGLE_AI_API_KEY")
if not api_key:
    print("Error: GOOGLE_AI_API_KEY not found in .env")
    logger.error("GOOGLE_AI_API_KEY not found in .env")
    exit(1)
genai.configure(api_key=api_key)

# Set up Gemini model
model = genai.GenerativeModel("gemini-2.5-pro")

# Read prompt from prompt.txt
def load_prompt(file_path="prompt.txt"):
    try:
        with open(file_path, 'r') as file:
            prompt = file.read().strip()
            logger.info("Loaded prompt.txt")
            return prompt
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        logger.error(f"{file_path} not found")
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        logger.error(f"Error reading {file_path}: {e}")
        return None

# Normalize card input (e.g., "AS" -> "Ace Spades", fix typos)
def normalize_card_input(card_input):
    if not card_input:
        return ""
    # Split by comma, space, or multiple spaces
    cards = [card.strip() for card in re.split(r'[,\s]+', card_input) if card.strip()]
    normalized_cards = []
    card_map = {
        'as': 'Ace Spades', 'ah': 'Ace Hearts', 'ad': 'Ace Diamonds', 'ac': 'Ace Clubs',
        'ks': 'King Spades', 'kh': 'King Hearts', 'kd': 'King Diamonds', 'kc': 'King Clubs',
        'qs': 'Queen Spades', 'qh': 'Queen Hearts', 'qd': 'Queen Diamonds', 'qc': 'Queen Clubs',
        'js': 'Jack Spades', 'jh': 'Jack Hearts', 'jd': 'Jack Diamonds', 'jc': 'Jack Clubs',
        '10s': '10 Spades', '10h': '10 Hearts', '10d': '10 Diamonds', '10c': '10 Clubs',
        '9s': '9 Spades', '9h': '9 Hearts', '9d': '9 Diamonds', '9c': '9 Clubs',
        '8s': '8 Spades', '8h': '8 Hearts', '8d': '8 Diamonds', '8c': '8 Clubs',
        '7s': '7 Spades', '7h': '7 Hearts', '7d': '7 Diamonds', '7c': '7 Clubs',
        '6s': '6 Spades', '6h': '6 Hearts', '6d': '6 Diamonds', '6c': '6 Clubs',
        '5s': '5 Spades', '5h': '5 Hearts', '5d': '5 Diamonds', '5c': '5 Clubs',
        '4s': '4 Spades', '4h': '4 Hearts', '4d': '4 Diamonds', '4c': '4 Clubs',
        '3s': '3 Spades', '3h': '3 Hearts', '3d': '3 Diamonds', '3c': '3 Clubs',
        '2s': '2 Spades', '2h': '2 Hearts', '2d': '2 Diamonds', '2c': '2 Clubs',
    }
    valid_ranks = {'2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'}
    valid_suits = {'Spades', 'Hearts', 'Diamonds', 'Clubs'}
    for card in cards:
        card_lower = card.lower().replace(" of ", " ")
        # Handle verbose inputs and typos
        card = re.sub(r'\bace\b', 'Ace', card, flags=re.IGNORECASE)
        card = re.sub(r'\bking\b', 'King', card, flags=re.IGNORECASE)
        card = re.sub(r'\bqueen\b', 'Queen', card, flags=re.IGNORECASE)
        card = re.sub(r'\bjack\b', 'Jack', card, flags=re.IGNORECASE)
        card = re.sub(r'\bspade\b', 'Spades', card, flags=re.IGNORECASE)
        card = re.sub(r'\bheart\b', 'Hearts', card, flags=re.IGNORECASE)
        card = re.sub(r'\bdiamond\b', 'Diamonds', card, flags=re.IGNORECASE)
        card = re.sub(r'\bclub\b', 'Clubs', card, flags=re.IGNORECASE)
        # Handle shorthand
        card_key = card_lower.replace(" ", "").replace("ten", "10")
        normalized = card_map.get(card_key, card)
        # Validate rank and suit
        parts = normalized.split()
        if len(parts) >= 2:
            rank, suit = parts[0], parts[-1]
            if rank in valid_ranks and suit in valid_suits:
                normalized_cards.append(normalized)
            else:
                logger.warning(f"Invalid card format: {card}")
        else:
            logger.warning(f"Invalid card format: {card}")
        if len(normalized_cards) >= 5:  # Limit community cards
            break
    return ", ".join(normalized_cards) if normalized_cards else card_input

# Normalize context (e.g., fix typos)
def normalize_context(context):
    if not context:
        return ""
    context = re.sub(r'\bearlly\b', 'early', context, flags=re.IGNORECASE)
    context = re.sub(r'\blatly\b', 'late', context, flags=re.IGNORECASE)
    context = re.sub(r'\bpositon\b', 'position', context, flags=re.IGNORECASE)
    return context

# Validate player cards (exactly 2 cards)
def validate_player_cards(player_cards):
    if not player_cards:
        return False, "Player's cards cannot be empty."
    cards = [card.strip() for card in player_cards.split(",") if card.strip()]
    if len(cards) != 2:
        return False, "Need exactly two player cards."
    return True, ""

def evaluate_hand():
    # Load prompt
    prompt_template = load_prompt()
    if not prompt_template:
        return

    # Initialize outputs file
    with open("outputs.txt", "a") as f:
        f.write(f"\n--- Session started at {datetime.now()} ---\n")

    while True:
        print("\nEnter poker hand details (or press Enter to skip fields):")
        player_cards = input("Player's cards (e.g., Ace Spades, King Hearts or AS, KH): ").strip()
        community_cards = input("Community cards (e.g., Queen Diamonds, 10 Clubs, 5 Spades or Qd, 10c, 5s): ").strip()
        context = input("Context (e.g., Early position, bet half the pot): ").strip()

        # Normalize inputs
        player_cards = normalize_card_input(player_cards)
        community_cards = normalize_card_input(community_cards)
        context = normalize_context(context)

        # Local validation for player cards
        is_valid, error_message = validate_player_cards(player_cards)
        if not is_valid:
            print(f"Error: {error_message}")
            logger.warning(f"Validation error: {error_message}")
            with open("outputs.txt", "a") as f:
                f.write(f"Input: Player's cards: {player_cards}; Community cards: {community_cards}; Context: {context}\n")
                f.write(f"Error: {error_message}\n")
            continue

        while True:
            # Format prompt with user inputs
            try:
                prompt = prompt_template.format(player_cards, community_cards, context)
            except ValueError as e:
                print(f"Error formatting prompt: {e}")
                logger.error(f"Error formatting prompt: {e}")
                break

            try:
                response = model.generate_content(prompt)
                response_text = response.text
                print("\nEvaluation:\n", response_text)
                with open("outputs.txt", "a") as f:
                    f.write(f"Input: Player's cards: {player_cards}; Community cards: {community_cards}; Context: {context}\n")
                    f.write(f"Output: {response_text}\n")
                logger.info(f"Evaluation: {response_text}")

                # Check if response indicates missing or unclear info
                response_lower = response_text.lower()
                if any(keyword in response_lower for keyword in ["needs", "missing", "incomplete", "unclear", "clarify", "invalid"]):
                    print("\nThe model needs more information to evaluate the hand.")
                    
                    # Determine which field needs clarification
                    if any(keyword in response_lower for keyword in ["player", "two cards", "hole cards"]):
                        print("Valid ranks: 2-10, J, Q, K, A; Valid suits: Spades, Hearts, Diamonds, Clubs")
                        additional_input = input("Provide player's cards (e.g., Ace Spades, King Hearts or AS, KH) or press Enter to retry: ").strip()
                        if additional_input:
                            player_cards = normalize_card_input(additional_input)
                            is_valid, error_message = validate_player_cards(player_cards)
                            if not is_valid:
                                print(f"Error: {error_message}")
                                logger.warning(f"Validation error: {error_message}")
                                continue
                            print(f"Updated player's cards: {player_cards}")
                            with open("outputs.txt", "a") as f:
                                f.write(f"Additional input: {additional_input}\n")
                            continue
                    elif any(keyword in response_lower for keyword in ["community", "flop", "board"]):
                        print("Valid ranks: 2-10, J, Q, K, A; Valid suits: Spades, Hearts, Diamonds, Clubs")
                        additional_input = input("Provide community cards (e.g., Queen Diamonds, 10 Clubs, 5 Spades or Qd, 10c, 5s) or press Enter to retry: ").strip()
                        if additional_input:
                            community_cards = normalize_card_input(additional_input)
                            print(f"Updated community cards: {community_cards}")
                            with open("outputs.txt", "a") as f:
                                f.write(f"Additional input: {additional_input}\n")
                            continue
                    elif any(keyword in response_lower for keyword in ["context", "position", "action"]):
                        print("Example context: Early position, bet half the pot; Late position, called a raise")
                        additional_input = input("Provide context (e.g., Early position, bet half the pot) or press Enter to retry: ").strip()
                        if additional_input:
                            context = normalize_context(additional_input)
                            print(f"Updated context: {context}")
                            with open("outputs.txt", "a") as f:
                                f.write(f"Additional input: {additional_input}\n")
                            continue
                    else:
                        additional_input = input("Provide additional details or press Enter to retry: ").strip()
                        if additional_input:
                            context = normalize_context(f"{context}, {additional_input}" if context else additional_input)
                            print(f"Updated context: {context}")
                            with open("outputs.txt", "a") as f:
                                f.write(f"Additional input: {additional_input}\n")
                            continue
                    print("Retrying with original inputs.")
                    with open("outputs.txt", "a") as f:
                        f.write("Retrying with original inputs.\n")
                    continue
                break  # Exit inner loop if evaluation is successful
            except Exception as e:
                print(f"Error querying Gemini API: {e}")
                logger.error(f"Error querying Gemini API: {e}")
                with open("outputs.txt", "a") as f:
                    f.write(f"Error: {e}\n")
                break

        # Ask user to continue
        continue_choice = input("\nEvaluate another hand? (y/n): ").strip().lower()
        with open("outputs.txt", "a") as f:
            f.write(f"Continue choice: {continue_choice}\n")
        if continue_choice != 'y':
            print("Exiting Poker Evaluator.")
            logger.info("Exiting Poker Evaluator")
            with open("outputs.txt", "a") as f:
                f.write(f"--- Session ended at {datetime.now()} ---\n")
            break

if __name__ == "__main__":
    evaluate_hand()