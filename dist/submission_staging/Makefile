CC = gcc
CFLAGS = -Wall -Wextra -std=c17 -I src/core -I src/vehicle -I src/station -I src/charging -I src/auth -I src/safety -I src/simulation -I src/communication -I src/monitoring -I src/logging -I src/database -I src/utils
TARGET = bin/smart_ev
PYTHON ?= python
.DEFAULT_GOAL := all
.PHONY: verify-all model static-analysis sanitizer-test smt-test bmc-test test fuzz-test e2e-test

verify-all:
	$(PYTHON) scripts/verify_all.py

model static-analysis sanitizer-test smt-test bmc-test test fuzz-test e2e-test:
	$(PYTHON) scripts/verify_all.py --stage $@

SRC = $(wildcard src/core/*.c) \
      $(wildcard src/vehicle/*.c) \
      $(wildcard src/station/*.c) \
      $(wildcard src/auth/*.c) \
      $(wildcard src/charging/*.c) \
      $(wildcard src/safety/*.c) \
      $(wildcard src/communication/*.c) \
      $(wildcard src/logging/*.c) \
      $(wildcard src/monitoring/*.c) \
      $(wildcard src/simulation/*.c) \
      $(wildcard src/database/*.c) \
      $(wildcard src/utils/*.c) \
      src/main.c

all: build

build:
	mkdir -p bin
	$(CC) $(CFLAGS) $(SRC) $(LDFLAGS) -o $(TARGET)

clean:
	rm -rf bin

run: build
	./$(TARGET)

docker-up:
	docker compose up -d

docker-down:
	docker compose down
