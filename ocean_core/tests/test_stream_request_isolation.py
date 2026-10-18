"""Exercise request isolation without starting Ocean's external services."""
import ast
from collections import deque
from pathlib import Path
from types import SimpleNamespace
import unittest


class RequestIsolationTests(unittest.TestCase):
    def setUp(self):
        source = Path(__file__).parents[1] / 'ocean_core_full.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        names = {'_memory_key', '_memory_get', '_memory_put', '_incoming_messages_context'}
        selected = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[])
        self.scope = {'ChatRequest': SimpleNamespace, 'List': list, 'Dict': dict, 'Any': object,
                      '_memory_store': {}, 'deque': deque}
        exec(compile(selected, str(source), 'exec'), self.scope)

    def test_anonymous_requests_do_not_share_turns(self):
        request = SimpleNamespace(clerk_user_id=None, user_id=None, user_name=None)
        self.scope['_memory_put'](request, 'private question', 'private answer', 'en')
        self.assertEqual(self.scope['_memory_get'](request), [])
        self.assertEqual(self.scope['_memory_store'], {})

    def test_body_identity_does_not_enable_shared_memory(self):
        request = SimpleNamespace(clerk_user_id='claimed-id', user_id='claimed-id', user_name='same-name')
        self.scope['_memory_put'](request, 'private question', 'private answer', 'en')
        self.assertEqual(self.scope['_memory_get'](request), [])

    def test_explicit_request_history_is_preserved(self):
        request = SimpleNamespace(messages=[{'role': 'user', 'content': 'My project is called Arbor.'}])
        self.assertIn('My project is called Arbor.', self.scope['_incoming_messages_context'](request))
        self.assertEqual(self.scope['_incoming_messages_context'](SimpleNamespace(messages=[])), '')


if __name__ == '__main__':
    unittest.main()
