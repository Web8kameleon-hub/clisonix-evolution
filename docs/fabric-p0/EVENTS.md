# CLX Events Integration (P0)

Ky dokument lidh Clisonix-cloud me kontraten `CLX Event v1`.

## Burimi kanonik

- Schema: `../kloud/docs/fabric-p0/contracts/clx-event-v1.schema.json`
- OpenAPI fragment: `../kloud/docs/fabric-p0/contracts/openapi-events-fragment.yaml`

## Kanale minimale

- `ai.requests`
- `ai.responses`
- `nodes.health`
- `nodes.jobs`
- `nodes.events`

## Evente kryesore

- `clx.llm.request`
- `clx.llm.response`
- `clx.node.heartbeat`
- `clx.node.degraded`
- `clx.job.assigned`
- `clx.job.completed`
- `clx.job.failed`

## Integrime detyruese

- Ingress validator: refuzo event pa `trace_id` ose `correlation_id`.
- DLQ policy: eventet e deshtuara kalojne ne dead-letter topic.
- Trace continuity: `trace_id` ruhet nga ingress deri ne response.

## Done when

- [ ] Cdo producer/consumer ne cloud perdor `CLX Event v1`.
- [ ] Validation middleware aktiv.
- [ ] DLQ aktiv per retry overflow.
- [ ] Testet trace continuity dhe retry kalojne.
