import os
import subprocess
import sys

def clean_data():
    input_file = "applicant_data.json"
    output_file = "llm_extend_applicant_data.json"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    print("Running LLM data cleaning via llm_hosting/app.py...")
    
    # 按照 README 说明，使用 CLI 模式调用 app.py
    cmd = [
        sys.executable, "llm_hosting/app.py",
        "--file", input_file,
        "--stdout"
    ]

    try:
        # 执行 app.py 并将输出结果捕获写入 llm_extend_applicant_data.json
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.stdout)
            
        print(f"Done! Successfully generated {output_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing app.py: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    clean_data()
