import re
import random

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
                if (a+i) > 0 and (b+i) > 0: variations.append(f"{a+i} : {b+i}")
                if (b+i) > 0: variations.append(f"{a} : {b+i}")
                if (a+i) > 0: variations.append(f"{a+i} : {b}")
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

    return options
