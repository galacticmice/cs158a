# A2: Chat

### Execution

In separate terminals, run the following commands
- first terminal
```python3 mychatserver.py```
- nth terminal
```python3 myvlclient.py```

### Results
![image](./a2-results.png)
- Messages sent by client will propagate to other clients connected to the server
- Sending 'exit' (case sensitive) will trigger a command to disconnect client from server
- SIGINT/SIGTSTP will run graceful shutdowns on both client and server instances


