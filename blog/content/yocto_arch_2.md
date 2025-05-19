+++
title = "Yocto setup on Arch linux Pt. 2"
date = 2025-05-07

[taxonomies]
tags = ["yocto", "linux", "beaglebone"]
+++

## Yocto Setup
Finally, after all this setup, we can go for yocto build. But sadly there one another problem we need to fix. If you use this setup and try to build yocto, in just few moments your build will start to fail all stating one error: `Too many files open`. This is a kind of error you may have never seen on your computer. There is a limit on how many files a process can open at any given moment of time which is usually 1024 open file descriptors, you can check that by running `ulimit -n`.  But you might be thinking why are we hitting the limit, if you build yocto on a native ubuntu os, you will not hit this limit, but why on the VM. **Reason Vritiofs**. 

## Why does this happen?

When you run a Yocto build natively (on your host system), `bitbake` spawns multiple worker processes — typically as many as the number of CPU cores (`nproc`). Each of these workers handles tasks like configuration, compilation, and installation.

For example, during the compilation phase, each worker may run `make`, which in turn spawns compiler processes like `gcc` or `g++`. These compiler processes perform the actual file I/O independently. Since they are separate processes, each one opens and closes its own files, and file descriptors are handled cleanly. Even with dozens of simultaneous compilations, you rarely hit system file descriptor limits.

However, when you run the same build inside a **virtual machine** with a **Virtio-FS-mounted shared directory**, things change.

Inside the VM, the build still behaves the same — multiple parallel compiler processes run. But from the **host's perspective**, **all file access goes through a single `virtiofsd` process**. That means every file opened by any process inside the VM is opened on the host by `virtiofsd`.

Now here’s the catch: **by default**, `virtiofsd` **does not immediately close file descriptors on the host** even after they’ve been closed inside the VM. This leads to a buildup of open file descriptors on the host — potentially in the hundreds of thousands — until you eventually hit the system limit, and the build fails with a **"Too many open files"** error.


## How to fix this
There are two steps to fix this.

### 1. Increase the file descriptor limit
If you use systemd edit file `/etc/systemd/system.conf` with sudo, look for a line with `DefaultLimitNOFILE` replace with following. It will increase the limit to `100000` and it will give a lot of space for virtiofsd.
```
DefaultLimitNOFILE=100000
```

### 2. Run virtiofsd with `--inode-file-handles=mandatory`
Even if you increase the `ulimit` you still have the problem of virtiofsd not closing the file descriptor. So even if you increase the ulimit it just delays the problem. I was not able to find a solution to this until I asked in a [gitlab issue](https://gitlab.com/virtio-fs/virtiofsd/-/issues/202) and also thanks to [Hanna Czenczek](https://czenczek.de). To use `--inode-file-handles=mandatory` we need root preveliges.
```sh
# for gid/uid 1000 
sudo /usr/lib/virtiofsd \
  --inode-file-handles=mandatory \
  --socket-path=/tmp/vm-share.sock \
  --shared-dir="$HOME/yocto"

# for others
sudo /usr/lib/virtiofsd \
  --inode-file-handles=mandatory \
  --socket-path=/tmp/vm-share.sock \
  --shared-dir="$HOME/yocto" \
  --sandbox namespace \
  --uid-map ":1000:<uid>:1:" \
  --gid-map ":1000:<gid>:1:"
```

We will have to run `QEMU` with sudo aswell because it wont be able to connect to the root created socket.
```sh
sudo qemu-system-x86_64 \
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

And thats about it. Now you can ssh into the VM and mount the directory as you did previously.
```sh
# SSH from host
ssh vmUsername@localhost -p 2222

# AFter ssh, mount directory in the vm
sudo mount -t virtiofs myfs yocto
```

## Yocto Build

Now we are good to build yocto with no problem. I recommend having two tabs on your terminal, first `tab1` for host system where you'll edit files and second `tab2` which is sshed into VM for building
```sh
#[VM] Get inside VM and install packages needed for building yocto
sudo apt install build-essential chrpath cpio debianutils diffstat file gawk gcc git iputils-ping libacl1 liblz4-tool locales python3 python3-git python3-jinja2 python3-pexpect python3-pip python3-subunit socat texinfo unzip wget xz-utils zstd

#[VM] clone poky
cd ~/yocto
git clone git://git.yoctoproject.org/poky -b scarthgap
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
#[VM]
cd ~/yocto/poky
source oe-init-build-env
bitbake core-image-minimal -k
```

After some load you must see the build configuration like follows and the build should start
```
Build Configuration:
BB_VERSION           = "2.8.0"
BUILD_SYS            = "x86_64-linux"
NATIVELSBSTRING      = "universal"
TARGET_SYS           = "aarch64-poky-linux"
MACHINE              = "qemuarm64"
DISTRO               = "poky"
DISTRO_VERSION       = "5.0.9"
TUNE_FEATURES        = "aarch64 crc cortexa57"
TARGET_FPU           = ""
meta                 
meta-poky            
meta-yocto-bsp       = "scarthgap:9c63e0c9646c61663e8cfc6b4c75865cd0cd3b34"
```
**Note:** You may see following error when build starts, its happening in ubuntu24
```
ERROR: User namespaces are not usable by BitBake, possibly due to AppArmor.
See https://discourse.ubuntu.com/t/ubuntu-24-04-lts-noble-numbat-release-notes/39890#unprivileged-user-namespace-restrictions for more information.

Summary: There was 1 ERROR message, returning a non-zero exit code.
```
Easiest fix I found is running following, but you'll have to run it each time your VM reboots. If you find any better solution, let me know :)
```sh
sudo apparmor_parser -R /etc/apparmor.d/unprivileged_userns

# Restart the build
bitbake core-image-minimal
```
Now you may wanna go do something else as this will take from 2-4 hours based on your system configuration.

If your build failed, just rerun the bitbake build.

## Build Finish
Now that your build is finised, it should look like this with a success message
```
Build Configuration:
BB_VERSION           = "2.8.0"
BUILD_SYS            = "x86_64-linux"
NATIVELSBSTRING      = "universal"
TARGET_SYS           = "aarch64-poky-linux"
MACHINE              = "qemuarm64"
DISTRO               = "poky"
DISTRO_VERSION       = "5.0.9"
TUNE_FEATURES        = "aarch64 crc cortexa57"
TARGET_FPU           = ""
meta                 
meta-poky            
meta-yocto-bsp       = "scarthgap:9c63e0c9646c61663e8cfc6b4c75865cd0cd3b34"

Sstate summary: Wanted 0 Local 0 Mirrors 0 Missed 0 Current 1849 (0% match, 100% complete)#        | ETA:  0:00:00
Initialising tasks: 100% |#########################################################################| Time: 0:00:06
NOTE: Executing Tasks
NOTE: Tasks Summary: Attempted 4059 tasks of which 4059 didn't need to be rerun and all succeeded.
```

Now lets lets your yocto, switch back to your host pc.
```sh
# [HOST] cd inside the poky directory
cd ~/yocto/poky

# [HOST] source yocto, this will give access to runqemu command
source oe-init-build-env

# Run qemu with the fresh yocto created linux distribution, this will ask for sudo password
runqemu qemuarm64
```
And now a new qemu screen should appear with poky distribution.

{{image(src="/img/poky1.png", position="center")}}

Enter **root** as login username, there is no password, it should give you shell directly. To close give sigint in the terminal (Ctrl+c).

> Congratulations 🎉🎉, You just made linux destroution from scratch and run it under qemu.

# Simplification
Now its time to reduce the manual work.

1. Virtiofs daemon + Ubuntu VM Qemu, Create a file `startvm.sh` in ~/yocto and enter following in it
```sh
#!/bin/bash

# **** REPLACE FOLLOWING WITH YOUR VRIOFSD COMMAND AND ADD & *******
sudo /usr/lib/virtiofsd \
  --inode-file-handles=mandatory \
  --socket-path=/tmp/vm-share.sock \
  --shared-dir="$HOME/yocto" &

sudo qemu-system-x86_64 \
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
Now make the script executable, make sure you close the ubuntu vm. 
```sh
# Change permission to make the script executable
chmod +x startvm.sh

# Now from now on just need to run following to start the vm
./startvm.sh
```
 
2. Automount myfs in vm.
```sh
# in your vm edit file /etc/fstab
sudo vim /etc/fstab

# Add following line in the file, update the username in path
myfs	/home/anurag/yocto	virtiofs	defaults	0	0

# now we can test it by running following
sudo mount -a

# this should mount virtiofs, you can confirm by listing ~/yocto
ls ~/yocto
```

<h3>Now you are all set to start working on yocto</h3>
