+++
title = "Yocto setup on Arch linux"
date = 2025-03-25

[taxonomies]
tags = ["yocto", "linux", "beaglebone"]
+++

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
# Set the processor core count and memory according to your pc, I have kep 6 core and 16GB memory
# Set the path for your ubuntu-server.iso
qemu-system-x86_64 \
    -enable-kvm \
    -m 16000 \
    -smp 6 \
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
- **`-m 16000`**: Allocates 16 GB (16000 MB) of RAM to the virtual machine.  
- **`-smp 6`**: Assigns 6 CPU cores to the virtual machine.  
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
    -m 16000 \
    -smp 6 \
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
    -m 20000 \
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

Congrats, you got ssh working, how time to have shared directory. But why Set Up a Shared Directory Between the Host and Ubuntu VM for Yocto?  
1. **Limited VM Storage**: The VM has only 20GB of space, while a Yocto build can exceed 100-200GB. Storing the build on the host prevents running out of space.  
2. **Persistence Across VMs**: Since all Yocto files remain on the host, you can delete or recreate VMs without affecting your Yocto setup.  
3. **Seamless Editing & Development**: Easily edit files from your host system using your preferred tools without needing to transfer files manually.  
4. **Immediate Access to Build Outputs**: Once the Ubuntu VM completes the Yocto build, the generated Linux images are instantly accessible on your host PC.  

The shared directory will be like this `(HOST)~/yocto <-> (VM)~/yocto`

```sh
# Stop your VM and rerun with following argument
qemu-system-x86_64 \
    -enable-kvm \
    -m 20000 \
    -smp 10 \
    -hda ubuntu-disk.qcow2 \
    -vga virtio \
    -display default \
    -netdev user,id=net0,hostfwd=tcp::2222-:22 \
    -device e1000,netdev=net0 \
    -virtfs local,path=$HOME/yocto,security_model=mapped,mount_tag=myshare,id=share0

```
- **`-virtfs local,path=$HOME/yocto,security_model=mapped,mount_tag=myshare,id=share0`**: Shares the `~/yocto` directory with the VM using `virtfs` (9p filesystem) under the mount tag `myshare`, mapping file ownership.

Now get inside VM using the VM window or by ssh
```sh
# Mount the shared directory
sudo mount -t 9p -o trans=virtio myshare yocto

# now if you ls in yocto you should see the disk image we created for ubuntu VM
ls yocto
ubuntu-disk.qcow2

# Now if the mount succeeded, Congrats. But you'll have to do this each time your start your VM
# To make this mouting process automatic, we need to a mounty entry in /etc/fstab
sudo nano /etc/fstab

# add Folling line at the end and save and quit
myshare  /home/anurag/yocto  9p  trans=virtio,version=9p2000.L,cache=loose  0  0

# now reboot the VM and your should see it being auto mounted
sudo reboot
```

## Yocto Setup
Finally, after all this setup, we can go for yocto build.
I recommend having two tabs on your terminal, tab1 for host system where you'll edit files and one tab2 which is sshed into VM for building
```sh
#[VM] Get inside VM and install packages needed for building yocto
sudo apt install build-essential chrpath cpio debianutils diffstat file gawk gcc git iputils-ping libacl1 liblz4-tool locales python3 python3-git python3-jinja2 python3-pexpect python3-pip python3-subunit socat texinfo unzip wget xz-utils zstd

#[VM] clone poky
cd yocto
git clone git://git.yoctoproject.org/poky -b styhead
cd poky
source oe-init-build-env
```
After you run the source command, it will create a new `build` directory and here will have build artifacts and configuration. The default machine is `qemux86-64` we want to change it to `qemuarm64` because beaglebone is also a ARM system so the builds created for qemuarm64 will be reused for beaglebone build later.
```sh
#[HOST] On your host pc open following for editing, in my case I use neovim
nvim ~/yocto/poky/build/conf/local.conf

# GOTO line 39 and comment out MACHINE ??= "qemux86-64"
# GOTO line 32 and uncomment MACHINE ?= "qemuarm64"
# save and quit
```

Now finally on your VM time to build the image
```sh
cd ~/yocto/poky
source oe-init-build-env
bitbake core-image-minimal -k
```

After some load you must see the build configuration like follows and the build should start
```
Build Configuration:
BB_VERSION           = "2.9.1"
BUILD_SYS            = "x86_64-linux"
NATIVELSBSTRING      = "universal"
TARGET_SYS           = "aarch64-poky-linux"
MACHINE              = "qemuarm64"
DISTRO               = "poky"
DISTRO_VERSION       = "5.1.3"
TUNE_FEATURES        = "aarch64 crc cortexa57"
TARGET_FPU           = ""
meta                 
meta-poky            
meta-yocto-bsp       = "my-styhead:11a8dec6e29ac0b2fd942c0fc00dd7fc30658841"
```
**Note:** You may see following error when build starts, its happening in ubuntu24
```py
Traceback (most recent call last):
  File "/home/anurag/yocto/poky/bitbake/bin/bitbake-worker", line 278, in child
    bb.utils.disable_network(uid, gid)
  File "/home/anurag/yocto/poky/bitbake/lib/bb/utils.py", line 1696, in disable_network
    with open("/proc/self/uid_map", "w") as f:
PermissionError: [Errno 1] Operation not permitted

ERROR: Task (/home/anurag/yocto/poky/meta/recipes-core/glibc/glibc_2.40.bb:do_install) failed with exit code '1'
```
Easiest fix I found is running following, but you'll have to run it each time your VM reboots. If you find any better solution, let me know :)
```sh
sudo apparmor_parser -R /etc/apparmor.d/unprivileged_userns

# Restart the build
bitbake core-image-minimal -k
```
Now you may wanna go do something else as this will take from 2-4 hours based on your system configuration.
