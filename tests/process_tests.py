#!/usr/bin/python

from log_event_monitor.process import Process
import unittest
import os
import time

class ProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.process = Process("echo \"Hello World\"", "/tmp/test.txt")

    def test1_start(self):
        self.process.start()
        time.sleep(1)
        self.assertEqual(self.process.return_code(), 0)

    def test2_file_exists(self):
        self.assertEqual(os.path.isfile("/tmp/test.txt"), True)

    def test3_delete_output_file(self):
        self.process.delete_output_file()
        self.assertEqual(os.path.isfile("/tmp/test.txt"), False)

if __name__ == "__main__":
    unittest.main()
