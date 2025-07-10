# quick_optimize.py

import os
from dotenv import load_dotenv
from gemini_prompt_optimizer import optimize_your_prompt

# Load environment variables
load_dotenv()

def main():
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Please set GEMINI_API_KEY in your .env file")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    print("🚀 Welcome to Prompt Optimizer!")
    print("=" * 50)
    
    # Get prompt from user
    print("\nEnter the prompt you want to optimize:")
    print("(Press Enter twice when done)")
    
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    
    prompt = "\n".join(lines)
    
    if prompt.strip():
        # Optimize the prompt
        results = optimize_your_prompt(prompt)
        
        # Ask if user wants to test improvements
        print("\n" + "=" * 50)
        choice = input("\nWould you like to test one of the improvements? (1/2/3/n): ")
        
        if choice in ['1', '2', '3']:
            idx = int(choice) - 1
            if idx < len(results['improvements']):
                improved_prompt = results['improvements'][idx]['prompt']
                print(f"\n✅ Selected improvement {choice}:")
                print(improved_prompt)
                
                # You can add code here to actually use the improved prompt
    else:
        print("No prompt provided.")

if __name__ == "__main__":
    main()