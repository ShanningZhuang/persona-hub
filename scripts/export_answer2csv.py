"""
Script to convert questionnaire answers from JSON to CSV format

Input: 
- output/questionnaire_synthesis_output.json: JSON file containing questionnaire responses
- data/questions.jsonl: JSONL file containing question definitions

Output:
- output/questionnaire_responses.csv: CSV file with formatted responses
"""

import json
import pandas as pd
import csv

def load_questions(file_path):
    """Load questions and their options from JSONL file"""
    questions = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            q = json.loads(line)
            questions[q['id']] = {
                'question': q['question'],
                'options': {opt_dict.keys().__iter__().__next__(): opt_dict.values().__iter__().__next__()
                          for opt_dict in q.get('options', [])}
            }
    return questions

def parse_answer(answer_text, question_options):
    """Parse answer text and convert to actual option text if applicable"""
    if not question_options:  # For text questions
        return answer_text
    
    if not answer_text:
        return ""
        
    # Handle multiple answers (comma-separated)
    answers = answer_text.split(',')
    parsed_answers = []
    
    for ans in answers:
        ans = ans.strip()
        if ans in question_options:
            parsed_answers.append(question_options[ans])
        else:
            parsed_answers.append(ans)
    
    return '; '.join(parsed_answers)

def main():
    # Load questions
    questions = load_questions('data/questions.jsonl')
    
    # Load responses
    with open('output/questionnaire_synthesis_output1126.jsonl', 'r', encoding='utf-8') as f:
        responses = []
        for line in f:
            responses.append(json.loads(line))
    
    # Prepare CSV data
    csv_data = []
    
    # Headers
    headers = ['Persona', 'Department', 'Research Topic']
    for i in range(18):  # Questions 0-17
        headers.append(f'Q{i}-{questions[i]["question"]}')
    '''
    response is a dictionary with the following keys:
    - input persona: the input persona -> string
    - responses: the responses -> list of dicts with the following keys:
        - question: the question text -> string
        - prompt: the prompt -> string
        - response: the answer -> string
            - the response is a jsonl string, each line is a json object
            - each json object has the following keys:
                - id: the id of the question -> int
                - question: the question text -> string
                - thoughts: the thoughts on the question -> string
                - answer: the answer -> string
                - fill-in: the fill-in response if the answer is "[fill-in]" -> string
    '''  
    # Process each response
    for response in responses:
        row = {}
        answers = response['responses']
        # Extract persona information
        persona = response['input_persona']
        # Extract department and research topic
        try:
            dept = persona.split('(')[0].strip()
            eng_dept = persona.split('(')[1].split(')')[0].strip()
            topic = persona.split('research topic is')[1].strip().rstrip('.')
        except:
            dept = persona
            eng_dept = ""
            topic = ""
        
        row['Persona'] = persona
        row['Department'] = f"{dept}({eng_dept})"
        row['Research Topic'] = topic
        
        # Process each answer
        for answer in answers:
            answer = json.loads(answer['response'].replace('\n',','))
            q_id = answer['id']
            q_question = answer['question']
            q_options = answer['answer']
            
            # Store main answer
            if answer['answer'] is not None:
                if 'fill-in' in answer and answer['fill-in']!='':
                    concat_answer = answer['answer'].replace('\n','') + '-' + answer['fill-in']
                else:
                    concat_answer = answer['answer'].replace('\n','')
                row[f'Q{q_id}-{q_question}'] = concat_answer
        csv_data.append(row)
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(csv_data)
    df = df.reindex(columns=headers)  # Ensure consistent column order
    df.to_csv('output/questionnaire_responses.csv', index=False, encoding='utf-8-sig')
    
    print(f"Successfully exported {len(csv_data)} responses to output/questionnaire_responses.csv")

if __name__ == "__main__":
    main()
