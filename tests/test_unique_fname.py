import unittest
import os
import subprocess
import shutil
from unique_fname import main

class TestUniqueFname(unittest.TestCase):

    def setUp(self):
        os.makedirs('test_dir/sub_dir', exist_ok=True)
        with open('test_dir/test1.txt', 'w') as f:
            f.write('test1')
        with open('test_dir/test2.log', 'w') as f:
            f.write('test2')
        with open('test_dir/sub_dir/test3.txt', 'w') as f:
            f.write('test3')

        with open('test_dir/.hidden.txt', 'w') as f:
            f.write('hidden')

    def tearDown(self):
        shutil.rmtree('test_dir')

    def test_hidden_file(self):
        result = subprocess.run(['python3', 'unique_fname/main.py', 'rename', 'test_dir', '--recursive'], capture_output=True, text=True)
        self.assertNotIn('hidden', result.stdout)

    def test_parse_fname(self):
        parts = main.parse_fname('d41d8cd98f00b204e9800998ecf8427e-20011125-153008-0001-fn-foo.txt')
        self.assertEqual(parts['checksum'], 'd41d8cd98f00b204e9800998ecf8427e')
        self.assertEqual(parts['date'], '20011125')
        self.assertEqual(parts['time'], '153008')
        self.assertEqual(parts['number'], '0001')
        self.assertEqual(parts['orignal_filename'], 'foo')
        self.assertEqual(parts['ext'], '.txt')

    def test_construct_fname(self):
        parts = {
            'checksum': 'd41d8cd98f00b204e9800998ecf8427e',
            'date': '20011125',
            'time': '153008',
            'number': '0001',
            'orignal_filename': 'foo',
            'ext': '.txt'
        }
        fname = main.construct_fname(parts, directory='.')
        self.assertEqual(fname, './d41d8cd98f00b204e9800998ecf8427e-20011125-153008-0001-fn-foo.txt')

    def test_rename(self):
        path = 'test_dir/test_rename.txt'
        with open(path, 'w') as f:
            f.write('test_rename')
        checksum = main.get_checksum(path)
        result = subprocess.run(['python3', 'unique_fname/main.py', 'rename', path, '--tags', 'checksum', '--rename'], capture_output=True, text=True)
        self.assertEqual(result.stdout, '')
        self.assertFalse(os.path.exists(path))
        new_fname = checksum + '-fn-test_rename.txt'
        self.assertTrue(os.path.exists('test_dir/' + new_fname))

    def test_default(self):
        path = 'test_dir/test1.txt'
        checksum = main.get_checksum(path)
        date = main.get_date(path)
        time = main.get_time(path)
        result = subprocess.run(['python3', 'unique_fname/main.py', 'rename', path], capture_output=True, text=True)
        self.assertIn(checksum, result.stdout)
        self.assertIn(date, result.stdout)
        self.assertIn(time, result.stdout)
        self.assertIn('0001', result.stdout)

    def test_rename_existing(self):
        path = 'test_dir/test_rename_existing.txt'
        with open(path, 'w') as f:
            f.write('test_rename_existing')
        checksum = main.get_checksum(path)
        new_fname = checksum + '-fn-test_rename_existing.txt'
        with open('test_dir/' + new_fname, 'w') as f:
            f.write('test_rename_existing')
        result = subprocess.run(['python3', 'unique_fname/main.py', 'rename', path, '--tags', 'checksum', '--rename'], capture_output=True, text=True)
        self.assertEqual(result.stdout, '')
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.exists('test_dir/' + new_fname))

    def test_recursive(self):
        result = subprocess.run(['python3', 'unique_fname/main.py', 'rename', 'test_dir', '--tags', 'checksum', '--recursive'], capture_output=True, text=True)
        self.assertIn(main.get_checksum('test_dir/test1.txt'), result.stdout)
        self.assertIn(main.get_checksum('test_dir/test2.log'), result.stdout)
        self.assertIn(main.get_checksum('test_dir/sub_dir/test3.txt'), result.stdout)

    def test_find_dups(self):
        with open('test_dir/dup1.txt', 'w') as f:
            f.write('dup')
        with open('test_dir/dup2.txt', 'w') as f:
            f.write('dup')
        checksum = main.get_checksum('test_dir/dup1.txt')
        subprocess.run(['python3', 'unique_fname/main.py', 'rename', 'test_dir/dup1.txt', '--tags', 'checksum', '--rename'], capture_output=True, text=True)
        subprocess.run(['python3', 'unique_fname/main.py', 'rename', 'test_dir/dup2.txt', '--tags', 'checksum', '--rename'], capture_output=True, text=True)
        result = subprocess.run(['python3', 'unique_fname/main.py', 'find-dups', 'test_dir'], capture_output=True, text=True)
        self.assertIn(f'Files with checksum: {checksum}', result.stdout)
        self.assertIn('dup1.txt', result.stdout)
        self.assertIn('dup2.txt', result.stdout)

if __name__ == '__main__':
    unittest.main()
