from django.test import TestCase


class SimpleTests(TestCase):
    def test_simple(self):
        self.assertEqual(1, 1)
