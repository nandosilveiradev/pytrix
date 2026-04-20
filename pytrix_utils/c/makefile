# PX-CODE Makefile
CC      = gcc
TARGET  = px-code
SRC     = px-code.c

# Auto-detect OS for linker flags
UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
    LDFLAGS = -lutil
else
    LDFLAGS = -lutil
endif

CFLAGS  = -O3 -march=native -Wall -Wextra -Wno-unused-parameter \
          -fomit-frame-pointer -funroll-loops

.PHONY: all clean install

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)
	@echo "Build OK → ./$(TARGET)"

# Debug build with sanitizers
debug: $(SRC)
	$(CC) -g -fsanitize=address,undefined -o $(TARGET)_debug $(SRC) $(LDFLAGS)

install: $(TARGET)
	@mkdir -p ~/.local/bin
	cp $(TARGET) ~/.local/bin/$(TARGET)
	@echo "Installed to ~/.local/bin/$(TARGET)"
	@echo "Make sure ~/.local/bin is in your PATH"

clean:
	rm -f $(TARGET) $(TARGET)_debug
