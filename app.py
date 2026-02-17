import os
import json
import random
import re
import markdown
import time
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this for production

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')

def load_questions():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_single_distractor_set(correct_answer):
    """
    Helper to generate one set of distractors for a single value.
    This contains the logic previously in generate_distractors.
    """
    options = set([correct_answer])
    
    # helper to add valid unique options
    def add_option(opt):
        if opt != correct_answer and len(options) < 30: # Max cap
            options.add(opt)

    # 1. Try Numerical Pattern
    num_match = re.match(r'^([^\d]*)([\d,]+(?:\.\d+)?)([^\d]*)$', correct_answer.strip())
    
    if num_match:
        prefix = num_match.group(1) or ""
        num_str = num_match.group(2)
        suffix = num_match.group(3) or ""
        
        try:
            val = float(num_str.replace(',', ''))
            is_int = '.' not in num_str
            
            step_size = 1
            if is_int and val != 0:
                p = 1
                while p < val:
                    if val % (p*10) == 0: p *= 10
                    else: break
                step_size = p 
                if val % (p*5) == 0: step_size = p * 5
                if step_size == 1 and val % 5 == 0: step_size = 5
            
            offsets = [1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 10, -10, 0.5, -0.5, 6, -6, 7, -7, 8, -8, 12, -12, 15, -15]
            random.shuffle(offsets)
            
            for off in offsets:
                if len(options) >= 25: break
                if isinstance(off, float) and step_size == 1: continue
                new_val = val + (off * step_size)
                if new_val <= 0: continue
                if new_val == val: continue

                if is_int and new_val.is_integer(): formatted_num = f"{int(new_val)}"
                elif is_int: continue 
                else:
                     formatted_num = f"{new_val:.2f}"
                     if formatted_num.endswith('.00'): formatted_num = formatted_num[:-3]

                if ',' in num_str:
                     try: formatted_num = f"{float(formatted_num):,.0f}" if is_int else f"{float(formatted_num):,.2f}"
                     except: pass

                add_option(f"{prefix}{formatted_num}{suffix}")

            # Fallback multipliers
            if len(options) < 25:
                multipliers = [0.9, 1.1, 0.8, 1.2, 0.75, 1.25, 1.5, 0.5, 2.0]
                for m in multipliers:
                    if len(options) >= 25: break
                    nv = val * m
                    if is_int: nv = round(nv)
                    else: nv = round(nv, 2)
                    if nv == val: continue
                    formatted_num = f"{int(nv)}" if is_int else f"{nv}"
                    add_option(f"{prefix}{formatted_num}{suffix}")

        except ValueError:
            pass 

    # 2. Try Ratio Pattern
    if len(options) < 25:
        ratio_match = re.search(r'(\d+)\s*:\s*(\d+)', correct_answer)
        if ratio_match:
            a, b = int(ratio_match.group(1)), int(ratio_match.group(2))
            variations = []
            for i in range(-5, 6):
                if i == 0: continue
                variations.append(f"{a+i} : {b+i}")
                variations.append(f"{a} : {b+i}")
                variations.append(f"{a+i} : {b}")
            variations.append(f"{b} : {a}")
            for v in variations: add_option(v)

    # 3. Categorical fallback
    if len(options) < 25:
        categorical_match = re.match(r'^(Product|Store|Class|Team|Brand|City|Department|Company|Option|Contract)\s*([A-Z0-9]*)$', correct_answer, re.IGNORECASE)
        # Added "Option", "Contract" for the new question type logic
        if categorical_match:
             entity = categorical_match.group(1)
             char = categorical_match.group(2)
             # If simple string like "Option A"
             if len(char) == 1 and char.isalpha():
                 candidates = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                 for c in candidates: 
                     if c != char: add_option(f"{entity} {c}")
             elif entity.lower() == "basic": # Handle "Basic" vs "Premium"
                 add_option("Premium")
                 add_option("Standard")
                 add_option("Gold")
             elif entity.lower() == "premium":
                 add_option("Basic")
                 add_option("Standard")
                 add_option("Gold")

    # 4. Month Pattern
    months_full = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    found_month = False
    for i, m in enumerate(months_full):
        if m.lower() == correct_answer.strip().lower():
            others = months_full[:i] + months_full[i+1:]
            for o in others: add_option(o)
            found_month = True
            break
            
    if not found_month:
        for i, m in enumerate(months_short):
             if m.lower() == correct_answer.strip().lower():
                others = months_short[:i] + months_short[i+1:]
                for o in others: add_option(o)
                found_month = True
                break

    # 5. Fill Generic
    # Try to fill up to 25 options with range logic if possible (re-implemented briefly)
    if len(options) < 25:
         pass

    final_options = list(options)
    
    # Sort options naturally
    def natural_sort_key(s):
        nums = re.findall(r'-?\d+(?:\.\d+)?', s.replace(',', ''))
        if nums: return float(nums[0])
        return s
        
    final_options.sort(key=natural_sort_key)
    return final_options[:30]


def generate_distractors(correct_answer, manual_options=None):
    """
    Generates distractors. Can return a list of strings (single dropdown)
    OR a list of lists (multiple dropdowns) if correct_answer contains '|'.
    If manual_options is provided (list of strings), uses that instead of generating.
    """
    if manual_options and isinstance(manual_options, list) and len(manual_options) > 0:
        return manual_options

    if '|' in correct_answer:
        # Split into parts
        parts = [p.strip() for p in correct_answer.split('|')]
        # Generate options for each part
        all_options = []
        for p in parts:
            all_options.append(generate_single_distractor_set(p))
        return all_options
    else:
        return generate_single_distractor_set(correct_answer)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

@app.route('/start_quiz/<level>')
def start_quiz(level):
    all_questions = load_questions()
    
    if level == 'all':
        quiz_questions = all_questions
    else:
        quiz_questions = [q for q in all_questions if q.get('level', '').lower() == level.lower()]
    
    # Group by context to select nice chunks
    questions_by_context = {}
    for q in quiz_questions:
        ctx = q['context']
        if ctx not in questions_by_context:
            questions_by_context[ctx] = []
        questions_by_context[ctx].append(q)
        
    # Select up to 10 contexts or max available
    # Increase the variety if reset
    available_contexts = list(questions_by_context.keys())
    if len(available_contexts) > 3:
        selected_contexts = random.sample(available_contexts, 3)
    else:
        selected_contexts = available_contexts
    
    final_questions = []
    for ctx in selected_contexts:
        final_questions.extend(questions_by_context[ctx])
        
    session['quiz_questions'] = final_questions
    session['current_index'] = 0
    session['score'] = 0
    session['answers'] = []
    
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    questions = session.get('quiz_questions', [])
    current_index = session.get('current_index', 0)
    
    if not questions or current_index >= len(questions):
        return redirect(url_for('result'))
    
    question_data = questions[current_index]
    
    # Parse Markdown Context to HTML
    context_html = markdown.markdown(question_data.get('context', ''), extensions=['tables'])
    
    # Generate Options
    options = generate_distractors(question_data.get('answer', ''), question_data.get('options', None))
    
    if request.method == 'POST':
        # Handle multiple answers if present
        # Check for answer_0, answer_1...
        user_answer_parts = []
        i = 0
        while True:
            part = request.form.get(f'answer_{i}')
            if part is None:
                # If we don't find answer_0, check generic 'answer'
                if i == 0:
                     val = request.form.get('answer')
                     if val: user_answer_parts.append(val.strip())
                break
            user_answer_parts.append(part.strip())
            i += 1
            
        user_answer = " | ".join(user_answer_parts) if len(user_answer_parts) > 1 else (user_answer_parts[0] if user_answer_parts else "")
        correct_answer = question_data.get('answer', '')
        
        # Timing calculation
        start_time = session.get('question_start_time', time.time())
        time_taken = time.time() - start_time
        
        # Compare ignoring whitespace around pipes
        # Standardize join
        correct_parts = [p.strip() for p in correct_answer.split('|')]
        user_parts = [p.strip() for p in user_answer.split('|')]
        
        is_correct = (correct_parts == user_parts)
        
        if is_correct:
            session['score'] = session.get('score', 0) + 1
            
        session['answers'].append({
            'question': question_data.get('question', ''),
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question_data.get('solution', ''),
            'time_taken': time_taken
        })
        
        session['current_index'] = current_index + 1
        session.modified = True 
        
        # Clear start time so next GET sets a new one
        session.pop('question_start_time', None)
        
        return redirect(url_for('quiz'))
    
    # GET request - Set start time if not already set 
    if 'question_start_time' not in session:
        session['question_start_time'] = time.time()
        
    # Determine time limit based on Korn Ferry rules
    # 90s for first question of a new context (or first question overall)
    # 75s for subsequent questions in the same context
    time_limit = 75
    if current_index == 0:
        time_limit = 90
    else:
        prev_q = questions[current_index - 1]
        # Compare context strings (using a hash might be safer if large, but string compare is fine here)
        if question_data.get('context') != prev_q.get('context'):
            time_limit = 90
            
    # Check if options is a list of lists (multi-select)
    # Passed to template
    
    return render_template('quiz.html', 
                           question=question_data, 
                           context_html=context_html,
                           options=options,
                           index=current_index + 1, 
                           total=len(questions),
                           time_limit=time_limit)

@app.route('/finish_early')
def finish_early():
    return redirect(url_for('result'))

@app.route('/result')
def result():
    return render_template('result.html', 
                           score=session.get('score', 0), 
                           total=len(session.get('answers', [])), # Completed questions
                           details=session.get('answers', []))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
