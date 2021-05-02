import websocketcilent as websocket
import requests, re, json, multiprocessing, atexit, time, warnings

class CloudSession():
  def __init__(self, projID, username, password): #Initializes the program
    self.projID = projID
    self.username = username
    self.password = password
    self._sessionId = self._login()
    self._ws = websocket.WebSocket()
    self._variables = {}
    self.connect()
    self._loop = multiprocessing.Process(target=self._varLoop)
    self._loop.start() #Runs the cloud loop
    atexit.register(self._stop) #Makes sure the websocket connection is closed when the program ends
  
  def _login(self): #Creates a Session ID from the scratch credentials
    headers = {
      "x-csrftoken": "a",
      "x-requested-with": "XMLHttpRequest",
      "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
      "referer": "https://scratch.mit.edu"
    }
    data = json.dumps({
      "username": self.username,
      "password": self.password
    })
    request = requests.post('https://scratch.mit.edu/login/', data=data, headers=headers)
    sessionID = re.search('\"(.*)\"', request.headers['Set-Cookie']).group()
    return sessionID
  
  def connect(self): #Connects to the cloud server
    self.connection = self._ws.connect('wss://clouddata.scratch.mit.edu', cookie='scratchsessionsid='+self._sessionId+';', origin='https://scratch.mit.edu', enable_multithread=True)
    self._sendPacket({
      'method': 'handshake',
      'user': self.username, 
      'project_id': str(self.projID)
    })
    self._handlePacket(self._ws.recv())
  
  def _sendPacket(self, packet): #Sends a packet to the websocket
    self._ws.send(json.dumps(packet) + '\n')

  def _handlePacket(self, packet): #This bit reads the data from the websocket and turns it into a dictionary
    cloudVars = packet.split("\n")[:-1]
    for var in cloudVars:
      varJSON = json.loads(var)
      self._variables.update({varJSON["name"]: varJSON["value"]})
  
  def _varLoop(self): #A loop to keep reciving the cloud variables
    while True:
      if self._ws.connected:
        try:
          packet = self._ws.recv()
          self._handlePacket(packet)
        except json.JSONDecodeError:
          warnings.warn("Unimplimented Packet: "+packet, SyntaxWarning)
        except:
          warnings.warn("Unknown error occoured", Warning)
      else:
        self.connect()

  def _stop(self): #Closes the connection once the program is finished
    self._loop.terminate()
    self._ws.close()
  
  def _validify(self, name): #This bit makes the variable a valid name
    return "☁ "+name if not name.startswith("☁ ") else name

  def getVar(self, varName): #Gets the variable stated
    validName = self._validify(varName)
    try:
      return self._variables[validName]
    except:
      raise ValueError("Could not find variable "+validName[2:])
  
  def setVar(self, varName, value): #Sets the variable stated
    self.getVar(varName)
    validName = self._validify(varName)
    try:
      self._sendPacket({
        "method": "set",
        "name": validName,
        "value": str(value),
        "user": self.username,
        "project_id": str(self.projID)
      })
    except BrokenPipeError:
      self.connect()
      time.sleep(0.1)
      self.setVar(varName, value)
    else:
      self._variables[varName] = value