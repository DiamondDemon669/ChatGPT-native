import tkinter as tk
import customtkinter as ctk
from revChatGPT.ChatGPT import Chatbot
from PIL import Image
from threading import Thread
import json, os, sys

class app(ctk.CTk):
    def __init__(self, cb):
        super().__init__()
        self.title("ChatGPT")
        self.minsize(800, 500)
        self.iconphoto(True, tk.PhotoImage(file="./assets/favicon.png"))
        self.cb = cb
        self.frame_menu = app_frame(self, width=200, height=500)
        self.frame_menu.grid(row=0, column=0, sticky="ne")
        self.favicon = ctk.CTkImage(light_image=Image.open("./assets/favicon.ico"), dark_image=Image.open("./assets/favicon.ico"), size=(25, 25))
        self.image_box = ctk.CTkLabel(self, text="", image=self.favicon)
        self.image_box.grid(row=0, column=1, sticky="se", padx=5, pady=5)
        self.entry_var = tk.StringVar()
        self.entry_box = ctk.CTkEntry(self, placeholder_text="Put your message here", textvariable=self.entry_var, width=625, height=25)
        self.entry_box.grid(row=0, column=2, sticky="se", padx=5, pady=5)
        self.entry_box.bind("<Return>", self.send_message)
        self.text_box = ctk.CTkTextbox(self, height=460, width=650)
        self.text_box.grid(row=0, column=1, sticky="nw", padx=5, pady=5, columnspan=2)
        self.text_box.configure(state="disabled")
        self.text_box.tag_config("tag-right", justify="right")
    def send_message(self, event):
        def real_func(self):
            msg = self.entry_var.get()
            self.entry_box.delete(0, tk.END)
            self.text_box.configure(state="normal")
            self.text_box.insert("end", "You:\n" + msg + '\n', "tag-right")
            try:
                message = self.cb.ask(msg, conversation_id=self.cb.config.get("conversation"))
            except Exception as exc:
                print(exc, message)
            self.text_box.insert("end", "ChatGPT:\n" + message["message"] + '\n')
            self.text_box.yview(tk.END)
            self.text_box.configure(state="disabled")
        t = Thread(target=real_func, args=(self,))
        t.start()
    def load_msg_history(self, id):
        cb = self.cb
        history = cb.get_msg_history(id)["mapping"]
        self.text_box.configure(state="normal")
        self.text_box.delete(1.0, tk.END)
        for x, y in history.items():
            if y["message"] == None:
                continue
            message = y["message"]["content"]["parts"][0]
            role = y["message"]["role"]
            if role == "user":
                self.text_box.insert("insert", "You:\n" + message + '\n', "tag-right")
            if role == "assistant":
                self.text_box.insert("insert", "ChatGPT:\n" + message + '\n')
        self.frame_menu.load_conversations()
        self.text_box.yview(tk.END)
        self.text_box.configure(state="disabled")

class app_frame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_propagate(0)
        self.menu_buttons = []
        self.exit_image = ctk.CTkImage(light_image=Image.open("./assets/exit.ico"), dark_image=Image.open("./assets/exit.ico"))
        self.exit_button = ctk.CTkButton(self, text="Exit", image=self.exit_image, width=180, height=40, command=self.master.destroy)
        self.exit_button.grid(row=0, column=0, sticky="sw", padx=10, pady=10)
        self.menu_buttons.append(self.exit_button)
        self.load_conversations()
    def load_conversations(self):
        convs = self.master.cb.get_conversations()
        self.convs = convs
        self.conv_buttons = []
        menu_buttons = self.menu_buttons
        chat_image = ctk.CTkImage(light_image=Image.open("./assets/chat.ico"), dark_image=Image.open("./assets/chat.ico"))
        for x in self.children:
            if x in menu_buttons:
                x.grid_forget()
                x.destroy()
        for x in convs:
            newcommand = (lambda self=self, cb=self.master.cb, x=x:
                (
                     cb.config.__setitem__("conversation", x.get("id")),
                     self.master.load_msg_history(x.get("id"))
                )
            )
            newbutton = ctk.CTkButton(self, text=x.get("title"), image=chat_image, width=180, height=40, command=newcommand)
            if len(self.conv_buttons) > 0:
                newbutton.grid(row=self.conv_buttons[-1].grid_info()["row"] + 1, column=0, sticky="nw", padx=10, pady=5)
            else:
                newbutton.grid(row=0, column=0, sticky="nw", padx=10, pady=5)
            self.conv_buttons.append(newbutton)
        for x in menu_buttons:
            if x.grid_info() == {}:
                continue
            row = x.grid_info()["row"]
            x.grid_forget()
            self.rowconfigure(row + len(self.conv_buttons), weight=1)
            x.grid(row=row + len(self.conv_buttons), column=0, sticky="s", padx=10, pady=10)

config = json.load(open("./config.json"))
cb = Chatbot(config)
w = app(cb)
w.mainloop()
