from XTax import Tax
import io
import unittest
import unittest.mock

class Test_XTax(unittest.TestCase):
    def test_TaxInitYear(self):
        MyTax = Tax(2019,autoload=False)
        self.assertEqual(MyTax.Year, 2019)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_TaxInitLog(self,mock_stdout):
        MyTax = Tax(2019,loglevel=1,autoload=False)
        OutputList = mock_stdout.getvalue().split('\n')
        self.assertEqual(len(OutputList), 4)
        self.assertEqual(OutputList[0], "Beginning of Init")
        self.assertEqual(OutputList[2], "End of Init")

if __name__ == '__main__':
    unittest.main()