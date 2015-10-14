import unittest

class TestHelpers(unittest.TestCase):
    def assertListAlmostEqual(self, list1, list2, decimals=None, msg=None):
        if not msg:
            new_msg = '{} did not almost equal {}'.format(list1,list2)
        else:
            new_msg = msg
        self.assertEqual(len(list1), len(list2), new_msg)
        for idx in range(0, len(list1)):
            if not msg:
                new_msg = '{} did not almost equal {} as {} was not {}'.format(list1, list2, list1[idx], list2[idx])
            else:
                new_msg = msg
            self.assertAlmostEqual(list1[idx], list2[idx], decimals, new_msg)