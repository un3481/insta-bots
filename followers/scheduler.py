
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

def worker_fun(worker: WorkerParam, message: str, delay_time: int, no_of_follows: int, queue: Queue):

    print()
    print("#" * 100)
    print("Logging in to account: " + worker['username'])
    
    # create bot
    bot = InstagramAutomationBot(
        worker['username'],
        worker['password'],
        worker['proxy']
    )
    
    # login to instagram
    login_ok, login_msg = bot.login()
    
    if not login_ok:
        bot.close_browser()
        print(login_msg)
        return

    print("Logged in to account: " + worker['username'])
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
        try: user = queue.get(block=True, timeout=2)
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

def schedule_bots(workers: list[WorkerParam], message: str, delay_time: int, no_of_follows: int, users: list[str]):
    
    # Write users into the queue
    queue = Queue()
    for user in users:
        if isinstance(user, str):
            queue.put(user)
    
    # Spawn worker processes
    processes: list[Process] = []
    for worker in workers:
        # Launch new Process
        target = lambda qq: worker_fun(worker, message, delay_time, no_of_follows, qq)
        process = Process(target=target, args=((queue),))
        process.daemon = True
        process.start()
        # Append Process
        processes.append(process)
        
    # Join processes
    print("Waiting for processes to join...")
    for process in processes:
        process.join()
        
    print("All processes finished!")
    
    # Collect remaining users
    rem: list[str] = []
    while True:
        try:
            user: str = queue.get(block=False)
            rem.append(user)
        except Exception:
            break
    
    # Return remaining users
    return rem

###########################################################################################################################################################
