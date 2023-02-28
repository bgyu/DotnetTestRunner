import xml.etree.ElementTree as ET


class TestRun:
    def __init__(self, root):
        self.name = root.attrib["name"]
        self.run_user = root.attrib["runUser"]
        self.timestamp = root.attrib["timestamp"]
        self.test_settings = TestSettings(root.find("TestSettings"))
        self.test_results = [TestResult(node) for node in root.findall(".//Results/UnitTestResult")]
        self.total_tests = len(self.test_results)
        self.passed_tests = sum(1 for result in self.test_results if result.outcome == "Passed")
        self.failed_tests = sum(1 for result in self.test_results if result.outcome == "Failed")
        self.skipped_tests = sum(1 for result in self.test_results if result.outcome == "NotExecuted")
        self.total_time = sum(float(result.duration) for result in self.test_results)
    
    def __str__(self):
        return f"TestRun(name={self.name}, run_user={self.run_user}, timestamp={self.timestamp}, test_settings={self.test_settings}, test_results={self.test_results}, total_tests={self.total_tests}, passed_tests={self.passed_tests}, failed_tests={self.failed_tests}, skipped_tests={self.skipped_tests}, total_time={self.total_time})"
    

class TestSettings:
    def __init__(self, node):
        self.name = node.attrib["name"]
        self.id = node.attrib["id"]
        self.execution = Execution(node.find("Execution"))
        self.deployment = Deployment(node.find("Deployment"))
    
    def __str__(self):
        return f"TestSettings(name={self.name}, id={self.id}, execution={self.execution}, deployment={self.deployment})"
    

class Execution:
    def __init__(self, node):
        self.id = node.attrib["id"]
    
    def __str__(self):
        return f"Execution(id={self.id})"
    

class Deployment:
    def __init__(self, node):
        self.run_configuration = RunConfiguration(node.find("RunConfiguration"))
    
    def __str__(self):
        return f"Deployment(run_configuration={self.run_configuration})"
    

class RunConfiguration:
    def __init__(self, node):
        self.id = node.attrib["id"]
        self.name = node.attrib["name"]
    
    def __str__(self):
        return f"RunConfiguration(id={self.id}, name={self.name})"
    

class TestResult:
    def __init__(self, node):
        self.execution_id = node.attrib["executionId"]
        self.test_id = node.attrib["testId"]
        self.test_name = node.attrib["testName"]
        self.duration = node.attrib["duration"]
        self.outcome = node.attrib["outcome"]
        self.output = Output(node.find("Output"))
    
    def __str__(self):
        return f"TestResult(execution_id={self.execution_id}, test_id={self.test_id}, test_name={self.test_name}, duration={self.duration}, outcome={self.outcome}, output={self.output})"
    

class Output:
    def __init__(self, node):
        self.std_out = node.find("StdOut").text.strip() if node.find("StdOut") is not None else ""
        self.std_err = node.find("StdErr").text.strip() if node.find("StdErr") is not None else ""
    
    def __str__(self):
        return f"Output(std_out={self.std_out}, std_err={self.std_err})"
    

def parse_trx_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    test_run = TestRun(root.find("TestRun"))
    return test_run


if __name__ == "__main__":
    # Replace with the path to the TRX file to parse
    test_run = parse_trx_file("path/to/trx/file.trx")
    print(test_run)

