# syntax=docker/dockerfile:1
FROM rust:1.77 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bullseye-slim
WORKDIR /app
COPY --from=builder /app/target/release/sidecar /app/sidecar
COPY configs ./configs
CMD ["/app/sidecar"]
