#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>

#define NB_SOLENOIDS 2

#define BUFFER_MAX 256

#define true 1
#define false 0

#define IN  "in"
#define OUT "out"

typedef unsigned int bool;

typedef struct
{
  int in1_pin;
  int in2_pin;
} Driver_Config;

static Driver_Config drivers [] =
{
  {
    /* Solenoid #0 */
    .in1_pin = 23,
    .in2_pin = 24
  },
  {
    /* Solenoid #1 */
    .in1_pin = 27,
    .in2_pin = 22
  }
};

static bool
_GPIOExport(int pin)
{
  char buffer[BUFFER_MAX];
  ssize_t bytes_written;
  int fd = open("/sys/class/gpio/export", O_WRONLY);

  if (-1 == fd)
  {
    fprintf(stderr, "Failed to open export for writing (pin %d)!\n", pin);
    return false;
  }

  bytes_written = snprintf(buffer, BUFFER_MAX, "%d", pin);
  write(fd, buffer, bytes_written);
  close(fd);
  return true;
}

static bool
_GPIOUnexport(int pin)
{
   char buffer[BUFFER_MAX];
   ssize_t bytes_written;

   int fd = open("/sys/class/gpio/unexport", O_WRONLY);
   if (-1 == fd)
   {
     fprintf(stderr, "Failed to open unexport for writing (pin %d)!\n", pin);
     return false;
   }

   bytes_written = snprintf(buffer, BUFFER_MAX, "%d", pin);
   write(fd, buffer, bytes_written);
   close(fd);
   return true;
}

static bool
_GPIOExists(int pin)
{
   char path[BUFFER_MAX];
   int fd;

   snprintf(path, BUFFER_MAX, "/sys/class/gpio/gpio%d/direction", pin);
   fd = open(path, O_WRONLY);
   if (fd != -1) close(fd);
   return (fd > 0);
}

static bool
_GPIODirection(int pin, const char *dir)
{
   char path[BUFFER_MAX];
   int fd;

   snprintf(path, BUFFER_MAX, "/sys/class/gpio/gpio%d/direction", pin);
   fd = open(path, O_WRONLY);
   if (-1 == fd)
   {
     fprintf(stderr, "Failed to open gpio %d direction for writing!\n", pin);
     return false;
   }

   if (-1 == write(fd, dir, strlen(dir)))
   {
     fprintf(stderr, "Failed to set %s directioni for pin %d!\n", dir, pin);
     return false;
   }

   close(fd);
   return true;
}

#if 0
static int
_GPIO_fd_get_for_interrupt(int pin)
{
   char path[BUFFER_MAX];
   int fd;

   snprintf(path, BUFFER_MAX, "/sys/class/gpio/gpio%d/edge", pin);
   fd = open(path, O_WRONLY);
   if (-1 == write(fd, "both", 5))
   {
     fprintf(stderr, "Failed to set the interrupt edge to 'both'!\n");
     close(fd);
     return false;
   }
   close(fd);

   snprintf(path, BUFFER_MAX, "/sys/class/gpio/gpio%d/value", pin);
   fd = open(path, O_RDONLY);
   if (-1 == fd)
   {
     fprintf(stderr, "Failed to open gpio value for reading!\n");
   }
   return fd;
}

static bool
_GPIORead(int pin, char *value)
{
   char path[BUFFER_MAX];
   int fd;

   *value = 0;

   snprintf(path, BUFFER_MAX, "/sys/class/gpio/gpio%d/value", pin);
   fd = open(path, O_RDONLY);
   if (-1 == fd)
     {
        fprintf(stderr, "Failed to open gpio value for reading!\n");
        return false;
     }
   if (-1 == read(fd, value, 1))
     {
        fprintf(stderr, "Failed to read value!\n");
        close(fd);
        return false;
     }

   close(fd);

   *value -= '0';
   return true;
}
#endif

static bool
_GPIOWrite(int pin, char value)
{
   static const char s_values_str[] = "01";

   char path[BUFFER_MAX];
   int fd;

   snprintf(path, BUFFER_MAX, "/sys/class/gpio/gpio%d/value", pin);
   fd = open(path, O_WRONLY);
   if (-1 == fd)
     {
        fprintf(stderr, "Failed to open gpio value for writing!\n");
        return false;
     }

   if (1 != write(fd, &s_values_str[value % 2], 1))
     {
        fprintf(stderr, "Failed to write value!\n");
        return false;
     }

   close(fd);
   return true;
}

static void
_driver_configure(int driver_id, int in1, int in2)
{
   printf("Driver %d In1 %d in2 %d\n", driver_id, in1, in2);
   _GPIOWrite(drivers[driver_id].in1_pin, !!in1);
   _GPIOWrite(drivers[driver_id].in2_pin, !!in2);
}

static void
_usage(void)
{
  fprintf(stderr, "%s start solenoid_id | stop solenoid_id | status\n", APP_NAME);
  fprintf(stderr, "  solenoid_id: 0..%d\n", NB_SOLENOIDS - 1);
}

int main(int argc, char **argv)
{
   int i;
   unsigned int sol_id;

   if (argc < 2)
   {
     _usage();
     return 1;
   }

   if (!strcmp(argv[1], "start") || !strcmp(argv[1], "stop"))
   {
     if (argc < 2)
     {
       _usage();
       return 1;
     }
     sol_id = strtoul(argv[2], NULL, 10);
     if (sol_id >= NB_SOLENOIDS)
     {
       _usage();
       return 1;
     }
   }

   /*
    * Enable GPIO pins
    */
   for (i = 0; i < NB_SOLENOIDS; i++)
   {
     if (!_GPIOExport(drivers[i].in1_pin) || !_GPIOExport(drivers[i].in2_pin)) goto end;
   }

   /*
    * Wait GPIO pins to be exported
    */
   for (i = 0; i < NB_SOLENOIDS; i++)
   {
     while (!_GPIOExists(drivers[i].in1_pin) || !_GPIOExists(drivers[i].in2_pin));
   }

   /*
    * Set GPIO directions
    */
   for (i = 0; i < NB_SOLENOIDS; i++)
   {
     if (!_GPIODirection(drivers[i].in1_pin, OUT) || !_GPIODirection(drivers[i].in2_pin, OUT)) goto end;
   }

   if (!strcmp(argv[1], "start"))
   {
     _driver_configure(sol_id, 0, 1);
     sleep(5); // TODO replace with wait until flow is constant and max time
     _driver_configure(sol_id, 0, 0);
   }

   if (!strcmp(argv[1], "stop"))
   {
     _driver_configure(sol_id, 1, 0);
     sleep(5); // TODO replace with wait until flow is zero and max time
     _driver_configure(sol_id, 0, 0);
   }
end:
   /*
    * Disable GPIO pins
    */
   for (i = 0; i < 2; i++)
   {
     _GPIOUnexport(drivers[i].in1_pin);
     _GPIOUnexport(drivers[i].in2_pin);
   }
   return 0;
}
