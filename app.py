import os
import json
import random
import re
import markdown
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this for production

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')

def load_questions():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_distractors(correct_answer):
    """
    Generates 5 distractor answers based on the correct answer.
    Handles numbers, percentages, ratios, and some text patterns.
    """
    options = set()
    options.add(correct_answer)
    
    # helper to add valid unique options (up to 6 total including correct)
    def add_option(opt):
        if opt != correct_answer and len(options) < 6:
            options.add(opt)

    try:
        # 1. Try Number Pattern: "123", "123.45", "$123", "123 units", "12%"
        # Regex to capture prefix, number, suffix
        num_match = re.match(r'^([^\d]*)([\d,]+(\.\d+)?)([^\d]*)$', correct_answer.strip())
        
        if num_match:
            prefix = num_match.group(1)
            number_str = num_match.group(2).replace(',', '')
            suffix = num_match.group(4)
            
            try:
                val = float(number_str)
                is_int = '.' not in num_match.group(2)
                
                # Generate variations
                multipliers = [0.8, 0.9, 0.95, 1.05, 1.1, 1.2, 0.5, 1.5]
                offsets = [-10, -5, -1, 1, 5, 10, 100]
                 
                # Mix of strategies
                for _ in range(20): # Try enough times
                    if len(options) >= 6: break
                    
                    if random.random() < 0.5:
                        mult = random.choice(multipliers)
                        new_val = val * mult
                    else:
                        off = random.choice(offsets)
                        # Scale offset by magnitude of val roughly
                        if val > 100: off *= 10
                        new_val = val + off
                    
                    if new_val < 0 and val >= 0: new_val = abs(new_val) # Avoid negative if original positive
                    
                    if is_int:
                        new_val = int(round(new_val))
                    else:
                        new_val = round(new_val, 2)
                        
                    # Format back
                    formatted_num = f"{new_val}"
                    if is_int: formatted_num = f"{int(new_val)}"
                    
                    # Check original string for comma
                    if ',' in num_match.group(2):
                         formatted_num = f"{new_val:,}"

                    new_ans = f"{prefix}{formatted_num}{suffix}"
                    add_option(new_ans)
                    
            except ValueError:
                pass # Parsing failed

        # 2. Try Ratio Pattern: "3 : 4"
        ratio_match = re.search(r'(\d+)\s*:\s*(\d+)', correct_answer)
        if ratio_match:
            a, b = int(ratio_match.group(1)), int(ratio_match.group(2))
            variations = [
                f"{a+1} : {b}",
                f"{a} : {b+1}",
                f"{b} : {a}", # Inverse
                f"{a+2} : {b+2}",
                f"{a+1} : {b-1}",
                f"{max(1, a-1)} : {max(1, b-1)}"
            ]
            for v in variations:
                add_option(v)

        # 3. Try "Product X", "Store Y", "Class A", "Team B"
        categorical_match = re.match(r'^(Product|Store|Class|Team|Brand|City|Department|Company)\s+([A-Z])$', correct_answer, re.IGNORECASE)
        if categorical_match:
            entity = categorical_match.group(1)
            char = categorical_match.group(2).upper()
            # Generate other chars
            import string
            chars = list(string.ascii_uppercase)
            random.shuffle(chars)
            for c in chars:
                if c != char:
                    add_option(f"{entity} {c}")
                    if len(options) >= 6: break
    except Exception:
        pass # Fallback safely
        
    # 4. Fallback: If we still don't have enough options
    # If < 6 and it looked like a number, force more number variations
    if len(options) < 6:
        # Check if we have a number match from before
         num_match = re.match(r'^([^\d]*)([\d,]+(\.\d+)?)([^\d]*)$', correct_answer.strip())
         if num_match:
             prefix = num_match.group(1)
             number_str = num_match.group(2).replace(',', '')
             suffix = num_match.group(4)
             try:
                 val = float(number_str)
                 is_int = '.' not in num_match.group(2)
                 while len(options) < 6:
                     new_val = val * (1 + (random.random() - 0.5) * 0.5) # +/- 25% random
                     if is_int: new_val = int(new_val)
                     else: new_val = round(new_val, 2)
                     formatted_num = f"{new_val:,}" if ',' in num_match.group(2) else f"{new_val}"
                     add_option(f"{prefix}{formatted_num}{suffix}")
             except: pass
             
    # Sort or shuffle?
    final_options = list(options)
    random.shuffle(final_options)
    return final_options

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
    # We generate them fresh on every render. If we wanted consistency on refresh, we'd store them.
    options = generate_distractors(question_data.get('answer', ''))
    
    if request.method == 'POST':
        user_answer = request.form.get('answer', '').strip()
        correct_answer = question_data.get('answer', '')
        
        is_correct = user_answer == correct_answer 
        
        if is_correct:
            session['score'] = session.get('score', 0) + 1
            
        session['answers'].append({
            'question': question_data.get('question', ''),
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question_data.get('solution', '')
        })
        
        session['current_index'] = current_index + 1
        session.modified = True 
        return redirect(url_for('quiz'))
        
    return render_template('quiz.html', 
                           question=question_data, 
                           context_html=context_html,
                           options=options,
                           index=current_index + 1, 
                           total=len(questions))

@app.route('/result')
def result():
    return render_template('result.html', 
                           score=session.get('score', 0), 
                           total=len(session.get('answers', [])),
                           details=session.get('answers', []))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
