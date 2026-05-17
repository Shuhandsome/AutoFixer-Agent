import os
import time
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import track

# Load environment variables
load_dotenv()

console = Console()

class AIAgent:
    """Generic AI Agent Base Class"""
    def __init__(self, name: str, role_prompt: str, model: str, client: OpenAI):
        self.name = name
        self.role_prompt = role_prompt
        self.model = model
        self.client = client

    def chat(self, user_input: str, history: List[Dict] = None) -> str:
        messages = [{"role": "system", "content": self.role_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[{self.name}] API Call Failed: {str(e)}"

class AutoFixerWorkflow:
    """AutoFixer Multi-Agent Collaboration Workflow Manager"""
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("MODEL_NAME", "gpt-4o")

        if not api_key:
            console.print("[bold red]❌ Error: OPENAI_API_KEY not detected, system will switch to Mock Demo Mode.[/bold red]")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

        self.analyzer_prompt = (
            "You are a top-tier backend troubleshooting expert. Use Chain-of-Thought reasoning to deeply analyze the Bug logs.\n"
            "Output a detailed 'Root Cause Analysis Report', including: 1. Root Cause 2. Core Vulnerability Point 3. Repair Plan Guidance."
        )
        
        self.developer_prompt = (
            "You are a senior developer. Based on the 'Root Cause Analysis Report', write perfect Patch Code and at least one Unit Test.\n"
            "Please only output standard Markdown code blocks."
        )
        
        self.reviewer_prompt = (
            "You are an extremely strict Code Reviewer. Review the patch and unit tests submitted by the developer.\n"
            "Review from three dimensions: 1. Security 2. Performance & Standards 3. Test Coverage\n"
            "If the review passes, explicitly write: [Review Passed] on the first line.\n"
            "If you find any flaws, write: [Rejected for Rewrite] on the first line, and detail the revision suggestions."
        )

    def run_workflow(self, issue_context: str, max_retries: int = 3):
        console.print(Panel.fit("[bold green]🚀 AutoFixer Agent System Initialized[/bold green]", border_style="green"))
        
        if not self.client:
            self._run_mock_demo()
            return

        analyzer = AIAgent("Analyzer Agent", self.analyzer_prompt, self.model, self.client)
        developer = AIAgent("Developer Agent", self.developer_prompt, self.model, self.client)
        reviewer = AIAgent("Reviewer Agent", self.reviewer_prompt, self.model, self.client)

        self._show_progress("Analyzer Agent is conducting root cause analysis...")
        analysis_report = analyzer.chat(issue_context)
        console.print(Panel(Markdown(analysis_report), title="🕵️‍♂️ Analyzer Agent: Root Cause", border_style="blue"))

        dev_history = [{"role": "user", "content": f"Issue:\n{issue_context}\n\nAnalysis:\n{analysis_report}"}]
        
        current_retry = 0
        while current_retry < max_retries:
            current_retry += 1
            self._show_progress(f"Developer Agent is writing patch code (Round {current_retry})...")
            
            fix_suggestion = developer.chat("Please provide patch code and unit tests.", history=dev_history)
            console.print(Panel(Markdown(fix_suggestion), title=f"💻 Developer Agent (Round {current_retry})", border_style="magenta"))

            self._show_progress(f"Reviewer Agent is executing quality review...")
            review_result = reviewer.chat(f"Please review the following code:\n{fix_suggestion}")
            console.print(Panel(Markdown(review_result), title=f"🧑‍🏫 Reviewer Agent (Round {current_retry})", border_style="yellow"))

            if "Review Passed" in review_result.split('\n')[0] or "[Review Passed]" in review_result:
                console.print("\n[bold green]🎉 [Success] Code passed review, automatically merged! Workflow closed.[/bold green]")
                break
            else:
                console.print(f"\n[bold red]❌ [Rejected] Architect triggered Reflection mechanism, rejected for rewrite.[/bold red]")
                dev_history.append({"role": "assistant", "content": fix_suggestion})
                dev_history.append({"role": "user", "content": f"Code rejected. Feedback:\n{review_result}\nPlease fix."})
        else:
            console.print(f"\n[bold yellow]⚠️ [Warning] Max iterations reached. Manual intervention required.[/bold yellow]")

    def _show_progress(self, text: str):
        console.print(f"\n[bold cyan]⚡ {text}[/bold cyan]")
        for _ in track(range(50), description="Thinking..."):
            time.sleep(0.02)

    def _run_mock_demo(self):
        self._show_progress("Analyzer Agent is conducting root cause analysis...")
        report = "**1. Fault Point**: `OrderService.java` Line 89\n**2. Root Cause**: No idempotent interception for preventing duplicates during high concurrency.\n**3. Recommendation**: Introduce Redis distributed locks."
        console.print(Panel(Markdown(report), title="🕵️‍♂️ Analyzer Agent (Mock)", border_style="blue"))
        
        self._show_progress("Developer Agent is writing patch code and test cases...")
        code = "
http://googleusercontent.com/immersive_entry_chip/0
