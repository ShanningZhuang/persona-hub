import argparse
import json
import time
from openai import OpenAI
from prompt_templates import instruction_template, knowledge_template, npc_template, math_template, questionnaire_template, questionnaire_note, questionnaire_josnl
from datasets import load_dataset
from tqdm import tqdm

system_prompt = '''You are a helpful assistant.'''
client = OpenAI()   # set up your config/env/api for calling openai models

def get_response(user_prompt, previous_context=None):
    try:
        # Add delay to maintain rate limits
        time.sleep(0.1)  
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add previous context if it exists
        if previous_context:
            for msg in previous_context:
                messages.append(msg)
                
        # Add current prompt
        messages.append({"role": "user", "content": user_prompt})
        
        completion = client.chat.completions.create(
            model="qwen-max-latest",
            temperature=0.9,
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"ERROR: {str(e)}"

def process_questionnaire(persona, template, questions):
    """Process questionnaire questions one by one with context"""
    responses = []
    conversation_context = []
    
    # First, send the initial persona and template
    initial_prompt = template.format(persona=persona)
    
    for question in questions:
        prompts = initial_prompt + questionnaire_note + question
        response = get_response(prompts)
        responses.append({
            "question": question,
            "prompt": prompts,
            "response": response
        })
        
        # # Add this interaction to context
        # conversation_context.extend([
        #     {"role": "user", "content": question},
        #     {"role": "assistant", "content": response}
        # ])
    
    return responses

def main(args):
    # Load the appropriate template
    if args.template == "instruction":
        template = instruction_template
    elif args.template == "knowledge":
        template = knowledge_template
    elif args.template == "npc":
        template = npc_template
    elif args.template == "math":
        template = math_template
    elif args.template == "questionnaire":
        template = questionnaire_template
    else:
        raise ValueError("Invalid template type. Choose from 'instruction', 'knowledge', 'npc', 'math' or 'questionnaire'.")

    # Load the dataset
    # persona_dataset = load_dataset("proj-persona/PersonaHub", data_files="persona.jsonl")['train']
    persona_data = []
    with open("data/persona_tsinghua_altitudes.jsonl", "r") as f:
        for line in f:
            persona_data.append(json.loads(line))
    
    questionnaire = []
    for line in questionnaire_josnl.split('\n'):
        if line.strip():
            questionnaire.append(line)
            
    persona_dataset = {"persona": [p["persona"] for p in persona_data]}
    # if args.sample_size > 0:
        # persona_dataset = persona_dataset[:args.sample_size]
    print(f"Total number of input personas: {len(persona_dataset['persona'])}")

    with open(args.output_path, "w") as out:
        for persona in tqdm(persona_dataset['persona']):
            try:
                persona = persona.strip()
                # Process questionnaire with separate requests
                responses = process_questionnaire(persona, template, questionnaire)
                
                o = {
                    "input_persona": persona,
                    "responses": responses
                }
                out.write(json.dumps(o, ensure_ascii=False) + '\n')
            except Exception as e:
                print(f"Error processing persona: {str(e)}")
                continue

    print(f"Outputted the results to: {args.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthesize text using a specified model and template.")
    parser.add_argument('--sample_size', type=int, default=10, help='Number of samples to process from the dataset; Set it to 0 if you want to use the full set of 200k personas.')
    parser.add_argument(
        '--template', 
        type=str, 
        required=True, 
        choices=['instruction', 'knowledge', 'npc', 'math', 'questionnaire'], 
        help=(
            "Prompt templates. Choose from 'instruction', 'knowledge', 'math', 'npc' or 'questionnaire'. "
            "You can also add more customized templates in prompt_templates.py"
        )
    )
    parser.add_argument('--output_path', type=str, required=True, help='Path to the output file.')

    args = parser.parse_args()
    main(args)
