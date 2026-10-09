FROM rust:1.86-bookworm AS builder
WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY profiles ./profiles

RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/target/release/oceancore-edge-node /usr/local/bin/oceancore-edge-node
COPY profiles ./profiles

ENTRYPOINT ["/usr/local/bin/oceancore-edge-node"]
