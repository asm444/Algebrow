import sys, unittest, time

class ProgressTestResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.testsRunCount += 1
        self._update_progress_bar()

    def _update_progress_bar(self):
        total = self.testsTotal
        done = self.testsRunCount
        percent = int(done / total * 100)
        bar_length = 40
        filled_length = int(bar_length * done // total)
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\r[{bar}] {percent}% ({done}/{total} tests)")
        sys.stdout.flush()
        time.sleep(0.05)  # apenas para visualização mais suave

class ProgressTestRunner(unittest.TextTestRunner):
    def run(self, test):
        result = self._makeResult()
        test_count = test.countTestCases()
        result.testsTotal = test_count
        result.testsRunCount = 0
        print(f"Running {test_count} tests...\n")
        start_time = time.time()
        test(result)
        duration = time.time() - start_time
        print(f"\n\nFinished in {duration:.2f}s")
        print(f"Ran {result.testsRunCount} tests total.")
        passed = result.testsRunCount - len(result.failures) - len(result.errors)
        print(f"Passed: {passed}")
        print(f"Failed: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return result

def progress_bar(Objeto):
    suite = unittest.TestLoader().loadTestsFromTestCase(Objeto)
    runner = ProgressTestRunner(verbosity=0, resultclass=ProgressTestResult)
    runner.run(suite)