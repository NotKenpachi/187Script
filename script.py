import time
import ast
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC

# excel w testcases
df = pd.read_excel("test/Updated_Gemini-Testing-New-Search-Testcases.xlsx")
results = []

# firefox profile finding (automation profile)
profile_root = "C:\\Users\\brand\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
profile_name = "QoSNDTlt.Profile 1"
profile_path = os.path.join(profile_root, profile_name)

if not os.path.exists(profile_path):
    raise Exception(f"Firefox profile not found: {profile_path}")

print(f"Using Firefox profile: {profile_path}")

options = webdriver.FirefoxOptions()
options.profile = profile_path
options.set_preference("dom.webnotifications.enabled", False)

driver = webdriver.Firefox(
    service=Service(GeckoDriverManager().install()),
    options=options
)

driver.get("https://gemini.google.com/")

input("\nLog in to Gemini, then press ENTER...\n")

def send_prompt(prompt_text):
    wait_time = 40 # Wait up to 20 seconds
    wait = WebDriverWait(driver, wait_time)
    
    editor_selector = "div[contenteditable='true']"
    submit_button_selector = "button[aria-label='Send message']" 

    try:
        #Wait until the editor element is present AND clickable
        editor = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, editor_selector))
        )

        #Use JavaScript to clear the previous content safely
        driver.execute_script("arguments[0].innerHTML = '';", editor)
        time.sleep(0.5)

        #Use JavaScript to inject the text and trigger necessary events.
        driver.execute_script(f"arguments[0].innerText = arguments[1];", editor, prompt_text)
        driver.execute_script("""
            var element = arguments[0];
            var event = new Event('input', { bubbles: true });
            element.dispatchEvent(event);
        """, editor)

        time.sleep(0.5) 
        
        #Find and click the submission button
        print("  Submitting prompt via Send button...")
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, submit_button_selector))
        )
        submit_button.click()
        
        #The prompt is now submitted. Waiting for a response...

        print("  Waiting for model output...")

        last_text = ""
        stable_count = 0

        # Wait for Model Response Stabilization
        while stable_count < 3:
            time.sleep(2)
            
            # Use try-except to handle stale elements during response read
            try:
                # Wait for at least one markdown block to be present
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.markdown")))
                blocks = driver.find_elements(By.CSS_SELECTOR, "div.markdown")
            except (TimeoutException, StaleElementReferenceException):
                 time.sleep(3) 
                 continue # Re-try the loop
            except:
                time.sleep(3) 
                continue 

            current = blocks[-1].text.strip()
            if current == last_text:
                stable_count += 1
            else:
                stable_count = 0
                last_text = current

        print("  Response stabilized.")
        model_output = last_text

        # Send ESCAPE to the body to dismiss any pop-up/modal
        print("  Attempting to dismiss modal with ESCAPE key...")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(1) 

        try:
            editor = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, editor_selector))
            )
            # Scroll the NEWLY FOUND element into view for the next iteration
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", editor)
            time.sleep(0.5)
        except Exception as e:
            # If we fail to re-find the editor, log the error but still return the model output
            print(f"  Warning: Could not re-find editor for scrolling. Error: {e}")
        
        return model_output

    except Exception as e:
        # Ensure the error message includes the full details for debugging
        return f"ERROR: Message: {e}"

# score output 
def score_accuracy(expected_algorithm, model_output):
    if expected_algorithm.lower() in model_output.lower():
        return "Correct"
    if "i don't know" in model_output.lower(): 
        return "No Answer"
    return "Incorrect"

def score_quality(model_output):
    if len(model_output.split()) > 12:
        return "Clear"
    return "Unclear"

start = time.time()
# main loop
for idx, row in df.iterrows():

    # parsing inputdict metadata
    try:
        input_meta = ast.literal_eval(row["inputDict"])
    except:
        input_meta = {}
        
    try:
        context_meta = ast.literal_eval(row["contextDict"])
    except:
        context_meta = {}

    prompt_type = input_meta.get("prompt type", "")
    algorithm = input_meta.get("data structure", "")
    context_country = context_meta.get("Country of Origin", "")
    context_grade = context_meta.get("Grade Level", "") # Added default "" for safety
    if context_country != "United States" or context_grade != "Undergraduate":
        continue
    
    else:
        # actual prompt to Gemini:
        print(f"\n▶ Running Test Case {idx+1}")
        prompt_text = row["input"]

        # running prompt
        model_output = send_prompt(prompt_text)

        # scoring with output tree
        actual_accuracy = score_accuracy(algorithm, model_output)
        actual_quality = score_quality(model_output)

        expected_accuracy = "Correct"
        expected_quality = "Clear"

        final_result = "PASS" if (
            actual_accuracy == expected_accuracy and
            actual_quality == expected_quality
        ) else "FAIL"

        # save results to csv
        results.append({
            "Test Case ID": idx+1,
            "Prompt": prompt_text,

            # InputDict parsed values
            "Prompt Type": prompt_type,
            "Data Structure or Algorithm": algorithm,
            # "Complexity": complexity,

            # Expected Output (Output Tree)
            "Expected Accuracy": expected_accuracy,
            "Expected Quality": expected_quality,

            # Actual Output
            "Actual Accuracy": actual_accuracy,
            "Actual Quality": actual_quality,
            "Model Output": model_output,

            # PASS/FAIL
            "Result": final_result
        })

# save csv
output_path = "gemini_test_results.xlsx"
pd.DataFrame(results).to_excel(output_path, index=False)

print("\nresults were saved to:", output_path)
end_time = time.time()
total_seconds = end_time - start

# Calculate minutes and remaining seconds for a cleaner display
minutes = int(total_seconds // 60)
seconds = total_seconds % 60 

# STEP 4: Print the total time
print("\n" + "="*50)
print(f"Total Execution Time: {minutes} minutes and {seconds:.2f} seconds.")
print("="*50)
driver.quit()