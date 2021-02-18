import unittest

from app import db


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
        db.drop_all()


if __name__ == '__main__':
    unittest.main()
