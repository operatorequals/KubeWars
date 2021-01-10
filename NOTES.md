# Kubernetes Game

# Desc

N players are Deploying X Pods in a K8s
The Pods all must contain specific docker images.

The docker images resemble spaceships or cowboys or whatever.

They have L open listening TCP ports and some stats like "Fire Rate".
Before deploying the image, the player configures the stats.

The Docker Image automatically and randomly sends TCP data to
random other pods.
If A Pod receives data it "dies"

# Deployment / Team

Each Team is a K8s Deployment containing X Pods.
The pods can be arbitrarily named (user-input).

# Announcer

Announcer is a special Pod that observes the game and provides an API
for announcing new "kills", "misses" etc.

This API can be skinned through a Frontent to show a starwars battle, a soccer match, whatever.

# Pod Outputs
Each Pod must output its state though stdout.
The state contains stuff like:
* Initial state (number of listening ports)
* Init stats
* shot to specific IP:port and number of bytes
* Receiving of bytes and from whom (IP:port)
* Death


# Webhook
A webhook should validate the deployments of the teams. The values
for initial stats should be in Helm values, and they should be 
checked by the Webhook.

This defends the overloading of values (over 9000)

----

Stats
* HP (a value in `[1, 4096]` )
* DAMAGE (a value in `[1, 4096]`)
* FIRERATE (a value in Hz, hits per second, in `[1,512]`)
* DAMAGE_SPREAD (an area between the exact DAMAGE value to chose the dealtdamage from. A value in `[1, 4096]`) - TODO
* SHIELD (a value in `[0, 128]`) - TODO
* COMPETENCE (a value in `[0,255]`. The value of IP addresses the bot remembers to have aimed) - TODO

# Frontend

Use a library like [`blessed`](https://pypi.org/project/blessed/) to create a program that will reside in the
docker image and will provide graphics like space invaders style. A use will be able to use it with `k exec [...] -- spaceship`