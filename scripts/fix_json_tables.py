import json
import re

def fix_questions():
    input_path = 'data/questions.json'
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    fixed_count = 0
    
    for q in data:
        context = q.get('context', '')
        # Check if context contains a table pattern that lacks a double newline
        # Pattern: look for newline followed immediately by pipe, without a preceding newline
        # matching ...\n|... but not ...\n\n|...
        
        # We can use regex to find instances where a line ends, and the next line starts with | 
        # but there isn't a blank line in between.
        # Actually, simpler: replace \n| with \n\n| if it's not already \n\n| 
        # But we must be careful not to break the table rows themselves (which are \n|... \n|...)
        # We only want to fix the *start* of the table.
        # The start of the table usually follows a header line (e.g. **Table 1...**)
        
        # Look for **\n|
        if "**\n|" in context:
            # Check specifically for the table header start
            # Usually users write **Title**\n| Header | ...
            # We want **Title**\n\n| Header | ...
            
            new_context = context.replace("**\n|", "**\n\n|")
            if new_context != context:
                q['context'] = new_context
                fixed_count += 1
                
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Fixed {fixed_count} questions.")

if __name__ == "__main__":
    fix_questions()
