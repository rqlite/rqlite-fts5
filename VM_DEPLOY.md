# Deploying Test Machines

This step-by-step instructions below explain how to form a 3-node cluster on Google Cloud Platform, using Virtual Machines (VMs) running Linux. It uses [automatic bootstrapping](https://rqlite.io/docs/clustering/automatic-clustering/), though there are many other ways to form an rqlite cluster. A similar process can be followed on most Cloud providers. You can also run your [rqlite cluster on Kubernetes](https://rqlite.io/docs/guides/kubernetes/), and, of course, on bare metal.

## Forming the cluster
Start by launching 3 virtual machines, and recording the network (IP) addresses of each.

To automatically bootstrap the rqlite cluster you must know the network (IP) addresses of each VM beforehand. Let's imagine your machines have been assigned network addresses `EXTERNAL_IP1`, `EXTERNAL_IP2`, and `EXTERNAL_IP3`. For this example each node must be reachable from every other node, using the specified network addresses.

## Launching rqlite
Next, `ssh` into each machine and download and install rqlite like so:
```bash
curl -L https://github.com/rqlite/rqlite/releases/download/v8.18.2/rqlite-v8.18.2-linux-amd64.tar.gz -o rqlite-v8.18.2-linux-amd64.tar.gz
tar xvfz rqlite-v8.18.2-linux-amd64.tar.gz
sudo cp rqlite-v8.18.2-linux-amd64/* /usr/bin
```
Once installed, run the following command on **each** node:
```bash
VM_IP=`curl -s -H "Metadata-Flavor: Google" http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip`
rqlited -http-addr 0.0.0.0:4001 -http-adv-addr $VM_IP:4001 -raft-addr 0.0.0.0:4002 -raft-adv-addr $VM_IP:4002 -write-queue-batch-size 128 -write-queue-capacity 1024 -bootstrap-expect 3 -join http://$EXTERNAL_IP1:4001,http://EXTERNAL_IP2:4001,http://$EXTERNAL_IP3:4001 data
```
**What does the above command do?**

It first gets the IP address of the VM, so that the launch command is identical on each node (this is just for convenience). Then it lauches the rqlite node, telling it to wait for 2 other nodes to contact it before forming a cluster. Each node waits, and whichever node is contacted first by 2 other nodes will form the cluster. Finally, this command also configures the _write queue_ for better indexing performance.

## Running the indexer
The [indexing program](https://github.com/rqlite/rqlite-fts4/blob/master/indexer.py) can be run from any VM, or from a 4th VM, or even your local machine. As long as the indexing program can contact one of the nodes in the cluster, it should operate fine.
