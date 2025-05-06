+++
title = "Yocto setup on Arch linux Pt 1"
date = 2025-03-25

[taxonomies]
tags = ["yocto", "linux", "beaglebone"]
+++

{{ youtube(id="-YcWtBhIcG0", class="youtube") }}

I am starting a new series of Yocto development for Beaglebone Black. If you don't know about yocto, this is how The Yocto Project themselves introduce.
> The Yocto Project (YP) is an open source collaboration project that helps developers create custom Linux-based systems regardless of the hardware architecture.


<!-- more -->

Basically yocto is the de facto tool used to make custom linux images for your embedded devices such as media player, router, IoT devices. This guide will not explain you about yocto in much detail, that will be next guide. This guide is focused on getting yocto up and running. If you use any of the distro mentioned [here](https://docs.yoctoproject.org/ref-manual/system-requirements.html#supported-linux-distributions) you can directly follow the offical guide for [Quick Build](https://docs.yoctoproject.org/brief-yoctoprojectqs/index.html). But if you are like me who uses Arch linux or any other unsupported linux distributions things are going to be little more complicated.

# Arch Linux
I did try to build yocto on arch linux directly but I was presented with endless dependencies and build errors which I got tired of fixing. So I came up with this whole system, and you may have guessed it already, its a `Ubuntu VM`. But not a simple VM. It will be a nicely integrated VM to your host system. We will be doing all the development and using the images from host system, the VM will be responsible for only building yocto.

## Creating Ubuntu server VM
1. Download the ubuntu [server iso](https://ubuntu.com/download/server). Currently I am using 24.04 LTS.
2. Install qemu on your system `sudo pacman -Sy qemu-full`
3. Create a directory called `yocto` where we will keep vm image and yocto artifacts.
```sh
mkdir ~/yocto
cd ~/yocto

# Create a disk image where you'll install ubuntu. 20Gb Disk size should be enough.
qemu-img create -f qcow2 ubuntu-disk.qcow2 20G

# Boot QEMU with ubuntu-server iso and disk image on which we'll install it
# Set the processor core count and memory according to your pc, I have kept 10 core and 16GB memory
# Set the path for your ubuntu-server.iso
qemu-system-x86_64 \
    -enable-kvm \
    -m 16G \
    -smp 10 \
    -cdrom Path/to/ubuntu-server.iso \
    -hda ubuntu-disk.qcow2 \
    -boot d \
    -net nic \
    -net user \
    -vga virtio \
    -display default
```
Here is explaination for each argument
- **`qemu-system-x86_64`**: Runs the QEMU emulator for 64-bit x86 systems.  
- **`-enable-kvm`**: Enables hardware acceleration via KVM for better performance.  
- **`-m 16G`**: Allocates 16 GB of RAM to the virtual machine.  
- **`-smp 10`**: Assigns 10 CPU cores to the virtual machine.  
- **`-cdrom ~/Downloads/ubuntu-24.04.2-live-server-amd64.iso`**: Sets the Ubuntu ISO as the virtual CD-ROM.  
- **`-hda ubuntu-disk.qcow2`**: Uses `ubuntu-disk.qcow2` as the VM's primary hard disk.  
- **`-boot d`**: Boots from the CD-ROM (`d` = CD drive) first.  
- **`-net nic`**: Creates a virtual network interface card (NIC).  
- **`-net user`**: Enables user-mode networking with NAT.  
- **`-vga virtio`**: Uses the VirtIO driver for improved graphics performance.  
- **`-display default`**: Uses the default display backend for QEMU.

Now you'll see a new window poping up, the ubuntu-server image will boot and and you can proceed with ubuntu installation. You can see the ubuntu install process on my video guide.

## Ubuntu VM initial setup
At this point you should have ubuntu installed on your disk image and you can boot from it and see if its running, We dont need to give path for iso anymore. Just enter your login id and password
```sh
qemu-system-x86_64 \
    -enable-kvm \
    -m 16G \
    -smp 10 \
    -hda ubuntu-disk.qcow2 \
    -net nic \
    -net user \
    -vga virtio \
    -display default

# After you are logged in, create a new directory called begale, we will use this directory for shared directory between this VM and host ~/beagle directory
mkdir ~/yocto
cd ~/yocto
```
### SSH Setup
Currently you must be interacting with your VM using the VM window, but this is not ideal as you cant copy paste and have more terminals. So its better to setup ssh on VM.
```sh
# Setup SSH server on your VM for easy shell access from host
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh   # It sould be active
```
But its not over yet, currently you dont have direct communication from host to VM. For this we have to setup host forward which will forward VM's port 22(ie. ssh port) to prot 2222 on host pc, read more about this [here](https://wiki.qemu.org/Documentation/Networking).
```sh
# Shutdown your VM
shutdown now

# Now rerun the vm with following argument

qemu-system-x86_64 \
    -enable-kvm \
    -m 16G \
    -smp 10 \
    -hda ubuntu-disk.qcow2 \
    -vga virtio \
    -display default \
    -netdev user,id=net0,hostfwd=tcp::2222-:22 \
    -device e1000,netdev=net0
```
- **`-netdev user,id=net0,hostfwd=tcp::2222-:22`**: Creates a user-mode network backend (`net0`) and forwards port 2222 on the host to port 22 in the VM (for SSH access).  
- **`-device e1000,netdev=net0`**: Attaches an Intel e1000 virtual network card to `net0`.  

Now the VM should boot normally but you can also access VM's shell using ssh.
```sh
# On your host pc, ssh into VM by entering the username
ssh vmUsername@localhost -p 2222
```

Congrats, you got ssh working, now time to have shared directory. But why Set Up a Shared Directory Between the Host and Ubuntu VM for Yocto?  
1. **Limited VM Storage**: The VM has only 20GB of space, while a Yocto build can exceed 100-200GB. Storing the build on the host prevents running out of space.  
2. **Persistence Across VMs**: Since all Yocto files remain on the host, you can delete or recreate VMs without affecting your Yocto setup.  
3. **Seamless Editing & Development**: Easily edit files from your host system using your preferred tools without needing to transfer files manually.  
4. **Immediate Access to Build Outputs**: Once the Ubuntu VM completes the Yocto build, the generated Linux images are instantly accessible on your host PC.  

The shared directory will be like this `(HOST)~/yocto <-> (VM)~/yocto`. For directory sharing system we will be using [virtiofsd](https://gitlab.com/virtio-fs/virtiofsd). This does require little extra setup than `9p`, `sshfs` or `nfs` but this provides near native performance which is essential for IO intensive workload of yocto build.

To get started with virtiofsd, first you need see if the `uid,gid` of your host system account matches with VM's `uid,gid`. The VM is fresh and there is only one user so the `uid,gid` will be `1000,1000`. But on host machine it could be different, if so then we'll have to add manually map them.

Check your `uid,gid` by running the `id` command, they should be 1000 like `uid=1000(anurag) gid=1000(anurag) groups=1000(anurag)`.

#### If your `uid,gid` is 1000
```sh
/usr/lib/virtiofsd \
  --socket-path=/tmp/vm-share.sock \
  --shared-dir="$HOME/yocto"
```

#### If your `uid,gid` is not 1000
```sh
# replace <uid> and <gid> with output of id command

/usr/lib/virtiofsd \
  --socket-path=/tmp/vm-share.sock \
  --shared-dir="$HOME/yocto" \
  --sandbox namespace \
  --uid-map ":1000:<uid>:1:" \
  --gid-map ":1000:<gid>:1:"
```

Now your virtiofsd deamon should be active, now start you qemu with following command.
```sh
qemu-system-x86_64 \
    -enable-kvm \
    -m 16G \
    -smp 10 \
    -hda ubuntu-disk.qcow2 \
    -vga virtio \
    -display default \
    -netdev user,id=net0,hostfwd=tcp::2222-:22 \
    -device e1000,netdev=net0 \
    -object memory-backend-memfd,id=mem,size=16G,share=on \
    -numa node,memdev=mem \
    -chardev socket,id=char0,path=/tmp/vm-share.sock \
    -device vhost-user-fs-pci,chardev=char0,tag=myfs
```
* **`-object memory-backend-memfd,id=mem,size=16G,share=on`**: Creates a memory backend (`mem`) with 16GB of shared memory.
* **`-numa node,memdev=mem`**: Configures a NUMA node and assigns the `mem` memory backend to it.
* **`-chardev socket,id=char0,path=/tmp/vm-share.sock`**: Creates a Unix socket (`char0`) at `/tmp/vm-share.sock` for communication.
* **`-device vhost-user-fs-pci,chardev=char0,tag=myfs`**: Attaches a shared filesystem device (`vhost-user-fs-pci`) using the socket `char0`, tagged as `myfs`.

If you get following error, make sure to change the ram size matches in line `-object memory-backend-memfd,id=mem,size=16G,share=on`
```
qemu-system-x86_64: total memory for NUMA nodes (0x400000000) should equal RAM size (0x100000000)
```

Now get inside VM using the VM window or by ssh
```sh
# Mount the shared directory
sudo mount -t virtiofs myfs yocto

# now if you ls in yocto you should see the disk image we created for ubuntu VM
ls yocto
ubuntu-disk.qcow2

```

