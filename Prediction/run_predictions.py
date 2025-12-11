import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Define paths
BASE_DIR = r"C:\Users\1234\OneDrive - Vanderbilt\Projects\LLM-clinical trials"
PROMPTS_PATH = os.path.join(BASE_DIR, "Prediction", "pilot_prompts.json")
TEMPLATE_PATH = os.path.join(BASE_DIR, "Prediction", "Prediction_prompts_instruct.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "Prediction", "predicted_outcomes")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "predictions.json")
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Configuration
SAMPLE_LIMIT = None # Process all samples
MODEL_NAME = "deepseek-chat" # or "deepseek-coder" depending on preference, usually 'deepseek-chat' for reasoning

def load_system_prompt():
    """Reads the system prompt template."""
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def run_predictions():
    # 1. Load Environment
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # Try to find it in the environment variables if not in .env
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        
    if not api_key:
        print("Error: DEEPSEEK_API_KEY not found in .env or environment variables.")
        return

    # Initialize Client
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # 2. Load Prompts
    print(f"Loading prompts from {PROMPTS_PATH}...")
    with open(PROMPTS_PATH, 'r', encoding='utf-8') as f:
        all_prompts = json.load(f)
    
    # Apply limit
    prompts_to_process = all_prompts[:SAMPLE_LIMIT]
    print(f"Processing {len(prompts_to_process)} samples (Test Run)...")

    # 3. Load Template
    system_template = load_system_prompt()

    results = []
    
    for i, entry in enumerate(prompts_to_process):
        nct_id = entry['nct_id']
        input_text = entry['input_text']
        true_outcome = entry['true_outcome']
        
        print(f"[{i+1}/{len(prompts_to_process)}] Predicting for {nct_id}...")
        
        # Prepare messages
        # The template contains {input_text}. We will replace it and send as a single user message
        # or split it. For simplicity and adherence to the template structure, we'll format it
        # and send it as the user message (DeepSeek handles this well).
        
        full_prompt = system_template.replace("{input_text}", input_text)
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1000,
                temperature=0.0,
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON
            try:
                prediction_data = json.loads(content)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON response for {nct_id}. Raw: {content[:50]}...")
                prediction_data = {"prediction": "Error", "reason": "JSON Parse Error", "confidence": 0, "raw_output": content}
                
            # Combine
            result_entry = {
                "nct_id": nct_id,
                "input_text": input_text,
                "true_outcome": true_outcome,
                "model_prediction": prediction_data,
                "system_fingerprint": response.system_fingerprint
            }
            results.append(result_entry)
            
        except Exception as e:
            print(f"API Error for {nct_id}: {e}")
            results.append({
                "nct_id": nct_id,
                "true_outcome": true_outcome,
                "error": str(e)
            })
            
        # Nice to have: sleep to avoid instant rate limiting if tier is low
        time.sleep(1)

    # 4. Save Results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"Saved results to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_predictions()
