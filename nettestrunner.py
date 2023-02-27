import os
import subprocess
import xml.etree.ElementTree as ET
from multiprocessing import Process, Manager, Semaphore, Value, Lock

class DotnetTestRunner:
    def __init__(self, assembly_path, max_concurrent_processes=2, trx_result_path=None, print_summary=True, filter=None):
        self.assembly_path = assembly_path
        self.max_concurrent_processes = max_concurrent_processes
        self.trx_result_path = trx_result_path
        self.print_summary = print_summary
        self.test_list_file_path = 'test_list.txt'
        self.result_dict = Manager().dict()
        self.passed = Value('i', 0)
        self.failed = Value('i', 0)
        self.filter = filter

    def run_tests(self):
        # Step 1: Save all dotnet unit test cases of a giving testing assembly to a file
        test_command = f'dotnet test "{self.assembly_path}" --list-tests'
        if self.filter:
            test_command += f' --filter "{self.filter}"'
        test_list_output = subprocess.check_output(test_command, shell=True)
        with open(self.test_list_file_path, 'wb') as f:
            f.write(test_list_output)

        # Step 2: Define a function to run a single test case in a separate process
        def run_test_case(test_case, sem):
            # acquire the semaphore to limit the number of concurrent processes
            sem.acquire()
            try:
                # run the test case and get the output
                process_command = f'dotnet test "{self.assembly_path}" --filter "{test_case}" --logger trx'
                process_output = subprocess.check_output(process_command, shell=True)
                self.result_dict[test_case] = process_output.decode('utf-8')
                # update the number of passed/failed test cases based on the output
                result_root = ET.fromstring(process_output)
                test_result = result_root.find('ResultSummary/Counters')
                with self.passed.get_lock():
                    self.passed.value += int(test_result.attrib['passed'])
                with self.failed.get_lock():
                    self.failed.value += int(test_result.attrib['failed'])
            except subprocess.CalledProcessError as e:
                # handle errors in running the test case
                self.result_dict[test_case] = f"Error occurred when running {test_case}: {e.output.decode('utf-8')}"
                with self.failed.get_lock():
                    self.failed.value += 1
            finally:
                # release the semaphore to allow other processes to start
                sem.release()

        # Step 3: Read test cases from the file and run each test case in a new process
        test_list = []
        with open(self.test_list_file_path, 'r') as f:
            test_list = f.readlines()

        test_list = [test.strip() for test in test_list if test.strip()]
        n_total_cases = len(test_list)
        sem = Semaphore(self.max_concurrent_processes)
        processes = []

        for test_case in test_list:
            p = Process(target=run_test_case, args=(test_case, sem))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        # Step 4: Save test results to a single file called result.trx in the format of trx and report the final result
        if self.trx_result_path:
            os.makedirs(os.path.dirname(self.trx_result_path), exist_ok=True)
            root = ET.Element('TestRun')
            for result in self.result_dict.values():
               result_root = ET.fromstring(result)
               for unit_test in result_root.iter('UnitTestResult'):
                   root.append(unit_test)

            tree = ET.ElementTree(root)
            tree.write(result_file_path)

        if self.print_summary:
             n_passed_cases = passed.value
             n_failed_cases = failed.value
             n_skipped_cases = n_total_cases - n_passed_cases - n_failed_cases
             
             print(f"Total number of test cases: {n_total_cases}")
             print(f"Number of passed test cases: {n_passed_cases}")
             print(f"Number of failed test cases: {n_failed_cases}")
             print(f"Number of skipped test cases: {n_skipped}")
             
