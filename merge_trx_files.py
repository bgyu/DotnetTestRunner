import os
import xml.etree.ElementTree as ET

def merge_trx_files(input_dir, output_file):
    # Create a new XML tree for the merged result file
    root = ET.Element("TestRun", {
        "xmlns": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        "name": "MergedTestResults",
        "runUser": os.environ['USERNAME']
    })

    # Iterate through all the input TRX files in the input directory
    for filename in os.listdir(input_dir):
        if not filename.endswith(".trx"):
            continue

        # Load the TRX file as an XML tree
        tree = ET.parse(os.path.join(input_dir, filename))
        root_node = tree.getroot()

        # Merge the contents of the TestDefinitions and Results elements into the merged result file
        for node in root_node.findall(".//TestDefinitions/*"):
            root.append(node)
        for node in root_node.findall(".//Results/*"):
            root.append(node)

    # Write the merged result file to disk
    ET.ElementTree(root).write(output_file, encoding="utf-8", xml_declaration=True)

    print(f"Merged TRX files successfully to {output_file}")


if __name__ == "__main__":
    # Replace with the input directory containing TRX files and the output file name
    merge_trx_files("C:/path/to/trx/files", "merged_results.trx")
