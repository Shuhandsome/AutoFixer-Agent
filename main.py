import os
import time
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import track

# Load environment configurations
load_dotenv()
console = Console()

class AIAgent:
    """Generic multi-agent base class"""
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
                model=self.model, messages=messages, temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[{self.name}] API Call Failed: {str(e)}"

class AutoFixerWorkflow:
    """Automated code fixing workflow manager"""
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("MODEL_NAME", "gpt-4o")
        self.client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None
        
        if not self.client:
            console.print("[bold red]❌ OPENAI_API_KEY not detected. Switching to Mock Demo Mode.[/bold red]")

        self.analyzer_prompt = "You are a backend expert. Analyze logs, output Root Cause Report."
        self.developer_prompt = "You are a developer. Write Patch Code and Unit Test."
        self.reviewer_prompt = "You are a Reviewer. Start with [Review Passed] or [Rejected for Rewrite]."

    def run_workflow(self, issue_context: str, max_retries: int = 3):
        console.print(Panel.fit("[bold green]🚀 AutoFixer System Initialized[/bold green]"))
        if not self.client:
            self._run_mock_demo()
            return

        analyzer = AIAgent("Analyzer", self.analyzer_prompt, self.model, self.client)
        developer = AIAgent("Developer", self.developer_prompt, self.model, self.client)
        reviewer = AIAgent("Reviewer", self.reviewer_prompt, self.model, self.client)

        self._show_progress("Analyzer Agent is analyzing the root cause...")
        analysis = analyzer.chat(issue_context)
        console.print(Panel(Markdown(analysis), title="🕵️‍♂️ Analyzer Agent", border_style="blue"))

        dev_history = [{"role": "user", "content": f"Issue:\n{issue_context}\n\nAnalysis:\n{analysis}"}]
        
        for i in range(max_retries):
            self._show_progress(f"Developer Agent is writing patch code (Round {i+1})...")
            code = developer.chat("Provide code.", history=dev_history)
            console.print(Panel(Markdown(code), title=f"💻 Developer (Round {i+1})", border_style="magenta"))

            self._show_progress("Reviewer Agent is performing multi-dimensional review...")
            review = reviewer.chat(f"Review this:\n{code}")
            console.print(Panel(Markdown(review), title=f"🧑‍🏫 Reviewer (Round {i+1})", border_style="yellow"))

            if "Review Passed" in review:
                console.print("\n[bold green]🎉 [Success] Code approved! Automatically merged.[/bold green]")
                break
            else:
                console.print("\n[bold red]❌ [Rejected] Code rejected! Triggering rewrite...[/bold red]")
                dev_history.extend([
                    {"role": "assistant", "content": code},
                    {"role": "user", "content": f"Feedback:\n{review}\nPlease fix."}
                ])
        else:
            console.print("\n[bold yellow]⚠️ [Warning] Maximum iterations reached.[/bold yellow]")

    def _show_progress(self, text: str):
        console.print(f"\n[bold cyan]⚡ {text}[/bold cyan]")
        for _ in track(range(20), description="Thinking..."): time.sleep(0.02)

    def _run_mock_demo(self):
        self._show_progress("Analyzer Agent is working...")
        console.print(Panel(Markdown("**Root Cause**: Null pointer exception at OrderService."), title="🕵️‍♂️ Analyzer (Mock)", border_style="blue"))
        
        self._show_progress("Developer Agent is writing code...")
        
        # Uses standard ASCII characters to safely print backticks in mock terminal
        ticks = chr(96) * 3
        code_mock = f"{ticks}python\ndef fix_order():\n    return 'Issue Fixed Successfully'\n{ticks}"
        console.print(Panel(Markdown(code_mock), title="💻 Developer (Mock)", border_style="magenta"))
        
        self._show_progress("Reviewer Agent is checking...")
        console.print(Panel(Markdown("[Review Passed] Code looks secure and clean."), title="🧑‍🏫 Reviewer (Mock)", border_style="yellow"))
        console.print("\n[bold green]🎉 [Demo Success] Workflow closed successfully![/bold green]")

if __name__ == "__main__":
    sample_issue = "NullPointerException at OrderService.java:89"
    console.print(Panel(sample_issue, title="📥 Received new Issue ticket", border_style="red"))
    workflow = AutoFixerWorkflow()
    workflow.run_workflow(sample_issue)
