
import unittest
from generators import generate_endless_set

class TestGenerators(unittest.TestCase):
    def test_endless_generation(self):
        """Test that the generator produces valid data structure."""
        for i in range(15): # Run multiple times to hit different generators
            print(f"--- Iteration {i+1} ---")
            data = generate_endless_set()
            
            self.assertIn('context', data)
            self.assertIn('questions', data)
            self.assertTrue(len(data['questions']) > 0)
            
            q = data['questions'][0]
            self.assertIn('question', q)
            self.assertIn('answer', q)
            self.assertIn('solution', q)
            
            print(f"Context Sample: {data['context'][:50]}...")
            print(f"Question: {q['question']}")
        print(f"Sample Answer: {q['answer']}")

if __name__ == '__main__':
    unittest.main()
