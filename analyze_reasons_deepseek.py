import os
import sys
import argparse
import pandas as pd
from openai import OpenAI
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DeepSeekAnalysisAgent:
    def __init__(self, input_file, output_file, taxonomy_file, model="deepseek-chat"):
        self.input_file = input_file
        self.output_file = output_file
        self.taxonomy_file = taxonomy_file
        self.model = model
        
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set.")
            
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        
        # Hardcoded System Prompt Template
        self.system_template = r"""You are a precise and methodical clinical research analyst. Your task is to extract and categorize the primary reasons for clinical trial termination from provided data. You must always output a valid JSON object and include clear reasoning based on explicit text evidence.

**TASK**
Analyze the clinical trial record below. Perform the following steps:
1.  **Extract Evidence:** Identify all text snippets relevant to *why the trial was terminated*. Focus on the `why_stopped` field, but also critically examine `brief_summary` and `detailed_description` for additional context or contradictory information.
2.  **Categorize:** Map the extracted evidence to one or more categories from the fixed taxonomy below. A trial can have multiple primary reasons.
3.  **Reason:** For each assigned category, provide a concise, bullet-point reasoning trace that directly quotes or references the text evidence that led to that conclusion.
4.  **Confidence:** Assign an overall confidence score (Low, Medium, High) based on the clarity and directness of the evidence.

**THE 17-CATEGORY ONTOLOGY (Use exact names):**

{TAXONOMY_BLOCK}

HIERARCHY RULES (Priority Order):

Scientific Trumps Operational: If a text says "Sponsor decision due to negative interim results," classify as Negative (not Business).

Safety Trumps Enrollment: If a text says "Recruitment challenges and observed toxicity," classify as Safety and Side Effects.

OUTPUT FORMAT: You must output a valid JSON object with this exact structure:
{
  "nct_id": "provided_id",
  "primary_reasons": ["CATEGORY_1", "CATEGORY_2"],
  "reasoning_traces": {
    "CATEGORY_1": ["Evidence: '[quote]'", "Inference: ..."],
    "CATEGORY_2": ["Evidence: '[quote]'", "Inference: ..."]
  },
  "confidence": "High/Medium/Low",
  "explanation": "One-sentence summary of the overall determination."
}

/* --- Example 2: Safety (with inference) --- */
{
  "nct_id": "NCT-TEST-002",
  "why_stopped": "Terminated by DSMB recommendation.",
  "brief_summary": "The trial was halted following an interim analysis.",
  "detailed_description": "An unplanned interim review by the Data and Safety Monitoring Board (DSMB) revealed a significant imbalance in serious adverse events (SAEs) in the treatment arm, including 3 cases of grade 3+ hepatotoxicity."
}
// Analysis for NCT-TEST-002:
{
  "nct_id": "NCT-TEST-002",
  "primary_reasons": ["SAFETY"],
  "reasoning_traces": {
    "SAFETY": ["Evidence: 'Terminated by DSMB recommendation.' (why_stopped)", "Evidence: 'significant imbalance in serious adverse events (SAEs)... including 3 cases of grade 3+ hepatotoxicity' (detailed_description)", "Inference: DSMB halts are often for safety/futility; the explicit mention of specific, severe adverse events confirms SAFETY as the primary reason."]
  },
  "confidence": "High",
  "explanation": "DSMB halt with clear evidence of specific, severe adverse events driving the decision."
}

**NOW, ANALYZE THE FOLLOWING TRIAL RECORD:**
{TRIAL_JSON}
"""

    def load_resources(self):
        """Loads taxonomy content."""
        if not os.path.exists(self.taxonomy_file):
            raise FileNotFoundError(f"Taxonomy file not found: {self.taxonomy_file}")
            
        with open(self.taxonomy_file, 'r', encoding='utf-8') as f:
            self.taxonomy_content = f.read()
            
    def _get_processed_ids(self):
        """Builds Preference Index from existing output file."""
        if not os.path.exists(self.output_file):
            return set()
            
        try:
            df = pd.read_csv(self.output_file)
            if 'nct_id' in df.columns:
                return set(df['nct_id'].astype(str).unique())
        except Exception as e:
            print(f"Warning: Could not read existing output file to build index: {e}")
            
        return set()

    def construct_prompt(self, row):
        """Constructs the prompt by injecting taxonomy and trial data."""
        # Inject Taxonomy
        prompt = self.system_template.replace("{TAXONOMY_BLOCK}", self.taxonomy_content)
        
        # Format Trial Data
        trial_data = {
            "nct_id": row.get('nct_id', 'N/A'),
            "why_stopped": row.get('why_stopped', 'N/A'),
            "brief_summary": row.get('brief_summary', 'N/A'),
            "detailed_description": row.get('detailed_description', 'N/A')
        }
        trial_json_str = json.dumps(trial_data, indent=2)
        
        # Inject Trial Data
        prompt = prompt.replace("{TRIAL_JSON}", trial_json_str)
        
        return prompt, trial_data['nct_id']

    def call_api(self, prompt):
        """Calls DeepSeek API with retries."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={'type': 'json_object'}
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"  API Error (Attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(2)
        return None

    def parse_response(self, response_text):
        """Parses JSON response."""
        try:
            # Cleanup markdown if present
            clean_text = response_text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0]
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0]
                
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            return {"error": "json_parse_error", "raw_output": response_text}

    def save_result(self, result_row):
        """Appends a single result to the output CSV (Checkpoint)."""
        df = pd.DataFrame([result_row])
        header = not os.path.exists(self.output_file)
        df.to_csv(self.output_file, mode='a', header=header, index=False)

    def run(self, limit=None):
        """Main execution loop with Preference Index."""
        print(f"Agent initialized.")
        print(f"Input: {self.input_file}")
        print(f"Output: {self.output_file}")
        print(f"Model: {self.model}")
        
        self.load_resources()
        
        # Load Input Data
        try:
            input_df = pd.read_csv(self.input_file)
        except Exception as e:
            print(f"Error reading input file: {e}")
            return

        # Preference Index: Filter out already processed IDs
        processed_ids = self._get_processed_ids()
        print(f"Preference Index: Found {len(processed_ids)} already processed studies.")
        
        pending_df = input_df[~input_df['nct_id'].isin(processed_ids)]
        print(f"Pending studies: {len(pending_df)} (out of {len(input_df)} total)")
        
        if len(pending_df) == 0:
            print("All studies in input have been processed. Nothing to do.")
            return

        # Limit
        if limit:
            pending_df = pending_df.head(limit)
            print(f"Limit applied: Processing next {limit} studies.")

        success_count = 0
        
        for index, row in pending_df.iterrows():
            nct_id = row.get('nct_id', 'Unknown')
            print(f"Processing {nct_id}...")
            
            prompt, _ = self.construct_prompt(row)
            
            # call api
            response_text = self.call_api(prompt)
            
            if response_text:
                parsed_data = self.parse_response(response_text)
                
                result_row = {
                    "nct_id": nct_id,
                    "input_why_stopped": row.get('why_stopped'),
                    "model": self.model,
                    "raw_response": response_text
                }
                
                if isinstance(parsed_data, dict):
                    result_row.update(parsed_data)
                
                # Check point save
                self.save_result(result_row)
                success_count += 1
            else:
                print(f"  Failed to get response for {nct_id}")

        print(f"Batch completed. Processed {success_count} new studies.")

def main():
    parser = argparse.ArgumentParser(description="DeepSeek Clinical Trial Analysis Agent")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", default="output/deepseek_extraction_results.csv", help="Path to output CSV")
    parser.add_argument("--taxonomy", default="Clinical trials endpoint taxonomy.txt", help="Path to taxonomy file")
    parser.add_argument("--model", default="deepseek-chat", help="DeepSeek model name")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of trials to process")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    try:
        agent = DeepSeekAnalysisAgent(
            input_file=args.input, 
            output_file=args.output, 
            taxonomy_file=args.taxonomy,
            model=args.model
        )
        agent.run(limit=args.limit)
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
