# SNAKES IO GAME CLIENT SIDE
# Azan Bin Zahid - 20100206
# Taimoor Ali - 20100217


import sys
import socket 
import pickle
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN


host = '127.0.0.1'
port = 12345

# if command-line args given, otherwise default
if (len(sys.argv)==3):
    host = sys.argv[1]
    port = int(sys.argv[2])

# socket init
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
s.connect((host,port))

# host snake, rest will be guest
snake = {
  "init_pos": [[0,0]],
  "key": KEY_RIGHT,
  "char": '0',
  "init": 0,
  "id": 0,
  "alive": 0,
  "win":0,
  "kill": 0,
  "score":0,
  "food": []
}

# one time usage
set_id = 1
msg = ""

# ---Screen Init----
curses.initscr()
win = curses.newwin(20, 60, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)
#---------------------

while True:  
    win.addstr(0, 2, 'Kills : ' + str(snake['kill']) + ' ') 
    win.addstr(0, 47, 'Score : ' + str(snake['score']) + ' ') 
    win.addstr(0, 20, ' You ARE SNAKE ' + str(snake['id']))

    # delay, lower is faster
    win.timeout(150)                                                  
    
    # using prevKey if no key pressed
    prevKey = snake['key']                                                
    event = win.getch()
    snake['key'] = snake['key'] if event == -1 else event 

    
    #sending this snake's state to server 
    toSend = pickle.dumps(snake)
    s.send(toSend)

    # only one time, to set host snake id
    if set_id:
      iid = s.recv(1024) 
      snake['id'] = pickle.loads(iid)
      set_id = 0

    # recving all snakes from server
    data = s.recv(1024)
    snakes = pickle.loads(data) 
    
    #updating only host snake 
    snake = snakes[snake['id']]

    # if host snake dies, end its screen
    if (snake['alive']==0):
          msg = "dead"
          break

    # if host snake wins, end its screen
    if (snake['win']==1):
          msg = "won"
          break

    # placing food on screen 
    if(len(snake['food'])>0):
      win.addch(snake['food'][0], snake['food'][1], '*')

    # redering all snakes
    for sn in snakes:
        # removing dead snakes
        if (sn['alive']==0): 
          for x in sn['init_pos']:
                win.addch(x[0], x[1], ' ')
        else:  
          last = sn['init_pos'].pop()
          win.addch(last[0], last[1], ' ')
          win.addch(sn['init_pos'][0][0], sn['init_pos'][0][1], sn['char'])


curses.endwin()
s.close()
print("\n---------END------------")
print("\nSnake", snake['id'],msg)
print("\nKills = " + str(snake['kill']))
print("\nScore = " + str(snake['score']))
print("\n---------END------------")