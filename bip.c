#include <fcntl.h>
#include <linux/kd.h>
#include <sys/ioctl.h>
#include <unistd.h>

int main() {
    int fd = open("/dev/console", O_WRONLY);
    // 0x06370637: Frequência e duração para um bip de aviso
    ioctl(fd, KDMKTONE, 0x06370637); 
    close(fd);
    return 0;
}