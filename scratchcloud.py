"""Connects python to scratch with cloud variables"""

import websocketcilent as websocket
import requests, re, json, multiprocessing, atexit, time, warnings

class IncorrectCredentials(Exception):
  """An error when the incorrect username or password is entered"""
  pass

class CloudSession():
  """Connects python to scratch with cloud variables"""
  def __init__(self, projID, username, password):
    """Connects python to scratch with cloud variables"""
    self.projID = projID
    self.username = username
    self.password = password
    self._sessionId = self._login()
    self._ws = websocket.WebSocket()
    self._variables = {}
    self.connect()
    self._loop = multiprocessing.Process(target=self._varLoop)
    self._loop.start() #Runs the cloud loop
    atexit.register(self.stop) #Makes sure the websocket connection is closed when the program ends
  
  def _login(self):
    """Creates a Session ID from the scratch credentials"""
    headers = {
      "x-csrftoken": "a",
      "x-requested-with": "XMLHttpRequest",
      "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
      "referer": "https://scratch.mit.edu",
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    }
    data = json.dumps({
      "username": self.username,
      "password": self.password
    })
    request = requests.post('https://scratch.mit.edu/login/', data=data, headers=headers)
    try:
      sessionID = re.search('\"(.*)\"', request.headers['Set-Cookie']).group()
      return sessionID
    except AttributeError:
      raise IncorrectCredentials("Incorrect username or password.")
  
  def connect(self):
    """Connects to the cloud server"""
    self.connection = self._ws.connect('wss://clouddata.scratch.mit.edu', cookie='scratchsessionsid='+self._sessionId+';', origin='https://scratch.mit.edu', enable_multithread=True)
    self._sendPacket({
      'method': 'handshake',
      'user': self.username, 
      'project_id': str(self.projID)
    })
    self._handlePacket(self._ws.recv())
  
  def _sendPacket(self, packet):
    """Sends a packet to the websocket"""
    self._ws.send(json.dumps(packet) + '\n')

  def _handlePacket(self, packet):
    """This bit reads the data from the websocket and turns it into a dictionary"""
    cloudVars = packet.split("\n")[:-1]
    for var in cloudVars:
      varJSON = json.loads(var)
      if varJSON["method"] == "ack":
        pass
      elif varJSON["method"] == "set":
        self._variables.update({varJSON["name"]: varJSON["value"]})
  
  def _varLoop(self):
    """A loop to keep reciving the cloud variables"""
    while True:
      if self._ws.connected:
        try:
          packet = self._ws.recv()
          self._handlePacket(packet)
        except json.JSONDecodeError:
          warnings.warn("Unimplimented Packet: "+packet, SyntaxWarning)
        except:
          pass
      else:
        self.connect()

  def stop(self):
    """Closes the connection once the program is finished"""
    self._loop.terminate()
    self._ws.close()

  def _checkValid(self, varName, error=True):
    """Turns an invalid cloud variable name to a valid one"""
    validName = "☁ "+varName if not varName.startswith("☁ ") else varName
    if (not validName in self._variables) and error:
      raise ValueError("Could not find variable "+validName[2:])
    return validName

  def _send(self, method, options):
    """Sends a message to cloud"""
    try:
      self._sendPacket(dict({
        "method": method,
        "user": self.username,
        "project_id": str(self.projID)
      }, **options))
    except BrokenPipeError:
      self.connect()
      time.sleep(0.1)
      self._send(method, options)

  def getVar(self, varName):
    """Returns the variable stated"""
    return self._variables[self._checkValid(varName)]
  
  def getVars(self):
    """Returns all the variables in the project"""
    myVars = {}
    for var, val in self._variables.items():
      myVars.update({var[2:]: val})
    return myVars

  def setVar(self, varName, value):
    """Sets the variable stated to a value"""
    validName = self._checkValid(varName)
    self._send("set", {"name": validName, "value": str(value)})
    self._variables[validName] = str(value)
  
  def changeVar(self, varName, changeBy):
    """Changes the variable stated by a value"""
    validName = self._checkValid(varName)
    value = float(self.getVar(varName)) + float(changeBy)
    value = int(value) if int(value) == value else value
    self._send("set", {"name": validName, "value": str(value)})
    self._variables[validName] = str(value)

  def createVar(self, varName):
    """Creates a new variable. Note that it will not edit the online project json so won't work properly"""
    validName = self._checkValid(varName, error=False)
    self._send("create", {"name": validName, "value": "0"})
    self._variables[validName] = "0"
  
  def deleteVar(self, varName):
    """Deletes the variable stated. Note that it will not edit the online project json so won't work properly"""
    validName = self._checkValid(varName)
    self._send("delete", {"name": validName})
    del self._variables[validName]

  def renameVar(self, oldVarName, newVarName):
    """Renames a variable to the name stated. Note that it will not edit the online project json so won't work properly"""
    oldValidName = self._checkValid(oldVarName)
    newValidName = self._checkValid(newVarName, error=False)
    self._send("rename", {"name": oldValidName, "new_name": newValidName})
    self._variables[newValidName] = self._variables[oldValidName]
    del self._variables[oldValidName]
