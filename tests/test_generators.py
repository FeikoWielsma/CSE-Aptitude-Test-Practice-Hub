
import unittest
import json
import os
import sys

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators import generate_endless_set
from distractors import generate_single_distractor_set

# Load questions helper for testing only, to avoid importing app
def load_questions():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'questions.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

class TestGenerators(unittest.TestCase):
    def test_endless_generation(self):
        """Test that the generator produces valid data structure."""
        for i in range(5): # Run multiple times to hit different generators
            data = generate_endless_set()
            
            self.assertIn('context', data)
            self.assertIn('questions', data)
            self.assertTrue(len(data['questions']) > 0)
            
            q = data['questions'][0]
            self.assertIn('question', q)
            self.assertIn('answer', q)
            self.assertIn('solution', q)
            
    def test_distractor_integrity_endless(self):
        """
        Test 100 random Endless Mode questions to ensuring the correct answer 
        is ALWAYS present in the generated options.
        """
        print("\nTesting 100 Endless Questions for distractor integrity...")
        for i in range(100):
            data = generate_endless_set()
            for q in data['questions']:
                answer = q['answer']
                
                # Generate options if they don't exist (most endless don't have pre-defined options)
                if not q.get('options'):
                    # Use the app's logic
                    generated_options = generate_single_distractor_set(answer)
                    options = list(generated_options)
                else:
                    options = q['options']
                    
                # CLEANUP for comparison:
                # The app logic adds the correct answer to the set.
                # Use strict string comparison? Or loose?
                # The app.py generate_single_distractor_set returns a SET including the correct answer.
                
                # Check if answer is in options
                self.assertIn(answer, options, 
                    f"Endless Question {i}: Answer '{answer}' not found in generated options: {options}")
                    
    def test_distractor_integrity_static(self):
        """
        Test ALL static questions in questions.json to ensure correct answer matches options.
        """
        print("\nTesting all Static Questions for distractor integrity...")
        questions = load_questions()
        for q in questions:
            answer = q['answer']
            
            # Static questions don't have pre-defined options in JSON usually, 
            # but if they did, we should check.
            # Mostly we want to verify that generate_single_distractor_set(answer) includes answer.
            # (which is trivial if the function explicitly adds it, but good to verify logic doesn't corrupt it)
            
            generated_options = generate_single_distractor_set(answer)
            self.assertIn(answer, generated_options,
                 f"Static Question ID {q['id']}: Answer '{answer}' lost during option generation.")

if __name__ == '__main__':
    unittest.main()
