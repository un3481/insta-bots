
from multiprocessing import Process, Queue
import time
import sys

from typing import TypedDict

from .bot import InstagramAutomationBot

###########################################################################################################################################################

class WorkerParam(TypedDict):
    username: str
    password: str
    proxy: str

###########################################################################################################################################################

class BotScheduler:
    
    def __init__(self):
        self.queue = Queue()
        self.processes: list[Process] = []
    
    ###########################################################################################################################################################

    def clear(self):
        # Collect current items
        queue_list: list = []
        
        while True:
            try:
                item = self.queue.get(block=False)
                queue_list.append(item)
            except Exception: break
        
        # Return current items
        return queue_list
    
    ###########################################################################################################################################################

    def join(self, timeout: float = None):
        process_list: list[Process] = []
        while len(self.processes) > 0:
            process = self.processes.pop(0)
            process.join(timeout)
            process_list.append(process)
        return process_list

    ###########################################################################################################################################################

    def worker(self, param: WorkerParam, message: str, delay_time: int, no_of_follows: int):

        print()
        print("#" * 100)
        print("Logging in to account: " + param['username'])

        # create bot
        bot = InstagramAutomationBot(
            param['username'],
            param['password'],
            param['proxy']
        )

        # login to instagram
        login_ok, login_msg = bot.login()

        if not login_ok:
            bot.close_browser()
            print(login_msg)
            return

        print("Logged in to account: " + param['username'])
        print()
        print("*" * 100)
        print("Checking for follow back users.")

        flag, msg = bot.send_dm_message_who_followed_me(message, delay_time)

        print(msg)
        print("*" * 100)
        time.sleep(2)

        print()
        print("-" * 100)
        print("Following {} users and sending DMs to them.".format(no_of_follows))

        message_count = 0

        # Read from the queue; this spawns as a separate Process
        while True:
            # Check message count
            if message_count >= no_of_follows:
                break
            
            # Read from the queue and check if it is ended
            user: str = None
            try: user = self.queue.get(block=True, timeout=2)
            except Exception: break

            # Execute method
            follow_ok, follow_msg = bot.follow_user_and_send_dm(user, message)

            print(follow_msg)

            if follow_ok: message_count += 1

            print("-" * 100)
            time.sleep(delay_time)

        print("Sent DMs to {} users.".format(message_count))

        # close browser
        bot.close_browser()

    ###########################################################################################################################################################

    def spawn(self, workers: list[WorkerParam], message: str, delay_time: int, no_of_follows: int, users: list[str]):

        # Write users into the queue
        for user in users:
            if isinstance(user, str):
                self.queue.put(user)

        # Spawn worker processes
        _processes: list[Process] = []
        
        for param in workers:
            # Launch new Process
            target = lambda: self.worker(param, message, delay_time, no_of_follows)
            process = Process(target=target)
            process.daemon = True
            process.start()
            # Append Process to list
            _processes.append(process)
            self.processes.append(process)

        # Join processes
        print("Waiting for processes to join...")
        
        while len(_processes) > 0:
            process = _processes.pop(0)
            self.processes.remove(process)
            process.join()

        print("All processes finished!")

        # Return remaining users
        return self.clear()

###########################################################################################################################################################
