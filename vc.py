import socket
import time
import sys
import pygame
import pygame.camera
import pyaudio


# sudo route add -net 239.192.0.0 netmask 255.255.0.0 dev enp0s25
port = 23333
addr = "239.192.0.233"
buf_size = 65536

pygame.init()
pygame.camera.init()
size = (128, 96)
cam = pygame.camera.Camera("/dev/video0", size)

NUM_SAMPLES = 2000
framerate = 8000
channels = 1
sampwidth = 2
sleep_time = 0.25

pin = pyaudio.PyAudio()
streamin = pin.open(format=pyaudio.paInt16, channels=1, rate=framerate,
                    input=True, frames_per_buffer=NUM_SAMPLES)
pout = pyaudio.PyAudio()
streamout = pout.open(format=pyaudio.paInt16, channels=1, rate=framerate,
                      output=True)

TYPE = 3


def init():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass
    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
    s.bind(('', port))
    intf = socket.gethostbyname(socket.gethostname())
    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf) + socket.inet_aton('0.0.0.0'))
    s.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(addr) + socket.inet_aton('0.0.0.0'))
    return s


def record(s, stream):
    if TYPE & 1:
        # video
        image = cam.get_image()
        image = pygame.transform.scale(image, size)
        data = pygame.image.tostring(image, 'RGB')
        s.sendto(data, (addr, port))
    if TYPE & 2:
        # audio
        data = stream.read(NUM_SAMPLES)
        s.sendto(data, (addr, port))


def play(s, screen, stream):
    for i in range((TYPE+1)/2):
        data, sender_addr = s.recvfrom(buf_size)
        # print len(data), sender_addr
        if TYPE & 1 and len(data) > NUM_SAMPLES*sampwidth:
            # video
            image = pygame.image.fromstring(data, size, 'RGB')
            image = pygame.transform.scale(image, (320, 240))
            screen.blit(image, (320*(int(sender_addr[0][-1])-1), 0))
            pygame.display.flip()
        if TYPE & 2 and len(data) == NUM_SAMPLES*sampwidth and sender_addr[0][-1] != '1':
            # audio
            stream.write(data)


def chat(s):
    cam.start()
    screen = pygame.display.set_mode([640, 240])
    while True:
        record(s, streamin)
        play(s, screen, streamout)
        time.sleep(sleep_time)


def close(s):
    s.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP,
                 socket.inet_aton(addr) + socket.inet_aton('0.0.0.0'))
    s.close()
    cam.stop()
    pygame.quit()
    sys.exit()
    streamin.stop_stream()
    streamin.close()
    pin.terminate()
    streamout.stop_stream()
    streamout.close()
    pout.terminate()


def main():
    s = init()
    chat(s)
    close(s)


if __name__ == '__main__':
    main()