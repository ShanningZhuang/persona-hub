"""
Questionnaire Visualization Script

Input data format (persona_tsinghua.json):
Each line is a JSON object containing:
{
    "user_prompt": "...",
    "input persona": "I am a student from [department], my research topic is [topic]",
    "synthesized text": {
        "id": [question number 0-17],
        "answer": [answer option(s)],
        "fill-in": [fill-in text if applicable]
    }
}

Output:
1. output/questionnaire_analysis.png: 2x2 grid of bar charts
2. output/demands_analysis.png: Horizontal bar chart

Question formats:
- Single choice: answer contains single letter (e.g., "a", "b", "c")
- Multiple choice: answer contains comma-separated letters (e.g., "a,b,c")
- Text input: answer contains text string
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from collections import Counter

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

def load_questionnaire_data(file_path):
    """
    Load and parse the questionnaire data from JSON file
    
    Input:
        file_path: Path to JSON file containing questionnaire responses
    
    Output:
        data: List of dictionaries, each containing:
            - id: question number
            - answer: response option(s)
            - fill-in: additional text if applicable
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        responses = json.load(f)
    
    for r in responses:
        if 'synthesized text' in r and r['synthesized text']:
            # Handle case where synthesized text is already a dict
            if isinstance(r['synthesized text'], dict):
                data.append(r['synthesized text'])
            # Handle case where synthesized text is a string
            else:
                try:
                    answer=[]
                    # Split the string by newlines and parse each line as JSON
                    text_lines = r['synthesized text'].strip().split('\n')
                    for line in text_lines:
                        if line.strip():  # Skip empty lines
                            answer.append(json.loads(line))
                    data.append(answer)
                except json.JSONDecodeError:
                    # Skip invalid JSON
                    continue
    return data

def analyze_multiple_choice_responses(data, question_id):
    """
    Analyze responses for a multiple choice question
    
    Input:
        data: List of response dictionaries
        question_id: ID of the question to analyze
    
    Output:
        response_counts: Counter object containing frequency of each option
    """
    responses = []
    for response in data:
        for r in response:
            if r['id'] == question_id and 'answer' in r and r['answer']:
                # Split multiple answers if they exist
                answers = r['answer'].split(',')
                responses.extend(answers)
    
    # Count frequencies
    response_counts = Counter(responses)
    return response_counts

def plot_multiple_choice_question(data, question_id, title, ax):
    """
    Create a bar plot for a multiple choice question
    
    Input:
        data: List of response dictionaries
        question_id: ID of the question to visualize
        title: Title for the plot
        ax: Matplotlib axis object to plot on
    
    Output:
        Updates the provided axis with a bar plot
    """
    response_counts = analyze_multiple_choice_responses(data, question_id)
    
    # Sort by option labels
    sorted_items = sorted(response_counts.items())
    options, counts = zip(*sorted_items)
    
    # Create bar plot
    bars = ax.bar(options, counts)
    ax.set_title(title)
    ax.set_ylabel('Number of Responses')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    # Rotate x-axis labels if needed
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

def main():
    """
    Main function to create visualizations
    
    Output files:
    1. output/questionnaire_analysis.png: 
       - Top left: First encounter with ChatGPT (Q2)
       - Top right: Usage frequency (Q3)
       - Bottom left: Work/study usage (Q5)
       - Bottom right: Efficiency impact (Q11)
    
    2. output/demands_analysis.png:
       - Horizontal bar chart of ChatGPT usage demands (Q6)
    """
    # Set style
    plt.style.use('seaborn-v0_8')
    
    # Load data
    data = load_questionnaire_data('/home/zsn/research/llm/persona-hub/output/questionnaire_synthesis_output.json')
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Questionnaire Response Analysis', fontsize=16)
    
    # Plot different questions
    plot_multiple_choice_question(data, 2, 'How did you first encounter ChatGPT?', axes[0,0])
    plot_multiple_choice_question(data, 3, 'How often do you currently use ChatGPT?', axes[0,1])
    plot_multiple_choice_question(data, 5, 'Do you frequently use ChatGPT for work/study?', axes[1,0])
    plot_multiple_choice_question(data, 11, 'Impact on Work Efficiency', axes[1,1])
    
    # Adjust layout
    plt.tight_layout()
    plt.savefig('output/questionnaire_analysis.png')
    
    # Create a separate figure for demands analysis (Question 6)
    plt.figure(figsize=(10, 6))
    demands_data = analyze_multiple_choice_responses(data, 6)
    
    # Sort demands by frequency
    sorted_demands = sorted(demands_data.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_demands)
    
    # Create horizontal bar chart
    plt.barh(labels, values)
    plt.title('Demands for Using ChatGPT')
    plt.xlabel('Number of Responses')
    
    # Add value labels
    for i, v in enumerate(values):
        plt.text(v, i, str(v), va='center')
    
    plt.tight_layout()
    plt.savefig('output/demands_analysis.png')

if __name__ == "__main__":
    main() 