# ScratchCloudV4
A new way to connect to [scratch](https://scratch.mit.edu) cloud variables from [python](https://www.python.com) without node.js

## Making a program
```python
import scratchcloud

cloud = scratchcloud.CloudSession(123456789, "username", "password")
```

* `cloud.getVar(name)`-Gets the variable stated
* `cloud.setVar(name, value)`-Sets the variable stated to a value

## Thats it!
ScratchCloud is designed to be really easy to use
