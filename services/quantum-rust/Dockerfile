FROM rust:1.87-bookworm AS builder

WORKDIR /build
COPY services/quantum-rust/Cargo.toml /build/Cargo.toml
COPY services/quantum-rust/src /build/src
RUN cargo build --release

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /build/target/release/clisonix-quantum-rust /usr/local/bin/clisonix-quantum-rust

ENV QUANTUM_UPSTREAM_URL=http://172.19.0.1:9080

EXPOSE 8008

CMD ["clisonix-quantum-rust"]
