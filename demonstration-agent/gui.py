import threading
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk


class AgentGui:
    """Tkinter chat interface for an agent response callback."""

    def __init__(self, root: tk.Tk, get_response: Callable[[str], str]):
        self.root = root
        self.get_response = get_response
        self.root.title("Agent Interaction")
        self.root.geometry("760x560")
        self.root.minsize(520, 400)
        self._build_widgets()

    def _build_widgets(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=(16, 14, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            header, text="Agent Interaction", font=("TkDefaultFont", 16, "bold")
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header, text="Ask the agent questions about files in this project."
        ).grid(row=1, column=0, pady=(3, 0), sticky="w")

        content = ttk.Frame(self.root, padding=(16, 0, 16, 16))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        ttk.Label(content, text="Conversation").grid(row=0, column=0, sticky="w")
        response_frame = ttk.Frame(content)
        response_frame.grid(row=1, column=0, pady=(6, 12), sticky="nsew")
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)

        self.response_area = tk.Text(
            response_frame,
            wrap="word",
            state="disabled",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=8,
        )
        self.response_area.grid(row=0, column=0, sticky="nsew")
        self.response_area.tag_configure(
            "user",
            justify="right",
            foreground="#ffffff",
            background="#2563eb",
            lmargin1=180,
            lmargin2=180,
            rmargin=8,
            spacing1=8,
            spacing3=8,
        )
        self.response_area.tag_configure(
            "agent",
            justify="left",
            foreground="#111827",
            background="#e5e7eb",
            lmargin1=8,
            lmargin2=8,
            rmargin=180,
            spacing1=8,
            spacing3=8,
        )

        scrollbar = ttk.Scrollbar(
            response_frame, orient="vertical", command=self.response_area.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.response_area.configure(yscrollcommand=scrollbar.set)

        ttk.Label(content, text="Message").grid(row=2, column=0, sticky="w")
        prompt_frame = ttk.Frame(content)
        prompt_frame.grid(row=3, column=0, pady=(6, 0), sticky="ew")
        prompt_frame.columnconfigure(0, weight=1)

        self.prompt_box = tk.Text(
            prompt_frame,
            height=3,
            wrap="word",
            undo=True,
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=8,
        )
        self.prompt_box.grid(row=0, column=0, sticky="ew")
        self.prompt_box.bind("<Return>", self._send_on_enter)

        self.send_button = ttk.Button(
            prompt_frame, text="↵", width=3, command=self.send_prompt
        )
        self.send_button.grid(row=0, column=1, padx=(8, 0), sticky="ns")
        ttk.Button(prompt_frame, text="Clear", command=self.clear).grid(
            row=0, column=2, padx=(8, 0), sticky="ns"
        )

        self.status = tk.StringVar(value="Ready")
        ttk.Label(content, textvariable=self.status).grid(
            row=4, column=0, pady=(8, 0), sticky="w"
        )
        self.prompt_box.focus_set()

    def _send_on_enter(self, event: tk.Event) -> str:
        if event.state & 0x0001:  # Shift+Enter inserts a newline.
            return ""
        self.send_prompt()
        return "break"

    def send_prompt(self) -> None:
        prompt = self.prompt_box.get("1.0", "end-1c").strip()
        if not prompt:
            return

        self.send_button.configure(state="disabled")
        self.status.set("Thinking...")
        self._append_response(f"You: {prompt}\n\n", "user")
        self.prompt_box.delete("1.0", "end")
        threading.Thread(
            target=self._get_response,
            args=(prompt,),
            daemon=True,
        ).start()

    def _get_response(self, prompt: str) -> None:
        try:
            response = self.get_response(prompt)
        except Exception as error:
            response = f"Error: {error}"
        self.root.after(0, self._show_response, response)

    def _show_response(self, response: str) -> None:
        self._append_response(f"Agent: {response}\n\n", "agent")
        self.status.set("Ready")
        self.send_button.configure(state="normal")
        self.prompt_box.focus_set()

    def _append_response(self, text: str, tag: str | None = None) -> None:
        self.response_area.configure(state="normal")
        self.response_area.insert("end", text, tag)
        self.response_area.see("end")
        self.response_area.configure(state="disabled")

    def clear(self) -> None:
        self.prompt_box.delete("1.0", "end")
        self.response_area.configure(state="normal")
        self.response_area.delete("1.0", "end")
        self.response_area.configure(state="disabled")
        self.status.set("Ready")
        self.prompt_box.focus_set()


def run_gui(get_response: Callable[[str], str]) -> None:
    root = tk.Tk()
    AgentGui(root, get_response)
    root.mainloop()
