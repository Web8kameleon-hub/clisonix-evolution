# Tide Protocol Specification v0.1

Date: 2026-04-16
Status: Draft for implementation
Rule: Protocol claims must be testable with replayable evidence.

## 1. Purpose

Tide protocol coordinates deterministic sync between edge nodes and control plane with signed state transitions.

## 2. Core Properties

- Deterministic ordering
- Replay resistance
- Signed envelope integrity
- Policy-bound application of state

## 3. Message Envelope

Required fields:

- schema_version
- node_id
- sequence_number
- monotonic_counter
- tide_phase
- event_time_utc
- payload_hash
- policy_epoch
- signature_alg
- signature

## 4. Validation Rules

A message is valid only if:

- Signature verifies against trusted identity
- sequence_number is strictly increasing per node stream
- monotonic_counter not lower than last accepted value
- policy_epoch compatible with current control-plane policy
- event_time within permitted skew window

## 5. Replay Protection

Reject message when:

- Duplicate sequence_number for same node_id
- Stale monotonic_counter
- Reused nonce where nonce is required by profile

Each rejection must emit an auditable reason code.

## 6. Tide Phases

Minimum phase states:

- CALM: normal synchronization
- SURGE: increased update cadence
- QUARANTINE: restricted apply path

Phase transitions are control-plane policy events and must be signed.

## 7. Error Codes

- TIDE_E_SIG_INVALID
- TIDE_E_SEQ_REPLAY
- TIDE_E_COUNTER_STALE
- TIDE_E_POLICY_MISMATCH
- TIDE_E_TIME_SKEW

## 8. Conformance Tests (v0.1)

Required tests:

- Valid signed message acceptance
- Signature tamper rejection
- Replay message rejection
- Out-of-order sequence rejection
- Policy epoch mismatch rejection

No protocol release without passing all conformance tests.

## 9. Evidence Requirements

For each test suite run, archive:

- Input vectors
- Validation logs
- Rejection reason distribution
- UTC timestamp and operator ID

## 10. Implementation Note

Protocol libraries may exist in multiple languages, but all must conform to the same canonical field definitions and validation semantics.
