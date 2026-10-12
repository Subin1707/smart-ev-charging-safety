FROM debian:bookworm-slim

RUN apt-get update && \
	apt-get install -y --no-install-recommends build-essential libpq-dev postgresql-client make ca-certificates && \
	rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN make clean && \
	make CFLAGS="-Wall -Wextra -std=c17 -DUSE_LIBPQ -I /usr/include/postgresql -I src/core -I src/vehicle -I src/station -I src/charging -I src/auth -I src/safety -I src/simulation -I src/communication -I src/monitoring -I src/logging -I src/database -I src/utils" \
		LDFLAGS="-lpq" \
		build

CMD ["./bin/smart_ev"]
