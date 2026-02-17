import unittest
import json
import os

class TestDataIntegrity(unittest.TestCase):
    def setUp(self):
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)

    def test_schema_validity(self):
        """Verify every question has required fields."""
        required_fields = ['id', 'level', 'context', 'question', 'solution', 'answer']
        
        for q in self.questions:
            for field in required_fields:
                self.assertIn(field, q, f"Question ID {q.get('id')} missing field: {field}")
                self.assertIsInstance(q[field], (str, int, type(None)), f"Field {field} in QID {q.get('id')} has wrong type")

    def test_answer_not_empty(self):
        """Verify answers are not empty strings."""
        for q in self.questions:
            self.assertTrue(len(str(q['answer']).strip()) > 0, f"Question ID {q.get('id')} has empty answer")

    def test_context_rendering(self):
        """Basic check that context is not empty."""
        for q in self.questions:
             self.assertTrue(len(q['context']) > 10, f"Question ID {q.get('id')} has suspiciously short context")

if __name__ == '__main__':
    unittest.main()
