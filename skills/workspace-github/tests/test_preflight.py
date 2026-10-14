import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('team_preflight', Path(__file__).parents[1] / 'scripts/preflight.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CandidateInspection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        for name in ('candidate.txt', 'test.txt', 'unrelated.txt'):
            (self.root / name).write_text('original\n', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True).stdout

    def test_dirty_candidate_and_unrelated_are_bounded(self):
        (self.root / 'candidate.txt').write_text('new\n')
        (self.root / 'unrelated.txt').write_text('private unrelated\n')
        before = (self.root / '.git/index').read_bytes()
        report = module.inspect(self.root, ['candidate.txt'], ['test.txt'])
        self.assertEqual(report['status'], 'eligible')
        self.assertEqual(report['changed_count'], 2)
        self.assertNotIn('unrelated.txt', report['input_hashes'])
        self.assertFalse(report['validation_passed'])
        self.assertEqual(before, (self.root / '.git/index').read_bytes())

    def test_changed_test_requires_candidate_inclusion(self):
        (self.root / 'test.txt').write_text('changed\n')
        self.assertEqual(module.inspect(self.root, [], ['test.txt'])['blocked_inputs'], ['test.txt'])
        self.assertEqual(module.inspect(self.root, ['test.txt'], ['test.txt'])['status'], 'eligible')

    def test_dependency_changes_fingerprint(self):
        before = module.inspect(self.root, ['test.txt'])['fingerprint']
        (self.root / 'test.txt').write_text('changed\n')
        self.assertNotEqual(before, module.inspect(self.root, ['test.txt'])['fingerprint'])

    def test_missing_untracked_file_blocks(self):
        with self.assertRaises(ValueError): module.inspect(self.root, ['missing.txt'])

    def test_escape_blocks(self):
        with self.assertRaises(ValueError): module.inspect(self.root, ['../outside.txt'])

    def test_absolute_path_blocks(self):
        with self.assertRaises(ValueError): module.inspect(self.root, [str(self.root / 'test.txt')])

    def test_windows_drive_relative_blocks(self):
        with self.assertRaises(ValueError): module.inspect(self.root, ['C:test.txt'])

    def test_metadata_file_blocks(self):
        with self.assertRaises(ValueError): module.inspect(self.root, ['.git/config'])

    def test_nested_root_blocks(self):
        nested = self.root / 'nested'; nested.mkdir()
        with self.assertRaises(ValueError): module.inspect(nested)

    def test_rename_counts_both_paths_and_accepts_old_tracked_path(self):
        self.git('mv', 'candidate.txt', 'renamed.txt')
        self.assertEqual(module.changed_paths(self.root), {'candidate.txt', 'renamed.txt'})
        report = module.inspect(self.root, ['candidate.txt', 'renamed.txt'])
        self.assertEqual(report['deleted_candidates'], ['candidate.txt'])
        self.assertEqual(report['staged_candidate'], ['candidate.txt', 'renamed.txt'])

    def test_unstaged_tracked_deletion_is_explicit(self):
        (self.root / 'candidate.txt').unlink()
        report = module.inspect(self.root, ['candidate.txt'])
        self.assertIsNone(report['input_hashes']['candidate.txt'])
        self.assertEqual(report['deleted_candidates'], ['candidate.txt'])
        self.assertEqual(report['staged_count'], 0)

    def test_staged_tracked_deletion_is_explicit(self):
        self.git('rm', 'candidate.txt')
        report = module.inspect(self.root, ['candidate.txt'])
        self.assertEqual(report['staged_count'], 1)
        self.assertIsNone(report['input_hashes']['candidate.txt'])

    def test_missing_required_input_blocks_even_if_candidate_deletes_it(self):
        (self.root / 'test.txt').unlink()
        with self.assertRaises(ValueError): module.inspect(self.root, ['test.txt'], ['test.txt'])

    def test_unrelated_staged_work_is_reported_without_exposing_its_names(self):
        (self.root / 'unrelated.txt').write_text('private staged\n')
        self.git('add', 'unrelated.txt')
        report = module.inspect(self.root, ['candidate.txt'])
        self.assertEqual(report['unrelated_staged_count'], 1)
        self.assertEqual(report['staged_candidate'], [])
        self.assertNotIn('unrelated.txt', json.dumps(report))
        self.assertFalse(report['validation_passed'])

    def test_staging_changes_context_without_invalidating_same_content(self):
        (self.root / 'candidate.txt').write_text('new\n')
        before = module.inspect(self.root, ['candidate.txt'])
        self.git('add', 'candidate.txt')
        after = module.inspect(self.root, ['candidate.txt'])
        self.assertEqual(before['fingerprint'], after['fingerprint'])
        self.assertNotEqual(before['context_fingerprint'], after['context_fingerprint'])

    def test_commit_changes_context_not_selected_content(self):
        before = module.inspect(self.root, ['candidate.txt'])
        self.git('commit', '--allow-empty', '-qm', 'metadata context')
        after = module.inspect(self.root, ['candidate.txt'])
        self.assertEqual(before['fingerprint'], after['fingerprint'])
        self.assertNotEqual(before['context_fingerprint'], after['context_fingerprint'])

    def test_detached_head_has_no_invented_branch(self):
        self.git('checkout', '--detach', '-q')
        self.assertIsNone(module.inspect(self.root, ['candidate.txt'])['branch'])

    def test_large_dirty_tree_is_bounded(self):
        for i in range(230): (self.root / ('untracked-%03d.txt' % i)).write_text('private\n')
        report = module.inspect(self.root, ['candidate.txt'])
        self.assertEqual(report['changed_count'], 230)
        self.assertLess(len(json.dumps(report)), 2000)
        self.assertNotIn('untracked-001.txt', json.dumps(report))

    def test_inspection_preserves_files_index_refs_and_configuration(self):
        (self.root / 'candidate.txt').write_text('new\r\n', newline='')
        self.git('add', 'candidate.txt')
        paths = [p for p in self.root.rglob('*') if p.is_file()]
        before = {p.relative_to(self.root): p.read_bytes() for p in paths}
        module.inspect(self.root, ['candidate.txt'], ['test.txt'])
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_cli_keeps_flags_and_reports_blocked_status(self):
        result = subprocess.run([sys.executable, str(Path(module.__file__)), '--repo', str(self.root),
                                 '--candidate', 'missing.txt'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'blocked')


if __name__ == '__main__':
    unittest.main()
