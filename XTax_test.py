from XTax import Tax
import unittest

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_TaxInit(self):
        MyTax = Tax(2019)
        self.assertEqual(MyTax.Year, 2019)

if __name__ == '__main__':
    unittest.main()