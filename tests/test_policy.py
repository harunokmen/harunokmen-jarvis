import unittest
from unittest.mock import patch
import core

class PolicyTests(unittest.TestCase):
    def test_turkish(self):
        self.assertEqual(core.resolve('Jervis görev yöneticisi aç', True), 'tasks')
        self.assertEqual(core.resolve('SİSTEM DURUMU'), 'status')

    def test_injection_rejected(self):
        for text in ['not defteri aç; calc', 'powershell whoami', 'bilgisayarı kapat', 'Jarvis not defteri aç && calc']:
            self.assertIsNone(core.resolve(text))
            self.assertIsNone(core.resolve(text, True))

    def test_no_wake_word(self):
        self.assertIsNone(core.resolve('saat kaç', True))
        self.assertIsNone(core.resolve('servis not defteri aç', True))

    @patch('core.subprocess.Popen')
    @patch('core.subprocess.run')
    @patch('core.os.startfile', create=True)
    def test_effects_require_approval(self, start, run, popen):
        assistant = core.Assistant(False)
        for action in ['notepad', 'calculator', 'tasks', 'browser', 'report', 'unknown']:
            assistant.execute(action)
        start.assert_not_called()
        run.assert_not_called()
        popen.assert_not_called()

    @patch('core.subprocess.Popen')
    def test_approved_fixed_program(self, popen):
        core.Assistant(False).execute('notepad', approved=True)
        args = popen.call_args.args[0]
        self.assertEqual(len(args), 1)
        self.assertTrue(args[0].endswith('System32\\notepad.exe'))

if __name__ == '__main__':
    unittest.main()
