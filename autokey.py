import os
import time
import subprocess


winTitle = window.get_active_title()
ret, user_input = dialog.input_dialog(title="Task", message="Enter task:")


if not ret:
    window.activate(winTitle)
    time.sleep(0.1)
    
    os.environ['OPENAI_API_KEY'] = "<YOUR_OPENAI_API_KEY>"
    os.environ['FAF_JSON_OUTPUT_PATH'] = "PATH_TO_JSON_OUTPUT"
    
    faf_path = "<PATH_TO_FAF_ON_YOUR_SYSTEM>"
     
    subprocess.run([faf_path, user_input], check=True)

    