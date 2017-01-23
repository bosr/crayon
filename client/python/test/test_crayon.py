import unittest
import time
import os

from helper import Helper
from crayon.crayon import CrayonClient

class CrayonClientTestSuite(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CrayonClientTestSuite, self).__init__(*args, **kwargs)

    def setUp(self):
        self.h = Helper()

    def tearDown(self):
        self.h.kill_remove()
        self.h = None

    # INIT
    def test_init(self):
        CrayonClient()

    def test_init_wrong_localhost(self):
        self.assertRaises(ValueError, CrayonClient, "not_open", 8889)

    def test_init_wrong_port(self):
        self.assertRaises(ValueError, CrayonClient, "localhost", 123412341234)

    def test_init_xp_empty(self):
        cc = CrayonClient()
        self.assertRaises(ValueError, cc.new_experiment, "")

    # scalars
    def test_add_scalar_value(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 2, wall_time=time.clock(), step=1)

    def test_add_scalar_less_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 2)

    # TODO These should really be tested singularly...
    def test_add_scalar_wrong_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        self.assertRaises(ValueError, foo.add_scalar_value,
                          "bar", "lol")

    def test_add_scalar_wrong_variable(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        self.assertRaises(ValueError, foo.add_scalar_value,
                          "", 2)

    def test_add_scalars_values(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"fizz": 3, "buzz": 5}
        foo.add_scalars_values(data, wall_time=0, step=5)
        data = {"fizz": 6, "buzz": 10}
        foo.add_scalars_values(data)

    def test_add_scalars_values_wrong_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"fizz": "foo", "buzz": 5}
        self.assertRaises(ValueError, foo.add_scalars_values, data)
        data = {3: 6, "buzz": 10}
        self.assertRaises(ValueError, foo.add_scalars_values, data)

    def test_get_scalars_no_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        self.assertRaises(ValueError, foo.get_scalars, "bar")

    def test_get_scalars_one_datum(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 0, wall_time=0, step=0)
        time.sleep(1)
        self.assertEqual(foo.get_scalars("bar"), [[0.0, 0, 0.0]])

    def test_get_scalars_two_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 0, wall_time=0, step=0)
        foo.add_scalar_value("bar", 1, wall_time=1, step=1)
        time.sleep(1)
        self.assertEqual(foo.get_scalars("bar"),
                         [[0.0, 0, 0.0], [1.0, 1, 1.0]])

    def test_get_scalars_auto_step(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 0, wall_time=0)
        foo.add_scalar_value("bar", 1, wall_time=1)
        foo.add_scalar_value("bar", 2, wall_time=2, step=10)
        foo.add_scalar_value("bar", 3, wall_time=3)
        time.sleep(1)
        self.assertEqual(foo.get_scalars("bar"),
                         [[0.0, 0, 0.0], [1.0, 1, 1.0],
                          [2.0, 10, 2.0], [3.0, 11, 3.0]])

    def test_get_scalars_wrong_variable(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 0)
        time.sleep(1)
        self.assertRaises(ValueError, foo.get_scalars,"")

    def test_add_scalars_values(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"fizz": 3, "buzz": 5}
        foo.add_scalars_values(data, wall_time=0, step=5)
        data = {"fizz": 6, "buzz": 10}
        foo.add_scalars_values(data, wall_time=1)
        time.sleep(1)
        self.assertEqual(foo.get_scalars("fizz"),
                         [[0.0, 5, 3.0], [1.0, 6, 6.0]])
        self.assertEqual(foo.get_scalars("buzz"),
                         [[0.0, 5, 5.0], [1.0, 6, 10.0]])

    # Histograms
    def test_add_histogram(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram("bar", data, wall_time=0, step=0)
        foo.add_histogram("bar", data)

    def test_add_histogram_with_sum(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum": 75}
        foo.add_histogram("bar", data)

    def test_add_histogram_with_sumsq(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum_squares": 5625}
        foo.add_histogram("bar", data)

    def test_add_histogram_with_sum_sumsq(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum": 75,
                "sum_squares": 2675}
        foo.add_histogram("bar", data)

    def test_add_histogram_to_build(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = [1,2,3,4,5]
        foo.add_histogram("bar", data, tobuild=True)

    def test_add_histogram_less_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"some data": 0}
        self.assertRaises(ValueError, foo.add_histogram,
                          "bar", data)

    # TODO These should really be tested singularly...
    def test_add_histogram_wrong_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = ["lolz", "lulz", "lelz"]
        self.assertRaises(ValueError, foo.add_histogram,
                          "bar", data, tobuild=True)

    def test_add_histogram_wrong_variable(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        self.assertRaises(ValueError, foo.add_histogram,
                          "", data)

    def test_get_histograms_no_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        self.assertRaises(ValueError, foo.get_histograms, "bar")

    def test_get_histograms_one_datum(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram("bar", data, wall_time=0, step=0)
        time.sleep(1)
        self.assertEqual(foo.get_histograms("bar"),
                         [[0.0, 0,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]]])

    def test_get_histograms_two_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram("bar", data, wall_time=0, step=0)
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram("bar", data, wall_time=1, step=1)
        time.sleep(1)
        self.assertEqual(foo.get_histograms("bar"),
                         [[0.0, 0,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]],
                          [1.0, 1,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]]])

    def test_get_histograms_wrong_variable(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram("bar", data, wall_time=0, step=0)
        time.sleep(1)
        self.assertRaises(ValueError, foo.get_histograms, "")

    # Only checks that we get a zip file.
    # TODO open and match data to recorded
    def test_get_data(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 2, wall_time=time.time(), step=1)
        time.sleep(1)
        filename = foo.get_data()
        os.remove(filename)

    # Only checks that we set a zip file.
    def test_init_from_file(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 2, wall_time=time.time(), step=1)
        time.sleep(1)
        filename = foo.get_data()
        time.sleep(1)
        new = cc.new_experiment("new", filename)
        os.remove(filename)

    def test_set_data_force(self):
        cc = CrayonClient()
        foo = cc.new_experiment("foo")
        foo.add_scalar_value("bar", 2, wall_time=time.time(), step=1)
        time.sleep(1)
        filename = foo.get_data()
        time.sleep(1)
        foo.init_from_file(filename, True)
        os.remove(filename)

    def test_set_data_wrong_file(self):
        cc = CrayonClient()
        self.assertRaises(IOError, cc.new_experiment, "foo",
                          "random_noise")