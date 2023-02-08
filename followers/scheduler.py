
from multiprocessing import Process, Queue
import time
import datetime

from typing import TypedDict

from .bot import InstagramAutomationBot

###########################################################################################################################################################

class WorkerParam(TypedDict):
    username: str
    password: str
    proxy: str

###########################################################################################################################################################

def queue_log(queue: Queue, file_path: str, proc: str, text: str):
    isotime = datetime.datetime.now().replace(microsecond=0).isoformat()
    queue.put((file_path, f"[{isotime}] {proc}: {text}"))

###########################################################################################################################################################

def log_fun(queue: Queue):
    # Read from the queue; this spawns as a separate Process
    while True:
        # Read from the queue and check if it is ended
        entry: tuple[str, str] = None
        try: entry = queue.get(block=True)
        except Exception: continue
        
        try:
            file_path, line = entry
            with open(file_path, "a") as f:
                print(line, file=f)
        except Exception: pass

###########################################################################################################################################################

def remover_fun(queue: Queue):
    # Read from the queue; this spawns as a separate Process
    while True:
        # Read from the queue and check if it is ended
        entry: tuple[str, str] = None
        try: entry = queue.get(block=True)
        except Exception: continue
        
        try:
            file_path, user = entry
            with open(file_path, "r") as f:
                lines = f.readlines()
            with open(file_path, "w") as f:
                for line in lines:
                    if line.strip("\n") != user:
                        f.write(line)
            f.close()
        except Exception: pass

###########################################################################################################################################################

def worker_fun(
    param: WorkerParam,
    message: str,
    delay_time: int,
    max_follows: int,
    users_file_path: str,
    queue: Queue,
    log_queue: Queue,
    remover_queue: Queue
):

    _log = lambda text: queue_log(log_queue, "followers.log", param['username'], text)
    _err = lambda text: queue_log(log_queue, "followers.err", param['username'], text)

    _log("")
    _log("#" * 100)
    _log("Logging in to account: " + param['username'])

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
        _log(login_msg)
        return

    _log("Logged in to account: " + param['username'])
    _log("")
    _log("*" * 100)
    
    # _log("Checking for follow back users.")
    # flag, msg = bot.send_dm_message_who_followed_me(message, delay_time)
    # _log(msg)
    # _log("*" * 100)
    # time.sleep(2)

    _log("")
    _log("-" * 100)
    _log(f"Following {max_follows} users and sending DMs to them.")

    follow_count = 0

    # Read from the queue; this spawns as a separate Process
    while True:
        # Check message count
        if follow_count >= max_follows: break
            
        # Read from the queue and check if it is ended
        user: str = None
        try: user = queue.get(block=True, timeout=2)
        except Exception: break

        # Execute method
        follow_ok, follow_msg = bot.follow_user_and_send_dm(user, message, _log, _err)

        _log(follow_msg)
        _log("-" * 100)
        
        is_private = (not follow_ok) and follow_msg == "User is private. Not able to send message."
        
        if follow_ok:
            follow_count += 1
        
        if follow_ok or is_private:
            remover_queue.put((users_file_path, user))
        
        # Wait for determined delay
        time.sleep(delay_time * 60)

    _log(f"Sent DMs to {follow_count} users.")

    # close browser
    bot.close_browser()
    
    _log(f"Bot Stopped: " + param['username'])

###########################################################################################################################################################

class BotScheduler:
    
    def __init__(self):
        # Init Log worker
        self.log_queue = Queue()
        self.log_proc = Process(target=log_fun, args=((self.log_queue),))
        self.log_proc.daemon = True
        self.log_proc.start()
        # Init remover worker
        self.remover_queue = Queue()
        self.remover_proc = Process(target=remover_fun, args=((self.remover_queue),))
        self.remover_proc.daemon = True
        self.remover_proc.start()
        # Init queues
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
        while len(self.processes) > 0:
            process = self.processes.pop(0)
            process.join(timeout)

    ###########################################################################################################################################################

    def spawn(self, workers: list[WorkerParam], message: str, delay_time: int, max_follows: int, users_file_path: str, users: list[str]):
    
        _log = lambda text: queue_log(self.log_queue, "followers.log", "_", text)

        # Write users into the queue
        for user in users:
            if isinstance(user, str):
                self.queue.put(user)

        # Spawn worker processes
        _processes: list[Process] = []
        
        for param in workers:
            # Launch new Process
            process = Process(
                target=worker_fun,
                args=(
                    param,
                    message,
                    delay_time,
                    max_follows,
                    users_file_path,
                    self.queue,
                    self.log_queue,
                    self.err_queue,
                    self.remover_queue
                )
            )
            process.daemon = True
            process.start()
            # Append Process to list
            _processes.append(process)
            self.processes.append(process)

        # Join processes
        _log("Waiting for processes to join...")
        
        while len(_processes) > 0:
            process = _processes.pop(0)
            process.join()
            try: self.processes.remove(process)
            except Exception: pass

        _log("All processes finished!")

        # Return remaining users
        return self.clear()

###########################################################################################################################################################
