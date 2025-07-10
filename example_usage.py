# example_usage.py

from dotenv import load_dotenv
from gemini_prompt_optimizer import GeminiLLM, EnhancedPromptOptimizer, PromptObjectives
from prompt_optimizer import OptimizationObjective, ObjectivePriority

load_dotenv()

# Example 1: Basic prompt optimization
def example_basic():
    prompt = "Tell me about AI"
    
    # This is too vague, let's see what the optimizer suggests
    from gemini_prompt_optimizer import optimize_your_prompt
    results = optimize_your_prompt(prompt)
    
    print("Original prompt was too vague!")
    print("Here's an improved version:")
    print(results['improvements'][0]['prompt'])

# Example 2: Custom objectives
def example_custom_objectives():
    # Create custom objectives for a specific use case
    objectives = PromptObjectives()
    
    # For technical documentation
    objectives.add_objective(OptimizationObjective(
        "technical_accuracy", "Technical correctness",
        ObjectivePriority.MUST_HAVE, weight=3.0
    ))
    
    objectives.add_objective(OptimizationObjective(
        "code_examples", "Includes code examples",
        ObjectivePriority.SHOULD_HAVE, weight=2.0
    ))
    
    objectives.add_objective(OptimizationObjective(
        "beginner_friendly", "Accessible to beginners",
        ObjectivePriority.NICE_TO_HAVE, weight=1.0
    ))
    
    # Now optimize with these objectives
    llm = GeminiLLM()
    optimizer = EnhancedPromptOptimizer(objectives, llm)
    
    prompt = "Explain Python decorators"
    results = optimizer.score_and_improve(prompt)
    
    return results

# Example 3: Batch optimization
def example_batch_optimization():
    prompts = [
        "Write a story",
        "Explain machine learning",
        "Create a Python function",
        "Summarize this text"
    ]
    
    from gemini_prompt_optimizer import optimize_your_prompt
    
    results = []
    for prompt in prompts:
        print(f"\nOptimizing: {prompt}")
        result = optimize_your_prompt(prompt)
        results.append({
            "original": prompt,
            "best_improvement": result['improvements'][0]['prompt'] if result['improvements'] else prompt,
            "score_improvement": result['improvements'][0]['weighted_score'] - result['original_weighted_score'] if result['improvements'] else 0
        })
    
    # Show summary
    import pandas as pd
    df = pd.DataFrame(results)
    print("\nOptimization Summary:")
    print(df)

if __name__ == "__main__":
    # Run examples
    print("Running Example 1: Basic Optimization")
    example_basic()
    
    print("\n" + "="*50 + "\n")
    print("Running Example 2: Custom Objectives")
    example_custom_objectives()
    
    print("\n" + "="*50 + "\n")
    print("Running Example 3: Batch Optimization")
    example_batch_optimization()