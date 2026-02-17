import unittest
import json
import os
import markdown

class TestContentRendering(unittest.TestCase):
    def setUp(self):
        # Load the questions data
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)

    def test_markdown_tables_render_correctly(self):
        """
        Verifies that if a context contains markdown table syntax, 
        it actually renders as an HTML table.
        Common issue: Missing newline between text and table causes it not to render.
        """
        for q in self.questions:
            context = q.get('context', '')
            
            # Check if it looks like it SHOULD have a table
            # We look for the separator line: |---| or |:---| etc.
            if '|---|' in context or '|---' in context:
                # Render using the same method as app.py
                html = markdown.markdown(context, extensions=['tables'])
                
                # Assert that the output contains <table> tag
                if '<table>' not in html:
                    print(f"\n[FAILURE] Question ID {q.get('id')} ({q.get('level')}) failed table rendering.")
                    print(f"Context Snippet:\n{context[:200]}...")
                    self.fail(f"Question ID {q.get('id')} contains table syntax but did not render a <table> tag. "
                              "Likely missing a newline before the table.")

if __name__ == '__main__':
    unittest.main()
