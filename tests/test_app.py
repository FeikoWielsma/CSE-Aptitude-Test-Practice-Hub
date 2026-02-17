import unittest
import json
import os
import sys

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, generate_distractors

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_load(self):
        """Test that the index page loads successfully."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aptitude Test Practice', response.data)

    def test_distractor_generation_basics(self):
        """Test basic distractor generation logic."""
        # Numerical
        opts = generate_distractors("100")
        self.assertIn("100", opts)
        self.assertGreater(len(opts), 5) # Should be plenty now
        
        # String/Categorical
        opts = generate_distractors("Company A")
        self.assertIn("Company A", opts)
        self.assertTrue(any("Company B" in o for o in opts))

    def test_double_dropdown_logic(self):
        """Test that pipe-delimited answers produce list of lists."""
        answer = "Premium | 50"
        distractors = generate_distractors(answer)
        
        # Should return list of lists
        self.assertIsInstance(distractors, list)
        self.assertIsInstance(distractors[0], list) 
        self.assertIsInstance(distractors[1], list)
        
        # Check content
        flat_first = [str(x) for x in distractors[0]]
        flat_second = [str(x) for x in distractors[1]]
        
        self.assertIn("Premium", flat_first)
        self.assertIn("50", flat_second)

    def test_manual_options(self):
        """Test that manual options are respected."""
        answer = "North"
        manual = ["North", "South", "East", "West"]
        opts = generate_distractors(answer, manual)
        self.assertEqual(opts, manual)
        self.assertIn("North", opts)

    def test_session_flow(self):
        """Test starting a quiz initializes session correctly."""
        with self.app as client:
            with client.session_transaction() as sess:
                pass # just to init
            
            response = client.get('/start_quiz/Basic')
            self.assertEqual(response.status_code, 302) # Redirects to /quiz
            
            # Check session
            with client.session_transaction() as sess:
                self.assertIn('quiz_questions', sess)
                self.assertEqual(sess['score'], 0)
                self.assertEqual(sess['current_index'], 0)
