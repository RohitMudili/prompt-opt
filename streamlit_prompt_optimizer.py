# streamlit_prompt_optimizer.py

import streamlit as st
import os
import json
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Prompt Optimizer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'gemini_configured' not in st.session_state:
    st.session_state.gemini_configured = False

class GeminiAnalyzer:
    """Gemini-based prompt analyzer and optimizer"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        try:
            self.model = genai.GenerativeModel(model_name)
            # Test the model
            self.model.generate_content("test")
        except Exception as e:
            st.error(f"Failed to initialize model {model_name}: {str(e)}")
            st.info("Available models: gemini-1.5-flash, gemini-1.5-pro")
            raise e
        
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt and return scores"""
        
        analysis_prompt = f"""
        Analyze this prompt and score it on multiple dimensions. Be critical and honest.
        
        PROMPT: "{prompt}"
        
        Score each dimension from 0-10 and provide specific feedback:
        
        1. Clarity: Is the instruction clear and unambiguous?
        2. Specificity: Does it provide enough context and constraints?
        3. Structure: Is it well-organized with logical flow?
        4. Completeness: Does it cover all necessary aspects?
        5. Effectiveness: Will it likely produce the desired output?
        
        Also identify:
        - Key strengths (2-3 points)
        - Main weaknesses (2-3 points)
        - Missing elements
        
        Respond in this exact JSON format:
        {{
            "clarity": <score>,
            "specificity": <score>,
            "structure": <score>,
            "completeness": <score>,
            "effectiveness": <score>,
            "overall_score": <average of all scores>,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "missing_elements": ["element1", "element2"],
            "one_line_summary": "Brief assessment of the prompt"
        }}
        """
        
        try:
            response = self.model.generate_content(analysis_prompt)
            # Clean the response text
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            analysis = json.loads(response_text)
            return analysis
        except json.JSONDecodeError as e:
            st.warning(f"Failed to parse JSON response: {str(e)}")
            return self._get_default_analysis("JSON parsing failed")
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return self._get_default_analysis(str(e))
    
    def _get_default_analysis(self, error_msg: str) -> Dict[str, Any]:
        """Return default analysis when actual analysis fails"""
        return {
            "clarity": 5,
            "specificity": 5,
            "structure": 5,
            "completeness": 5,
            "effectiveness": 5,
            "overall_score": 5,
            "strengths": ["Could not analyze"],
            "weaknesses": ["Analysis failed"],
            "missing_elements": [],
            "one_line_summary": f"Error: {error_msg}"
        }
    
    def optimize_prompt(self, prompt: str, analysis: Dict[str, Any], 
                       optimization_focus: str = "balanced") -> str:
        """Generate optimized version of the prompt"""
        
        optimization_prompt = f"""
        Improve this prompt based on the analysis provided.
        
        ORIGINAL PROMPT: "{prompt}"
        
        ANALYSIS:
        - Clarity: {analysis['clarity']}/10
        - Specificity: {analysis['specificity']}/10
        - Structure: {analysis['structure']}/10
        - Completeness: {analysis['completeness']}/10
        - Effectiveness: {analysis['effectiveness']}/10
        - Weaknesses: {', '.join(analysis['weaknesses'])}
        - Missing elements: {', '.join(analysis.get('missing_elements', []))}
        
        OPTIMIZATION FOCUS: {optimization_focus}
        
        Create an improved version that:
        1. Addresses all weaknesses
        2. Adds missing elements
        3. Maintains the original intent
        4. {"Maximizes " + optimization_focus if optimization_focus != "balanced" else "Balances all aspects"}
        
        Return ONLY the improved prompt, nothing else.
        """
        
        try:
            response = self.model.generate_content(optimization_prompt)
            return response.text.strip()
        except Exception as e:
            st.error(f"Optimization error: {str(e)}")
            return prompt  # Return original if optimization fails

def create_score_chart(scores: Dict[str, float]) -> go.Figure:
    """Create radar chart for scores"""
    
    categories = ['Clarity', 'Specificity', 'Structure', 'Completeness', 'Effectiveness']
    values = [scores.get(cat.lower(), 0) for cat in categories]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Scores'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        height=400
    )
    
    return fig

def create_history_chart(history: List[Dict]) -> go.Figure:
    """Create line chart showing score progression"""
    
    if not history:
        return go.Figure()
    
    df = pd.DataFrame([
        {
            'iteration': i + 1,
            'overall_score': h['analysis']['overall_score'],
            'prompt_preview': h['prompt'][:50] + '...' if len(h['prompt']) > 50 else h['prompt']
        }
        for i, h in enumerate(history)
    ])
    
    fig = px.line(df, x='iteration', y='overall_score', 
                  hover_data=['prompt_preview'],
                  markers=True)
    
    fig.update_layout(
        title='Score Progression',
        xaxis_title='Iteration',
        yaxis_title='Overall Score',
        yaxis=dict(range=[0, 10]),
        height=300
    )
    
    return fig

def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎯 Prompt Optimizer Pro")
        st.markdown("*Transform your prompts into precision instruments*")
    with col2:
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.history = []
            st.session_state.current_analysis = None
            st.rerun()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Gemini API Key",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            help="Get your API key from https://makersuite.google.com/app/apikey"
        )
        
        # Model selection
        model_name = st.selectbox(
            "Select Model",
            ["gemini-1.5-flash", "gemini-1.5-pro"],
            help="Choose the Gemini model to use"
        )
        
        if api_key:
            try:
                st.session_state.gemini_configured = True
                analyzer = GeminiAnalyzer(api_key, model_name)
                st.success(f"✅ Connected to {model_name}")
            except Exception as e:
                st.session_state.gemini_configured = False
                st.error("Failed to connect to Gemini API")
                st.stop()
        else:
            st.error("Please enter your Gemini API key")
            st.stop()
        
        st.divider()
        
        # Optimization settings
        st.subheader("🎨 Optimization Focus")
        optimization_focus = st.selectbox(
            "Choose optimization priority",
            ["balanced", "clarity", "specificity", "structure", "completeness", "effectiveness"],
            help="Select which aspect to prioritize in optimization"
        )
        
        auto_optimize = st.checkbox(
            "Auto-optimize after analysis",
            value=True,
            help="Automatically generate optimized version"
        )
        
        st.divider()
        
        # History
        st.subheader("📊 History")
        if st.session_state.history:
            st.metric("Total Optimizations", len(st.session_state.history))
            avg_improvement = sum(h['analysis']['overall_score'] for h in st.session_state.history) / len(st.session_state.history)
            st.metric("Average Score", f"{avg_improvement:.1f}/10")
        else:
            st.info("No optimization history yet")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["✍️ Optimize", "📈 Analysis", "📜 History"])
    
    with tab1:
        # Input section
        st.subheader("Enter Your Prompt")
        
        # Check if we need to load a prompt from history
        if hasattr(st.session_state, 'load_prompt'):
            default_prompt = st.session_state.load_prompt
            del st.session_state.load_prompt
        else:
            default_prompt = ""
        
        prompt_input = st.text_area(
            "Prompt to optimize",
            height=150,
            value=default_prompt,
            placeholder="Enter your prompt here... (e.g., 'Write a blog post about AI')",
            help="The more detailed your prompt, the better the analysis"
        )
        
        col1, col2, col3 = st.columns([2, 2, 6])
        with col1:
            analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
        with col2:
            if st.session_state.current_analysis:
                optimize_button = st.button("🚀 Optimize", type="secondary", use_container_width=True)
            else:
                optimize_button = False
        
        # Analysis section
        if analyze_button and prompt_input:
            with st.spinner("🧠 Analyzing your prompt..."):
                try:
                    analysis = analyzer.analyze_prompt(prompt_input)
                    st.session_state.current_analysis = {
                        'prompt': prompt_input,
                        'analysis': analysis,
                        'timestamp': datetime.now()
                    }
                    
                    # Add to history
                    st.session_state.history.append(st.session_state.current_analysis)
                    
                    # Auto-optimize if enabled
                    if auto_optimize:
                        time.sleep(0.5)  # Brief pause for UX
                        optimized = analyzer.optimize_prompt(prompt_input, analysis, optimization_focus)
                        st.session_state.current_analysis['optimized'] = optimized
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
        
        # Display current analysis
        if st.session_state.current_analysis:
            analysis = st.session_state.current_analysis['analysis']
            
            # Score summary
            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Overall score with color coding
                score = analysis['overall_score']
                if score >= 8:
                    color = "green"
                    emoji = "🌟"
                elif score >= 6:
                    color = "orange"
                    emoji = "⭐"
                else:
                    color = "red"
                    emoji = "💫"
                
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: rgba(0,0,0,0.05); border-radius: 10px;'>
                    <h1 style='color: {color}; margin: 0;'>{emoji} {score:.1f}/10</h1>
                    <p style='margin: 0;'>Overall Score</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Summary:** {analysis['one_line_summary']}")
            
            with col2:
                # Radar chart
                fig = create_score_chart(analysis)
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed scores
            st.subheader("📊 Detailed Scores")
            cols = st.columns(5)
            metrics = ['clarity', 'specificity', 'structure', 'completeness', 'effectiveness']
            emojis = ['🔍', '🎯', '🏗️', '✅', '⚡']
            
            for col, metric, emoji in zip(cols, metrics, emojis):
                with col:
                    score = analysis[metric]
                    delta = score - 5  # Comparing to average
                    col.metric(
                        f"{emoji} {metric.title()}",
                        f"{score}/10",
                        f"{delta:+.0f}",
                        delta_color="normal" if delta >= 0 else "inverse"
                    )
            
            # Strengths and weaknesses
            col1, col2 = st.columns(2)
            
            with col1:
                st.success("**💪 Strengths**")
                for strength in analysis['strengths']:
                    st.write(f"• {strength}")
            
            with col2:
                st.error("**🔧 Areas for Improvement**")
                for weakness in analysis['weaknesses']:
                    st.write(f"• {weakness}")
            
            # Missing elements
            if analysis.get('missing_elements') and len(analysis['missing_elements']) > 0:
                st.warning("**📝 Missing Elements**")
                for element in analysis['missing_elements']:
                    if element:  # Check if element is not empty
                        st.write(f"• {element}")
            
            # Optimized prompt
            if optimize_button or 'optimized' in st.session_state.current_analysis:
                if optimize_button:
                    with st.spinner("🚀 Generating optimized prompt..."):
                        try:
                            optimized = analyzer.optimize_prompt(
                                st.session_state.current_analysis['prompt'],
                                analysis,
                                optimization_focus
                            )
                            st.session_state.current_analysis['optimized'] = optimized
                        except Exception as e:
                            st.error(f"Optimization failed: {str(e)}")
                
                if 'optimized' in st.session_state.current_analysis:
                    st.divider()
                    st.subheader("✨ Optimized Prompt")
                    
                    # Show before/after
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Original:**")
                        st.text_area("", st.session_state.current_analysis['prompt'], 
                                   height=200, disabled=True, key="original_display")
                    
                    with col2:
                        st.markdown("**Optimized:**")
                        optimized_text = st.text_area("", 
                                                    st.session_state.current_analysis.get('optimized', ''),
                                                    height=200, key="optimized_display")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("📋 Copy", use_container_width=True):
                                st.code(optimized_text, language=None)
                        with col_b:
                            if st.button("🔄 Re-analyze", use_container_width=True, type="primary"):
                                st.session_state.load_prompt = optimized_text
                                st.rerun()
    
    with tab2:
        st.subheader("📈 Performance Analytics")
        
        if st.session_state.history:
            # Score progression
            fig = create_history_chart(st.session_state.history)
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            scores = [h['analysis']['overall_score'] for h in st.session_state.history]
            
            with col1:
                st.metric("Best Score", f"{max(scores):.1f}/10")
            with col2:
                st.metric("Average Score", f"{sum(scores)/len(scores):.1f}/10")
            with col3:
                st.metric("Total Prompts", len(scores))
            with col4:
                improvement = scores[-1] - scores[0] if len(scores) > 1 else 0
                st.metric("Net Improvement", f"{improvement:+.1f}", 
                         delta_color="normal" if improvement >= 0 else "inverse")
            
            # Category breakdown
            st.subheader("📊 Category Performance")
            
            category_data = []
            for metric in ['clarity', 'specificity', 'structure', 'completeness', 'effectiveness']:
                metric_scores = [h['analysis'][metric] for h in st.session_state.history]
                category_data.append({
                    'Category': metric.title(),
                    'Average Score': sum(metric_scores) / len(metric_scores),
                    'Best Score': max(metric_scores),
                    'Worst Score': min(metric_scores)
                })
            
            df = pd.DataFrame(category_data)
            
            fig = px.bar(df, x='Category', y=['Average Score', 'Best Score', 'Worst Score'],
                        barmode='group', height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No analysis data yet. Start by optimizing a prompt!")
    
    with tab3:
        st.subheader("📜 Optimization History")
        
        if st.session_state.history:
            # Filter and sort options
            col1, col2 = st.columns([2, 1])
            with col1:
                search = st.text_input("🔍 Search prompts", placeholder="Filter by prompt content...")
            with col2:
                sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Highest Score", "Lowest Score"])
            
            # Filter history
            filtered_history = st.session_state.history
            if search:
                filtered_history = [h for h in filtered_history if search.lower() in h['prompt'].lower()]
            
            # Sort history
            if sort_by == "Newest First":
                filtered_history = filtered_history[::-1]
            elif sort_by == "Highest Score":
                filtered_history = sorted(filtered_history, key=lambda x: x['analysis']['overall_score'], reverse=True)
            elif sort_by == "Lowest Score":
                filtered_history = sorted(filtered_history, key=lambda x: x['analysis']['overall_score'])
            
            # Display history
            for i, item in enumerate(filtered_history):
                with st.expander(
                    f"📝 {item['prompt'][:60]}... | "
                    f"Score: {item['analysis']['overall_score']:.1f}/10 | "
                    f"{item['timestamp'].strftime('%Y-%m-%d %H:%M')}"
                ):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown("**Original Prompt:**")
                        st.text(item['prompt'])
                        
                        if 'optimized' in item:
                            st.markdown("**Optimized Version:**")
                            st.text(item['optimized'])
                    
                    with col2:
                        st.markdown("**Scores:**")
                        for metric in ['clarity', 'specificity', 'structure', 'completeness', 'effectiveness']:
                            st.write(f"{metric.title()}: {item['analysis'][metric]}/10")
                        
                        if st.button(f"🔄 Use This", key=f"use_{i}"):
                            st.session_state.load_prompt = item.get('optimized', item['prompt'])
                            st.rerun()
            
            # Export options
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Export History (JSON)", use_container_width=True):
                    json_str = json.dumps(st.session_state.history, indent=2, default=str)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"prompt_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("📊 Export Analytics (CSV)", use_container_width=True):
                    # Create DataFrame for export
                    export_data = []
                    for item in st.session_state.history:
                        row = {
                            'timestamp': item['timestamp'],
                            'prompt': item['prompt'],
                            'overall_score': item['analysis']['overall_score'],
                            **{k: v for k, v in item['analysis'].items() if k in ['clarity', 'specificity', 'structure', 'completeness', 'effectiveness']}
                        }
                        export_data.append(row)
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"prompt_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("No history yet. Start optimizing prompts to build your history!")

if __name__ == "__main__":
    main()