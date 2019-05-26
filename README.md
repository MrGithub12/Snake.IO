# Snake IO 

CS 382 Network Centric Computing   
Spring 2019   
LUMS  

### Azan Bin Zahid - 20100206@lums.edu.pk
### Taimoor Ali - 20100217@lums.edu.pk


## Introduction: 
This assignment is a multiplayer version of the classic game “Snake”.  
The rules of the game are as follows: 

1. When the game starts, all players have a snake spawn in a random position on the board. 
2. Each player is able to move their snake in in four directions (up, down, left or right) using their arrow keys. 
3. If a snake collides with the border of the stage, it gets eliminated. 
4. If a snake (A) collides with another snake (B) from the side, then snake A gets eliminated while snake B survives.  
5. If two snakes have a head-on collision, they both get eliminated (if these were the last two snakes, then nobody wins). 
6. The last snake alive wins the game. 


## Server Side:
### server.py

It does the following: 
1. Connect with all the clients 
2. Start the game and spawn a snake for each player on the board 
3. Communicate the positions and moves of each player to every other player

The command for starting the server is:  
```
python3 server.py *IP address* *port* *number of players*  
```
For example:
```
python3 server.py 192.168.5.5 2000 5 
python3 server.py 127.0.0.1 2000 3
```
## Client Side:
### client.py

It does the following: 
1. Connect with the server
2. Display the board and all of the players and their positions.
3. Recieves information from the srver and render in real time. 
4. It uses the “curses” library in python to make the game.

The command for starting the client is:  
```
python3 client.py *IP address* *port*  
```
For example:
```
python3 client.py 192.168.5.5 2000  
python3 client..py 127.0.0.1 200
```

## Bonus Part:
1. Food on the stage which snakes can eat to score.  
2. Kill counters.

## Pull Request:
Server does not close after all clinets disconnect.
