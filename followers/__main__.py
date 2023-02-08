
import tkinter as tkr

from .scheduler import BotScheduler
from .view import InstagramBot

###########################################################################################################################################################

if __name__ == '__main__':
    # Init app
    root = tkr.Tk()
    scheduler = BotScheduler()
    # Instance Bot Window
    app = InstagramBot(root, scheduler)
    app.render()
    app.mainloop()

###########################################################################################################################################################
