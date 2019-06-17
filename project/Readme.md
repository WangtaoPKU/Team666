## 第四章 项目实现 
我们将搭建一个简便、实用的 NAS 云盘系统，在这个中心化的存储系统中存储数据，并且让它每晚都会自动的备份增量数据，我们将利用 NFS 文件系统将磁盘挂载到同一网络下的不同设备上，使用 Nextcloud 来离线访问数据、分享数据，并结合transmission作为下载机。 
#### 1 准备USB磁盘驱动器 
为了更好地读写数据，我们建议使用 `ext4` 文件系统去格式化磁盘。首先，必须先找到连接到树莓派的磁盘。可以在 `/dev/sd/<x>` 中找到磁盘设备。使用命令 `fdisk -l`，可以找到刚刚连接的USB 磁盘驱动器。请注意，操作下面的步骤将会清除 USB 磁盘驱动器上的所有数据，请做好备份。
```
pi@raspberrypi:~ $ sudo fdisk -l
<...>
Disk /dev/sda: 931.5 GiB, 1000204886016 bytes, 1953525168 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xe8900690
Device     Boot Start        End    Sectors   Size Id Type
/dev/sda1        2048 1953525167 1953523120 931.5G 83 Linux
Disk /dev/sdb: 931.5 GiB, 1000204886016 bytes, 1953525168 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x6aa4f598
Device     Boot Start        End    Sectors   Size Id Type
/dev/sdb1  *     2048 1953521663 1953519616 931.5G  83 Linux
``` 
由于这些设备是连接到树莓派的唯一的磁盘，所以我们可以很容易的辨别出` /dev/sda` 和 `/dev/sdb` 就是那两个 USB 磁盘驱动器。每个磁盘末尾的分区表提示了在执行以下的步骤后如何查看，这些步骤将会格式化磁盘并创建分区表。为每个 USB 磁盘驱动器按以下步骤进行操作。  
（1）删除磁盘分区表   
创建一个新的并且只包含一个分区的新分区表。在 `fdisk` 中，你可以使用交互单字母命令来告诉程序你想要执行的操作。只需要在提示符 `Command(m for help):` 后输入相应的字母即可（可以使用` m` 命令获得更多详细信息）
```
pi@raspberrypi:~ $ sudo fdisk /dev/sda
Welcome to fdisk (util-linux 2.29.2).
Changes will remain in memory only, until you decide to write them.
Be careful before using the write command.
Command (m for help): o
Created a new DOS disklabel with disk identifier 0x9c310964.
Command (m for help): n
Partition type
   p   primary (0 primary, 0 extended, 4 free)
   e   extended (container for logical partitions)
Select (default p): p
Partition number (1-4, default 1):
First sector (2048-1953525167, default 2048):
Last sector, +sectors or +size{K,M,G,T,P} (2048-1953525167, default 1953525167):
Created a new partition 1 of type 'Linux' and of size 931.5 GiB.
Command (m for help): p
Disk /dev/sda: 931.5 GiB, 1000204886016 bytes, 1953525168 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x9c310964
Device     Boot Start        End    Sectors   Size Id Type
/dev/sda1        2048 1953525167 1953523120 931.5G 83 Linux
Command (m for help): w
The partition table has been altered.
Syncing disks.
 ```
（2）格式化新建分区  
我们将用` ext4` 文件系统格式化新创建的分区` /dev/sda1` 
```
pi@raspberrypi:~ $ sudo mkfs.ext4 /dev/sda1  
mke2fs 1.43.4 (31-Jan-2017)  
Discarding device blocks: done  
<...>  
Allocating group tables: done  
Writing inode tables: done  
Creating journal (1024 blocks): done  
Writing superblocks and filesystem accounting information: done
```
（3）建立标签   
重复以上步骤后，我们根据用途来对它们建立标签   
```
pi@raspberrypi:~ $ sudo e2label /dev/sda1 data  
pi@raspberrypi:~ $ sudo e2label /dev/sdb1 backup 
```
（4）创建挂载点   
安装 `autofs` 并创建挂载点   
```
pi@raspberrypi:~ $ sudo apt install autofs  
pi@raspberrypi:~ $ sudo mkdir /nas
```
（5）挂载设备   
添加下面这行来挂载设备 `/etc/auto.master `   
`/nas    /etc/auto.usb`   
如果不存在以下内容，则创建 `/etc/auto.usb`，然后重新启动 `autofs` 服务  
```
data -fstype=ext4,rw :/dev/disk/by-label/data   
backup -fstype=ext4,rw :/dev/disk/by-label/backup   
pi@raspberrypi3:~ $ sudo service autofs restart   
```
（6）确认是否挂载成功   
```
pi@raspberrypi3:~ $ cd /nas/data  
pi@raspberrypi3:/nas/data $ cd /nas/backup  
pi@raspberrypi3:/nas/backup $ mount  
<...>  
/etc/auto.usb on /nas type autofs   (rw,relatime,fd=6,pgrp=463,timeout=300,minproto=5,maxproto=5,indirect)  
<...>  
/dev/sda1 on /nas/data type ext4 (rw,relatime,data=ordered)  
/dev/sdb1 on /nas/backup type ext4 (rw,relatime,data=ordered)
```
进入对应目录以确保 `autofs `能够挂载设备。`autofs` 会跟踪文件系统的访问记录，并随时挂载所需要的设备。然后 `mount` 命令会显示这两个 USB 磁盘驱动器已经挂载到我们想要的位置了。   
#### 2 挂载网络设备    
（1）安装NFS服务器    
设置了基本的网络存储，我们希望将它安装到远程 Linux 机器上。这里使用 NFS 文件系统，首先在树莓派上安装 NFS 服务器   
`pi@raspberrypi:~ $ sudo apt install nfs-kernel-server`  
（2）添加允许访问目录   
需要告诉 NFS 服务器公开` /nas/data` 目录，这是从树莓派外部可以访问的唯一设备（另一个用于备份）。编辑 `/etc/exports` 添加如下内容以允许所有可以访问 NAS 云盘的设备挂载存储   
`/nas/data *(rw,sync,no_subtree_check)`   
经过上面的配置，任何人都可以访问数据，只要他们可以访问 NFS 所需的端口：111 和 2049。我通过上面的配置，只允许通过路由器防火墙访问到我的家庭网络的 22 和 443 端口。这样，只有在家庭网络中的设备才能访问 NFS 服务器   
#### 3 实现BT下载   
（1）安装Transmission   
`sudo apt-get install transmission-daemon`  
在移动硬盘上创建两个文件夹Download和DownloadCache   
（2）配置权限   
`sudo usermod -a -G debian-transmission pi`  
修改配置文件  
```
/etc/transmission-daemon/settings.json  
已完成的目录  
"download-dir": "/media/usbhdd/Download",  
未完成的目录  
"incomplete-dir": "/media/usbhdd/DownloadCache",  
允许Web访问的白名单地址  
"rpc-whitelist": "*.*.*.*",
```
（3）重启服务 
```
sudo service transmission-daemon reload  
sudo service transmission-daemon restart
```
然后在浏览器中访问IP/域名加 9091端口输入用户名和密码，默认都是：transmission   
修改用户名和密码的方法：   
先停止服务： `sudo service transmission-daemon stop`  
修改配置文件，下面两项分别是用户和密码，直接把密码改为你想要的密码明文就可以：
```
“rpc-username”: “transmission”,  
“rpc-password”: “{2dc2c41724aab07ccc301e97f56360cb35f8ba1fGVVrdHDX”, 
```
再次启动服务 ：`sudo service transmission-daemon start`，启动的时候transmission会自动把新密码加密。  
