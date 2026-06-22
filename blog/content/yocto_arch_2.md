+++
title = "Yocto setup on Arch linux Pt 2"
date = 2026-05-19

[taxonomies]
tags = ["yocto", "linux", "beaglebone"]
+++

In part 1 we setup the build environment for yocto build. In this part we actually setup yocto and do our basic build. Before we do there is a small update. When I was trying to build yocto I was hitting an error `OSError: [Errno 23] Too many open files in system` after 3-5 minutes after starting the build. Aparently `virtiofs` daemon keeps the file descriptor open on host system even after the VM has closed it. I had a discussion about this on a gitlab issue you can checkout [here](https://gitlab.com/virtio-fs/virtiofsd/-/work_items/202). TLDR is to use `--inode-file-handles=mandatory`


> WARNING: this flag needs to be run as `sudo` so the `qemu` command also needs to be run as `sudo` else you get error `Failed to connect to '/tmp/vm-share.sock': Permission denied`


<!-- more -->

So new `virtiofsd` commands would be following
```sh
# If your `uid,gid` is 1000
sudo /usr/lib/virtiofsd \
  --inode-file-handles=mandatory \
  --socket-path=/tmp/vm-share.sock \
  --shared-dir="$HOME/yocto"

# If your `uid,gid` is not 1000
sudo /usr/lib/virtiofsd \
  --inode-file-handles=mandatory \
  --socket-path=/tmp/vm-share.sock \
  --shared-dir="$HOME/yocto" \
  --sandbox namespace \
  --uid-map ":1000:<uid>:1:" \
  --gid-map ":1000:<gid>:1:"
```

## fstab entry for automount
The part 1 we ended by mounting the `virtiofs` shared partition. This can get annoying as you have to type the mount command each time you start the VM. So we setup fstab entry for it to automount.

1. Start the virtiofsd `/usr/lib/virtiofsd --socket-path=/t..`
2. Start the VM `qemu-system-x86_64 -enable-kvm...`
3. SSH into the VM `ssh vmUsername@localhost -p 2222`
4. Open fstab file in editor: `vim /etc/fstab`
5. Add following at the end, make sure to replace the username
    ```sh
    myfs   /home/<vmUsername>/yocto   virtiofs   defaults   0   0
    ```
6. Evaluate the mounts: `sudo mount -a`
7. Verify mount: `sudo mount | grep virtiofs`

# Yocto build
Now its time to do a yocto build for beaglebone black

## Setup poky
> All the commands are supposed to be run on HOST machine. For VM it will be specified

1. We'll get the `poky` sources for `scarthgap`. 
    ```sh
    # cd into the yocto dir
    cd ~/yocto
    
    # clone poky
    git clone -b scarthgap https://git.yoctoproject.org/poky
    ```

2. Switch to VM and source the `oe-init-build-env`. 
    ```sh
    # RUN in VM
    cd ~/yocto/poky
    
    # I like to keep the build outside the poky dir, thats why ../build
    source oe-init-build-env ../build
    ```
3. Now on host machine, we can look into the `local.conf` file and change the machine to `beaglebone black`
    ```sh
    # cd into the yocto conf dir
    cd ~/yocto/build/conf
    
    # open the local.conf in editor
    vim local.conf
    
    # Look for following line, it will be commented. Uncomment it
    MACHINE ?= "beaglebone-yocto"
    ```
4. We are finally good to start the build. Switch back to VM and start the build
    ```sh
    # RUN in VM
    
    # Invoke bitbake to build the core-image-minimal
    # The -k flag keeps the build to continue if some error occur
    bitbake -k core-image-minimal
    ```

## core-image-minimal build
If you did everything right you should see following when start `bitbake`.
```yaml
Build Configuration:
BB_VERSION           = "2.8.1"
BUILD_SYS            = "x86_64-linux"
NATIVELSBSTRING      = "universal"
TARGET_SYS           = "arm-poky-linux-gnueabi"
MACHINE              = "beaglebone-yocto"
DISTRO               = "poky"
DISTRO_VERSION       = "5.0.18"
TUNE_FEATURES        = "arm vfp cortexa8 neon callconvention-hard"
TARGET_FPU           = "hard"
meta                 
meta-poky            
meta-yocto-bsp       = "scarthgap:44dcf08572ce391d7c0df4f8c7510af5e096baca"
```
Make sure you have `MACHINE = "beaglebone-yocto"`. If you do **CONGRATULATIONS 🎉** you have the correct setup. Now its going to build over 4K packages so gonna take a while.

> If you build fails for some reason, mostly likely it will be fine, you just need to restart the build. In some cases you get repeated error from a particular package, you just clean it and redo the build `bitbake -c cleansstate <package_name>`
