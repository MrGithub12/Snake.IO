# SNAKES IO GAME SERVER SIDE
# Azan Bin Zahid - 20100206
# Taimoor Ali - 20100217


import socket 
import sys 
import random
from _thread import *
import threading 
import pickle 
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN

# --------------- global variables ------------

#all clients/threads record 
clients = set();

# default parameters
N = 2
host = ""
port = 12345

#  update if provided in command-line
if (len(sys.argv)==4):
    host = sys.argv[1]
    port = int(sys.argv[2])
    N = int(sys.argv[3])

# record for all snakes connected
snakes = []

# globals
recv_count = 0
init_pos = [9]

#locks 
recv_count_lock = threading.Lock()
snakes_lock = threading.Lock()
# ----------------------------------------------

def wins():
    with snakes_lock:
        # count number of snakes alive 
        win = []
        for sn in snakes:
            if(sn['alive']==1):
                win.append(sn)

        #  if only one snake is alive, its the winner
        if (len(win)==1):
            iid = win[0]['id']
            snakes[iid]['win']=1
            print("\n--------WINNER----------")
            print ("\nSnake", iid, "won!!")
            print("\n--------WINNER----------")
            print("\n------------------------")
            print ("\nGame Ended")
            print("\n------------------------")
            return iid
        # if none is alive, all dead
        elif (len(win)==0):
            print("\n------------------------")
            print("\nAll Dead - No won")
            print("\n------------------------")
            sys.exit()
        else: 
            return (-1)
        return -1

# -----------------------------------------------


# --------DEAD CODE------------------------------

def dead():
    body = []
    # check for dead

    # extracting full snake bodies
    with snakes_lock:
        for sn in snakes:
            body.append([sn['id'], sn['init_pos']])
        # check all heads
        for head in body:
            # in all bodies
            for belly in body:
                #  head to head colloision
                if head[1][0] == belly[1][0] and head[0]!=belly[0] and snakes[head[0]]['alive']==1:
                    # id of hurted snake
                    hurt1 = belly[0]
                    hurt2 = head[0]
                    # making them dead
                    snakes[hurt1]['alive']=0
                    snakes[hurt2]['alive']=0

                    # communicate the dead snakes to all
                    for cl in clients:
                        try:
                            cl.send(pickle.dumps(snakes))
                        except:
                            pass
                    # setting them to 0,0 position to avoid re-rendring
                    snakes[hurt1]['init_pos']=[[0,0]]
                    snakes[hurt2]['init_pos']=[[1,0]]
                    print("\n------Head Collision-------")
                    print("\nSnake", hurt1, "dead")
                    print("\nSnake", hurt2, "dead")
                    print("\n------Head Collision-------")
                    return 2
                # if A's head in B's body, condition can be reversed
                elif head[1][0] in belly[1][1:] and head[0]!=belly[0] and snakes[belly[0]]['alive']==1:
                    # id of hurted snake
                    hurt = (belly[0])
                    kill = head[0]
                    # making it dead
                    snakes[hurt]['alive']=0
                    snakes[kill]['kill']+=1
                    # communicate the dead snakes to all
                    for cl in clients:
                        try:
                            cl.send(pickle.dumps(snakes))
                        except:
                            pass
                    # setting them to 0,0 position to avoid re-rendring
                    snakes[hurt]['init_pos']=[[0,0]]
                    print("\n------------------------")
                    print("\nSnake", hurt, "dead")
                    print("\n------------------------")
                    return 1
    return 0
    
# ----------------------------------------------------------

# using for to re-calculate N
def setN():
    global N
    with snakes_lock:
        temp = 0
        for sn in snakes:
            if(sn['alive']==1):
                temp = temp + 1
        N = temp


# ----------------------------------------------------------
# waiting for all threads to recieve then, broadcast all
def broadcaster():
    global recv_count
    global N
    with recv_count_lock:
        recv_count += 1

        # wait till all threads are ready to broadcast
        if (recv_count == N):

            # if any snake ate food
            for sn in snakes:
                if sn['init_pos'][0] == sn['food']:                                            # When snake eats the food
                    snakes[sn['id']]['score'] += 1

                    # re add food to new location
                    food = [random.randint(1, 18), random.randint(1, 58)] 
                    for s in snakes:
                        iid = s['id']
                        snakes[iid]['food'] = food
                    break



            # for speacial case when snake hit the border
            setN()

            # dead function call to check dead conditions
            out = dead()

            # see who wins
            wins()

            # no dead
            if(out==0):
                for cl in clients:
                    try:
                        cl.send(pickle.dumps(snakes))
                    except:
                        pass
                recv_count = 0
                return

            # one dead
            elif(out==1):
                N = N-1
                recv_count = 0
                return
            
            # head collision, both dead
            elif(out==2):
                N = N-2
                recv_count = 0
                return
    # meaning all threads not yet responded
    return
# ----------------------------------------------------------



#snake initialization
def init(snake, c):
    # check if not already initiated
    if snake['init'] == 1:
        return
    else:
        global snakes
        with snakes_lock:
            # random snake position
            while True:
                r = random.randint(2,18)
                if r not in init_pos:
                    init_pos.append(r)
                    break

            idx = len(snakes)
            snake['init_pos'] = [[r,10], [r,9], [r,8], [r,7], [r,6]]
            snake['key'] = KEY_RIGHT
            snake['char'] = str(idx)
            snake['id'] = idx
            snake['init'] = 1
            snake['alive'] = 1
            snake['food'] = [init_pos[0],10]
            snakes.append(snake)
            c.send(pickle.dumps(idx))




# thread fuction 
def clients_thread(c):
    # for record keeping  
    clients.add(c)

    while True: 
        # data received from client
        try: 
            data = c.recv(1024)
            # this specific clients/thread's snake
            snake = pickle.loads(data)
        except:
            break
        
        
        # init on first recv
        init(snake, c)

        # update move
        snake['init_pos'].insert(0,
            [
                snake['init_pos'][0][0] + (snake['key'] == KEY_DOWN and 1) + (snake['key'] == KEY_UP and -1), 
                snake['init_pos'][0][1] + (snake['key'] == KEY_LEFT and -1) + (snake['key'] == KEY_RIGHT and 1)
            ]
        )

        # ---------------------------------------------------------------
        # if snake hits the border, dead the snake and broadcast to all imediately  
        if snake['init_pos'][0][0] == 0 or snake['init_pos'][0][0] == 19 or snake['init_pos'][0][1] == 0 or snake['init_pos'][0][1] == 59: 
            snake['alive']=0
            with snakes_lock:
                try:
                    snakes[snake['id']] = snake
                    c.send(pickle.dumps(snakes))
                    print("\n------------------------")
                    print("\nSnake", snake['id'], "dead")
                    print("\n------------------------")
                except:
                    pass
        # ---------------------------------------------------------------

        # update only its own snake['init_pos']
        with snakes_lock:
            snakes[snake['id']] = snake
        
        broadcaster()

    # connection closed 
    c.close() 
  
  
def Main(): 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port)) 
    print("socket binded to post", port) 

    # put the socket into listening mode 
    s.listen(N) 
    print("socket is listening") 
  
    # a forever loop until client wants to exit 
    snake_count = 0
    while True: 
        # establish connection with client 
        c, addr = s.accept()   
        print('Snake', snake_count,'connected to :', addr[0], ':', addr[1]) 
        snake_count = snake_count+1
        # Start a new thread
        start_new_thread(clients_thread, (c,)) 

    s.close() 
  
  
if __name__ == '__main__': 
    Main() 