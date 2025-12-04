Here's a structured `README.md` file for your Gemini Testing Automation project, formatted with proper code blocks and sections for clarity:

```markdown
# Gemini Testing Automation

This project automates the testing of prompts on Google Gemini using Selenium and Firefox. It reads test cases from an Excel file, sends prompts to Gemini, captures the model output, and scores the results based on accuracy and quality. Finally, it generates a detailed Excel report of test results.

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Scoring](#scoring)
- [Output](#output)
- [Notes](#notes)

## Requirements

- Python 3.10+
- Firefox Browser
- Firefox Automation Profile (optional but recommended)
- Python packages:
  
  ```bash
  pip install selenium pandas webdriver-manager openpyxl
  ```

## Setup

### Firefox Profile

1. Create or use an existing Firefox profile for automation.
2. Note the path to your Firefox profile, e.g.:

   ```
   C:\Users\<YourUsername>\AppData\Roaming\Mozilla\Firefox\Profiles\
   ```

3. Update the `profile_path` variable in the script to match your profile path:

   ```python
   profile_root = "C:\\Users\\<YourUsername>\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
   profile_name = "<YourProfileName>"
   profile_path = os.path.join(profile_root, profile_name)
   ```

### Test Case Excel File

Place your test case Excel file in the `test/` folder.

- Default path in script:
  
  ```
  test/Updated_Gemini-Testing-New-Search-Testcases.xlsx
  ```

Ensure the Excel file has columns: `inputDict`, `contextDict`, `input`.

## Usage

Run the script in a terminal:

```bash
python gemini_test_script.py
```

- Firefox will launch.
- Log in to Google Gemini manually.
- Press ENTER in the terminal to start running test cases.

The script iterates through test cases, sends prompts, captures outputs, and saves results.

## Configuration

### Profile Path

```python
profile_root = "C:\\Users\\<YourUsername>\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
profile_name = "<YourProfileName>"
```

### Prompt Waiting Time

Adjust in `send_prompt()` if responses are slow:

```python
wait_time = 40
```

### Filtering Test Cases

Currently only tests cases where:
- Country of Origin = "United States"
- Grade Level = "Undergraduate"

Modify this logic if needed.

## How It Works

1. Reads test cases from Excel.
2. Filters test cases based on metadata.
3. Sends prompts to Gemini using Selenium:

   ```python
   driver.execute_script(f"arguments[0].innerText = arguments[1];", editor, prompt_text)
   submit_button.click()
   ```

4. Waits for the model response to stabilize (checks text 3 consecutive times).
5. Captures the output and dismisses modals if present.
6. Scores the response and stores results.

Results are saved to:

```
gemini_test_results.xlsx
```

Columns include:

- Test Case ID
- Prompt
- Prompt Type
- Data Structure / Algorithm
- Expected Accuracy & Quality
- Actual Accuracy & Quality
- Model Output
- Final Result

Total execution time is printed in minutes and seconds:

```python
print(f"Total Execution Time: {minutes} minutes and {seconds:.2f} seconds.")
```

## Notes

- Log in to Gemini before pressing ENTER in the terminal.
- Selenium may occasionally throw `StaleElementReferenceException`; the script handles it.
- Long-running scripts may take time depending on the number of test cases and model response times.
```

Feel free to modify any sections as necessary!
