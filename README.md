# Log Parser and GUI Application

This project consists of a log parsing script, a check server status script, and a GUI application combined into a single script (`main.py`) for managing and displaying log data. The parser processes log files, extracts relevant information based on predefined keywords, and stores the results in an organized manner. The GUI allows users to interact with the parsed data, search through it, and run various commands.

## Table of Contents
- [Features](#features)
  - [Log Parser](#log-parser)
  - [GUI Application](#gui-application)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Log Parser](#running-the-log-parser)
  - [Using the GUI](#using-the-gui)
- [Directory Structure](#directory-structure)
- [Error Reference Materials](#error-reference-materials)
- [Customization](#customization)
- [License](#license)

## Features

### Log Parser
- Reads a log file (`sam_techsupportinfo`).
- Processes the log file to extract information based on a list of keywords (`KEYWORDS_LIST`).
- Outputs the extracted information into separate text files in the `commands_output` directory.

### GUI Application
- Dark-themed, user-friendly interface built with `customtkinter`.
- Side menu for navigating commands and viewing their outputs.
- Text search functionality within the displayed log data.
- Button to run the log parser from the GUI.
- Dynamic button creation for each command output file.
- Tooltips for additional information display on hover.
- Faults and server status details display with color-coded statuses.

## Requirements
- Python 3.x
- `customtkinter` for the GUI
- Additional Python modules: `os`, `re`, `subprocess`, `tkinter`, `json`

## Installation
1. Clone the repository:

    ```sh
    git clone https://github.com/chomacheto/ucs_log_parser.git
    ```

2. Done

## Usage

### Running the Log Parser
1. Start the GUI application:

    ```sh
    python main.py
    ```

2. **Run Log Parser**: Click the "Run Log Parser" button to execute the log parser script. This will process the `sam_techsupportinfo` file and generate output files in the `commands_output` directory.

### Using the GUI
1. **Command Output Buttons**: After running the parser, buttons for each output file will be created in the side menu. Click on these buttons to view the corresponding log data in the main frame.

2. **Search Functionality**: Use the search entries to filter buttons or search within the displayed log data.

3. **Show Server Status Detail**: Click this button to view the detailed status of servers. The status will be color-coded based on its state. **You can click on the server and the parser will display all the data from the file that includes the server.**

4. **Show Faults**: Click this button to display parsed faults. Faults are also color-coded based on their severity. **You can click on the fault and the parser will display the entire fault**

## Directory Structure

ucs_log_parser/
├── commands_output/ # Directory for storing parsed log outputs will be created when the file is parsed
├── sam_techsupportinfo # Input log file to be parsed must be pasted here
├── main.py # Combined script for log parsing, server status checking, and GUI
├── keywords.py # Module containing the KEYWORDS_LIST
├── README.md # This README file
├── !error_reference_materials/ # Directory containing error reference materials
│ ├── Cisco_UCS_Faults.pdf
│ ├── Cisco_UCS_Faults_and_Error.pdf
│ └── Cisco_UCS_Faults_and_Error_Messages_Reference-4-1.pdf
└── LICENSE.md # License agreement


## Error Reference Materials

In the `!error_reference_materials` directory, you will find three PDF files containing error reference materials:
- `Cisco_UCS_Faults.pdf`
- `Cisco_UCS_Faults_and_Error.pdf`
- `Cisco_UCS_Faults_and_Error_Messages_Reference-4-1.pdf`

These files provide detailed information on various fault and error messages that can help you understand and troubleshoot the issues identified by the log parser.

## Customization

- **Keywords List**: Modify the `KEYWORDS_LIST` in `keywords.py` to customize which keywords the parser looks for in the log file.

- **Regex Patterns**: Adjust the regex patterns in `main.py` if needed to match specific formats in your logs.

## License

**Log Parser Application** is licensed under the following terms:

1. **Non-Commercial Use**: This software is provided solely for personal or educational use. Commercial use is strictly prohibited unless explicitly approved by the original author.

2. **Distribution**: Redistribution of this software, in part or in whole, is prohibited without explicit permission from the original author.

3. **Modification**: Modifications to the software are allowed for personal or educational use. However, distribution of modified versions is prohibited without explicit permission from the original author.

4. **Citation**: Any use of this software must include proper citation to the original author. The citation must include the name of the author and a link to the original repository.

5. **Approval for Use**: Explicit approval must be obtained from the original author for any use beyond personal or educational purposes. Requests for approval should be directed to ivanchomakov@icloud.com / ivan.chomakov@ibm.com

6. **Disclaimer**: This software is provided "as-is", without any express or implied warranty. In no event shall the author be held liable for any damages arising from the use of this software.

By using this software, you agree to the terms of this license.

Author: Ivan Chomakov  
Contact: ivanchomakov@icloud.com / ivan.chomakov@ibm.com
