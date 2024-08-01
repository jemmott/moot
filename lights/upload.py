import pixelblaze

f = [
    ("Boot", "boot"),
    ("Interactive-backwards", "backward"),
    ("Interactive-passive", "passive"),
    ("Shutdown", "shutdown"),
    ("Central Script Logic", "main"),
    ("Interactive-forwards", "forward"),
    ("Standby", "standby"),
]

pb = pixelblaze.Pixelblaze("pb-moot")
print(pb.getFileList())
for here, there in f:
    pb.putFile("/p/" + there, open(here).read())
