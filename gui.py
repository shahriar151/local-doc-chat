"""
Tkinter GUI for Local Document Chat
Simple, clean interface for chatting with documents
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from datetime import datetime

class ChatGUI:
    """Simple Tkinter chat interface"""
    
    def __init__(self, rag_engine, on_index_callback):
        self.rag_engine = rag_engine
        self.on_index_callback = on_index_callback
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Local Document Chat")
        self.root.geometry("800x600")
        
        # Configure colors
        self.bg_color = "#1e1e1e"
        self.chat_bg = "#2d2d2d"
        self.user_color = "#4a9eff"
        self.bot_color = "#9b9b9b"
        self.button_color = "#0d7377"
        
        self._setup_ui()
        
        # Flag for processing state
        self.is_processing = False
    
    def _setup_ui(self):
        """Setup all UI components"""
        self.root.configure(bg=self.bg_color)
        
        # Header
        header = tk.Frame(self.root, bg=self.bg_color)
        header.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        title = tk.Label(
            header,
            text="📄 Local Document Chat",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg="white"
        )
        title.pack(side=tk.LEFT)
        
        # Index button
        self.index_btn = tk.Button(
            header,
            text="🔄 Re-Index Documents",
            command=self._on_index_click,
            bg=self.button_color,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=10
        )
        self.index_btn.pack(side=tk.RIGHT)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg=self.chat_bg,
            fg="white",
            font=("Arial", 11),
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=(0, 10)
        )
        
        # Input area
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        
        self.input_field = tk.Entry(
            input_frame,
            bg="#3d3d3d",
            fg="white",
            font=("Arial", 11),
            relief=tk.FLAT,
            insertbackground="white"
        )
        self.input_field.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            ipady=8,
            padx=(0, 10)
        )
        self.input_field.bind("<Return>", lambda e: self._on_send())
        
        self.send_btn = tk.Button(
            input_frame,
            text="Send ➤",
            command=self._on_send,
            bg=self.button_color,
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            padx=20
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Welcome message
        self._add_system_message(
            "Welcome to Local Document Chat!\n"
            "• Add PDF, DOCX, TXT, or XLSX files to 'watched_folder/'\n"
            "• Click 'Re-Index Documents' to process new files\n"
            "• Ask questions about your documents\n"
            "• Everything runs offline on your machine"
        )
    
    def _add_message(self, sender: str, message: str, color: str):
        """Add a message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        self.chat_display.insert(tk.END, f"\n{sender} ", ("sender",))
        self.chat_display.insert(tk.END, f"[{timestamp}]\n", ("timestamp",))
        self.chat_display.insert(tk.END, f"{message}\n", ("message",))
        
        self.chat_display.tag_config("sender", foreground=color, font=("Arial", 11, "bold"))
        self.chat_display.tag_config("timestamp", foreground="#666666", font=("Arial", 9))
        self.chat_display.tag_config("message", foreground="white")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _add_system_message(self, message: str):
        """Add a system notification"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n🤖 System\n", ("system",))
        self.chat_display.insert(tk.END, f"{message}\n", ("system_msg",))
        self.chat_display.tag_config("system", foreground="#ffaa00", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("system_msg", foreground="#cccccc")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _on_send(self):
        """Handle send button click"""
        if self.is_processing:
            return
        
        question = self.input_field.get().strip()
        if not question:
            return
        
        # Clear input
        self.input_field.delete(0, tk.END)
        
        # Display user message
        self._add_message("You", question, self.user_color)
        
        # Process in background thread
        self.is_processing = True
        self.send_btn.config(state=tk.DISABLED, text="Thinking...")
        self.input_field.config(state=tk.DISABLED)
        
        def process_query():
            try:
                response = self.rag_engine.query(question)
                
                # Display answer
                self.root.after(0, lambda: self._add_message(
                    "Assistant",
                    response['answer'],
                    self.bot_color
                ))
                
                # Display sources if available
                if response['sources']:
                    sources_text = "📎 Sources: " + ", ".join(response['sources'])
                    self.root.after(0, lambda: self._add_system_message(sources_text))
                
            except Exception as e:
                self.root.after(0, lambda: self._add_system_message(f"Error: {str(e)}"))
            finally:
                self.is_processing = False
                self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL, text="Send ➤"))
                self.root.after(0, lambda: self.input_field.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.input_field.focus())
        
        thread = threading.Thread(target=process_query)
        thread.daemon = True
        thread.start()
    
    def _on_index_click(self):
        """Handle index button click"""
        if self.is_processing:
            messagebox.showwarning("Busy", "Please wait for current operation to complete")
            return
        
        self.is_processing = True
        self.index_btn.config(state=tk.DISABLED, text="Indexing...")
        
        def index_docs():
            try:
                count = self.on_index_callback()
                self.root.after(0, lambda: self._add_system_message(
                    f"✓ Indexed {count} documents successfully!"
                ))
            except Exception as e:
                self.root.after(0, lambda: self._add_system_message(f"Indexing error: {str(e)}"))
            finally:
                self.is_processing = False
                self.root.after(0, lambda: self.index_btn.config(
                    state=tk.NORMAL,
                    text="🔄 Re-Index Documents"
                ))
        
        thread = threading.Thread(target=index_docs)
        thread.daemon = True
        thread.start()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    # Test GUI without RAG engine
    print("Testing GUI in standalone mode...")
    
    class DummyEngine:
        def query(self, q):
            return {'answer': 'Test response', 'sources': ['test.pdf']}
    
    gui = ChatGUI(DummyEngine(), lambda: 5)
    gui.run()