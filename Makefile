APP_NAME = walter
PREFIX = /opt/mine

CUR_DIR = $(shell pwd)

default: build/$(APP_NAME)

CFLAGS := -Wall -Wextra -Wshadow -Wno-type-limits -g3 -O0 -Wpointer-arith -fvisibility=hidden

CFLAGS += -DAPP_NAME=\"$(APP_NAME)\"

build/$(APP_NAME): main.c
	mkdir -p $(@D)
	gcc -g $^ $(CFLAGS) -o $@

install: build/$(APP_NAME)
	mkdir -p $(PREFIX)/bin
	install -c build/$(APP_NAME) $(PREFIX)/bin/

clean:
	rm -rf build/
