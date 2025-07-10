# gemini_prompt_optimizer.py

import os
import json
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
import numpy as np

# Import the base classes from your existing code
from prompt_optimizer import (
    PromptObjectives, OptimizationObjective, ObjectivePriority,
    PromptOptimizer, TestCase, PromptVariation,
    AccuracyEvaluator, BrevityEvaluator, StyleEvaluator,
    FormatComplianceEvaluator, MetricEvaluator, EvaluationResult
)

# Load environment variables
load_dotenv()

class GeminiLLM:
    """Wrapper for Google Gemini API"""
    
    def __init__(self, model_name: str = "gemini-pro", temperature: float = 0.7):
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
        
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response from Gemini"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return ""

class PromptImprover:
    """Analyze prompts and suggest improvements"""
    
    def __init__(self, llm: GeminiLLM):
        self.llm = llm
        
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze a prompt for various qualities"""
        analysis_prompt = f"""
        Analyze the following prompt and provide a detailed assessment:
        
        PROMPT: {prompt}
        
        Please analyze the prompt for:
        1. Clarity: Is the instruction clear and unambiguous? (score 0-10)
        2. Specificity: Does it provide enough context and constraints? (score 0-10)
        3. Structure: Is it well-organized and easy to follow? (score 0-10)
        4. Completeness: Does it cover all necessary aspects? (score 0-10)
        5. Potential Issues: What problems might arise from this prompt?
        
        Provide your response in JSON format:
        {{
            "clarity_score": <number>,
            "specificity_score": <number>,
            "structure_score": <number>,
            "completeness_score": <number>,
            "overall_score": <average of all scores>,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "potential_issues": ["issue1", "issue2"]
        }}
        """
        
        response = self.llm.generate(analysis_prompt, max_tokens=600)
        
        try:
            # Parse JSON response
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            # Fallback analysis
            return {
                "clarity_score": 5,
                "specificity_score": 5,
                "structure_score": 5,
                "completeness_score": 5,
                "overall_score": 5,
                "strengths": ["Unable to parse analysis"],
                "weaknesses": ["Analysis failed"],
                "potential_issues": ["JSON parsing error"]
            }
    
    def generate_improvements(self, prompt: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate improved versions of the prompt"""
        
        improvement_prompt = f"""
        Given this prompt and its analysis, create 3 improved versions:
        
        ORIGINAL PROMPT: {prompt}
        
        ANALYSIS:
        - Clarity Score: {analysis.get('clarity_score', 'N/A')}/10
        - Specificity Score: {analysis.get('specificity_score', 'N/A')}/10
        - Structure Score: {analysis.get('structure_score', 'N/A')}/10
        - Completeness Score: {analysis.get('completeness_score', 'N/A')}/10
        - Weaknesses: {', '.join(analysis.get('weaknesses', []))}
        
        Create 3 improved versions that address the weaknesses while maintaining the original intent:
        
        1. VERSION 1 (Focus on Clarity): Make the prompt clearer and more direct
        2. VERSION 2 (Focus on Specificity): Add more specific constraints and context
        3. VERSION 3 (Focus on Structure): Reorganize for better flow and comprehension
        
        Format each version clearly with labels.
        """
        
        response = self.llm.generate(improvement_prompt, max_tokens=800)
        
        # Parse the improvements
        improvements = []
        lines = response.split('\n')
        current_improvement = []
        
        for line in lines:
            if line.strip().startswith(('VERSION', '1.', '2.', '3.')):
                if current_improvement:
                    improvements.append('\n'.join(current_improvement).strip())
                current_improvement = []
            elif line.strip():
                current_improvement.append(line)
        
        if current_improvement:
            improvements.append('\n'.join(current_improvement).strip())
        
        return improvements[:3]  # Return max 3 improvements

class EnhancedPromptOptimizer(PromptOptimizer):
    """Extended optimizer with improvement suggestions"""
    
    def __init__(self, objectives: PromptObjectives, llm: GeminiLLM):
        super().__init__(objectives)
        self.llm = llm
        self.improver = PromptImprover(llm)
        
    def score_and_improve(self, prompt: str, test_cases: List[TestCase] = None) -> Dict[str, Any]:
        """Score a prompt and provide improvements"""
        
        # If no test cases provided, create generic ones
        if not test_cases:
            test_cases = self._create_generic_test_cases()
        
        # Create a PromptVariation for the original prompt
        original_variation = PromptVariation(
            name="original",
            template=prompt,
            parameters={}
        )
        
        # Test the original prompt
        print("📊 Scoring your original prompt...")
        original_results = self.test_prompt(
            original_variation, 
            test_cases, 
            lambda p: self.llm.generate(p)
        )
        
        # Analyze the prompt
        print("🔍 Analyzing prompt structure...")
        analysis = self.improver.analyze_prompt(prompt)
        
        # Generate improvements
        print("💡 Generating improvements...")
        improvements = self.improver.generate_improvements(prompt, analysis)
        
        # Test improved versions
        improved_results = []
        for i, improved_prompt in enumerate(improvements):
            if improved_prompt:
                variation = PromptVariation(
                    name=f"improved_v{i+1}",
                    template=improved_prompt,
                    parameters={}
                )
                result = self.test_prompt(
                    variation,
                    test_cases,
                    lambda p: self.llm.generate(p)
                )
                improved_results.append({
                    "version": f"Version {i+1}",
                    "prompt": improved_prompt,
                    "scores": result["aggregate_scores"],
                    "weighted_score": result["weighted_score"]
                })
        
        return {
            "original_prompt": prompt,
            "original_scores": original_results["aggregate_scores"],
            "original_weighted_score": original_results["weighted_score"],
            "analysis": analysis,
            "improvements": improved_results,
            "recommendations": self._generate_recommendations(
                original_results["aggregate_scores"], 
                analysis
            )
        }
    
    def _create_generic_test_cases(self) -> List[TestCase]:
        """Create generic test cases for prompt evaluation"""
        return [
            TestCase("What is the capital of France?"),
            TestCase("Explain quantum computing simply"),
            TestCase("Write a haiku about spring"),
            TestCase("List 3 benefits of exercise"),
            TestCase("How do I make coffee?")
        ]
    
    def _generate_recommendations(self, scores: Dict[str, float], 
                                 analysis: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on scores"""
        recommendations = []
        
        # Check each metric
        if scores.get("brevity", 1) < 0.7:
            recommendations.append("📝 Consider adding length constraints to your prompt")
            
        if scores.get("accuracy", 1) < 0.8:
            recommendations.append("🎯 Add more specific context or examples to improve accuracy")
            
        if scores.get("style_match", 1) < 0.7:
            recommendations.append("✨ Specify the desired tone, style, or format more clearly")
            
        # Check analysis scores
        if analysis.get("clarity_score", 10) < 7:
            recommendations.append("🔍 Simplify language and avoid ambiguous terms")
            
        if analysis.get("specificity_score", 10) < 7:
            recommendations.append("📋 Add more specific requirements or constraints")
            
        if analysis.get("structure_score", 10) < 7:
            recommendations.append("🏗️ Reorganize prompt with clear sections or bullet points")
            
        return recommendations

# Main execution function
def optimize_your_prompt(prompt: str):
    """Main function to score and improve a prompt"""
    
    print("🚀 Prompt Optimization Tool")
    print("=" * 50)
    
    # Initialize Gemini
    llm = GeminiLLM(temperature=0.7)
    
    # Create objectives
    objectives = PromptObjectives()
    
    # Add objectives with appropriate weights
    objectives.add_objective(OptimizationObjective(
        "clarity", "Clear and unambiguous instructions",
        ObjectivePriority.MUST_HAVE, weight=2.0, target_value=0.9
    ))
    
    objectives.add_objective(OptimizationObjective(
        "brevity", "Concise yet complete",
        ObjectivePriority.SHOULD_HAVE, weight=1.5, target_value=150
    ))
    
    objectives.add_objective(OptimizationObjective(
        "specificity", "Specific requirements and constraints",
        ObjectivePriority.SHOULD_HAVE, weight=1.5, target_value=0.85
    ))
    
    objectives.add_objective(OptimizationObjective(
        "effectiveness", "Gets desired results",
        ObjectivePriority.MUST_HAVE, weight=2.0, target_value=0.9
    ))
    
    # Initialize optimizer
    optimizer = EnhancedPromptOptimizer(objectives, llm)
    
    # Add evaluators
    optimizer.add_evaluator("accuracy", AccuracyEvaluator())
    optimizer.add_evaluator("brevity", BrevityEvaluator(target_length=150))
    optimizer.add_evaluator("style_match", StyleEvaluator())
    
    # Score and improve
    results = optimizer.score_and_improve(prompt)
    
    # Display results
    print(f"\n📊 Original Prompt Score: {results['original_weighted_score']:.2f}")
    print("\nDetailed Scores:")
    for metric, score in results['original_scores'].items():
        print(f"  • {metric}: {score:.2f}")
    
    print(f"\n🔍 Analysis:")
    print(f"  • Overall Score: {results['analysis'].get('overall_score', 'N/A')}/10")
    print(f"  • Strengths: {', '.join(results['analysis'].get('strengths', []))}")
    print(f"  • Weaknesses: {', '.join(results['analysis'].get('weaknesses', []))}")
    
    print("\n💡 Recommendations:")
    for rec in results['recommendations']:
        print(f"  {rec}")
    
    print("\n🎯 Improved Versions:")
    for i, improvement in enumerate(results['improvements']):
        print(f"\n--- Version {i+1} (Score: {improvement['weighted_score']:.2f}) ---")
        print(improvement['prompt'])
        
    # Save results
    with open("prompt_optimization_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n💾 Results saved to prompt_optimization_results.json")
    
    return results

# Interactive mode
def interactive_mode():
    """Run in interactive mode"""
    print("🤖 Interactive Prompt Optimizer")
    print("Type 'quit' to exit\n")
    
    while True:
        prompt = input("\nEnter your prompt (or 'quit' to exit):\n> ")
        
        if prompt.lower() == 'quit':
            break
            
        if prompt.strip():
            optimize_your_prompt(prompt)
        else:
            print("Please enter a valid prompt.")

if __name__ == "__main__":
    # Example usage
    example_prompt = """
    Write a blog post about artificial intelligence
    """
    
    # You can either run with a specific prompt
    # optimize_your_prompt(example_prompt)
    
    # Or run in interactive mode
    interactive_mode()