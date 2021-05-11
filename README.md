# ScratchCloudV4
A new way to connect to [scratch](https://scratch.mit.edu) cloud variables from [python](https://www.python.com) without node.js

## Making a program
```python
import scratchcloud

cloud = scratchcloud.CloudSession(123456789, "username", "password")
```

* `cloud.getVar(name)` -Returns the variable stated
* `cloud.getVars()` -Returns all the variables in the project
* `cloud.setVar(name, value)` -Sets the variable stated to a value
* `cloud.changeVar(name, changeBy)` -Changes the variable stated by a value
### Note that these below won't edit the project json and will not work properly except in the cloud log
* `cloud.createVar(name)` -Creates a new variable
* `cloud.deleteVar(name)` -Deletes the variable stated
* `cloud.renameVar(oldName, newName)` -Renames a variable to the name stated

## Thats it!
ScratchCloud is designed to be really easy to use

#Credit
Credit to @PikahuB2005 for help
