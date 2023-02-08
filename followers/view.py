
import os
import re
import threading
import tkinter as tkr
from tkinter import ttk, filedialog, END
from PIL import ImageTk, Image

from .scheduler import BotScheduler

###########################################################################################################################################################

class InstagramBot(tkr.Frame):

    def __init__(self, master: tkr.Tk, scheduler: BotScheduler):
        super().__init__(master)
        self.master = master
        self.scheduler = scheduler
        
        # self.master.iconbitmap(os.path.join(os.getcwd(), 'assets', 'insta_icon.ico'))
        img_path = Image.open(os.path.join(os.getcwd(), 'assets', 'insta_logo.png'))
        self.instagram_logo = ImageTk.PhotoImage(img_path)
    
    ###########################################################################################################################################################

    def start_bot_thread(self):
        
        self.start_btn.config(state=tkr.DISABLED)
        self.message_file_browse_btn.config(state=tkr.DISABLED)
        self.users_file_browse_btn.config(state=tkr.DISABLED)

        thread = threading.Thread(target=self.start_bot)
        thread.daemon = True
        thread.start()
        
        return thread

    ###########################################################################################################################################################

    def start_bot(self):
        # get accounts file path
        accounts_file_path = self.accounts_file_entry.get()

        # read accounts file
        workers: list[dict] = []
        
        with open(accounts_file_path) as f:
            for line in f:
                items = line.strip().split(';')
                if len(items) == 3:
                    workers.append({
                        'username': items[0],
                        'password': items[1],
                        'proxy': items[2]
                    })

        if len(workers) == 0:
        
            tkr.messagebox.showerror("Error", "No accounts found in the accounts file.")
            
            self.stop_btn.config(state=tkr.NORMAL)
            self.start_btn.config(state=tkr.NORMAL)
            self.accounts_file_browse_btn.config(state=tkr.NORMAL)
            self.message_file_browse_btn.config(state=tkr.NORMAL)

            self.accounts_file_entry.focus()
            
            return False

        # get users file path -- corrected read directly from file
        users_file_path = self.users_file_entry.get() # :::Hardcoding the file
        users: list[str] = []
        with open(users_file_path) as f:
            for line in f:
                row = line.strip()
                if row != "":
                    users.append(row)

        if len(users) == 0:
        
            tkr.messagebox.showerror("Error", "No users found in the users file.")
            
            self.stop_btn.config(state=tkr.NORMAL)
            self.start_btn.config(state=tkr.NORMAL)
            self.accounts_file_browse_btn.config(state=tkr.NORMAL)
            self.message_file_browse_btn.config(state=tkr.NORMAL)

            self.accounts_file_entry.focus()
            
            return False

        # get message file path
        message_file_path = self.message_file_entry.get()

        # read message from file
        with open(message_file_path, "r", encoding="utf8") as message_file:
            message = message_file.read()
            message = message.strip().rstrip()

        if message.__len__() == 0:
            
            tkr.messagebox.showerror("Error", "No Message Found in File.")
            
            self.stop_btn.config(state=tkr.NORMAL)
            self.start_btn.config(state=tkr.NORMAL)
            self.message_file_browse_btn.config(state=tkr.NORMAL)

            self.message_file_entry.focus()
            
            return False

        # get number of comments per post to be made by each account
        max_follows = self.max_follow_entry.get()
        
        if max_follows.__len__() == 0:
            
            tkr.messagebox.showerror("Error", "Please Enter No. of Follow to Follow People.")
            
            self.stop_btn.config(state=tkr.NORMAL)
            self.start_btn.config(state=tkr.NORMAL)
            self.message_file_browse_btn.config(state=tkr.NORMAL)

            self.max_follow_entry.focus()
            
            return False

        # no_of_users_follow_and_send_message_by_one_account
        max_follows = int(max_follows)

        # get delay time
        delay_time = self.delay_entry.get()
        
        if delay_time.__len__() == 0:
            
            tkr.messagebox.showerror("Error", "Please Enter Delay Time.")
            
            self.stop_btn.config(state=tkr.NORMAL)
            self.start_btn.config(state=tkr.NORMAL)
            self.message_file_browse_btn.config(state=tkr.NORMAL)

            self.delay_entry.focus()
            
            return False

        delay_time = int(delay_time)

        # Spawn and run processes
        rem_users: list[str] = self.scheduler.spawn(workers, message, delay_time, max_follows, users_file_path, users)
        
        if len(rem_users) > 0:
            print("Could not Follow and send DMs to {} users".format(len(rem_users)))
        else:
            print("All People Followed and DM sent Successfully.")

        # print success message
        self.bot_status_label.config(text="Bot Successfully Completed.")
        tkr.messagebox.showinfo("Success", "Bot Successfully Completed.")

        # stop bot
        self.accounts_file_entry.delete(0, tkr.END)
        self.users_file_entry.delete(0, tkr.END)
        self.message_file_entry.delete(0, tkr.END)
        self.max_follow_entry.delete(0, tkr.END)
        self.delay_entry.delete(0, tkr.END)

        self.stop_btn.config(state=tkr.NORMAL)
        self.start_btn.config(state=tkr.NORMAL)
        self.message_file_browse_btn.config(state=tkr.NORMAL)
        self.users_file_browse_btn.config(state=tkr.NORMAL)
        
        return True

    ###########################################################################################################################################################

    def stop(self):
        try:
            self.scheduler.clear()
            self.scheduler.join(timeout=10)
            self.bot_status_label.config(text="Bot Stopped.")
            print("Bot stopped.")
        except Exception: pass
        
        self.accounts_file_entry.delete(0, tkr.END)
        self.users_file_entry.delete(0, tkr.END)
        self.message_file_entry.delete(0, tkr.END)
        self.max_follow_entry.delete(0, tkr.END)
        self.delay_entry.delete(0, tkr.END)

        self.stop_btn.config(state=tkr.NORMAL)
        self.start_btn.config(state=tkr.NORMAL)
        self.message_file_browse_btn.config(state=tkr.NORMAL)
        self.users_file_browse_btn.config(state=tkr.NORMAL)

    ###########################################################################################################################################################

    def validate_delay_entry(self, p):
        if len(p) != 0:
            x = re.match(r"^\d+$", p)
            if x is not None:
                return True
            else:
                tkr.messagebox.showinfo('Error Message', 'Please Enter Only Numeric Value (e.g. 5, 10, 15 etc)')
                self.delay_entry.delete(0, END)
                self.delay_entry.focus()
                return False

    ###########################################################################################################################################################

    def validate_max_follow_entry(self, p):
        if len(p) != 0:
            x = re.match(r"^\d+$", p)
            if x is not None:
                return True
            else:
                tkr.messagebox.showinfo('Error Message', 'Please Enter Only Numeric Value (e.g. 5, 10, 15 etc)')
                self.max_follow_entry.delete(0, END)
                self.max_follow_entry.focus()
                return False

    ###########################################################################################################################################################

    def select_accounts_file_location(self):
        accounts_file_location = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select Text File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.txt"))
        )
        self.accounts_file_entry.delete(0, END)
        self.accounts_file_entry.insert(0, accounts_file_location)

    ###########################################################################################################################################################

    def select_users_file_location(self):
        users_file_location = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select Text File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.txt"))
        )
        self.users_file_entry.delete(0, END)
        self.users_file_entry.insert(0, users_file_location)

    ###########################################################################################################################################################

    def select_message_file_location(self):
        comments_file_location = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select Text File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.txt"))
        )
        self.message_file_entry.delete(0, END)
        self.message_file_entry.insert(0, comments_file_location)

    ###########################################################################################################################################################

    def render(self):
        # add padding of 88px to the right, left and top of the window
        self.master.grid_columnconfigure(0, minsize=88)
        self.master.grid_columnconfigure(0, minsize=88)
        self.master.grid_rowconfigure(0, minsize=88)
        # Set window Title
        self.master.title("Instagram Bot")
        # Set Geometry
        self.master.geometry('640x560')
        self.master.resizable(False, False)

        mycolor = '#%02x%02x%02x' % (68, 68, 68)

        vcmd_1 = (self.master.register(self.validate_max_follow_entry), '%P')
        vcmd_2 = (self.master.register(self.validate_delay_entry), '%P')

        # self.img_label = ttk.Label(self.master, image=self.instagram_logo)
        self.img_label = ttk.Label(self.master, image=self.instagram_logo, width=10)
        self.img_label.grid(column=1, row=0, columnspan=3, padx=80, pady=5, sticky='w')
        
        self.label_1 = ttk.Label(text="")
        self.label_1.grid(row=1, column=0, sticky="w")

        # Bot Accounts File Input
        self.accounts_file_label = tkr.Label(self.master, text="*Accounts Text File : ")
        self.accounts_file_label.grid(column=0, row=3, pady=5, ipadx=10, ipady=3, padx=10, sticky="w")

        self.accounts_file_entry = tkr.Entry(self.master, bd=4, width=42, relief="groove")
        self.accounts_file_entry.grid(column=1, row=3, padx=5, pady=5, ipady=3, sticky="w")

        self.accounts_file_browse_btn = tkr.Button(self.master, text="Browse", command=self.select_accounts_file_location, bg='#567', fg='White')
        self.accounts_file_browse_btn.grid(column=2, row=3, padx=5, pady=5, ipadx=15, ipady=3)

        self.accounts_file_help = tkr.Label(self.master, text="*Text file containing credentials.", fg='red')
        self.accounts_file_help.grid(row=4, column=1)

        # Scraped Users File Input
        self.users_file_label = tkr.Label(self.master, text="*Users Text File : ")
        self.users_file_label.grid(column=0, row=5, pady=5, ipadx=10, ipady=3, padx=10, sticky="w")
        
        self.users_file_entry = tkr.Entry(self.master, bd=4, width=42, relief="groove")
        self.users_file_entry.grid(column=1, row=5, padx=5, pady=5, ipady=3, sticky="w")
        
        self.users_file_browse_btn = tkr.Button(self.master, text="Browse", command=self.select_users_file_location, bg='#567', fg='White')
        self.users_file_browse_btn.grid(column=2, row=5, padx=5, pady=5, ipadx=15, ipady=3)
        
        self.users_file_help = tkr.Label(self.master, text="*Text file containing scraped usernames.", fg='red')
        self.users_file_help.grid(row=6, column=1)

        # Message File Input
        self.message_file_label = tkr.Label(self.master, text="Message file : ")
        self.message_file_label.grid(column=0, row=9, pady=5, ipadx=10, ipady=3, padx=10, sticky="w")
        
        self.message_file_entry = tkr.Entry(self.master, bd=4, width=42, relief="groove")
        self.message_file_entry.grid(column=1, row=9, padx=5, pady=5, ipady=3, sticky="w")
        
        self.message_file_browse_btn = tkr.Button(self.master, text="Browse", command=self.select_message_file_location, bg='#567', fg='White')
        self.message_file_browse_btn.grid(column=2, row=9, padx=5, pady=5, ipadx=15, ipady=3)
        
        self.message_file_help = tkr.Label(self.master, text="Select Text File with Message.", fg='red')
        self.message_file_help.grid(row=10, column=1)

        # Users To Follow Input
        self.max_follow_label = tkr.Label(self.master, text="Max Users to Follow : ")
        self.max_follow_label.grid(column=0, row=11, pady=5, ipadx=10, ipady=3, padx=10, sticky="w")
        
        self.max_follow_entry = tkr.Entry(self.master, bd=4, width=42, relief="groove", validate="key", validatecommand=vcmd_1)
        self.max_follow_entry.grid(column=1, row=11, padx=5, pady=5, ipady=3, sticky="w")
        
        self.max_follow_help = tkr.Label(self.master, text="Maximum Number of Users to Follow by Account.", fg='red')
        self.max_follow_help.grid(row=12, column=1)

        # delay
        self.delay_label = tkr.Label(self.master, text="Break Time : ")
        self.delay_label.grid(column=0, row=13, pady=5, ipadx=10, ipady=3, padx=10, sticky="w")
        
        self.delay_entry = tkr.Entry(self.master, bd=4, width=42, relief="groove", validate="key", validatecommand=vcmd_2)
        self.delay_entry.grid(column=1, row=13, padx=5, pady=5, ipady=3, sticky="w")
        
        self.delay_entry_help = tkr.Label(self.master, text="Break Time To Check Follow Back in Minutes.", fg='red')
        self.delay_entry_help.grid(row=14, column=1)

        self.bot_status_prefix = tkr.Label(self.master, text="Bot Status : ")
        self.bot_status_prefix.grid(column=0, row=15, pady=5, ipadx=10, ipady=3, padx=15, sticky="w")

        self.bot_status_label = tkr.Label(text="Idle", foreground='red')
        self.bot_status_label.grid(row=15, column=1, pady=5, sticky='w')

        self.stop_btn = tkr.Button(self.master, text="Stop Bot", command=self.stop, bg=mycolor, fg='white')
        self.stop_btn.grid(column=0, row=16, pady=20, ipadx=10, ipady=3, padx=25, sticky="w")

        self.start_btn = tkr.Button(self.master, text="Start Bot", command=self.start_bot_thread, bg=mycolor, fg='white')
        self.start_btn.grid(column=2, row=16, pady=20, padx=10, ipadx=10, ipady=3, sticky='w')

###########################################################################################################################################################
