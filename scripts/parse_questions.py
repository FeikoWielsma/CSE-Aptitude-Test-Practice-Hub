import os
import re
import json

BASE_DIR = r"c:\Git\CSE-Aptitude-Test-Practice-Hub\04 Data Interpretation and Analysis"
OUTPUT_FILE = r"c:\Git\CSE-Aptitude-Test-Practice-Hub\data\questions.json"

def parse_readme(file_path, level):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    questions = []
    current_context = []
    current_question = {}
    
    # Regex patterns
    context_start_pattern = re.compile(r'^\*\*(Table|Bar Graph|Pie Chart|Line Graph|Caselet|Combination Chart).*?\*\*', re.IGNORECASE)
    question_start_pattern = re.compile(r'^\d+\.\s+\*\*Question\*\*:\s+(.*)')
    solution_start_pattern = re.compile(r'^\s*\*\*Solution\*\*:\s*')
    answer_start_pattern = re.compile(r'^\s*\*\*Answer\*\*:\s+(.*)')
    
    # State tracking
    is_capturing_context = False
    is_capturing_question_text = False
    is_capturing_solution = False
    
    # Temporary buffers
    context_buffer = []

    # Iterate through lines
    for line in lines:
        line_stripped = line.strip()
        
        # 1. Check for new Context (Group of questions)
        if context_start_pattern.match(line_stripped):
            # Save previous state if needed? 
            # Actually, questions are added to list as they are finished.
            # But context needs to be "active" for subsequent questions.
            
            # Start new context
            current_context = [line.strip()]
            context_buffer = [] # Reset buffer if we were tracking extra context lines
            is_capturing_context = True
            is_capturing_question_text = False
            is_capturing_solution = False
            continue

        # 2. Check for new Question
        question_match = question_start_pattern.match(line_stripped)
        if question_match:
            # If we were building a previous question, ensure it's saved (though usually Answer triggers save)
            if current_question and 'answer' in current_question:
                 # It should have been saved already by Answer block, but valid check
                 pass

            is_capturing_context = False # Stop capturing context once questions start
            is_capturing_question_text = True
            is_capturing_solution = False
            
            # Initialize new question
            current_question = {
                "id": str(len(questions) + 1), # Simple ID generation
                "level": level,
                "context": "\n".join(current_context),
                "question": question_match.group(1),
                "solution": "",
                "answer": ""
            }
            questions.append(current_question)
            continue

        # 3. Check for Solution
        if solution_start_pattern.match(line_stripped):
            is_capturing_question_text = False
            is_capturing_solution = True
            continue

        # 4. Check for Answer
        answer_match = answer_start_pattern.match(line_stripped)
        if answer_match:
            is_capturing_solution = False
            if current_question:
                current_question['answer'] = answer_match.group(1)
            continue

        # 5. Capture Content based on state
        if is_capturing_context:
            # If we are in a context block (tables, etc), strip strictly but keep structure for tables
            if line_stripped:
                current_context.append(line.rstrip())
        
        elif is_capturing_question_text:
             if current_question and line_stripped:
                 # Append multiline question text
                 current_question['question'] += " " + line_stripped
        
        elif is_capturing_solution:
            if current_question and line_stripped:
                if current_question['solution']:
                    current_question['solution'] += "\n" + line_stripped
                else:
                    current_question['solution'] = line_stripped

    return questions

def main():
    all_questions = []
    
    # Define directories and levels
    directories = [
        (os.path.join(BASE_DIR, "01 Basic"), "Basic"),
        (os.path.join(BASE_DIR, "02 Intermediate"), "Intermediate"),
        (os.path.join(BASE_DIR, "03 Advance"), "Advanced")
    ]
    
    global_id_counter = 1

    for dir_path, level in directories:
        readme_path = os.path.join(dir_path, "README.md")
        if os.path.exists(readme_path):
            print(f"Parsing {level} level from {readme_path}...")
            level_questions = parse_readme(readme_path, level)
            
            # Re-assign global IDs
            for q in level_questions:
                q['id'] = global_id_counter
                global_id_counter += 1
                all_questions.append(q)
        else:
            print(f"Warning: README not found at {readme_path}")

    # Ensure output directory exists [Adjusted path to use relative or absolute correctly]
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=4)

    print(f"Successfully parsed {len(all_questions)} questions into {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
