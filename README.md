# Socket编程实验报告


## 摘要
&#160; &#160; &#160; &#160;基于Socket编程的基本原理和开发流程，本文设计并实现了基于单播和组播的多人聊天工具，以及基于组播的视频会议软件。本次Socket网络可视化编程的开发平台为Python + Qt。通过对两款软件的开发，深入理解了Socket编程的过程细节和核心思想。

## 1 多人聊天工具的开发
### 1.1 多人聊天工具设计思想
&#160; &#160; &#160; &#160;多人聊天工具的关键功能是，当若干人加入同一聊天集合后，任意成员发言，集合中的所有人都能收到。在此，实验基于单播和组播两种不同的方式设计多人聊天工具。在都达到多人聊天目的的前提下，理解单播与组播的共性及各自的优缺点。
#### 1.1.1 基于单播的多人聊天
&#160; &#160; &#160; &#160;基于单播的多人聊天可采取两种方式实现：
* 第一种，每个用户都记录下所有用户的地址，单个用户每次发送聊天消息都必须发送到所有用户地址。显然，每个用户保存所有用户的地址既不利于空间管理、又会引发安全问题。
* 第二种，采用客户端/服务器的模式，即额外引入一台服务器，每个用户都作为客户端。用户将数据发送给服务器，服务器再转发给其他所有用户。

&#160; &#160; &#160; &#160;显然，第二种方案既方便管理，又有助于提升安全性，正是本次多人聊天工具采用的开发方式。并且，为了进一步提高可靠性，实验中采用TCP包传输聊天数据。
#### 1.1.2 基于组播的多人聊天
&#160; &#160; &#160; &#160;基于UDP包的组播传输多人聊天数据，即把所有用户加入同一组播组，任一用户的聊天信息数据包都发送到组播地址，这样便能顺利地到达所有加入了该组播组的主机并被用户接收。另外，可以禁止组播回传造成的额外开销。
### 1.2 多人聊天工具的实现
&#160; &#160; &#160; &#160;基于Socket的多人聊天程序流程可以依次分为以下6个部分：
> 配置Socket并监听 -> 编码用户输入 -> 传输数据包 -> 接收数据包 -> 展示收到内容 -> 关闭程序。

&#160; &#160; &#160; &#160;单播与组播程序在第2部分编码用户输入数据、及第5部分展示收到内容两个部分代码相同，所以只对其他3个部分进行两种不同播的实现说明。
#### 1.2.1 配置Socket并监听
* 单播：
```
    def initUnicast(self):
        s1 = socket.socket()
        s1.connect(('localhost', 2333))
        return s1
```
* 多播：
```
    def initMulticast(self):
        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
        s2.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        s2.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 0)
        s2.bind(('', 23333))
        intf = socket.gethostbyname(socket.gethostname())
        s2.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,
                      socket.inet_aton(intf) + socket.inet_aton('0.0.0.0'))
        s2.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                      socket.inet_aton('239.0.0.222') + socket.inet_aton('0.0.0.0'))
```

#### 1.2.2 编码用户输入
```
        text = self.input.text()
        text = unicode(text.toUtf8(), 'utf-8', 'ignore')
        data = text.encode("utf-8")
```

#### 1.2.3 传输数据包
* 单播（客户端发送后需服务器转发）：
  * 客户端发送
```
self.s1.send(data)
```
  * 服务器转发
```
    r, w, e = select.select(users, [], [])
        for temp in r:
            if temp is s:
                newer(s)
            else:
                disconnect = False
                try:
                    data = temp.recv(1024)
                    data = names[temp] + ': ' + data
                except socket.error:
                    disconnect = True
                if disconnect:
                    users.remove(temp)
                    del names[temp]
                else:
                    print data
                    for user in users:
                        if user != temp and user != s:
                            user.send(data)
```
* 多播（只需客户端发送组播）：
```
        self.s2.sendto(data, ('239.0.0.222', 23333))
        self.chat.append(data)
        self.input.clear()
        self.flag = 'multicast'
```

#### 1.2.4 接收数据包
* 单播：
```
        r, w, e = select.select([self.s1], [], [])
        if self.s1 in r:
            data = self.s1.recv(1024)
```
* 多播：
```
        data, sender_addr = self.s2.recvfrom(1024)
```

#### 1.2.5 展示收到内容
```
        self.chat.append(data)
```

#### 1.2.6 关闭程序
* 使用组播传输时，需先退出多播组
```
    s.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP,
                 socket.inet_aton(addr) + socket.inet_aton('0.0.0.0'))
```
* 然后关闭Socket
```
s.close()
```

### 1.3 多人聊天工具示意图

![多人聊天工具运行图](http://upload-images.jianshu.io/upload_images/177786-85495a50cb265103.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


## 2 视频会议软件的开发
### 2.1 视频会议软件设计思想
&#160; &#160; &#160; &#160;视频会议软件基于UDP组播进行数据包的传输。由于视频的本质就是多帧图像和音频流的组合，我们不传输视频格式文件，而是传输另外两类数据包，分别是图像包和音频包。实验通过等间隔时间采集图像帧和音频流，并发送给组播组内的所有用户，在其他用户处显示图像帧、播放音频流，以达到播放视频的同等效果。
### 2.2 视频会议软件的实现
&#160; &#160; &#160; &#160;整个视频会议软件的程序流程可以依次分为以下6个部分：
> 配置Socket并监听 -> 采集图像声音 -> 传输数据包 -> 接收数据包 -> 播放图像声音 -> 关闭程序。

&#160; &#160; &#160; &#160;流程中1、3、4、6部分与上一节中基于组播的多人聊天会议类似在此我们不再赘述这部分的关键代码。值得注意的是，虽然我们将连续的视频离散为了等间隔时间的图像声音，然而为了保证视频会议的流畅性，传输的稳定性和时效性需要得到更强的保证。
&#160; &#160; &#160; &#160;在第2和第5部分中，为实现其等间隔采集并播放图像及声音的功能，实验中额外使用了Python中的图像库pygame和音频库pyaudio。接下来我们重点阐述这两部分功能实现的核心代码。

#### 2.2.1 采集图像
```
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0", size)
cam.start()
image = cam.get_image()
image = pygame.transform.scale(image, size)
data = pygame.image.tostring(image, 'RGB')
```
#### 2.2.2 播放图像
```
pygame.init()
size = (128, 96)
image = pygame.image.fromstring(data, size, 'RGB')
image = pygame.transform.scale(image, (320, 240))
screen.blit(image, (0, 0))
```

#### 2.2.3 采集音频流
```
pin = pyaudio.PyAudio()
streamin = pin.open(format=pyaudio.paInt16, channels=1, rate=framerate,
                    input=True, frames_per_buffer=NUM_SAMPLES)
```

#### 2.2.4 播放音频流
```
pout = pyaudio.PyAudio()
streamout = pout.open(format=pyaudio.paInt16, channels=1, rate=framerate, output=True)
data = stream.read(NUM_SAMPLES)
stream.write(data)
```

### 2.3 视频会议软件示意图
![视频会议软件运行图](http://upload-images.jianshu.io/upload_images/177786-ad96ef2c1e1a1723.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### 3 总结
&#160; &#160; &#160; &#160;通过使用Python语言实现Socket编程，使用Qt创造可视化界面，基于单播和组播的多人聊天工具，以及基于组播的视频会议软件被成功开发出来。但不可否认的是，在界面优化、缓存利用、数据传输、性能稳定等诸多方面，这两款软件都有很多可以改进的空间，以待后续研究。
