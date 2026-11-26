import unittest

from cache_simulator import Cache, run_trace


class CacheTests(unittest.TestCase):
    def test_address_zero_starts_as_a_miss(self):
        cache = Cache()
        self.assertFalse(cache.access(0).hit)
        self.assertTrue(cache.access(0).hit)

    def test_lru_evicts_dirty_line_and_restores_its_value_from_memory(self):
        cache = Cache(memory_size=4, slots=2)
        cache.access(0)
        cache.access(1, 42)
        self.assertEqual(cache.memory[1], 0)
        cache.access(0)
        miss = cache.access(2)
        self.assertEqual(miss.write_back, (1, 42))
        self.assertEqual(cache.access(1).value, 42)

    def test_trace_handles_comments_and_line_numbers(self):
        cache = Cache()
        trace = run_trace(["# example", "W 7 2", "R 2 # hit", "R -1"], cache)
        self.assertEqual(next(trace).value, 7)
        self.assertTrue(next(trace).hit)
        with self.assertRaisesRegex(ValueError, "line 4"):
            next(trace)


if __name__ == "__main__":
    unittest.main()
