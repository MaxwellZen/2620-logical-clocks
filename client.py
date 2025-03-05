import socket 
import sys
import random
import time

# Note: we know this is bad practice, but since this code is only meant as a toy experiment we
#       decided there's no point in making host and port command line arguments
host = "127.0.0.1"
port = 5544

# grabs id and filename from command-line arguments
if len(sys.argv) < 3 or not sys.argv[1].isdigit():
    print("Please provide an id and filename for the client")
    print("Example: python3 client.py 0 normal1")
    sys.exit(0)

# initialize machine id and file names
id = int(sys.argv[1])
logname = "logs/" + sys.argv[2] + "_" + str(id) + ".txt"
dataname = "data/" + sys.argv[2] + "_" + str(id) + "_data.txt"
logfile = open(logname, "w")
datafile = open(dataname, "w")

# initalize rest of machine information
cycles_per_sec = random.randint(1,6)
datafile.write(f"cycles per second: {cycles_per_sec}\n")
log_clock = 0
start = time.time()
multiplier = 10

# return amount of time elapsed (multiplied by multiplier for faster testing)
def sys_time():
    return (time.time() - start) * multiplier

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))

    # login
    s.sendall(f"login {id}".encode("utf-8"))
    data = s.recv(1024).decode('utf-8')
    assert(data == "success")

    # keep track of information for data collection
    avg_queue_len = 0
    times = []
    log_times = []

    for iter in range(60 * cycles_per_sec):
        # wait for the correct time to run the iter'th cycle (note: blocking implementation is better)
        while sys_time() < iter / cycles_per_sec:
            continue
        
        # get queue size
        s.sendall("size".encode("utf-8"))
        queue_len = int(s.recv(1024).decode('utf-8'))
        avg_queue_len += queue_len

        # if there is a messge:
        if queue_len > 0:
            # read message and update logical clock
            s.sendall("pop".encode("utf-8"))
            msg = s.recv(1024).decode('utf-8')
            log_clock = max(log_clock, int(msg)) + 1
            logfile.write(f"receive {sys_time()} {queue_len} {log_clock}\n")
        else:
            # roll random operation
            # note: (1,5) bounds correspond to low internal event probability, (1,10) bounds correspond to normal settings
            op = random.randint(1,5)
            if op <= 3:
                log_clock += 1
                # observation: the bits of op correspond to which machines receive a message, so we can perform a bitwise
                #              and operation to determine which sends happen
                if op & 1:
                    s.sendall(f"send {(id+1)%3} {log_clock}".encode("utf-8"))
                    data = s.recv(1024).decode('utf-8')
                    assert(data == "success")
                if op & 2:
                    s.sendall(f"send {(id+2)%3} {log_clock}".encode("utf-8"))
                    data = s.recv(1024).decode('utf-8')
                    assert(data == "success")
                logfile.write(f"send {op} {sys_time()} {log_clock}\n")
            else:
                # internal event
                log_clock += 1
                logfile.write(f"internal {sys_time()} {log_clock}\n")
        
        # append time / log_clock data
        times.append(sys_time())
        log_times.append(log_clock)

    # write data to file
    avg_queue_len /= (60 * cycles_per_sec)
    datafile.write(f"system times: {times}\n")
    datafile.write(f"logical clock times: {log_times}\n")
    datafile.write(f"average queue length: {avg_queue_len}\n")
    datafile.write(f"final logical clock value: {log_clock}\n")
    datafile.write(f"average logical clock jump: {log_clock / (60 * cycles_per_sec)}\n")