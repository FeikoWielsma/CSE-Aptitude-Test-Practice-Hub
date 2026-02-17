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
                "answer": "",
                "chart_data": parse_chart_data(current_context)
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
            # If we are in a context block, keep lines as is (stripped of trailing whitespace)
            # We must preserve empty lines for markdown structure (e.g. separation between title and table)
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

def parse_chart_data(context_lines):
    """
    Parses context lines to extract chart data if a graph is detected.
    Returns a dictionary suitable for Chart.js or None.
    """
    full_text = "\n".join(context_lines)
    
    chart_type = None
    if 'Bar Graph' in full_text: chart_type = 'bar'
    elif 'Line Graph' in full_text: chart_type = 'line'
    elif 'Pie Chart' in full_text: chart_type = 'pie'
    
    if not chart_type:
        return None

    # Parse Data lines
    # Format: "- Label: Series1 (Val1), Series2 (Val2)..."
    # Or: "- Label: Value"
    
    labels = []
    datasets_map = {} # { 'SeriesName': [val, val, ...] }
    
    # We need to process lines in order to keep labels aligned
    data_lines = [line for line in context_lines if line.strip().startswith('-')]
    
    if not data_lines:
        return None
        
    for line in data_lines:
        # Remove "- "
        content = line.strip().lstrip('-').strip()
        
        # Split Label and Data
        parts = content.split(':')
        if len(parts) < 2: continue
        
        label = parts[0].strip()
        labels.append(label)
        
        data_part = parts[1].strip()
        
        # Check for series
        # Regex to find "Name (Value)"
        # e.g. "P (50), Q (40)"
        series_matches = list(re.finditer(r'([^(]+)\s*\((\d+(\.\d+)?)\)', data_part))
        
        if series_matches:
            found_series = set()
            for match in series_matches:
                series_name = match.group(1).strip()
                val = float(match.group(2))
                
                if series_name not in datasets_map:
                    datasets_map[series_name] = []
                    # Pad with 0s or nulls if this series appeared late? 
                    # For simplicity, we assume consistent series across labels or handle alignment later.
                    # Actually, better to initialize with current length - 1 nulls?
                    # Let's just append and fix lengths later.
                
                datasets_map[series_name].append(val)
                found_series.add(series_name)
            
            # Handle missing series for this label?
            # If a series was seen before but not here, we should append 0 or similar.
            # Complex to sync perfectly in one pass. 
        else:
            # Single value case: "500 units"
            # Extract first number
            val_match = re.search(r'(\d+(\.\d+)?)', data_part)
            val = float(val_match.group(1)) if val_match else 0
            
            series_name = "Value"
            if series_name not in datasets_map: datasets_map[series_name] = []
            datasets_map[series_name].append(val)

    # Post-process datasets to ensure equal lengths (though typical aptitude qs are consistent)
    final_datasets = []
    for series_name, data in datasets_map.items():
        # Pad if short (simple heuristic)
        while len(data) < len(labels):
            data.insert(0, 0) # or append? 
            # If we missed data at start, insert 0. If data is just short, well...
            # This parser is best-effort.
            
        final_datasets.append({
            "label": series_name,
            "data": data,
            "borderWidth": 1
        })

    return {
        "type": chart_type,
        "data": {
            "labels": labels,
            "datasets": final_datasets
        }
    }

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
