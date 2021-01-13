# KubeWars
What if I told you that an Armageddon is going on in the TCP layer of your Kubernetes cluster?

## Enter KubeWars

KubeWars is a game that was created using Kubernetes as a _Game Engine_!
Its audience probably is all these DevOps and SRE Teams around the technical world,
that would enjoy a break for shooting some enemy Spacecraft Pods, just before
going about debugging that Jenkins issue again.


### Description

Several Spacecrafts tagged in Teams are entering the Kubernetes cluster as Pods,
flying around the TCP layer. They can be targeted by their cluster IP addresses.

The Teams rosters are cooked by the players in a nice Helm Chart!

The spacecraft default stance is "_Fire on all directions_", shooting TCP packets
on randomly generated targets in the subnet.

If a TCP packet finds an enemy spacecraft, (its HP get lowered and) it goes down!

The Team with its members staying in `Running` state for longer is the winning team!


## Fasten your seatbelt Commander

The Team commanders can directly control the Spacecrafts of their Team, by executing
the `spacecraft` application with a TTY from inside the pod as below:
```bash
kubectl exec -ti jacob-blue-kubewars-bot -- spacecraft
```

From there you can enter the "_Search and Destroy_" mode, by selecting the target spacecraft
by IP and shooting using SPACE.


## Demo

Deploy your Team and Get In!
[![asciicast](https://asciinema.org/a/384292.svg)](https://asciinema.org/a/384292)
