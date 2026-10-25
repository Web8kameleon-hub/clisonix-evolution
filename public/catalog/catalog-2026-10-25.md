# Daily Public Package Catalog

Generated: 2026-10-25T06:14:48Z

## Summary
- npm packages (records/unique): 267/131
- PyPI packages (records/unique): 450/136
- Cargo/Carter packages (records/unique): 40/24
- API routes discovered: 1625
- Protocols discovered: 5
- Recursive scan files/directories/depth: 3794/816/11

## Download & Integration Quick Links
| ecosystem | package | download_url | install_command |
| --- | --- | --- | --- |
| npm | @aws-sdk/client-s3 | https://www.npmjs.com/package/@aws-sdk/client-s3 | npm i @aws-sdk/client-s3 |
| npm | @aws-sdk/s3-request-presigner | https://www.npmjs.com/package/@aws-sdk/s3-request-presigner | npm i @aws-sdk/s3-request-presigner |
| npm | @clisonix/shared | https://www.npmjs.com/package/@clisonix/shared | npm i @clisonix/shared |
| npm | @eslint/eslintrc | https://www.npmjs.com/package/@eslint/eslintrc | npm i @eslint/eslintrc |
| npm | @eslint/js | https://www.npmjs.com/package/@eslint/js | npm i @eslint/js |
| npm | @fastify/cors | https://www.npmjs.com/package/@fastify/cors | npm i @fastify/cors |
| npm | @fastify/rate-limit | https://www.npmjs.com/package/@fastify/rate-limit | npm i @fastify/rate-limit |
| npm | @fontsource/noto-color-emoji | https://www.npmjs.com/package/@fontsource/noto-color-emoji | npm i @fontsource/noto-color-emoji |
| npm | @jest/globals | https://www.npmjs.com/package/@jest/globals | npm i @jest/globals |
| npm | @opennextjs/cloudflare | https://www.npmjs.com/package/@opennextjs/cloudflare | npm i @opennextjs/cloudflare |
| npm | @radix-ui/react-avatar | https://www.npmjs.com/package/@radix-ui/react-avatar | npm i @radix-ui/react-avatar |
| npm | @radix-ui/react-dialog | https://www.npmjs.com/package/@radix-ui/react-dialog | npm i @radix-ui/react-dialog |
| npm | @radix-ui/react-dropdown-menu | https://www.npmjs.com/package/@radix-ui/react-dropdown-menu | npm i @radix-ui/react-dropdown-menu |
| npm | @radix-ui/react-scroll-area | https://www.npmjs.com/package/@radix-ui/react-scroll-area | npm i @radix-ui/react-scroll-area |
| npm | @radix-ui/react-select | https://www.npmjs.com/package/@radix-ui/react-select | npm i @radix-ui/react-select |
| pypi | Clisonix-cloud | https://pypi.org/project/Clisonix-cloud/ | pip install Clisonix-cloud |
| pypi | Pillow | https://pypi.org/project/Pillow/ | pip install Pillow |
| pypi | PyJWT | https://pypi.org/project/PyJWT/ | pip install PyJWT |
| pypi | SpeechRecognition | https://pypi.org/project/SpeechRecognition/ | pip install SpeechRecognition |
| pypi | XlsxWriter | https://pypi.org/project/XlsxWriter/ | pip install XlsxWriter |
| pypi | accelerate | https://pypi.org/project/accelerate/ | pip install accelerate |
| pypi | aiofiles | https://pypi.org/project/aiofiles/ | pip install aiofiles |
| pypi | aiohttp | https://pypi.org/project/aiohttp/ | pip install aiohttp |
| pypi | aioredis | https://pypi.org/project/aioredis/ | pip install aioredis |
| pypi | aiosqlite | https://pypi.org/project/aiosqlite/ | pip install aiosqlite |
| pypi | alembic | https://pypi.org/project/alembic/ | pip install alembic |
| pypi | anyio | https://pypi.org/project/anyio/ | pip install anyio |
| pypi | apscheduler | https://pypi.org/project/apscheduler/ | pip install apscheduler |
| pypi | asyncpg | https://pypi.org/project/asyncpg/ | pip install asyncpg |
| pypi | bandit | https://pypi.org/project/bandit/ | pip install bandit |
| cargo | aes-gcm | https://crates.io/crates/aes-gcm | cargo add aes-gcm |
| cargo | algebra | https://crates.io/crates/algebra | cargo add algebra |
| cargo | axum | https://crates.io/crates/axum | cargo add axum |
| cargo | base64 | https://crates.io/crates/base64 | cargo add base64 |
| cargo | clap | https://crates.io/crates/clap | cargo add clap |
| cargo | criterion | https://crates.io/crates/criterion | cargo add criterion |
| cargo | ed25519-dalek | https://crates.io/crates/ed25519-dalek | cargo add ed25519-dalek |
| cargo | futures-util | https://crates.io/crates/futures-util | cargo add futures-util |
| cargo | lru | https://crates.io/crates/lru | cargo add lru |
| cargo | protocol | https://crates.io/crates/protocol | cargo add protocol |
| cargo | quinn | https://crates.io/crates/quinn | cargo add quinn |
| cargo | rand | https://crates.io/crates/rand | cargo add rand |
| cargo | rcgen | https://crates.io/crates/rcgen | cargo add rcgen |
| cargo | reqwest | https://crates.io/crates/reqwest | cargo add reqwest |
| cargo | rmp-serde | https://crates.io/crates/rmp-serde | cargo add rmp-serde |

## API Inventory
| method | route | file | line |
| --- | --- | --- | --- |
| GET | / | multi_tenant_api.py | 155 |
| GET | /health | multi_tenant_api.py | 169 |
| POST | /tenants | multi_tenant_api.py | 179 |
| GET | /tenants | multi_tenant_api.py | 185 |
| GET | /tenants/{tenant_id} | multi_tenant_api.py | 191 |
| PATCH | /tenants/{tenant_id} | multi_tenant_api.py | 199 |
| GET | /health | alda_server.py | 317 |
| GET | /health | clx_hybrid_service.py | 296 |
| POST | /api/v1/hybrid/scan-print | clx_hybrid_service.py | 342 |
| GET | /health | slack_integration_service.py | 325 |
| GET | /service-health | slack_integration_service.py | 336 |
| GET | /status-report | slack_integration_service.py | 352 |
| POST | /send-alert | slack_integration_service.py | 411 |
| POST | /send-message | slack_integration_service.py | 421 |
| POST | /metric-alert | slack_integration_service.py | 430 |
| POST | /notify-deployment | slack_integration_service.py | 460 |
| GET | / | matia_service.py | 83 |
| GET | /health | matia_service.py | 101 |
| GET | /status | matia_service.py | 111 |
| POST | /api/v1/analyse | matia_service.py | 123 |
| POST | /api/v1/stream | matia_service.py | 160 |
| POST | /api/v1/screen | matia_service.py | 198 |
| GET | /health | tracing.py | 15 |
| POST | /metrics/upload | mesh_hq_receiver.py | 53 |
| GET | /health | mesh_hq_receiver.py | 79 |
| GET | /metrics/latest | mesh_hq_receiver.py | 96 |
| GET | /health | clx_i_service.py | 215 |
| GET | /metrics | clx_i_service.py | 239 |
| POST | /api/v1/icons/analyze | clx_i_service.py | 244 |
| POST | /api/models/register | ai_model_versioning.py | 719 |
| GET | /api/models/{model_id}/versions | ai_model_versioning.py | 724 |
| GET | /api/models/{model_id}/production | ai_model_versioning.py | 729 |
| POST | /api/models/{model_id}/{version}/promote | ai_model_versioning.py | 736 |
| GET | / | shopping_therapy_service.py | 78 |
| GET | /health | shopping_therapy_service.py | 98 |
| GET | /status | shopping_therapy_service.py | 103 |
| GET | /api/v1/catalogue | shopping_therapy_service.py | 112 |
| POST | /api/v1/search | shopping_therapy_service.py | 121 |
| POST | /api/v1/stream | shopping_therapy_service.py | 131 |
| POST | /api/v1/register | shopping_therapy_service.py | 153 |
| POST | /api/v1/read | shopping_therapy_service.py | 168 |
| POST | /api/v1/ocean-chat | shopping_therapy_service.py | 181 |
| GET | / | alba_service_5555.py | 757 |
| GET | /health | alba_service_5555.py | 792 |
| GET | /status | alba_service_5555.py | 808 |
| GET | /api/status | alba_service_5555.py | 809 |
| POST | /ingest | alba_service_5555.py | 830 |
| GET | /data | alba_service_5555.py | 836 |
| GET | /metrics | alba_service_5555.py | 841 |
| POST | /api/telemetry/ingest | alba_service_5555.py | 846 |
| POST | /execute | alba_service_5555.py | 868 |
| POST | /receive | alba_service_5555.py | 894 |
| GET | /api/v1/spec | alba_service_5555.py | 919 |
| GET | /gs26/status | alba_service_5555.py | 928 |
| POST | /gs26/ingest | alba_service_5555.py | 950 |
| POST | /gs26/wave | alba_service_5555.py | 962 |
| GET | /gs26/waves | alba_service_5555.py | 977 |
| POST | /gs26/resonance | alba_service_5555.py | 982 |
| GET | /gs26/resonance/{source}/{target} | alba_service_5555.py | 996 |
| GET | /gs26/resonance/graph | alba_service_5555.py | 1001 |
| GET | /gs26/continuity/{source} | alba_service_5555.py | 1006 |
| POST | /gs26/purity/validate | alba_service_5555.py | 1011 |
| POST | /gs26/search | alba_service_5555.py | 1020 |
| GET | /gs26/metrics | alba_service_5555.py | 1032 |
| POST | /gs26/stream | alba_service_5555.py | 1041 |
| POST | /pulse/heartbeat | balancer_pulse_3336.py | 39 |
| GET | /pulse/status/{nodeId} | balancer_pulse_3336.py | 74 |
| GET | /pulse/nodes | balancer_pulse_3336.py | 103 |
| GET | /pulse/dead-nodes | balancer_pulse_3336.py | 134 |
| POST | /pulse/resuscitate/{nodeId} | balancer_pulse_3336.py | 158 |
| GET | /pulse/config | balancer_pulse_3336.py | 178 |
| POST | /pulse/config | balancer_pulse_3336.py | 188 |
| GET | /pulse/metrics | balancer_pulse_3336.py | 204 |
| POST | /pulse/reset/{nodeId} | balancer_pulse_3336.py | 221 |
| GET | /health | balancer_pulse_3336.py | 236 |
| GET | /info | balancer_pulse_3336.py | 253 |
| POST | /analyze | albi_service_6680.py | 65 |
| GET | /insights | albi_service_6680.py | 129 |
| GET | /anomalies | albi_service_6680.py | 143 |
| POST | /api/analytics/agent | albi_service_6680.py | 157 |
| GET | /metrics | albi_service_6680.py | 197 |
| GET | /health | albi_service_6680.py | 211 |
| GET | /api/v1/status | albi_service_6680.py | 231 |
| GET | /api/status | albi_service_6680.py | 232 |
| GET | /api/v1/spec | albi_service_6680.py | 244 |
| POST | /execute | albi_service_6680.py | 250 |
| POST | /receive | albi_service_6680.py | 270 |
| GET | / | ocean_nanogrid.py | 1417 |
| GET | /health | ocean_nanogrid.py | 1422 |
| GET | /api/v1/personality/contract | ocean_nanogrid.py | 1427 |
| POST | /api/v1/chat | ocean_nanogrid.py | 1452 |
| POST | /api/v1/chat/stream | ocean_nanogrid.py | 1578 |
| POST | /api/v1/query | ocean_nanogrid.py | 1606 |
| GET | /api/v1/chat/history | ocean_nanogrid.py | 1615 |
| DELETE | /api/v1/chat/history | ocean_nanogrid.py | 1627 |
| GET | /api/v1/algebra/op | ocean_nanogrid.py | 1643 |
| GET | /api/v1/algebra/convert | ocean_nanogrid.py | 1658 |
| GET | /api/v1/labs | ocean_nanogrid.py | 1684 |
| GET | /api/v1/labs/{lab_id} | ocean_nanogrid.py | 1695 |
| POST | /api/v1/labs/{lab_id}/query | ocean_nanogrid.py | 1709 |
| GET | /api/v1/browse | ocean_nanogrid.py | 1726 |
| GET | /api/v1/search | ocean_nanogrid.py | 1746 |
| POST | /api/v1/chat/browse | ocean_nanogrid.py | 1766 |
| GET | /api/v1/rate-limit | ocean_nanogrid.py | 1822 |
| GET | /api/v1/status | ocean_nanogrid.py | 1844 |
| GET | /api/v1/now | ocean_nanogrid.py | 1853 |
| GET | /api/v1/weather/{city} | ocean_nanogrid.py | 1866 |
| GET | /api/v1/wiki/{query} | ocean_nanogrid.py | 1873 |
| GET | /api/v1/crypto/{symbol} | ocean_nanogrid.py | 1884 |
| GET | /api/v1/github/{owner}/{repo} | ocean_nanogrid.py | 1897 |
| GET | /api/v1/arxiv/{query} | ocean_nanogrid.py | 1918 |
| GET | /api/v1/earthquake | ocean_nanogrid.py | 1938 |
| GET | /api/v1/sources | ocean_nanogrid.py | 1960 |
| POST | /api/v1/vision/analyze | ocean_nanogrid.py | 2011 |
| POST | /api/v1/audio/transcribe | ocean_nanogrid.py | 2100 |
| POST | /api/v1/document/analyze | ocean_nanogrid.py | 2203 |
| POST | /api/v1/document/write | ocean_nanogrid.py | 2295 |
| GET | /api/v1/multimodal/status | ocean_nanogrid.py | 2382 |
| POST | /api/nodes/register | balancer_nodes_3334.py | 44 |
| GET | /api/nodes | balancer_nodes_3334.py | 77 |
| GET | /api/nodes/{nodeId} | balancer_nodes_3334.py | 90 |
| PUT | /api/nodes/{nodeId}/status | balancer_nodes_3334.py | 105 |
| GET | /api/load-balance | balancer_nodes_3334.py | 128 |
| POST | /api/external-nodes/register | balancer_nodes_3334.py | 149 |
| GET | /api/external-nodes | balancer_nodes_3334.py | 181 |
| POST | /api/route-to-external | balancer_nodes_3334.py | 194 |
| POST | /api/offline-nodes/register | balancer_nodes_3334.py | 227 |
| GET | /api/offline-nodes | balancer_nodes_3334.py | 244 |
| POST | /api/route-to-offline | balancer_nodes_3334.py | 257 |
| GET | /api/mesh-status | balancer_nodes_3334.py | 278 |
| GET | /health | balancer_nodes_3334.py | 295 |
| GET | /info | balancer_nodes_3334.py | 313 |
| POST | /api/vendor-nodes/register | balancer_nodes_3334.py | 348 |
| GET | /api/vendor-nodes | balancer_nodes_3334.py | 380 |
| POST | /api/vendor-nodes/heartbeat | balancer_nodes_3334.py | 395 |
| POST | /api/vendor-nodes/complete | balancer_nodes_3334.py | 413 |
| GET | /api/vendor-nodes/best | balancer_nodes_3334.py | 426 |
| GET | /health | alba_idle_chat.py | 11 |
| GET | / | alba_idle_chat.py | 16 |
| POST | /chat | alba_idle_chat.py | 21 |
| GET | /health | advanced_analytics_api.py | 309 |
| GET | / | saas_api.py | 102 |
| GET | /health | saas_api.py | 119 |
| GET | /plans | saas_api.py | 129 |
| POST | /subscriptions | saas_api.py | 134 |
| GET | /subscriptions | saas_api.py | 145 |
| GET | /subscriptions/{tenant_id} | saas_api.py | 151 |
| POST | /usage/check | saas_api.py | 161 |
| POST | /features/check | saas_api.py | 174 |
| POST | /data/documents | balancer_data_3337.py | 38 |
| GET | /data/documents/{docId} | balancer_data_3337.py | 67 |
| GET | /data/collections/{collection} | balancer_data_3337.py | 80 |
| PUT | /data/documents/{docId} | balancer_data_3337.py | 100 |
| DELETE | /data/documents/{docId} | balancer_data_3337.py | 119 |
| POST | /data/metrics | balancer_data_3337.py | 137 |
| GET | /data/metrics/{nodeId} | balancer_data_3337.py | 159 |
| POST | /data/config | balancer_data_3337.py | 176 |
| GET | /data/config/{configId} | balancer_data_3337.py | 195 |
| GET | /data/collections | balancer_data_3337.py | 209 |
| GET | /data/stats | balancer_data_3337.py | 221 |
| POST | /data/export | balancer_data_3337.py | 236 |
| POST | /data/import | balancer_data_3337.py | 258 |
| DELETE | /data/collections/{collection} | balancer_data_3337.py | 286 |
| GET | /health | balancer_data_3337.py | 304 |
| GET | /info | balancer_data_3337.py | 317 |
| GET | / | health_monitor_service.py | 111 |
| GET | /health | health_monitor_service.py | 121 |
| GET | /status | health_monitor_service.py | 131 |
| GET | /status/{service_name} | health_monitor_service.py | 148 |
| POST | /alba/frame | alba_api_server.py | 67 |
| GET | /alba/latest | alba_api_server.py | 95 |
| GET | / | alba_api_server.py | 122 |
| GET | /health | alba_api_server.py | 131 |
| POST | /auth/users | neurosonix_industrial_api.py | 211 |
| POST | /auth/api-keys | neurosonix_industrial_api.py | 227 |
| GET | /auth/api-keys | neurosonix_industrial_api.py | 250 |
| DELETE | /auth/api-keys/{key_id} | neurosonix_industrial_api.py | 259 |
| POST | /api/ask | neurosonix_industrial_api.py | 306 |
| GET | /health | neurosonix_industrial_api.py | 328 |
| GET | /status | neurosonix_industrial_api.py | 337 |
| POST | /api/uploads/eeg/process | neurosonix_industrial_api.py | 352 |
| POST | /api/uploads/audio/process | neurosonix_industrial_api.py | 383 |
| POST | /billing/paypal/order | neurosonix_industrial_api.py | 424 |
| POST | /billing/paypal/capture/{order_id} | neurosonix_industrial_api.py | 455 |
| POST | /billing/stripe/payment-intent | neurosonix_industrial_api.py | 476 |
| POST | /billing/sepa/initiate | neurosonix_industrial_api.py | 498 |
| GET | /db/ping | neurosonix_industrial_api.py | 509 |
| GET | /redis/ping | neurosonix_industrial_api.py | 519 |
| GET | /api/alba/status | neurosonix_industrial_api.py | 532 |
| GET | /api/alba/alba/cbor | neurosonix_industrial_api.py | 544 |
| POST | /api/alba/alba/cbor | neurosonix_industrial_api.py | 555 |
| POST | /api/alba/streams/start | neurosonix_industrial_api.py | 565 |
| POST | /api/alba/streams/{stream_id}/stop | neurosonix_industrial_api.py | 588 |
| GET | /api/alba/streams | neurosonix_industrial_api.py | 608 |
| GET | /api/alba/streams/{stream_id}/data | neurosonix_industrial_api.py | 617 |
| POST | /api/alba/config | neurosonix_industrial_api.py | 633 |
| GET | /api/alba/metrics | neurosonix_industrial_api.py | 643 |
| GET | /api/alba/health | neurosonix_industrial_api.py | 655 |
| GET | /api/data-sources | neurosonix_industrial_api.py | 669 |
| GET | /api/activity-log | neurosonix_industrial_api.py | 702 |
| POST | /api/start-bulk-collection | neurosonix_industrial_api.py | 722 |
| GET | /api/performance-metrics | neurosonix_industrial_api.py | 733 |
| GET | /api/system-status | neurosonix_industrial_api.py | 748 |
| GET | /api/storage-alert | neurosonix_industrial_api.py | 764 |
| GET | /api/audio-spectrometer-error | neurosonix_industrial_api.py | 778 |
| GET | /asi/status | neurosonix_industrial_api.py | 791 |
| GET | /asi/health | neurosonix_industrial_api.py | 808 |
| POST | /asi/execute | neurosonix_industrial_api.py | 820 |
| POST | /alignments/evaluate | neurosonix_industrial_api.py | 848 |
| POST | /alignments/create-adaptive | neurosonix_industrial_api.py | 861 |
| GET | /alignments/dashboard | neurosonix_industrial_api.py | 880 |
| GET | /favicon.ico | neurosonix_industrial_api.py | 894 |
| GET | / | neurosonix_industrial_api.py | 906 |
| GET | / | reporting_service.py | 33 |
| GET | /health | reporting_service.py | 43 |
| GET | /status | reporting_service.py | 51 |
| GET | /health | saas_services_orchestrator.py | 66 |
| GET | /status | saas_services_orchestrator.py | 78 |
| POST | /agents/register | saas_services_orchestrator.py | 130 |
| POST | /agents/{agent_id}/heartbeat | saas_services_orchestrator.py | 169 |
| POST | /agents/{agent_id}/scale | saas_services_orchestrator.py | 183 |
| GET | /agents | saas_services_orchestrator.py | 216 |
| GET | /agents/{agent_id} | saas_services_orchestrator.py | 224 |
| POST | /api-docs/generate | saas_services_orchestrator.py | 236 |
| GET | /api-docs | saas_services_orchestrator.py | 318 |
| GET | /api-docs/{agent_id} | saas_services_orchestrator.py | 326 |
| GET | /api-docs/{agent_id}/openapi.json | saas_services_orchestrator.py | 334 |
| POST | /api/behavioral/mood/log | behavioral_science_api.py | 244 |
| POST | /api/behavioral/mood/sync | behavioral_science_api.py | 277 |
| POST | /api/behavioral/habits/log | behavioral_science_api.py | 375 |
| POST | /api/behavioral/habits/sync | behavioral_science_api.py | 403 |
| POST | /api/behavioral/focus/log | behavioral_science_api.py | 442 |
| GET | /api/behavioral/focus/analysis/{device_id} | behavioral_science_api.py | 476 |
| GET | /api/behavioral/insights/{device_id} | behavioral_science_api.py | 490 |
| GET | /api/behavioral/research/aggregate | behavioral_science_api.py | 562 |
| GET | / | behavioral_science_api.py | 602 |
| GET | /health | behavioral_science_api.py | 617 |
| GET | /api/behavioral/health | behavioral_science_api.py | 618 |
| GET | /api/status | behavioral_science_api.py | 638 |
| GET | /status | behavioral_science_api.py | 639 |
| GET | /health | alphabet_layers_api.py | 49 |
| GET | /api/v1/alphabet/stats | alphabet_layers_api.py | 67 |
| GET | /api/v1/alphabet/consciousness | alphabet_layers_api.py | 73 |
| POST | /api/v1/alphabet/process | alphabet_layers_api.py | 79 |
| GET | /api/v1/curiosity/algebra/op | alphabet_layers_api.py | 85 |
| GET | /health | multi_tenant_manager.py | 10 |
| GET | / | multi_tenant_manager.py | 15 |
| GET | /tenants | multi_tenant_manager.py | 20 |
| GET | / | balancer_simple.py | 65 |
| GET | /status | balancer_simple.py | 69 |
| POST | /balance | balancer_simple.py | 84 |
| GET | /health | jona_neural_api.py | 477 |
| GET | /status | jona_neural_api.py | 487 |
| POST | /session/start | jona_neural_api.py | 504 |
| POST | /session/{session_id}/stop | jona_neural_api.py | 531 |
| GET | /session/{session_id}/metrics | jona_neural_api.py | 564 |
| GET | /presets | jona_neural_api.py | 577 |
| GET | /presets/{preset_id} | jona_neural_api.py | 582 |
| GET | /settings/default | jona_neural_api.py | 590 |
| GET | /channels | jona_neural_api.py | 613 |
| POST | /session/{session_id}/export | jona_neural_api.py | 621 |
| GET | /synthesis/preview | jona_neural_api.py | 668 |
| GET | /audio/list | jona_neural_api.py | 712 |
| DELETE | /audio/{file_id} | jona_neural_api.py | 723 |
| GET | /files/{filename} | jona_neural_api.py | 763 |
| GET | /health | nanogridata_gateway.js | 329 |
| GET | /stats | nanogridata_gateway.js | 332 |
| GET | /metrics | nanogridata_gateway.js | 335 |
| GET | /metrics | distributed_pulse_balancer.py | 289 |
| GET | /balancer/status | distributed_pulse_balancer.py | 374 |
| POST | /balancer/request | distributed_pulse_balancer.py | 395 |
| POST | /balancer/feedback | distributed_pulse_balancer.py | 471 |
| GET | /health | nanogridata_gateway.ts | 353 |
| GET | /stats | nanogridata_gateway.ts | 357 |
| GET | /metrics | nanogridata_gateway.ts | 361 |
| POST | /api/query/analyze | balancer_ts_3338.ts | 184 |
| GET | /api/pool/stats | balancer_ts_3338.ts | 219 |
| POST | /api/pool/optimize | balancer_ts_3338.ts | 243 |
| POST | /api/query/execute | balancer_ts_3338.ts | 266 |
| GET | /api/slow-queries | balancer_ts_3338.ts | 318 |
| GET | /health | balancer_ts_3338.ts | 368 |
| GET | /info | balancer_ts_3338.ts | 393 |
| POST | /cache/set | balancer_cache_3335.py | 42 |
| GET | /cache/get/{key} | balancer_cache_3335.py | 64 |
| DELETE | /cache/delete/{key} | balancer_cache_3335.py | 85 |
| GET | /cache/keys | balancer_cache_3335.py | 102 |
| POST | /cache/clear | balancer_cache_3335.py | 118 |
| GET | /cache/stats | balancer_cache_3335.py | 132 |
| POST | /cache/batch/set | balancer_cache_3335.py | 150 |
| POST | /cache/batch/get | balancer_cache_3335.py | 172 |
| GET | /health | balancer_cache_3335.py | 191 |
| GET | /info | balancer_cache_3335.py | 204 |
| GET | /health | agiem_telemetry_service.py | 66 |
| GET | /status | agiem_telemetry_service.py | 81 |
| GET | /nodes | agiem_telemetry_service.py | 100 |
| GET | /nodes/{node_id} | agiem_telemetry_service.py | 110 |
| PUT | /nodes/{node_id}/status | agiem_telemetry_service.py | 123 |
| GET | /stages | agiem_telemetry_service.py | 134 |
| GET | /stages/{stage_name} | agiem_telemetry_service.py | 143 |
| POST | /stages/{stage_name}/metrics | agiem_telemetry_service.py | 161 |
| GET | /metrics | agiem_telemetry_service.py | 173 |
| GET | /logs | agiem_telemetry_service.py | 186 |
| POST | /logs/event | agiem_telemetry_service.py | 197 |
| GET | /cycles | agiem_telemetry_service.py | 209 |
| GET | /multi-tenant | agiem_telemetry_service.py | 220 |
| POST | /register | agiem_telemetry_service.py | 229 |
| POST | /report | agiem_telemetry_service.py | 239 |
| GET | /info | agiem_telemetry_service.py | 250 |
| GET | /api | api_root_patch.py | 2 |
| GET | /health | albi_user_api.py | 199 |
| POST | /session/start | albi_user_api.py | 212 |
| POST | /session/{session_id}/stop | albi_user_api.py | 246 |
| GET | /session/{session_id}/metrics | albi_user_api.py | 266 |
| POST | /session/{session_id}/event | albi_user_api.py | 314 |
| POST | /session/{session_id}/stream | albi_user_api.py | 344 |
| GET | /session/{session_id}/export | albi_user_api.py | 419 |
| GET | /sessions | albi_user_api.py | 527 |
| GET | /channels | albi_user_api.py | 556 |
| GET | /brainwave-bands | albi_user_api.py | 570 |
| POST | /synthesize | jona_service_7777.py | 66 |
| GET | /synthesize/{synthesis_id} | jona_service_7777.py | 102 |
| GET | /synthesize/{synthesis_id}/audio | jona_service_7777.py | 110 |
| POST | /coordinate | jona_service_7777.py | 167 |
| GET | /queue | jona_service_7777.py | 190 |
| POST | /api/coordination/event | jona_service_7777.py | 200 |
| GET | /metrics | jona_service_7777.py | 232 |
| GET | /health | jona_service_7777.py | 245 |
| POST | /execute | jona_service_7777.py | 264 |
| POST | /receive | jona_service_7777.py | 286 |
| GET | /health | economy_api_server.py | 47 |
| GET | /status | economy_api_server.py | 52 |
| GET | /api/status | economy_api_server.py | 53 |
| GET | / | economy_api_server.py | 65 |
| POST | /economy/compute | economy_api_server.py | 79 |
| GET | /economy/report | economy_api_server.py | 90 |
| GET | /health | clx_agent.py | 332 |
| GET | /status | clx_agent.py | 343 |
| POST | /chat | clx_agent.py | 370 |
| GET | /memory | clx_agent.py | 395 |
| POST | /observe | clx_agent.py | 412 |
| POST | /learn/start | clx_agent.py | 422 |
| POST | /learn/stop | clx_agent.py | 435 |
| GET | /health | marketplace_api.py | 10 |
| GET | / | marketplace_api.py | 15 |
| GET | /items | marketplace_api.py | 20 |
| GET | /health | cycle_api_server.py | 21 |
| GET | /cycles | cycle_api_server.py | 42 |
| POST | /cycles/create | cycle_api_server.py | 46 |
| GET | /metrics | cycle_api_server.py | 51 |
| GET | /health | jona_server.py | 34 |
| GET | / | .git_ocean_core_full.py | 620 |
| GET | /health | .git_ocean_core_full.py | 637 |
| GET | /api/v1/status | .git_ocean_core_full.py | 645 |
| GET | /api/v1/enterprise/status | .git_ocean_core_full.py | 665 |
| GET | /api/v1/enterprise/contract | .git_ocean_core_full.py | 676 |
| POST | /api/v1/chat | .git_ocean_core_full.py | 686 |
| POST | /api/v1/chat/stream | .git_ocean_core_full.py | 694 |
| POST | /api/v1/query | .git_ocean_core_full.py | 749 |
| POST | /api/v1/chat/specialized | .git_ocean_core_full.py | 770 |
| GET | /api/v1/services | .git_ocean_core_full.py | 865 |
| GET | /api/v1/engines | .git_ocean_core_full.py | 873 |
| GET | /api/v1/arxiv/{query} | .git_ocean_core_full.py | 905 |
| GET | /api/v1/wiki/{query} | .git_ocean_core_full.py | 972 |
| GET | /api/v1/pubmed/{query} | .git_ocean_core_full.py | 1021 |
| GET | /api/v1/sources | .git_ocean_core_full.py | 1088 |
| GET | /api/v1/browse | .git_ocean_core_full.py | 1184 |
| GET | /api/v1/search | .git_ocean_core_full.py | 1246 |
| POST | /api/v1/chat/browse | .git_ocean_core_full.py | 1363 |
| POST | /api/v1/chat/browse/stream | .git_ocean_core_full.py | 1423 |
| POST | /api/v1/zurich | .git_ocean_core_full.py | 1700 |
| GET | /api/v1/zurich/info | .git_ocean_core_full.py | 1740 |
| POST | /api/v1/debate/stream | .git_ocean_core_full.py | 2040 |
| POST | /api/v1/debate | .git_ocean_core_full.py | 2208 |
| GET | /api/v1/debate/personas | .git_ocean_core_full.py | 2271 |
| POST | /api/v1/tts | .git_ocean_core_full.py | 2340 |
| GET | /api/v1/tts/voices | .git_ocean_core_full.py | 2415 |
| POST | /api/v1/voice/conversation | .git_ocean_core_full.py | 2427 |
| GET | /health | liam_server.py | 184 |
| GET | /health | saas_services_orchestrator_v3.py | 185 |
| GET | /status | saas_services_orchestrator_v3.py | 198 |
| GET | /registry | saas_services_orchestrator_v3.py | 232 |
| POST | /agents/register | saas_services_orchestrator_v3.py | 249 |
| POST | /agents/{agent_id}/heartbeat | saas_services_orchestrator_v3.py | 288 |
| POST | /agents/{agent_id}/scale | saas_services_orchestrator_v3.py | 302 |
| GET | /agents | saas_services_orchestrator_v3.py | 334 |
| GET | /agents/{agent_id} | saas_services_orchestrator_v3.py | 342 |
| POST | /api-docs/generate | saas_services_orchestrator_v3.py | 354 |
| GET | /api-docs | saas_services_orchestrator_v3.py | 426 |
| GET | /api-docs/{agent_id} | saas_services_orchestrator_v3.py | 434 |
| GET | /api-docs/{agent_id}/openapi.json | saas_services_orchestrator_v3.py | 442 |
| POST | /communicate | saas_services_orchestrator_v3.py | 454 |
| GET | /communication/log | saas_services_orchestrator_v3.py | 486 |
| POST | /services/{service}/execute | saas_services_orchestrator_v3.py | 524 |
| POST | /api/nodes/register | balancer_nodes_3333.js | 29 |
| GET | /api/nodes | balancer_nodes_3333.js | 63 |
| GET | /api/nodes/:nodeId | balancer_nodes_3333.js | 77 |
| PUT | /api/nodes/:nodeId/status | balancer_nodes_3333.js | 95 |
| GET | /health | balancer_nodes_3333.js | 119 |
| GET | /info | balancer_nodes_3333.js | 134 |
| GET | /api/monitoring/health | monitoring_system_config.py | 206 |
| GET | /api/monitoring/metrics | monitoring_system_config.py | 222 |
| POST | /api/monitoring/service/{service_name} | monitoring_system_config.py | 226 |
| GET | / | asi_api_server.py | 76 |
| GET | /health | asi_api_server.py | 96 |
| GET | /status | asi_api_server.py | 106 |
| GET | /api/status | asi_api_server.py | 107 |
| GET | /metrics | asi_api_server.py | 126 |
| GET | /nodes | asi_api_server.py | 130 |
| GET | /logs | asi_api_server.py | 134 |
| GET | /system | asi_api_server.py | 143 |
| POST | /mesh/register | asi_api_server.py | 151 |
| POST | /mesh/send | asi_api_server.py | 162 |
| GET | /asi/joint-status | asi_api_server.py | 173 |
| POST | /test | test_security_middleware.py | 21 |
| POST | /test | test_security_middleware.py | 30 |
| POST | /test | test_security_middleware.py | 42 |
| POST | /test | test_security_middleware.py | 53 |
| GET | /health | personas_api.py | 16 |
| GET | / | personas_api.py | 21 |
| GET | /personas | personas_api.py | 26 |
| POST | /api/payments/create-intent | payment_gateway_config.py | 188 |
| POST | /api/payments/sepa/mandate | payment_gateway_config.py | 197 |
| GET | /status | master.py | 25 |
| POST | /log | master.py | 38 |
| POST | /control | master.py | 46 |
| GET | /health | master.py | 61 |
| GET | /industrial/data | master.py | 67 |
| GET | /dashboard | master.py | 79 |
| GET | / | docker-stubs/multi_tenant_stub.py | 14 |
| GET | /health | docker-stubs/multi_tenant_stub.py | 18 |
| GET | /tenants | docker-stubs/multi_tenant_stub.py | 22 |
| GET | / | docker-stubs/agiem_stub.py | 45 |
| GET | /health | docker-stubs/agiem_stub.py | 55 |
| GET | /regions | docker-stubs/agiem_stub.py | 64 |
| GET | /region/{name} | docker-stubs/agiem_stub.py | 72 |
| POST | /query | docker-stubs/agiem_stub.py | 82 |
| GET | /markets | docker-stubs/agiem_stub.py | 100 |
| GET | /analytics/{sector} | docker-stubs/agiem_stub.py | 125 |
| GET | / | docker-stubs/core_engine_stub.py | 38 |
| GET | /health | docker-stubs/core_engine_stub.py | 48 |
| POST | /process | docker-stubs/core_engine_stub.py | 57 |
| GET | /status | docker-stubs/core_engine_stub.py | 71 |
| GET | /config | docker-stubs/core_engine_stub.py | 82 |
| GET | / | docker-stubs/neurosonix_stub.py | 14 |
| GET | /health | docker-stubs/neurosonix_stub.py | 18 |
| POST | /process | docker-stubs/neurosonix_stub.py | 22 |
| GET | / | docker-stubs/behavioral_stub.py | 16 |
| GET | /health | docker-stubs/behavioral_stub.py | 20 |
| POST | /analyze | docker-stubs/behavioral_stub.py | 24 |
| GET | / | docker-stubs/quantum_stub.py | 50 |
| GET | /health | docker-stubs/quantum_stub.py | 60 |
| GET | /backends | docker-stubs/quantum_stub.py | 69 |
| GET | /algorithms | docker-stubs/quantum_stub.py | 77 |
| POST | /simulate | docker-stubs/quantum_stub.py | 84 |
| GET | /random/{num_bits} | docker-stubs/quantum_stub.py | 107 |
| GET | /entanglement | docker-stubs/quantum_stub.py | 118 |
| GET | / | docker-stubs/economy_stub.py | 14 |
| GET | /health | docker-stubs/economy_stub.py | 18 |
| GET | /credits | docker-stubs/economy_stub.py | 22 |
| GET | / | docker-stubs/cognitive_stub.py | 95 |
| GET | /health | docker-stubs/cognitive_stub.py | 104 |
| POST | /analyze | docker-stubs/cognitive_stub.py | 113 |
| GET | /analyze/{query} | docker-stubs/cognitive_stub.py | 118 |
| GET | /levels | docker-stubs/cognitive_stub.py | 123 |
| GET | / | docker-stubs/datasource_stub.py | 34 |
| GET | /health | docker-stubs/datasource_stub.py | 43 |
| GET | /sources | docker-stubs/datasource_stub.py | 52 |
| GET | /data/{source_id} | docker-stubs/datasource_stub.py | 60 |
| GET | / | docker-stubs/personas_stub.py | 69 |
| GET | /health | docker-stubs/personas_stub.py | 78 |
| GET | /personas | docker-stubs/personas_stub.py | 88 |
| GET | /persona/{name} | docker-stubs/personas_stub.py | 96 |
| POST | /query | docker-stubs/personas_stub.py | 103 |
| GET | /recommend | docker-stubs/personas_stub.py | 129 |
| GET | / | docker-stubs/marketplace_stub.py | 35 |
| GET | /health | docker-stubs/marketplace_stub.py | 45 |
| GET | /models | docker-stubs/marketplace_stub.py | 54 |
| GET | /plugins | docker-stubs/marketplace_stub.py | 62 |
| GET | /featured | docker-stubs/marketplace_stub.py | 70 |
| GET | /search | docker-stubs/marketplace_stub.py | 79 |
| GET | /stats | docker-stubs/marketplace_stub.py | 101 |
| GET | / | docker-stubs/agent_telemetry_stub.py | 45 |
| GET | /health | docker-stubs/agent_telemetry_stub.py | 54 |
| GET | /agents | docker-stubs/agent_telemetry_stub.py | 63 |
| GET | /agent/{agent_id} | docker-stubs/agent_telemetry_stub.py | 71 |
| POST | /event | docker-stubs/agent_telemetry_stub.py | 87 |
| GET | /metrics | docker-stubs/agent_telemetry_stub.py | 96 |
| GET | /summary | docker-stubs/agent_telemetry_stub.py | 114 |
| GET | / | docker-stubs/service_stub.py | 22 |
| GET | /health | docker-stubs/service_stub.py | 31 |
| GET | /info | docker-stubs/service_stub.py | 40 |
| GET | /api | docker-stubs/service_stub.py | 50 |
| POST | /process | docker-stubs/service_stub.py | 59 |
| GET | / | docker-stubs/router_stub.py | 135 |
| GET | /health | docker-stubs/router_stub.py | 144 |
| POST | /route | docker-stubs/router_stub.py | 153 |
| GET | /personas | docker-stubs/router_stub.py | 158 |
| GET | /strategy/{level} | docker-stubs/router_stub.py | 176 |
| GET | / | docker-stubs/aviation_stub.py | 14 |
| GET | /health | docker-stubs/aviation_stub.py | 18 |
| GET | /flights | docker-stubs/aviation_stub.py | 22 |
| GET | / | docker-stubs/asi_component_stub.py | 43 |
| GET | /health | docker-stubs/asi_component_stub.py | 54 |
| GET | /info | docker-stubs/asi_component_stub.py | 63 |
| POST | /query | docker-stubs/asi_component_stub.py | 73 |
| GET | /status | docker-stubs/asi_component_stub.py | 84 |
| POST | /analyze | docker-stubs/asi_component_stub.py | 96 |
| GET | / | docker-stubs/lab_stub.py | 52 |
| GET | /health | docker-stubs/lab_stub.py | 63 |
| GET | /capabilities | docker-stubs/lab_stub.py | 73 |
| POST | /analyze | docker-stubs/lab_stub.py | 83 |
| GET | /research/{project_id} | docker-stubs/lab_stub.py | 96 |
| GET | / | docker-stubs/reporting_stub.py | 16 |
| GET | /health | docker-stubs/reporting_stub.py | 20 |
| GET | /reports | docker-stubs/reporting_stub.py | 24 |
| POST | /generate/{report_type} | docker-stubs/reporting_stub.py | 28 |
| GET | / | docker-stubs/health_monitor.py | 177 |
| GET | /health | docker-stubs/health_monitor.py | 186 |
| GET | /status | docker-stubs/health_monitor.py | 195 |
| GET | /status/{service_name} | docker-stubs/health_monitor.py | 214 |
| GET | /services | docker-stubs/health_monitor.py | 230 |
| GET | /summary | docker-stubs/health_monitor.py | 262 |
| GET | / | docker-stubs/excel_stub.py | 14 |
| GET | /health | docker-stubs/excel_stub.py | 18 |
| POST | /export | docker-stubs/excel_stub.py | 22 |
| POST | /import | docker-stubs/excel_stub.py | 26 |
| GET | / | docker-stubs/saas_api_stub.py | 14 |
| GET | /health | docker-stubs/saas_api_stub.py | 18 |
| GET | /subscriptions | docker-stubs/saas_api_stub.py | 22 |
| GET | / | docker-stubs/cycle_engine_stub.py | 35 |
| GET | /health | docker-stubs/cycle_engine_stub.py | 44 |
| GET | /cycles | docker-stubs/cycle_engine_stub.py | 54 |
| GET | /cycle/{name} | docker-stubs/cycle_engine_stub.py | 62 |
| POST | /cycle/{name}/start | docker-stubs/cycle_engine_stub.py | 72 |
| POST | /cycle/{name}/stop | docker-stubs/cycle_engine_stub.py | 80 |
| POST | /cycle | docker-stubs/cycle_engine_stub.py | 87 |
| GET | /status | docker-stubs/cycle_engine_stub.py | 98 |
| GET | / | docker-stubs/analytics_stub.py | 14 |
| GET | /health | docker-stubs/analytics_stub.py | 18 |
| GET | /metrics | docker-stubs/analytics_stub.py | 22 |
| GET | / | docker-stubs/saas_orchestrator_stub.py | 46 |
| GET | /health | docker-stubs/saas_orchestrator_stub.py | 56 |
| GET | /tenants | docker-stubs/saas_orchestrator_stub.py | 65 |
| GET | /tenant/{tenant_id} | docker-stubs/saas_orchestrator_stub.py | 73 |
| GET | /plans | docker-stubs/saas_orchestrator_stub.py | 83 |
| POST | /tenant | docker-stubs/saas_orchestrator_stub.py | 90 |
| GET | /usage/{tenant_id} | docker-stubs/saas_orchestrator_stub.py | 105 |
| GET | /metrics | docker-stubs/saas_orchestrator_stub.py | 123 |
| GET | /api/status | backend/server-optimized.ts | 86 |
| GET | /health | services/developer_portal.py | 96 |
| GET | / | services/developer_portal.py | 110 |
| GET | /api/v1/keys | services/developer_portal.py | 518 |
| POST | /api/v1/keys/generate | services/developer_portal.py | 535 |
| GET | /api/v1/usage | services/developer_portal.py | 557 |
| GET | /api/v1/billing | services/developer_portal.py | 597 |
| POST | /api/v1/keys/{key_id}/revoke | services/developer_portal.py | 636 |
| GET | /health | services/usage_analytics.py | 98 |
| GET | /status | services/usage_analytics.py | 109 |
| GET | /api/v1/usage | services/usage_analytics.py | 183 |
| GET | /api/v1/endpoints | services/usage_analytics.py | 253 |
| POST | /api/v1/track | services/usage_analytics.py | 310 |
| GET | / | excel-core/excel_reporting_api.py | 53 |
| GET | /health | excel-core/excel_reporting_api.py | 72 |
| GET | /api/reporting/system-metrics | excel-core/excel_reporting_api.py | 80 |
| GET | /api/reporting/docker-containers | excel-core/excel_reporting_api.py | 92 |
| GET | /api/reporting/docker-stats | excel-core/excel_reporting_api.py | 117 |
| GET | /api/lagter/v1/meta | excel-core/excel_reporting_api.py | 140 |
| GET | /api/lagter/v1/template | excel-core/excel_reporting_api.py | 165 |
| GET | /api/lagter/v1/process-map | excel-core/excel_reporting_api.py | 218 |
| GET | /api/lagter/v1/export | excel-core/excel_reporting_api.py | 227 |
| POST | /api/lagter/v1/export/custom | excel-core/excel_reporting_api.py | 242 |
| GET | / | excel-core/lagter_v1_api.py | 30 |
| GET | /health | excel-core/lagter_v1_api.py | 46 |
| GET | /api/lagter/v1/meta | excel-core/lagter_v1_api.py | 55 |
| GET | /api/lagter/v1/template | excel-core/lagter_v1_api.py | 80 |
| GET | /api/lagter/v1/process-map | excel-core/lagter_v1_api.py | 133 |
| GET | /api/lagter/v1/export | excel-core/lagter_v1_api.py | 154 |
| GET | / | 9999/app.py | 278 |
| GET | /health | 9999/app.py | 305 |
| GET | /api/v1/tools/status | 9999/app.py | 315 |
| POST | /api/v1/chat | 9999/app.py | 333 |
| POST | /api/v1/discussion | 9999/app.py | 363 |
| POST | /api/v1/voice/transcribe | 9999/app.py | 380 |
| POST | /api/v1/vision/analyze | 9999/app.py | 396 |
| POST | /api/v1/vision/create | 9999/app.py | 412 |
| POST | /api/v1/document/read | 9999/app.py | 431 |
| POST | /api/v1/document/write | 9999/app.py | 460 |
| POST | /api/v1/video/create | 9999/app.py | 489 |
| POST | /api/v1/video/create/external | 9999/app.py | 512 |
| POST | /api/v1/video/process | 9999/app.py | 525 |
| POST | /api/v1/music/ai-generate | 9999/app.py | 543 |
| POST | /api/v1/music/create | 9999/app.py | 605 |
| POST | /api/v1/algebra/binary-solfege | 9999/app.py | 799 |
| POST | /api/v1/memory/store | 9999/app.py | 841 |
| POST | /api/v1/memory/search | 9999/app.py | 857 |
| GET | /api/v1/memory | 9999/app.py | 870 |
| POST | /api/v1/tasks/create | 9999/app.py | 875 |
| GET | /api/v1/tasks | 9999/app.py | 893 |
| GET | /api/v1/tasks/{task_id} | 9999/app.py | 898 |
| POST | /api/v1/tasks/{task_id}/run | 9999/app.py | 906 |
| POST | /api/v1/workflows/run | 9999/app.py | 940 |
| GET | /api/v1/files/list | 9999/app.py | 977 |
| GET | /api/v1/system/self-check | 9999/app.py | 996 |
| POST | /api/v1/publish/blog | 9999/app.py | 1014 |
| GET | /api/v1/publish/status | 9999/app.py | 1089 |
| GET | /health | orchestra/server.py | 76 |
| GET | /status | orchestra/server.py | 86 |
| GET | /domains | orchestra/server.py | 105 |
| GET | /report | orchestra/server.py | 114 |
| GET | /report/{domain} | orchestra/server.py | 140 |
| POST | /report/refresh | orchestra/server.py | 149 |
| GET | /api/info | ocean_core/ocean_api.py | 1285 |
| GET | /favicon.ico | ocean_core/ocean_api.py | 1321 |
| GET | / | ocean_core/ocean_api.py | 1350 |
| GET | /chat | ocean_core/ocean_api.py | 1360 |
| GET | /status | ocean_core/ocean_api.py | 1371 |
| GET | /weather | ocean_core/ocean_api.py | 1670 |
| GET | /nasa | ocean_core/ocean_api.py | 1681 |
| GET | /coingecko | ocean_core/ocean_api.py | 1688 |
| GET | /wikipedia | ocean_core/ocean_api.py | 1698 |
| GET | /archive | ocean_core/ocean_api.py | 1708 |
| GET | /api/excel/status | ocean_core/ocean_api.py | 1972 |
| GET | /api/excel/templates | ocean_core/ocean_api.py | 1988 |
| GET | /api/excel/formulas | ocean_core/ocean_api.py | 2004 |
| GET | /api/excel/generate | ocean_core/ocean_api.py | 2020 |
| POST | /api/excel/validate | ocean_core/ocean_api.py | 2044 |
| POST | /api/excel/parse | ocean_core/ocean_api.py | 2065 |
| GET | /health | ocean_core/ocean_api.py | 3869 |
| GET | /api/chat | ocean_core/ocean_api.py | 4259 |
| GET | /api/status | ocean_core/ocean_api.py | 4265 |
| GET | /api/documents/capabilities | ocean_core/ocean_api.py | 5287 |
| GET | /api/documents/agents | ocean_core/ocean_api.py | 5313 |
| POST | /api/documents/scan | ocean_core/ocean_api.py | 5335 |
| POST | /api/documents/generate | ocean_core/ocean_api.py | 5587 |
| GET | / | ocean_core/ocean_nanogrid_old.py | 624 |
| GET | /health | ocean_core/ocean_nanogrid_old.py | 628 |
| POST | /api/v1/chat | ocean_core/ocean_nanogrid_old.py | 632 |
| POST | /api/v1/chat/stream | ocean_core/ocean_nanogrid_old.py | 763 |
| POST | /api/v1/query | ocean_core/ocean_nanogrid_old.py | 815 |
| GET | /api/v1/rate-limit | ocean_core/ocean_nanogrid_old.py | 819 |
| GET | /api/v1/status | ocean_core/ocean_nanogrid_old.py | 840 |
| GET | /api/v1/now | ocean_core/ocean_nanogrid_old.py | 849 |
| GET | /api/v1/weather/{city} | ocean_core/ocean_nanogrid_old.py | 862 |
| GET | /api/v1/wiki/{query} | ocean_core/ocean_nanogrid_old.py | 869 |
| GET | /api/v1/browse | ocean_core/ocean_nanogrid_old.py | 880 |
| GET | /api/v1/search | ocean_core/ocean_nanogrid_old.py | 903 |
| POST | /api/v1/chat/browse | ocean_core/ocean_nanogrid_old.py | 923 |
| GET | /api/v1/crypto/{symbol} | ocean_core/ocean_nanogrid_old.py | 994 |
| GET | /api/v1/github/{owner}/{repo} | ocean_core/ocean_nanogrid_old.py | 1007 |
| GET | /api/v1/arxiv/{query} | ocean_core/ocean_nanogrid_old.py | 1028 |
| GET | /api/v1/earthquake | ocean_core/ocean_nanogrid_old.py | 1048 |
| GET | /api/v1/sources | ocean_core/ocean_nanogrid_old.py | 1070 |
| POST | /api/v1/chat/stream | ocean_core/ocean_simple.py | 62 |
| POST | /api/v1/chat | ocean_core/ocean_simple.py | 76 |
| GET | /health | ocean_core/ocean_simple.py | 103 |
| GET | / | ocean_core/ocean_simple.py | 108 |
| GET | /health | ocean_core/ocean_strict_chat.py | 157 |
| POST | /api/v1/chat | ocean_core/ocean_strict_chat.py | 168 |
| POST | /api/v1/analyze | ocean_core/ocean_strict_chat.py | 240 |
| DELETE | /api/v1/session/{session_id} | ocean_core/ocean_strict_chat.py | 283 |
| GET | /api/v1/sessions | ocean_core/ocean_strict_chat.py | 292 |
| GET | /health | ocean_core/ocean_multimodal.py | 462 |
| POST | /api/v1/analyze | ocean_core/ocean_multimodal.py | 467 |
| POST | /api/v1/vision | ocean_core/ocean_multimodal.py | 478 |
| POST | /api/v1/audio | ocean_core/ocean_multimodal.py | 489 |
| POST | /api/v1/document | ocean_core/ocean_multimodal.py | 500 |
| POST | /api/v1/reason | ocean_core/ocean_multimodal.py | 510 |
| POST | /api/v1/chat | ocean_core/ocean_orchestrator.py | 449 |
| POST | /api/v1/chat/stream | ocean_core/ocean_orchestrator.py | 545 |
| GET | /api/v1/services | ocean_core/ocean_orchestrator.py | 606 |
| GET | /api/v1/services/{service_id} | ocean_core/ocean_orchestrator.py | 626 |
| POST | /api/v1/services/{service_id}/call | ocean_core/ocean_orchestrator.py | 646 |
| GET | /api/v1/health | ocean_core/ocean_orchestrator.py | 659 |
| GET | /health | ocean_core/ocean_orchestrator.py | 670 |
| GET | / | ocean_core/ocean_orchestrator.py | 676 |
| GET | /health | ocean_core/api_mega_layer.py | 143 |
| GET | /status | ocean_core/api_mega_layer.py | 152 |
| POST | /process | ocean_core/api_mega_layer.py | 185 |
| GET | /demo | ocean_core/api_mega_layer.py | 259 |
| POST | /api/v1/chat/stream | ocean_core/ocean_simple_new.py | 38 |
| POST | /api/v1/chat | ocean_core/ocean_simple_new.py | 45 |
| GET | /health | ocean_core/ocean_simple_new.py | 55 |
| GET | / | ocean_core/ocean_simple_new.py | 59 |
| GET | / | ocean_core/ocean_nanogrid.py | 1263 |
| GET | /health | ocean_core/ocean_nanogrid.py | 1268 |
| POST | /api/v1/chat | ocean_core/ocean_nanogrid.py | 1273 |
| POST | /api/v1/chat/stream | ocean_core/ocean_nanogrid.py | 1446 |
| POST | /api/v1/query | ocean_core/ocean_nanogrid.py | 1469 |
| GET | /api/v1/chat/history | ocean_core/ocean_nanogrid.py | 1478 |
| DELETE | /api/v1/chat/history | ocean_core/ocean_nanogrid.py | 1490 |
| GET | /api/v1/algebra/op | ocean_core/ocean_nanogrid.py | 1506 |
| GET | /api/v1/algebra/convert | ocean_core/ocean_nanogrid.py | 1521 |
| GET | /api/v1/labs | ocean_core/ocean_nanogrid.py | 1547 |
| GET | /api/v1/labs/{lab_id} | ocean_core/ocean_nanogrid.py | 1558 |
| POST | /api/v1/labs/{lab_id}/query | ocean_core/ocean_nanogrid.py | 1572 |
| GET | /api/v1/browse | ocean_core/ocean_nanogrid.py | 1589 |
| GET | /api/v1/search | ocean_core/ocean_nanogrid.py | 1609 |
| POST | /api/v1/chat/browse | ocean_core/ocean_nanogrid.py | 1629 |
| GET | /api/v1/rate-limit | ocean_core/ocean_nanogrid.py | 1685 |
| GET | /api/v1/status | ocean_core/ocean_nanogrid.py | 1707 |
| GET | /api/v1/now | ocean_core/ocean_nanogrid.py | 1716 |
| GET | /api/v1/weather/{city} | ocean_core/ocean_nanogrid.py | 1729 |
| GET | /api/v1/wiki/{query} | ocean_core/ocean_nanogrid.py | 1736 |
| GET | /api/v1/crypto/{symbol} | ocean_core/ocean_nanogrid.py | 1747 |
| GET | /api/v1/github/{owner}/{repo} | ocean_core/ocean_nanogrid.py | 1760 |
| GET | /api/v1/arxiv/{query} | ocean_core/ocean_nanogrid.py | 1781 |
| GET | /api/v1/earthquake | ocean_core/ocean_nanogrid.py | 1801 |
| GET | /api/v1/sources | ocean_core/ocean_nanogrid.py | 1823 |
| POST | /api/v1/vision/analyze | ocean_core/ocean_nanogrid.py | 1874 |
| POST | /api/v1/audio/transcribe | ocean_core/ocean_nanogrid.py | 1961 |
| POST | /api/v1/document/analyze | ocean_core/ocean_nanogrid.py | 2064 |
| POST | /api/v1/document/write | ocean_core/ocean_nanogrid.py | 2158 |
| GET | /api/v1/multimodal/status | ocean_core/ocean_nanogrid.py | 2245 |
| GET | / | ocean_core/asi_lite_server.py | 58 |
| GET | /health | ocean_core/asi_lite_server.py | 62 |
| GET | /api/v1/status | ocean_core/asi_lite_server.py | 66 |
| POST | /api/v1/chat | ocean_core/asi_lite_server.py | 78 |
| POST | /api/v1/query | ocean_core/asi_lite_server.py | 83 |
| GET | /health | ocean_core/gpt_oss_microservice.py | 84 |
| GET | /model/info | ocean_core/gpt_oss_microservice.py | 94 |
| POST | /api/v1/chat | ocean_core/gpt_oss_microservice.py | 109 |
| POST | /api/v1/task/submit | ocean_core/gpt_oss_microservice.py | 174 |
| GET | /api/v1/task/{task_id} | ocean_core/gpt_oss_microservice.py | 236 |
| GET | /api/v1/tasks | ocean_core/gpt_oss_microservice.py | 244 |
| DELETE | /api/v1/task/{task_id} | ocean_core/gpt_oss_microservice.py | 252 |
| GET | /health | ocean_core/run_ocean_blerina.py | 17 |
| POST | /api/v1/chat | ocean_core/run_ocean_blerina.py | 22 |
| GET | /health | ocean_core/ollama_multi_api.py | 155 |
| GET | /models | ocean_core/ollama_multi_api.py | 186 |
| POST | /api/v1/generate | ocean_core/ollama_multi_api.py | 211 |
| POST | /api/v1/chat | ocean_core/ollama_multi_api.py | 281 |
| GET | /stats | ocean_core/ollama_multi_api.py | 342 |
| GET | / | ocean_core/ocean_super_lite.py | 155 |
| GET | /health | ocean_core/ocean_super_lite.py | 166 |
| POST | /api/v1/chat | ocean_core/ocean_super_lite.py | 171 |
| POST | /api/v1/query | ocean_core/ocean_super_lite.py | 190 |
| GET | /api/v1/status | ocean_core/ocean_super_lite.py | 195 |
| POST | /api/v2/chat | ocean_core/ocean_super_lite.py | 215 |
| POST | /api/v2/query | ocean_core/ocean_super_lite.py | 221 |
| GET | /api/v2/status | ocean_core/ocean_super_lite.py | 227 |
| GET | /api/v2/models | ocean_core/ocean_super_lite.py | 250 |
| GET | /api/v2/ping | ocean_core/ocean_super_lite.py | 262 |
| GET | /health | ocean_core/bridge_engine.py | 221 |
| GET | /routes | ocean_core/bridge_engine.py | 231 |
| GET | /routes/{signal_type} | ocean_core/bridge_engine.py | 239 |
| POST | /routes/rules | ocean_core/bridge_engine.py | 247 |
| POST | /signals/process | ocean_core/bridge_engine.py | 253 |
| POST | /signals/publish | ocean_core/bridge_engine.py | 258 |
| GET | / | ocean_core/nanogrid_v3.py | 590 |
| GET | /health | ocean_core/nanogrid_v3.py | 595 |
| POST | /api/v1/chat | ocean_core/nanogrid_v3.py | 604 |
| POST | /api/v1/chat/stream | ocean_core/nanogrid_v3.py | 661 |
| POST | /api/v1/audio/transcribe | ocean_core/nanogrid_v3.py | 732 |
| POST | /api/v1/vision/analyze | ocean_core/nanogrid_v3.py | 740 |
| POST | /api/v1/document/analyze | ocean_core/nanogrid_v3.py | 786 |
| POST | /api/v1/tts | ocean_core/nanogrid_v3.py | 827 |
| GET | /api/v1/tts/voices | ocean_core/nanogrid_v3.py | 854 |
| POST | /api/v1/voice/conversation | ocean_core/nanogrid_v3.py | 863 |
| POST | /api/v1/omni | ocean_core/nanogrid_v3.py | 922 |
| GET | /api/v1/status | ocean_core/nanogrid_v3.py | 1094 |
| GET | /api/v1/diagnostics | ocean_core/nanogrid_v3.py | 1114 |
| GET | /api/v1/tools | ocean_core/nanogrid_v3.py | 1125 |
| POST | /api/v1/tools/refresh | ocean_core/nanogrid_v3.py | 1146 |
| DELETE | /api/v1/memory/{session_id} | ocean_core/nanogrid_v3.py | 1152 |
| GET | / | ocean_core/ocean_mission_service.py | 554 |
| GET | /health | ocean_core/ocean_mission_service.py | 570 |
| GET | /missions/tools | ocean_core/ocean_mission_service.py | 581 |
| POST | /missions/submit | ocean_core/ocean_mission_service.py | 586 |
| GET | /missions/{mission_id} | ocean_core/ocean_mission_service.py | 601 |
| POST | /missions/{mission_id}/resume | ocean_core/ocean_mission_service.py | 609 |
| GET | /missions | ocean_core/ocean_mission_service.py | 615 |
| GET | /regulatory/status | ocean_core/ocean_mission_service.py | 621 |
| GET | /health | ocean_core/cognitive_api.py | 24 |
| GET | / | ocean_core/cognitive_api.py | 33 |
| POST | /analyze | ocean_core/cognitive_api.py | 42 |
| GET | /api/data | ocean_core/rate_limiter.py | 16 |
| GET | /health | ocean_core/adaptive_router_api.py | 34 |
| GET | / | ocean_core/adaptive_router_api.py | 43 |
| POST | /route | ocean_core/adaptive_router_api.py | 52 |
| GET | / | ocean_core/ocean_api_hybrid.py | 162 |
| GET | /api/status | ocean_core/ocean_api_hybrid.py | 192 |
| GET | /api/sources | ocean_core/ocean_api_hybrid.py | 227 |
| GET | /api/personas | ocean_core/ocean_api_hybrid.py | 272 |
| POST | /api/query | ocean_core/ocean_api_hybrid.py | 293 |
| GET | /api/labs | ocean_core/ocean_api_hybrid.py | 407 |
| GET | /api/agents | ocean_core/ocean_api_hybrid.py | 425 |
| GET | /api/threads/{topic} | ocean_core/ocean_api_hybrid.py | 443 |
| GET | /health | ocean_core/ocean_api_hybrid.py | 497 |
| GET | /health | ocean_core/production_middleware.py | 109 |
| GET | /health/detailed | ocean_core/production_middleware.py | 117 |
| GET | /status | ocean_core/production_middleware.py | 148 |
| GET | /external-api | ocean_core/production_middleware.py | 210 |
| GET | /new-feature | ocean_core/production_middleware.py | 248 |
| GET | /external | ocean_core/production_middleware.py | 297 |
| GET | /beta-feature | ocean_core/production_middleware.py | 304 |
| GET | / | ocean_core/ocean_api_giant_restored.py | 80 |
| GET | /api/status | ocean_core/ocean_api_giant_restored.py | 99 |
| GET | /api/sources | ocean_core/ocean_api_giant_restored.py | 134 |
| POST | /api/query | ocean_core/ocean_api_giant_restored.py | 187 |
| GET | /api/labs | ocean_core/ocean_api_giant_restored.py | 250 |
| GET | /api/agents | ocean_core/ocean_api_giant_restored.py | 264 |
| GET | /api/threads/{topic} | ocean_core/ocean_api_giant_restored.py | 278 |
| GET | /health | ocean_core/ocean_api_giant_restored.py | 332 |
| GET | / | ocean_core/ocean_core_full.py | 3518 |
| GET | /health | ocean_core/ocean_core_full.py | 3535 |
| GET | /api/v1/status | ocean_core/ocean_core_full.py | 3586 |
| GET | /status | ocean_core/ocean_core_full.py | 3611 |
| GET | /api/status | ocean_core/ocean_core_full.py | 3616 |
| GET | /api/v1/integrations/status | ocean_core/ocean_core_full.py | 3696 |
| GET | /api/v1/integrations/kloud/status | ocean_core/ocean_core_full.py | 3743 |
| GET | /api/v1/kloud/status | ocean_core/ocean_core_full.py | 3744 |
| POST | /api/v1/integrations/kloud/publish | ocean_core/ocean_core_full.py | 3753 |
| POST | /api/v1/kloud/publish | ocean_core/ocean_core_full.py | 3754 |
| POST | /api/v1/integrations/kloud/sync | ocean_core/ocean_core_full.py | 3761 |
| POST | /api/v1/kloud/sync | ocean_core/ocean_core_full.py | 3762 |
| GET | /api/v1/selflearning/status | ocean_core/ocean_core_full.py | 3846 |
| POST | /api/v1/selfregeneration/rebuild | ocean_core/ocean_core_full.py | 3874 |
| GET | /api/v1/languages/world | ocean_core/ocean_core_full.py | 3887 |
| GET | /api/v1/companion/state | ocean_core/ocean_core_full.py | 3918 |
| GET | /api/v1/ocean/stack/full | ocean_core/ocean_core_full.py | 3934 |
| POST | /api/v1/signals/validate | ocean_core/ocean_core_full.py | 3997 |
| POST | /api/v1/v6/nas/select | ocean_core/ocean_core_full.py | 4025 |
| GET | /api/v1/v6/nas/stats | ocean_core/ocean_core_full.py | 4041 |
| POST | /api/v1/v6/quantum/superposition | ocean_core/ocean_core_full.py | 4055 |
| GET | /api/v1/v6/quantum/entanglement | ocean_core/ocean_core_full.py | 4080 |
| GET | /api/v1/v6/cache/predictions | ocean_core/ocean_core_full.py | 4092 |
| GET | /api/v1/v6/cache/hit_rate | ocean_core/ocean_core_full.py | 4127 |
| GET | /api/v1/v6/evolution/status | ocean_core/ocean_core_full.py | 4146 |
| POST | /api/v1/v6/evolution/trigger | ocean_core/ocean_core_full.py | 4157 |
| POST | /api/v1/signals/external | ocean_core/ocean_core_full.py | 4174 |
| POST | /api/v1/signals/internal | ocean_core/ocean_core_full.py | 4181 |
| POST | /api/v1/signals/system | ocean_core/ocean_core_full.py | 4187 |
| GET | /api/v1/signals/status | ocean_core/ocean_core_full.py | 4194 |
| GET | /api/v1/signals/recent | ocean_core/ocean_core_full.py | 4217 |
| GET | /api/v1/signals/metrics/histogram | ocean_core/ocean_core_full.py | 4228 |
| GET | /api/v1/enterprise/status | ocean_core/ocean_core_full.py | 4334 |
| GET | /api/v1/enterprise/contract | ocean_core/ocean_core_full.py | 4345 |
| POST | /api/v1/chat | ocean_core/ocean_core_full.py | 4355 |
| POST | /api/v1/chat/fast | ocean_core/ocean_core_full.py | 4394 |
| POST | /api/v1/chat/stream/warm | ocean_core/ocean_core_full.py | 4746 |
| POST | /api/v1/chat/stream | ocean_core/ocean_core_full.py | 4777 |
| POST | /api/v1/message/reaction | ocean_core/ocean_core_full.py | 5266 |
| GET | /api/v1/message/{message_id}/reactions | ocean_core/ocean_core_full.py | 5302 |
| POST | /api/v1/query | ocean_core/ocean_core_full.py | 5318 |
| GET | /api/v1/module-cores | ocean_core/ocean_core_full.py | 5354 |
| POST | /api/v1/module-cores/resolve | ocean_core/ocean_core_full.py | 5367 |
| GET | /api/v1/algebra/bits | ocean_core/ocean_core_full.py | 5399 |
| GET | /api/v1/bin/algebra | ocean_core/ocean_core_full.py | 5400 |
| POST | /api/v1/binary-algebra/operate | ocean_core/ocean_core_full.py | 5413 |
| POST | /api/v1/chat/specialized | ocean_core/ocean_core_full.py | 5479 |
| GET | /api/v1/services | ocean_core/ocean_core_full.py | 5629 |
| GET | /api/v1/advanced-array | ocean_core/ocean_core_full.py | 5659 |
| GET | /api/v1/engines | ocean_core/ocean_core_full.py | 5751 |
| GET | /api/v1/albanian/dictionary | ocean_core/ocean_core_full.py | 5779 |
| GET | /api/v1/nanogrid/status | ocean_core/ocean_core_full.py | 5800 |
| POST | /api/v1/nanogrid/vision/analyze | ocean_core/ocean_core_full.py | 5838 |
| GET | /api/v1/arxiv/{query} | ocean_core/ocean_core_full.py | 5906 |
| GET | /api/v1/wiki/{query} | ocean_core/ocean_core_full.py | 5973 |
| GET | /api/v1/pubmed/{query} | ocean_core/ocean_core_full.py | 6022 |
| GET | /api/v1/sources | ocean_core/ocean_core_full.py | 6089 |
| GET | /api/v1/browse | ocean_core/ocean_core_full.py | 6185 |
| GET | /api/v1/search | ocean_core/ocean_core_full.py | 6247 |
| POST | /api/v1/chat/browse | ocean_core/ocean_core_full.py | 6370 |
| POST | /api/v1/chat/browse/stream | ocean_core/ocean_core_full.py | 6430 |
| POST | /api/v1/zurich | ocean_core/ocean_core_full.py | 6716 |
| GET | /api/v1/zurich/info | ocean_core/ocean_core_full.py | 6756 |
| POST | /api/v1/debate/stream | ocean_core/ocean_core_full.py | 7469 |
| POST | /api/v1/debate | ocean_core/ocean_core_full.py | 7738 |
| GET | /api/v1/debate/personas | ocean_core/ocean_core_full.py | 7832 |
| POST | /api/v1/tts | ocean_core/ocean_core_full.py | 7930 |
| GET | /api/v1/tts/voices | ocean_core/ocean_core_full.py | 8005 |
| POST | /api/v1/voice/conversation | ocean_core/ocean_core_full.py | 8017 |
| GET | /api/v1/document/capabilities | ocean_core/ocean_core_full.py | 8327 |
| GET | /api/v1/documents/capabilities | ocean_core/ocean_core_full.py | 8328 |
| POST | /api/v1/documents/scan | ocean_core/ocean_core_full.py | 8353 |
| POST | /api/v1/document/scan | ocean_core/ocean_core_full.py | 8354 |
| GET | /api/v1/video/status | ocean_core/ocean_core_full.py | 8402 |
| POST | /api/v1/video/create | ocean_core/ocean_core_full.py | 8421 |
| GET | /api/documents/agents | ocean_core/ocean_core_full.py | 8463 |
| GET | /api/v1/documents/agents | ocean_core/ocean_core_full.py | 8464 |
| POST | /api/documents/generate | ocean_core/ocean_core_full.py | 8485 |
| POST | /api/v1/documents/generate | ocean_core/ocean_core_full.py | 8486 |
| GET | /api/v1/documents/metrics | ocean_core/ocean_core_full.py | 8650 |
| GET | /api/documents/metrics | ocean_core/ocean_core_full.py | 8651 |
| POST | /api/v1/documents/workflow | ocean_core/ocean_core_full.py | 8674 |
| POST | /api/documents/workflow | ocean_core/ocean_core_full.py | 8675 |
| GET | /xlc/health | ocean_core/ocean_core_full.py | 8801 |
| GET | /xlc/security/profiles | ocean_core/ocean_core_full.py | 8813 |
| GET | /xlc/security/profiles/{endpoint_name} | ocean_core/ocean_core_full.py | 8820 |
| POST | /xlc/route | ocean_core/ocean_core_full.py | 8830 |
| POST | /xlc/route/stream | ocean_core/ocean_core_full.py | 8878 |
| POST | /xlc/inspect | ocean_core/ocean_core_full.py | 9225 |
| POST | /xlc/register | ocean_core/ocean_core_full.py | 9260 |
| GET | / | ocean_core/ocean_core_lite.py | 259 |
| GET | /health | ocean_core/ocean_core_lite.py | 264 |
| GET | /api/v1/status | ocean_core/ocean_core_lite.py | 269 |
| POST | /api/v1/chat | ocean_core/ocean_core_lite.py | 274 |
| POST | /api/v1/chat/stream | ocean_core/ocean_core_lite.py | 279 |
| POST | /api/v1/query | ocean_core/ocean_core_lite.py | 295 |
| GET | /api/v1/services | ocean_core/ocean_core_lite.py | 300 |
| GET | / | ocean_core/translation_node.py | 403 |
| GET | /health | ocean_core/translation_node.py | 412 |
| GET | /api/v1/languages | ocean_core/translation_node.py | 421 |
| GET | /api/v1/languages/{region} | ocean_core/translation_node.py | 429 |
| POST | /api/v1/detect | ocean_core/translation_node.py | 439 |
| POST | /api/v1/translate | ocean_core/translation_node.py | 453 |
| GET | /api/v1/stats | ocean_core/translation_node.py | 462 |
| GET | /api/v1/phrase/{phrase_key} | ocean_core/translation_node.py | 467 |
| POST | /api/v1/chat | ocean_core/api/router.py | 113 |
| POST | /api/v1/strict | ocean_core/api/router.py | 119 |
| POST | /api/v1/admin | ocean_core/api/router.py | 125 |
| GET | /health | ocean_core/api/router.py | 220 |
| GET | /metrics | ocean_core/api/router.py | 231 |
| GET | /stats | ocean_core/api/router.py | 237 |
| POST | /admin/command | ocean_core/api/router.py | 248 |
| GET | /admin/log | ocean_core/api/router.py | 265 |
| GET | /health | packages/gram/server.py | 61 |
| POST | /gram/nodes | packages/gram/server.py | 71 |
| GET | /gram/nodes/{node_id} | packages/gram/server.py | 85 |
| POST | /gram/search | packages/gram/server.py | 93 |
| POST | /gram/json | packages/gram/server.py | 108 |
| POST | /gram/plot | packages/gram/server.py | 125 |
| POST | /gram/sequence | packages/gram/server.py | 161 |
| GET | /info | packages/signal-gen/backend/src/real-api-routes.ts | 200 |
| GET | /info | packages/signal-gen/backend/src/real-api-routes.ts | 315 |
| GET | /info | packages/signal-gen/backend/src/real-api-routes.ts | 417 |
| GET | /albi | packages/signal-gen/backend/src/real-api-routes.ts | 784 |
| GET | /alba | packages/signal-gen/backend/src/real-api-routes.ts | 788 |
| GET | /jona | packages/signal-gen/backend/src/real-api-routes.ts | 792 |
| GET | /ecosystem | packages/signal-gen/backend/src/real-api-routes.ts | 796 |
| GET | /sensors | packages/signal-gen/backend/src/real-api-routes.ts | 801 |
| GET | /system | packages/signal-gen/backend/src/real-api-routes.ts | 806 |
| GET | /metrics | packages/signal-gen/backend/src/real-api-routes.ts | 810 |
| POST | /webhook | tests/unit/test_stripe_webhook.py | 23 |
| GET | /test | tests/unit/test_minimal.py | 15 |
| GET | /status | scripts/hardware/kloud_upstream_stub.py | 32 |
| GET | /peers | scripts/hardware/kloud_upstream_stub.py | 49 |
| GET | /state | scripts/hardware/kloud_upstream_stub.py | 60 |
| POST | /submit | scripts/hardware/kloud_upstream_stub.py | 72 |
| POST | /sync_from_producer | apps/api_manager/manager.py | 70 |
| GET | /catalog | apps/api_manager/manager.py | 92 |
| POST | /apply_policy | apps/api_manager/manager.py | 97 |
| GET | /health | apps/api_manager/manager.py | 105 |
| GET | /policies | apps/api_manager/manager.py | 110 |
| GET | /status | apps/api_manager/app.py | 141 |
| GET | /metrics/full | apps/api_manager/app.py | 154 |
| POST | /control | apps/api_manager/app.py | 159 |
| GET | /status | apps/api_producer/app.py | 6 |
| POST | /register | apps/api_producer/producer.py | 40 |
| POST | /publish | apps/api_producer/producer.py | 53 |
| GET | /apis | apps/api_producer/producer.py | 66 |
| GET | /apis/{api_id} | apps/api_producer/producer.py | 73 |
| GET | /health | apps/api_producer/producer.py | 80 |
| GET | /audit | apps/api_producer/producer.py | 85 |
| GET | /health | apps/api/ocean_api_v2.py | 136 |
| GET | /api/ocean/status | apps/api/ocean_api_v2.py | 155 |
| POST | /api/ocean/users | apps/api/ocean_api_v2.py | 177 |
| GET | /api/ocean/users/{user_id} | apps/api/ocean_api_v2.py | 193 |
| POST | /api/ocean/billing/{user_id}/add-credits | apps/api/ocean_api_v2.py | 209 |
| GET | /api/ocean/billing/{user_id} | apps/api/ocean_api_v2.py | 225 |
| POST | /api/ocean/telemetry/ingest | apps/api/ocean_api_v2.py | 241 |
| POST | /api/ocean/telemetry/batch | apps/api/ocean_api_v2.py | 264 |
| GET | /api/ocean/telemetry/unprocessed | apps/api/ocean_api_v2.py | 285 |
| POST | /api/ocean/telemetry/mark-processed | apps/api/ocean_api_v2.py | 296 |
| GET | /api/ocean/analytics/sensor/{sensor_id}/stats | apps/api/ocean_api_v2.py | 309 |
| GET | /api/ocean/analytics/sensor/{sensor_id}/timeseries | apps/api/ocean_api_v2.py | 323 |
| GET | /api/ocean/analytics/sensor/{sensor_id}/anomalies | apps/api/ocean_api_v2.py | 335 |
| POST | /api/ocean/analytics/compare | apps/api/ocean_api_v2.py | 352 |
| POST | /api/ocean/profiles/store | apps/api/ocean_api_v2.py | 373 |
| GET | /api/ocean/profiles/{profile_id} | apps/api/ocean_api_v2.py | 390 |
| POST | /api/ocean/sessions/create | apps/api/ocean_api_v2.py | 409 |
| POST | /api/ocean/sessions/validate | apps/api/ocean_api_v2.py | 435 |
| POST | /api/ocean/metadata/{key} | apps/api/ocean_api_v2.py | 452 |
| GET | /api/ocean/metadata/{key} | apps/api/ocean_api_v2.py | 462 |
| GET | /api/ocean/docs | apps/api/ocean_api_v2.py | 478 |
| GET | /health | apps/api/user_data_api.py | 737 |
| GET | / | apps/api/saas_signal_api.py | 30 |
| GET | /health | apps/api/saas_signal_api.py | 35 |
| GET | /status | apps/api/saas_signal_api.py | 40 |
| POST | /signal/create | apps/api/saas_signal_api.py | 97 |
| GET | /quota/{username} | apps/api/saas_signal_api.py | 131 |
| POST | /billing/event | apps/api/saas_signal_api.py | 141 |
| GET | /billing/{username} | apps/api/saas_signal_api.py | 148 |
| GET | /audit/log | apps/api/saas_signal_api.py | 152 |
| POST | /webhook/register | apps/api/saas_signal_api.py | 156 |
| GET | /monitoring/nodes | apps/api/saas_signal_api.py | 161 |
| GET | /license/{username} | apps/api/saas_signal_api.py | 165 |
| GET | /signal/{signal_id} | apps/api/saas_signal_api.py | 172 |
| GET | /node/{node}/signals | apps/api/saas_signal_api.py | 180 |
| POST | /user/login | apps/api/saas_signal_api.py | 189 |
| POST | /auth/users | apps/api/main.py | 417 |
| POST | /auth/api-keys | apps/api/main.py | 429 |
| GET | /auth/api-keys | apps/api/main.py | 465 |
| DELETE | /auth/api-keys/{key_id} | apps/api/main.py | 480 |
| GET | /health | apps/api/main.py | 496 |
| GET | /metrics | apps/api/main.py | 509 |
| GET | /metrics | apps/api/main.py | 1480 |
| GET | /api/security/status | apps/api/main.py | 1547 |
| GET | /api/security/events | apps/api/main.py | 1577 |
| GET | /api/wwwmmm/stigma | apps/api/main.py | 1589 |
| GET | /api/ocean/status | apps/api/main.py | 1613 |
| POST | /api/ocean/session/create | apps/api/main.py | 1619 |
| GET | /api/ocean/session/{session_id} | apps/api/main.py | 1626 |
| DELETE | /api/ocean/session/{session_id} | apps/api/main.py | 1635 |
| GET | /api/ocean/cell/{cell_id} | apps/api/main.py | 1642 |
| GET | /api/ocean/cells | apps/api/main.py | 1695 |
| GET | /api/ocean/labs/list | apps/api/main.py | 1701 |
| POST | /api/ocean/labs/execute | apps/api/main.py | 1723 |
| GET | /api/ocean/web-reader | apps/api/main.py | 1761 |
| POST | /api/ocean/web-reader | apps/api/main.py | 1813 |
| POST | /api/ocean/web-reader/stream | apps/api/main.py | 1863 |
| POST | /api/ocean/megalayer | apps/api/main.py | 1904 |
| GET | /metrics | apps/api/main.py | 1945 |
| GET | /api/billing/metering-status | apps/api/main.py | 2562 |
| GET | /api/openapi-unified | apps/api/main.py | 2649 |
| GET | /api/docs-unified | apps/api/main.py | 2678 |
| GET | /health | apps/api/main.py | 2936 |
| POST | /api/uploads/eeg/process | apps/api/main.py | 3059 |
| POST | /api/uploads/audio/process | apps/api/main.py | 3132 |
| GET | /api/asi/alba/metrics | apps/api/main.py | 3621 |
| GET | /asi/alba/metrics | apps/api/main.py | 3622 |
| GET | /api/asi/albi/metrics | apps/api/main.py | 3626 |
| GET | /asi/albi/metrics | apps/api/main.py | 3627 |
| GET | /api/asi/jona/metrics | apps/api/main.py | 3631 |
| GET | /asi/jona/metrics | apps/api/main.py | 3632 |
| GET | /api/asi/status | apps/api/main.py | 3636 |
| GET | /asi/status | apps/api/main.py | 3637 |
| GET | /api/asi/health | apps/api/main.py | 3641 |
| GET | /asi/health | apps/api/main.py | 3642 |
| GET | /api/asi/joint-status | apps/api/main.py | 3647 |
| GET | /asi/joint-status | apps/api/main.py | 3648 |
| GET | /api/signals/all | apps/api/main.py | 3715 |
| GET | /signals/all | apps/api/main.py | 3716 |
| GET | /api/signals/recent | apps/api/main.py | 3752 |
| GET | /signals/recent | apps/api/main.py | 3753 |
| GET | /api/albi/eeg/analysis | apps/api/main.py | 3792 |
| GET | /api/albi/eeg/waves | apps/api/main.py | 3832 |
| GET | /api/albi/eeg/quality | apps/api/main.py | 3864 |
| GET | /api/albi/health | apps/api/main.py | 3903 |
| GET | /api/jona/status | apps/api/main.py | 3974 |
| GET | /api/jona/health | apps/api/main.py | 4009 |
| GET | /api/jona/audio/list | apps/api/main.py | 4032 |
| GET | /api/jona/session | apps/api/main.py | 4050 |
| POST | /api/jona/synthesis/start | apps/api/main.py | 4077 |
| POST | /api/jona/synthesis/stop | apps/api/main.py | 4119 |
| GET | /api/jona/audio/{file_id}/download | apps/api/main.py | 4138 |
| GET | /api/spectrum/live | apps/api/main.py | 4174 |
| GET | /api/spectrum/bands | apps/api/main.py | 4206 |
| GET | /api/spectrum/history | apps/api/main.py | 4262 |
| GET | /api/monitoring/dashboards | apps/api/main.py | 4294 |
| GET | /api/monitoring/real-metrics-info | apps/api/main.py | 4359 |
| POST | /asi/execute | apps/api/main.py | 4411 |
| GET | /api/crypto/market | apps/api/main.py | 4521 |
| GET | /api/crypto/market/detailed/{coin_id} | apps/api/main.py | 4554 |
| GET | /api/weather | apps/api/main.py | 4624 |
| GET | /api/weather/multiple-cities | apps/api/main.py | 4694 |
| GET | /api/realdata/dashboard | apps/api/main.py | 4760 |
| POST | /api/ai/analyze-neural | apps/api/main.py | 4833 |
| POST | /api/ai/eeg-interpretation | apps/api/main.py | 4907 |
| GET | /api/ai/health | apps/api/main.py | 4979 |
| POST | /api/ai/trinity-analysis | apps/api/main.py | 5114 |
| POST | /api/ai/curiosity-ocean | apps/api/main.py | 5209 |
| POST | /api/ai/quick-interpret | apps/api/main.py | 5268 |
| GET | /api/ai/agents-status | apps/api/main.py | 5326 |
| GET | /api/laboratories | apps/api/main.py | 5750 |
| GET | /api/laboratories/summary | apps/api/main.py | 5761 |
| GET | /api/laboratories/types | apps/api/main.py | 5780 |
| GET | /api/laboratories/health/{city} | apps/api/main.py | 5795 |
| GET | /api/agents/status | apps/api/main.py | 5819 |
| POST | /billing/stripe/payment-intent | apps/api/main.py | 5869 |
| POST | /api/v1/publish | apps/api/main.py | 7022 |
| POST | /api/v1/publish/batch | apps/api/main.py | 7028 |
| GET | /api/v1/published | apps/api/main.py | 7038 |
| GET | /api/docs-index | apps/api/main.py | 7078 |
| POST | /api/livekit/token | apps/api/main.py | 7107 |
| GET | /api/livekit/rooms | apps/api/main.py | 7170 |
| GET | / | apps/api/main.py | 7230 |
| GET | /health | apps/api/health_server.py | 16 |
| GET | /api/metrics | apps/api/caching_middleware.py | 289 |
| POST | /api/update | apps/api/caching_middleware.py | 304 |
| GET | /health | apps/api/main_minimal.py | 39 |
| GET | /status | apps/api/main_minimal.py | 44 |
| GET | /api/asi-status | apps/api/main_minimal.py | 58 |
| GET | / | apps/api/main_minimal.py | 74 |
| GET | /status | apps/api/master.py | 26 |
| POST | /log | apps/api/master.py | 37 |
| POST | /control | apps/api/master.py | 43 |
| GET | /health | apps/api/master.py | 53 |
| GET | /dashboard | apps/api/master.py | 57 |
| POST | /api/phone/sensor-reading | apps/api/hybrid_biometric_api.py | 165 |
| GET | /api/phone/session/{session_id} | apps/api/hybrid_biometric_api.py | 196 |
| GET | /api/phone/active-sessions | apps/api/hybrid_biometric_api.py | 212 |
| POST | /api/clinic/device/register | apps/api/hybrid_biometric_api.py | 228 |
| POST | /api/clinic/device/{device_id}/reading | apps/api/hybrid_biometric_api.py | 251 |
| GET | /api/clinic/device/{device_id}/latest | apps/api/hybrid_biometric_api.py | 292 |
| GET | /api/clinic/readings/{clinic_id} | apps/api/hybrid_biometric_api.py | 304 |
| POST | /api/session/start-hybrid | apps/api/hybrid_biometric_api.py | 325 |
| POST | /api/session/{session_id}/stop | apps/api/hybrid_biometric_api.py | 354 |
| GET | /api/session/{session_id} | apps/api/hybrid_biometric_api.py | 378 |
| GET | /api/user/{user_id}/sessions | apps/api/hybrid_biometric_api.py | 397 |
| POST | /api/clinic/register | apps/api/hybrid_biometric_api.py | 410 |
| GET | /api/clinic/{clinic_id}/config | apps/api/hybrid_biometric_api.py | 427 |
| GET | /api/clinic/{clinic_id}/devices | apps/api/hybrid_biometric_api.py | 438 |
| GET | /api/analytics/session/{session_id} | apps/api/hybrid_biometric_api.py | 485 |
| GET | /api/clinic/{clinic_id}/analytics | apps/api/hybrid_biometric_api.py | 523 |
| GET | /health | apps/api/hybrid_biometric_api.py | 558 |
| GET | /status | apps/signal_gen/server.js | 5 |
| POST | /mesh/register | apps/api/mesh/server.py | 32 |
| POST | /mesh/status | apps/api/mesh/server.py | 38 |
| GET | /mesh/nodes | apps/api/mesh/server.py | 44 |
| GET | /health | apps/api/mesh/server.py | 51 |
| GET | / | apps/api/mesh/server.py | 55 |
| GET | /favicon.ico | apps/api/utils/favicon.py | 11 |
| GET | /jona/role | apps/api/services/jona_character.py | 630 |
| POST | /jona/start | apps/api/services/jona_character.py | 635 |
| POST | /jona/stop | apps/api/services/jona_character.py | 641 |
| GET | /jona/health | apps/api/services/jona_character.py | 647 |
| GET | /jona/alerts | apps/api/services/jona_character.py | 652 |
| GET | /jona/personality | apps/api/services/jona_character.py | 660 |
| GET | /jona/session | apps/api/services/jona_character.py | 665 |
| POST | /jona/eeg/start | apps/api/services/jona_character.py | 670 |
| POST | /jona/eeg/stop | apps/api/services/jona_character.py | 676 |
| GET | /jona/eeg/latest | apps/api/services/jona_character.py | 682 |
| GET | /info | apps/api/src/server.ts | 210 |
| POST | /process | apps/api/src/server.ts | 238 |
| GET | /info | apps/api/src/server.ts | 266 |
| GET | /info | apps/api/src/server.ts | 296 |
| GET | /info | apps/api/src/server-clean.ts | 210 |
| POST | /process | apps/api/src/server-clean.ts | 238 |
| GET | /info | apps/api/src/server-clean.ts | 266 |
| GET | /info | apps/api/src/server-clean.ts | 296 |
| GET | /auth/me | apps/api/src/auth/auth-routes.ts | 331 |
| POST | /billing/create | apps/api/src/billing/payment-routes.ts | 74 |
| POST | /billing/process/:payment_id | apps/api/src/billing/payment-routes.ts | 144 |
| POST | /billing/refund | apps/api/src/billing/payment-routes.ts | 204 |
| GET | /billing/payment/:payment_id | apps/api/src/billing/payment-routes.ts | 254 |
| GET | /billing/user/:user_id/payments | apps/api/src/billing/payment-routes.ts | 286 |
| GET | /billing/stats | apps/api/src/billing/payment-routes.ts | 311 |
| GET | /billing/config | apps/api/src/billing/payment-routes.ts | 345 |
| POST | /billing/fail/:payment_id | apps/api/src/billing/payment-routes.ts | 380 |
| GET | /health | apps/alba-collector/src/server.ts | 49 |
| POST | /collect | apps/alba-collector/src/server.ts | 73 |
| GET | /data | apps/alba-collector/src/server.ts | 112 |
| GET | /health | services/ocean-voice-stt/app.py | 123 |
| GET | /capabilities | services/ocean-voice-stt/app.py | 134 |
| POST | /transcribe | services/ocean-voice-stt/app.py | 170 |
| POST | /synthesize | services/ocean-voice-stt/app.py | 199 |
| GET | / | services/dr_albana/main.py | 242 |
| GET | /health | services/dr_albana/main.py | 294 |
| GET | /api/v1/medical/domains | services/dr_albana/main.py | 305 |
| POST | /api/v1/medical/pillars/generate | services/dr_albana/main.py | 350 |
| GET | /api/v1/medical/pillars/{pillar_id} | services/dr_albana/main.py | 390 |
| GET | /api/v1/medical/pillars | services/dr_albana/main.py | 397 |
| POST | /api/v1/medical/auto-generate | services/dr_albana/main.py | 1298 |
| GET | /api/v1/medical/stats | services/dr_albana/main.py | 1309 |
| POST | /api/v1/medical/publish/{article_id} | services/dr_albana/main.py | 1326 |
| GET | / | services/ai-global-9999/app.py | 60 |
| GET | /health | services/ai-global-9999/app.py | 71 |
| GET | /api/v1/tools/status | services/ai-global-9999/app.py | 81 |
| POST | /api/v1/automation/plan | services/ai-global-9999/app.py | 113 |
| POST | /api/v1/chat | services/ai-global-9999/app.py | 158 |
| GET | /health | services/platform_orchestrator/main.py | 52 |
| GET | /api/v1/orchestrator/status | services/platform_orchestrator/main.py | 61 |
| GET | /api/v1/orchestrator/health | services/platform_orchestrator/main.py | 71 |
| GET | / | services/excel/main.py | 84 |
| GET | /health | services/excel/main.py | 103 |
| GET | /status | services/excel/main.py | 115 |
| GET | /api/status | services/excel/main.py | 116 |
| GET | /api/excel/generate | services/excel/main.py | 129 |
| POST | /api/excel/validate | services/excel/main.py | 200 |
| POST | /api/excel/parse | services/excel/main.py | 254 |
| GET | /api/excel/formulas | services/excel/main.py | 301 |
| GET | /api/excel/office-scripts | services/excel/main.py | 319 |
| POST | /api/excel/run-script | services/excel/main.py | 357 |
| GET | /api/excel/templates | services/excel/main.py | 368 |
| GET | /health | services/clx_brain/api.py | 92 |
| GET | /public/health | services/clx_brain/api.py | 109 |
| GET | /status | services/clx_brain/api.py | 114 |
| GET | /public/status | services/clx_brain/api.py | 135 |
| GET | /metrics | services/clx_brain/api.py | 140 |
| GET | /public/metrics | services/clx_brain/api.py | 164 |
| GET | / | services/clx_brain/api.py | 173 |
| GET | /public | services/clx_brain/api.py | 209 |
| GET | /health | services/user-management/main.py | 183 |
| GET | / | services/user-management/main.py | 189 |
| POST | /api/users/register | services/user-management/main.py | 208 |
| POST | /api/users/login | services/user-management/main.py | 238 |
| POST | /api/users/logout | services/user-management/main.py | 266 |
| POST | /api/users/password/forgot | services/user-management/main.py | 286 |
| POST | /api/users/password/reset | services/user-management/main.py | 312 |
| POST | /api/users/password/change | services/user-management/main.py | 328 |
| POST | /api/users/validate-token | services/user-management/main.py | 347 |
| POST | /api/users/validate-api-key | services/user-management/main.py | 369 |
| GET | /api/users/me | services/user-management/main.py | 391 |
| GET | /api/users/me/profile | services/user-management/main.py | 412 |
| PUT | /api/users/me/profile | services/user-management/main.py | 426 |
| GET | /api/users/me/usage | services/user-management/main.py | 444 |
| GET | /api/users/me/api-key | services/user-management/main.py | 458 |
| GET | /api/admin/users | services/user-management/main.py | 477 |
| GET | /api/admin/users/{user_id} | services/user-management/main.py | 519 |
| POST | /api/admin/users/{user_id}/activate | services/user-management/main.py | 542 |
| POST | /api/admin/users/{user_id}/suspend | services/user-management/main.py | 557 |
| POST | /api/admin/users/{user_id}/change-plan | services/user-management/main.py | 573 |
| POST | /api/admin/users/{user_id}/add-credits | services/user-management/main.py | 594 |
| GET | /api/admin/stats | services/user-management/main.py | 610 |
| GET | /api/users/check-email/{email} | services/user-management/main.py | 625 |
| GET | /api/users/check-username/{username} | services/user-management/main.py | 641 |
| GET | /api/users/by-clerk/{clerk_id} | services/user-management/main.py | 657 |
| GET | /health | services/concept_gap/service.py | 6 |
| GET | /health | services/billing_core/main.py | 186 |
| GET | /api/v1/plans | services/billing_core/main.py | 197 |
| POST | /api/v1/register | services/billing_core/main.py | 214 |
| POST | /api/v1/checkout | services/billing_core/main.py | 242 |
| POST | /api/v1/webhooks/stripe | services/billing_core/main.py | 270 |
| GET | /api/v1/entitlements/{api_key} | services/billing_core/main.py | 326 |
| GET | /api/v1/entitlements/resolve | services/billing_core/main.py | 352 |
| GET | / | services/lab/main.py | 202 |
| GET | /health | services/lab/main.py | 207 |
| GET | /readiness | services/lab/main.py | 221 |
| GET | /manifest | services/lab/main.py | 234 |
| GET | /capabilities | services/lab/main.py | 239 |
| GET | /traces | services/lab/main.py | 245 |
| GET | /traces/{trace_id} | services/lab/main.py | 252 |
| POST | /analyze | services/lab/main.py | 260 |
| GET | / | services/crawler/api.py | 335 |
| GET | /health | services/crawler/api.py | 345 |
| POST | /crawl | services/crawler/api.py | 350 |
| GET | /status | services/crawler/api.py | 361 |
| GET | /status/{job_id} | services/crawler/api.py | 382 |
| GET | /coverage | services/crawler/api.py | 390 |
| GET | /coverage/{job_id} | services/crawler/api.py | 435 |
| GET | /jobs/recent | services/crawler/api.py | 440 |
| GET | /export/{job_id} | services/crawler/api.py | 459 |
| GET | / | services/curiosity_ocean/api.py | 671 |
| POST | /ask | services/curiosity_ocean/api.py | 693 |
| POST | /search-links | services/curiosity_ocean/api.py | 727 |
| POST | /open-data | services/curiosity_ocean/api.py | 739 |
| GET | /explore/{topic} | services/curiosity_ocean/api.py | 748 |
| GET | /discover | services/curiosity_ocean/api.py | 764 |
| GET | /stats | services/curiosity_ocean/api.py | 783 |
| GET | /health | services/curiosity_ocean/api.py | 788 |
| GET | /regions | services/curiosity_ocean/api.py | 797 |
| GET | /categories | services/curiosity_ocean/api.py | 816 |
| GET | / | services/eap/main.py | 50 |
| GET | /health | services/eap/main.py | 59 |
| POST | /eap/process | services/eap/main.py | 68 |
| POST | /eap/phases | services/eap/main.py | 102 |
| GET | /health | services/reporting/main.py | 876 |
| GET | /api/reporting/health | services/reporting/main.py | 877 |
| GET | /status | services/reporting/main.py | 907 |
| GET | /api/status | services/reporting/main.py | 908 |
| GET | /api/reporting/docker-containers | services/reporting/main.py | 941 |
| GET | /api/reporting/docker-stats | services/reporting/main.py | 960 |
| GET | /api/reporting/system-metrics | services/reporting/main.py | 977 |
| GET | /api/reporting/capabilities | services/reporting/main.py | 993 |
| GET | /api/reporting/project-materials | services/reporting/main.py | 1024 |
| GET | /api/reporting/metrics-history | services/reporting/main.py | 1034 |
| GET | /api/reporting/alerts | services/reporting/main.py | 1051 |
| GET | /api/reporting/list-reports | services/reporting/main.py | 1061 |
| GET | /api/reporting/download/{filename} | services/reporting/main.py | 1084 |
| DELETE | /api/reporting/clear-reports | services/reporting/main.py | 1092 |
| GET | /api/reporting/dashboard | services/reporting/main.py | 1115 |
| GET | /api/reporting/export-excel | services/reporting/main.py | 1121 |
| GET | /api/reporting/export-pptx | services/reporting/main.py | 1359 |
| GET | / | services/intelligence-lab/main.py | 127 |
| GET | /health | services/intelligence-lab/main.py | 145 |
| GET | /status | services/intelligence-lab/main.py | 168 |
| POST | /klajdi/signal | services/intelligence-lab/main.py | 185 |
| GET | /klajdi/signals | services/intelligence-lab/main.py | 212 |
| POST | /klajdi/case | services/intelligence-lab/main.py | 243 |
| GET | /klajdi/cases | services/intelligence-lab/main.py | 267 |
| POST | /klajdi/case/{case_id}/analyze | services/intelligence-lab/main.py | 277 |
| GET | /klajdi/diagnostics | services/intelligence-lab/main.py | 299 |
| GET | /klajdi/stats | services/intelligence-lab/main.py | 307 |
| GET | /klajdi/export | services/intelligence-lab/main.py | 314 |
| POST | /mali/cycle | services/intelligence-lab/main.py | 325 |
| GET | /mali/report | services/intelligence-lab/main.py | 333 |
| GET | /mali/report/markdown | services/intelligence-lab/main.py | 341 |
| POST | /mali/monitor/start | services/intelligence-lab/main.py | 353 |
| POST | /mali/monitor/stop | services/intelligence-lab/main.py | 369 |
| GET | /mali/announcements | services/intelligence-lab/main.py | 377 |
| POST | /mali/announce | services/intelligence-lab/main.py | 400 |
| POST | /mali/acknowledge/{announcement_id} | services/intelligence-lab/main.py | 427 |
| GET | /mali/stats | services/intelligence-lab/main.py | 440 |
| GET | /tables/all | services/intelligence-lab/main.py | 451 |
| GET | /tables/system | services/intelligence-lab/main.py | 458 |
| GET | /tables/docker | services/intelligence-lab/main.py | 465 |
| GET | /tables/liam | services/intelligence-lab/main.py | 472 |
| GET | /tables/alda | services/intelligence-lab/main.py | 479 |
| GET | /combined/dashboard | services/intelligence-lab/main.py | 490 |
| GET | /combined/article-data | services/intelligence-lab/main.py | 511 |
| GET | / | services/regulatory/main.py | 162 |
| GET | /health | services/regulatory/main.py | 181 |
| GET | /api/regulatory/status | services/regulatory/main.py | 190 |
| POST | /api/regulatory/preflight | services/regulatory/main.py | 207 |
| POST | /api/regulatory/drift/evaluate | services/regulatory/main.py | 233 |
| POST | /api/regulatory/change/propose | services/regulatory/main.py | 245 |
| POST | /api/regulatory/change/approve | services/regulatory/main.py | 255 |
| GET | /api/regulatory/change/log | services/regulatory/main.py | 271 |
| POST | /api/regulatory/liability/link | services/regulatory/main.py | 279 |
| GET | /api/regulatory/liability/{prediction_id} | services/regulatory/main.py | 292 |
| POST | /api/regulatory/federated/collect | services/regulatory/main.py | 300 |
| POST | /api/regulatory/federated/can-transfer | services/regulatory/main.py | 315 |
| GET | /api/regulatory/federated/export | services/regulatory/main.py | 325 |
| GET | / | services/kloud_bridge/main.py | 681 |
| GET | /health | services/kloud_bridge/main.py | 732 |
| GET | /status | services/kloud_bridge/main.py | 1328 |
| GET | /failure-modes | services/kloud_bridge/main.py | 1361 |
| GET | /fabric/summary | services/kloud_bridge/main.py | 1372 |
| GET | /fabric/state | services/kloud_bridge/main.py | 1373 |
| GET | /ocean/status | services/kloud_bridge/main.py | 1382 |
| GET | /hardware/profile | services/kloud_bridge/main.py | 1388 |
| GET | /hardware/contracts/firmware-v0.1 | services/kloud_bridge/main.py | 1413 |
| GET | /hardware/hierarchy/blueprint | services/kloud_bridge/main.py | 1425 |
| GET | /hardware/hierarchy | services/kloud_bridge/main.py | 1436 |
| GET | /contracts/openapi-v1 | services/kloud_bridge/main.py | 1450 |
| GET | /hardware/nodes | services/kloud_bridge/main.py | 1462 |
| GET | /hardware/registry | services/kloud_bridge/main.py | 1473 |
| GET | /hardware/nodes/{node_id} | services/kloud_bridge/main.py | 1484 |
| POST | /hardware/nodes/register | services/kloud_bridge/main.py | 1497 |
| POST | /hardware/nodes/heartbeat | services/kloud_bridge/main.py | 1572 |
| POST | /hardware/nodes/control | services/kloud_bridge/main.py | 1650 |
| POST | /hardware/hierarchy/dispatch | services/kloud_bridge/main.py | 1701 |
| POST | /hardware/nodes/pulse | services/kloud_bridge/main.py | 1769 |
| GET | /hardware/mesh/status | services/kloud_bridge/main.py | 1823 |
| POST | /hardware/mesh/ping | services/kloud_bridge/main.py | 1841 |
| GET | /admin/diagnostics | services/kloud_bridge/main.py | 1905 |
| GET | /admin/audit/recent | services/kloud_bridge/main.py | 1948 |
| POST | /ocean/signals/publish | services/kloud_bridge/main.py | 1965 |
| POST | /signals/publish | services/kloud_bridge/main.py | 2012 |
| POST | /fabric/sync | services/kloud_bridge/main.py | 2070 |
| POST | /v1/chat/completions | services/kloud_bridge/main.py | 2381 |
| POST | /api/generate | services/kloud_bridge/main.py | 2405 |
| GET | /health | services/cycle-engine/main.py | 50 |
| GET | /status | services/cycle-engine/main.py | 55 |
| POST | /api/v1/cycle/run | services/cycle-engine/main.py | 65 |
| GET | /api/v1/cycle/runs | services/cycle-engine/main.py | 89 |
| GET | /health | services/blog-paywall/blog_paywall_service.py | 476 |
| GET | /api/tiers | services/blog-paywall/blog_paywall_service.py | 487 |
| POST | /api/subscribe | services/blog-paywall/blog_paywall_service.py | 505 |
| GET | /api/subscription/{email} | services/blog-paywall/blog_paywall_service.py | 519 |
| POST | /api/subscription/cancel | services/blog-paywall/blog_paywall_service.py | 525 |
| POST | /api/stripe/bootstrap-products | services/blog-paywall/blog_paywall_service.py | 536 |
| POST | /api/access/check | services/blog-paywall/blog_paywall_service.py | 545 |
| POST | /api/articles/{article_id}/tier | services/blog-paywall/blog_paywall_service.py | 556 |
| POST | /webhook/stripe | services/blog-paywall/blog_paywall_service.py | 563 |
| GET | /health | services/video-generator/main.py | 177 |
| GET | /status | services/video-generator/main.py | 189 |
| POST | /generate | services/video-generator/main.py | 217 |
| GET | /jobs/{job_id} | services/video-generator/main.py | 258 |
| GET | /jobs | services/video-generator/main.py | 267 |
| GET | /videos | services/video-generator/main.py | 276 |
| GET | /videos/download/{video_name} | services/video-generator/main.py | 300 |
| GET | /videos/subtitles/{video_name} | services/video-generator/main.py | 315 |
| POST | /publish/youtube | services/video-generator/main.py | 330 |
| GET | / | services/marketplace/main.py | 166 |
| GET | /health | services/marketplace/main.py | 181 |
| GET | /api/marketplace/plans | services/marketplace/main.py | 194 |
| GET | /api/marketplace/plans/{plan_id} | services/marketplace/main.py | 204 |
| POST | /api/marketplace/keys/generate | services/marketplace/main.py | 215 |
| POST | /api/marketplace/keys/validate | services/marketplace/main.py | 250 |
| GET | /api/marketplace/keys/{key_id}/usage | services/marketplace/main.py | 300 |
| GET | /api/marketplace/keys/user/{user_id} | services/marketplace/main.py | 326 |
| DELETE | /api/marketplace/keys/{key_id} | services/marketplace/main.py | 345 |
| GET | /api/marketplace/sdk | services/marketplace/main.py | 359 |
| GET | /api/marketplace/stats | services/marketplace/main.py | 391 |
| GET | /api/marketplace/quickstart | services/marketplace/main.py | 423 |
| GET | /health | services/agent-telemetry/main.py | 24 |
| GET | /status | services/agent-telemetry/main.py | 29 |
| POST | /api/v1/telemetry/events | services/agent-telemetry/main.py | 40 |
| GET | /api/v1/telemetry/events | services/agent-telemetry/main.py | 50 |
| GET | /api/v1/telemetry/metrics | services/agent-telemetry/main.py | 58 |
| DELETE | /api/v1/telemetry/events | services/agent-telemetry/main.py | 85 |
| GET | / | services/kloud_upstream_runtime/main.py | 165 |
| GET | /health | services/kloud_upstream_runtime/main.py | 176 |
| GET | /status | services/kloud_upstream_runtime/main.py | 189 |
| GET | /peers | services/kloud_upstream_runtime/main.py | 221 |
| GET | /state | services/kloud_upstream_runtime/main.py | 242 |
| GET | /nodes | services/kloud_upstream_runtime/main.py | 263 |
| POST | /nodes/register | services/kloud_upstream_runtime/main.py | 273 |
| POST | /nodes/heartbeat | services/kloud_upstream_runtime/main.py | 292 |
| POST | /submit | services/kloud_upstream_runtime/main.py | 322 |
| GET | /admin/summary | services/kloud_upstream_runtime/main.py | 366 |
| GET | / | services/aviation-weather/main.py | 201 |
| GET | /health | services/aviation-weather/main.py | 217 |
| GET | /status | services/aviation-weather/main.py | 228 |
| GET | /api/status | services/aviation-weather/main.py | 229 |
| GET | /metar/{icao} | services/aviation-weather/main.py | 240 |
| GET | /taf/{icao} | services/aviation-weather/main.py | 286 |
| GET | /conditions/{icao} | services/aviation-weather/main.py | 308 |
| GET | /multi | services/aviation-weather/main.py | 325 |
| GET | /airports/search | services/aviation-weather/main.py | 361 |
| GET | / | services/openmind/main.py | 23 |
| GET | /health | services/openmind/main.py | 33 |
| GET | /status | services/openmind/main.py | 43 |
| GET | /api/openmind/providers | services/openmind/main.py | 54 |
| POST | /api/openmind | services/openmind/main.py | 59 |
| GET | /health | services/kitchen-api/main.py | 204 |
| GET | / | services/core/main.py | 77 |
| GET | /health | services/core/main.py | 89 |
| GET | /status | services/core/main.py | 101 |
| GET | /api/status | services/core/main.py | 120 |
| GET | /asi/status | services/core/main.py | 126 |
| GET | /api/metrics | services/core/main.py | 143 |
| GET | /api/services | services/core/main.py | 160 |
| GET | /health | services/blog_api/main.py | 690 |
| GET | / | services/blog_api/main.py | 701 |
| GET | /app.js | services/blog_api/main.py | 720 |
| GET | /status | services/blog_api/main.py | 728 |
| POST | /api/v1/auth/register | services/blog_api/main.py | 753 |
| GET | /api/v1/auth/profile | services/blog_api/main.py | 788 |
| GET | /api/v1/articles | services/blog_api/main.py | 812 |
| GET | /api/v1/articles/categories | services/blog_api/main.py | 887 |
| GET | /api/v1/articles/{article_id} | services/blog_api/main.py | 915 |
| POST | /api/v1/articles/{article_id}/feedback | services/blog_api/main.py | 984 |
| GET | /api/v1/articles/{article_id}/feedback | services/blog_api/main.py | 1032 |
| GET | /api/v1/articles/{article_id}/feedback/summary | services/blog_api/main.py | 1061 |
| PATCH | /api/v1/feedback/{feedback_id}/moderate | services/blog_api/main.py | 1088 |
| GET | /api/v1/feedback/admin | services/blog_api/main.py | 1108 |
| POST | /api/v1/payments/article | services/blog_api/main.py | 1146 |
| POST | /api/v1/payments/subscribe | services/blog_api/main.py | 1204 |
| POST | /api/v1/payments/webhook | services/blog_api/main.py | 1266 |
| GET | /api/v1/adsense/config | services/blog_api/main.py | 1371 |
| GET | /api/v1/ads | services/blog_api/main.py | 1385 |
| POST | /api/v1/ads/{ad_id}/impression | services/blog_api/main.py | 1422 |
| POST | /api/v1/ads/{ad_id}/click | services/blog_api/main.py | 1457 |
| GET | /api/v1/admin/ads | services/blog_api/main.py | 1487 |
| POST | /api/v1/admin/ads | services/blog_api/main.py | 1518 |
| PUT | /api/v1/admin/ads/{ad_id} | services/blog_api/main.py | 1556 |
| DELETE | /api/v1/admin/ads/{ad_id} | services/blog_api/main.py | 1596 |
| GET | /api/v1/admin/analytics | services/blog_api/main.py | 1622 |
| GET | /health | services/ads_core/main.py | 142 |
| GET | /api/v1/ads/config | services/ads_core/main.py | 154 |
| POST | /api/v1/ads/track | services/ads_core/main.py | 171 |
| GET | /api/v1/ads/stats | services/ads_core/main.py | 196 |
| GET | /health | services/nanogrid_zeiss/main.py | 38 |
| GET | /api/v1/nanogrid/status | services/nanogrid_zeiss/main.py | 67 |
| POST | /api/v1/nanogrid/vision/analyze | services/nanogrid_zeiss/main.py | 97 |
| GET | /health | services/content-factory/linkedin_oauth_server.py | 53 |
| GET | /api/linkedin/auth | services/content-factory/linkedin_oauth_server.py | 59 |
| GET | /api/linkedin/callback | services/content-factory/linkedin_oauth_server.py | 89 |
| POST | /api/linkedin/post | services/content-factory/linkedin_oauth_server.py | 162 |
| GET | /api/linkedin/posts | services/content-factory/linkedin_oauth_server.py | 238 |
| GET | / | services/content-factory/main.py | 306 |
| GET | /health | services/content-factory/main.py | 323 |
| GET | /status | services/content-factory/main.py | 336 |
| GET | /stats | services/content-factory/main.py | 377 |
| POST | /analyze | services/content-factory/main.py | 387 |
| POST | /process | services/content-factory/main.py | 491 |
| POST | /publish | services/content-factory/main.py | 559 |
| POST | /pipeline | services/content-factory/main.py | 604 |
| POST | /auto/start | services/content-factory/main.py | 711 |
| POST | /auto/stop | services/content-factory/main.py | 738 |
| GET | /auto/stats | services/content-factory/main.py | 755 |
| POST | /auto/cycle | services/content-factory/main.py | 769 |
| GET | /auto/articles | services/content-factory/main.py | 785 |
| GET | /auto/article/{filename} | services/content-factory/main.py | 821 |
| POST | /auto/github-push | services/content-factory/main.py | 848 |
| POST | /blog/sync | services/content-factory/main.py | 868 |
| GET | /blog/stats | services/content-factory/main.py | 890 |
| POST | /blog/init | services/content-factory/main.py | 905 |
| POST | /academic/generate | services/content-factory/main.py | 925 |
| GET | /academic/status | services/content-factory/main.py | 940 |
| POST | /academic/start | services/content-factory/main.py | 954 |
| POST | /academic/stop | services/content-factory/main.py | 977 |
| GET | /health | services/content-factory/linkedin_auto_poster.py | 1880 |
| GET | /health/detailed | services/content-factory/linkedin_auto_poster.py | 1907 |
| POST | /api/linkedin/post-now | services/content-factory/linkedin_auto_poster.py | 1930 |
| POST | /api/linkedin/schedule | services/content-factory/linkedin_auto_poster.py | 1938 |
| POST | /api/linkedin/post-custom | services/content-factory/linkedin_auto_poster.py | 1963 |
| GET | /api/linkedin/pending | services/content-factory/linkedin_auto_poster.py | 2014 |
| GET | /api/linkedin/posted | services/content-factory/linkedin_auto_poster.py | 2024 |
| GET | /api/linkedin/sources | services/content-factory/linkedin_auto_poster.py | 2033 |
| GET | /api/linkedin/analytics | services/content-factory/linkedin_auto_poster.py | 2049 |
| GET | /api/linkedin/analytics/export | services/content-factory/linkedin_auto_poster.py | 2058 |
| POST | /api/linkedin/generate | services/content-factory/linkedin_auto_poster.py | 2088 |
| POST | /api/linkedin/optimize-hashtags | services/content-factory/linkedin_auto_poster.py | 2119 |
| POST | /api/linkedin/trigger-lagter | services/content-factory/linkedin_auto_poster.py | 2134 |
| POST | /api/linkedin/webhook | services/content-factory/linkedin_auto_poster.py | 2159 |
| GET | /health | services/zurich_engine/main.py | 41 |
| POST | /api/zurich | services/zurich_engine/main.py | 65 |
| GET | / | services/lagter/main.py | 73 |
| GET | /health | services/lagter/main.py | 74 |
| GET | /status | services/lagter/main.py | 75 |
| POST | /publish | services/lagter/main.py | 90 |
| POST | /publish/batch | services/lagter/main.py | 91 |
| POST | /api/v1/publish/batch | services/lagter/main.py | 92 |
| GET | /health | services/blerina/main.py | 636 |
| GET | /status | services/blerina/main.py | 652 |
| GET | /api/v1/topics | services/blerina/main.py | 684 |
| POST | /api/v1/pillars/generate | services/blerina/main.py | 701 |
| GET | /api/v1/pillars | services/blerina/main.py | 717 |
| POST | /api/v1/content/register | services/blerina/main.py | 738 |
| GET | /api/v1/pillars/{pillar_id} | services/blerina/main.py | 760 |
| POST | /api/v1/quality/check | services/blerina/main.py | 784 |
| POST | /api/v1/documents/analyze | services/blerina/main.py | 809 |
| POST | /api/v1/narratives/generate | services/blerina/main.py | 824 |
| GET | /health | services/agiem/main.py | 27 |
| GET | /status | services/agiem/main.py | 32 |
| POST | /api/v1/agents/register | services/agiem/main.py | 44 |
| POST | /api/v1/agents/heartbeat | services/agiem/main.py | 57 |
| GET | /api/v1/agents | services/agiem/main.py | 69 |
| DELETE | /api/v1/agents/{agent_id} | services/agiem/main.py | 77 |
| GET | / | services/lab_registry/main.py | 112 |
| GET | /health | services/lab_registry/main.py | 124 |
| GET | /api/v1/labs | services/lab_registry/main.py | 130 |
| GET | /api/v1/labs/{lab_id} | services/lab_registry/main.py | 143 |
| POST | /api/v1/labs/{lab_id}/analyze | services/lab_registry/main.py | 160 |
| GET | /api/v1/labs/{lab_id}/traces | services/lab_registry/main.py | 193 |
| GET | /api/v1/labs/{lab_id}/traces/{trace_id} | services/lab_registry/main.py | 205 |
| GET | /api/v1/snapshot | services/lab_registry/main.py | 221 |
| GET | / | services/blog_publisher/main.py | 1336 |
| GET | /health | services/blog_publisher/main.py | 1391 |
| GET | /api/v1/adsense/config | services/blog_publisher/main.py | 1403 |
| POST | /api/v1/publish | services/blog_publisher/main.py | 1429 |
| POST | /api/v1/publish/direct | services/blog_publisher/main.py | 1505 |
| POST | /api/v1/publish/batch | services/blog_publisher/main.py | 1556 |
| GET | /api/v1/pending | services/blog_publisher/main.py | 1592 |
| GET | /api/v1/status | services/blog_publisher/main.py | 1601 |
| GET | /api/v1/published | services/blog_publisher/main.py | 1621 |
| GET | /api/v1/articles/latest | services/blog_publisher/main.py | 1631 |
| POST | /api/v1/index/refresh | services/blog_publisher/main.py | 1693 |
| GET | / | services/knowledge_index/api.py | 110 |
| GET | /search | services/knowledge_index/api.py | 129 |
| GET | /link/{link_id} | services/knowledge_index/api.py | 197 |
| GET | /country/{country_code} | services/knowledge_index/api.py | 213 |
| GET | /category/{category} | services/knowledge_index/api.py | 241 |
| GET | /region/{region} | services/knowledge_index/api.py | 269 |
| GET | /stats | services/knowledge_index/api.py | 297 |
| GET | /random | services/knowledge_index/api.py | 323 |
| GET | /health | services/knowledge_index/api.py | 340 |
| POST | /mesh/register | backend/mesh/server.py | 32 |
| POST | /mesh/status | backend/mesh/server.py | 38 |
| GET | /mesh/nodes | backend/mesh/server.py | 44 |
| GET | /health | backend/mesh/server.py | 51 |
| GET | / | backend/mesh/server.py | 55 |
| GET | /health | backend/api/main.py | 25 |
| GET | /asi/status | backend/api/main.py | 30 |
| GET | / | backend/system/smart_orchestrator.py | 34 |
| GET | /api/events | backend/system/smart_orchestrator.py | 205 |
| GET | /api/scan | backend/system/smart_orchestrator.py | 213 |
| POST | /api/heal | backend/system/smart_orchestrator.py | 221 |
| GET | /api/export/pdf | backend/system/smart_orchestrator.py | 231 |
| POST | /api/send-now | backend/system/smart_orchestrator.py | 238 |
| GET | /reports/{filename} | backend/system/smart_orchestrator.py | 245 |
| GET | / | backend/system/web_controller.py | 80 |
| GET | /results | backend/system/web_controller.py | 84 |
| POST | /scan | backend/system/web_controller.py | 90 |
| GET | /export/json | backend/system/web_controller.py | 100 |
| GET | /export/cbor | backend/system/web_controller.py | 107 |
| GET | /export/pdf | backend/system/web_controller.py | 117 |
| GET | /status | backend/layers/layer12-asi/index.ts | 460 |
| POST | /metacognition | backend/layers/layer12-asi/index.ts | 526 |
| POST | /improve | backend/layers/layer12-asi/index.ts | 563 |
| GET | /strategy | backend/layers/layer12-asi/index.ts | 606 |
| POST | /metacognition | backend/layers/layer12-asi/optimized.ts | 26 |
| POST | /improve | backend/layers/layer12-asi/optimized.ts | 75 |
| GET | /status | backend/layers/layer12-asi/optimized.ts | 116 |
| POST | /optimize | backend/layers/layer12-asi/optimized.ts | 155 |
| GET | /status | backend/layers/layer9-memory/index.ts | 26 |
| POST | /node | backend/layers/layer9-memory/index.ts | 37 |
| POST | /strategy | backend/layers/layer9-memory/index.ts | 73 |
| POST | /gc | backend/layers/layer9-memory/index.ts | 93 |
| POST | /allocate | backend/layers/layer9-memory/optimized.ts | 24 |
| GET | /status | backend/layers/layer9-memory/optimized.ts | 70 |
| POST | /gc | backend/layers/layer9-memory/optimized.ts | 103 |
| GET | /status | backend/layers/layer10-quantum/index.ts | 354 |
| POST | /quantum/circuit | backend/layers/layer10-quantum/index.ts | 404 |
| POST | /quantum/gate | backend/layers/layer10-quantum/index.ts | 439 |
| POST | /quantum/measure | backend/layers/layer10-quantum/index.ts | 474 |
| POST | /energy/optimize | backend/layers/layer10-quantum/index.ts | 511 |
| GET | /energy/sources | backend/layers/layer10-quantum/index.ts | 533 |
| GET | /status | backend/layers/layer11-agi/index.ts | 385 |
| POST | /decision | backend/layers/layer11-agi/index.ts | 437 |
| GET | /goals | backend/layers/layer11-agi/index.ts | 483 |
| POST | /reasoning | backend/layers/layer11-agi/index.ts | 508 |
| POST | /knowledge | backend/layers/layer11-agi/index.ts | 542 |
| POST | /decision | backend/layers/layer11-agi/optimized.ts | 21 |
| GET | /status | backend/layers/layer11-agi/optimized.ts | 75 |
| POST | /knowledge | backend/layers/layer11-agi/optimized.ts | 104 |
| GET | /mesh/status | backend/layers/layer3-mesh/index.ts | 5 |
| GET | /alba/status | backend/layers/layer4-alba/index.ts | 213 |
| GET | /alba/streams | backend/layers/layer4-alba/index.ts | 215 |
| GET | /alba/streams/:id | backend/layers/layer4-alba/index.ts | 219 |
| POST | /alba/refresh | backend/layers/layer4-alba/index.ts | 225 |
| POST | /alba/optimize | backend/layers/layer4-alba/index.ts | 230 |
| GET | /alba/audit | backend/layers/layer4-alba/index.ts | 235 |
| GET | /alba/analyze | backend/layers/layer4-alba/index.ts | 239 |
| GET | /alba/alerts | backend/layers/layer4-alba/index.ts | 243 |
| GET | /alba/info | backend/layers/layer4-alba/index.ts | 247 |
| GET | /api/health | ultrawebthinking-backup/backend/server.ts | 83 |
| GET | /api/agi/status | ultrawebthinking-backup/backend/server.ts | 94 |
| GET | /api/agisheet/info | ultrawebthinking-backup/backend/server.ts | 108 |
| GET | /api/guardian/dashboard | ultrawebthinking-backup/backend/server.ts | 119 |
| GET | /api/guardian/logs | ultrawebthinking-backup/backend/server.ts | 120 |
| GET | /api/guardian/stats | ultrawebthinking-backup/backend/server.ts | 121 |
| GET | /api/guardian/status | ultrawebthinking-backup/backend/server.ts | 124 |
| POST | /api/agixmed/analyze | ultrawebthinking-backup/backend/server.ts | 134 |
| GET | /health | microservices/agi/index.ts | 33 |
| GET | /status | microservices/agi/index.ts | 38 |
| POST | /process | microservices/agi/index.ts | 50 |
| POST | /query | microservices/agi/index.ts | 97 |
| GET | /layers | microservices/agi/index.ts | 117 |
| GET | /metrics | microservices/agi/index.ts | 132 |
| GET | /health | microservices/auth/index.ts | 29 |
| POST | /register | microservices/auth/index.ts | 34 |
| POST | /login | microservices/auth/index.ts | 70 |
| POST | /refresh | microservices/auth/index.ts | 101 |
| GET | /me | microservices/auth/index.ts | 129 |
| POST | /logout | microservices/auth/index.ts | 134 |
| GET | /health | microservices/data/index.ts | 26 |
| GET | /stats | microservices/data/index.ts | 31 |
| POST | /store | microservices/data/index.ts | 40 |
| GET | /store/:id | microservices/data/index.ts | 66 |
| PUT | /store/:id | microservices/data/index.ts | 82 |
| DELETE | /store/:id | microservices/data/index.ts | 102 |
| GET | /store | microservices/data/index.ts | 121 |
| POST | /batch | microservices/data/index.ts | 138 |
| POST | /search | microservices/data/index.ts | 165 |
| GET | /health | microservices/realtime/index.ts | 33 |
| GET | /stats | microservices/realtime/index.ts | 44 |
| POST | /broadcast | microservices/realtime/index.ts | 56 |
| GET | /health | microservices/gateway/index.ts | 40 |
| GET | /services | microservices/gateway/index.ts | 50 |
| GET | / | microservices/gateway/index.ts | 84 |

## Protocol Matrix
| protocol | endpoint | file |
| --- | --- | --- |
| http | http://${host}:${port}/health`, | ALBI_EEG_SETTINGS_TAB_ANALYSIS.md |
| http | http://0.0.0.0:8000 | CURRENT_STATUS.md |
| http | http://127.0.0.1:6681 | ALBI_EEG_SETTINGS_TAB_ANALYSIS.md |
| http | http://127.0.0.1:6681` | ALBI_EEG_SETTINGS_TAB_ANALYSIS.md |
| http | http://46.225.14.83:11434/api/tags | OCEAN_CORE_v2_DEPLOYMENT_READY.md |
| http | http://46.225.14.83:8030/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8030/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8030/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8030/health | OCEAN_CORE_v2_DEPLOYMENT_READY.md |
| http | http://46.225.14.83:8032/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8032/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8032/health | OCEAN_CORE_v2_DEPLOYMENT_READY.md |
| http | http://46.225.14.83:8033/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8033/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8033/health | OCEAN_CORE_v2_DEPLOYMENT_READY.md |
| http | http://46.225.14.83:8035/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8035/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://46.225.14.83:8035/health | OCEAN_CORE_v2_DEPLOYMENT_READY.md |
| http | http://46.62.210.251:11434 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:16686 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:3000 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:3001 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:3001 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:5555 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:6680 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:7474 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:7777 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:8000 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:8000/docs | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:8030 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:8040 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:8041 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:8041/publish | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:8095/api/test-payment | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9001 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9090 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9094 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9101 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9102 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9103 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9123 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9301 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9302 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9303 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9304 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9305 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9306 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9307 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://46.62.210.251:9308 | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://clisonix-api:8000 | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ocean-core-blerina:8032 | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ocean-core-multimodal:8033 | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ocean-core-strict-chat:8035 | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ocean-core:8030 | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ocean-core:8030/api/v1/chat | ocean-core-diagnostic.py |
| http | http://clisonix-ocean-core:8030/api/v1/status | ocean-core-diagnostic.py |
| http | http://clisonix-ocean-core:8030/health | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ocean-core:8030/health | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ocean-core:8030/health | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ocean-core:8030/health` | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-ollama:11434 | docker-compose.local-llama.yml |
| http | http://clisonix-ollama:11434 | docker-compose.local-llama.yml |
| http | http://clisonix-ollama:11434 | docker-compose.lean.yml |
| http | http://clisonix-ollama:11434 | OCEAN_CORE_v2_DEPLOYMENT_READY.md |
| http | http://clisonix-openmind:9999 | DOCKER_LOCALHOST_FIX.md |
| http | http://clisonix-web:3000/api/ocean | ocean-core-diagnostic.py |
| http | http://localhost | docker-compose.lean.yml |
| http | http://localhost:${API_PORT}/health | docker-compose.lean.yml |
| http | http://localhost:11434/api/tags | docker-compose.lean.yml |
| http | http://localhost:11434/api/tags | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://localhost:3000 | docker-compose.lean.yml |
| http | http://localhost:3000 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:3000/api/service-discovery | DOCKER_LOCALHOST_FIX.md |
| http | http://localhost:3000/api/service-info | DOCKER_LOCALHOST_FIX.md |
| http | http://localhost:3000/api/service-info | DOCKER_LOCALHOST_FIX.md |
| http | http://localhost:3000/api/service-info` | DOCKER_LOCALHOST_FIX.md |
| http | http://localhost:3000/api/system-status | DOCKER_LOCALHOST_FIX.md |
| http | http://localhost:3000/modules/hybrid-biometric-dashboard | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| http | http://localhost:3001 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:3001 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:3001 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:3001 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:3001 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:3001 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:3001/d/clisonix-ai-agents | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:3002 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:3002 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:3002 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:3004 | CURRENT_STATUS.md |
| http | http://localhost:3004 | CURRENT_STATUS.md |
| http | http://localhost:3004/modules/fitness-dashboard | CURRENT_STATUS.md |
| http | http://localhost:3004/modules/fitness-dashboard` | CURRENT_STATUS.md |
| http | http://localhost:3004` | CURRENT_STATUS.md |
| http | http://localhost:5432 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:5555 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:6666 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:7777 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:8000 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:8000 | CURRENT_STATUS.md |
| http | http://localhost:8000 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/ai/agents-status | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/ai/agents-status | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/ai/agents-status | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/ai/curiosity-ocean | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/ai/curiosity-ocean | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/ai/trinity-analysis | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/asi/status | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/external/crypto | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/external/weather | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/api/v1/service-discovery | FIREBASE_KEY_SETUP_QUICK.md |
| http | http://localhost:8000/docs | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:8000/docs | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:8000/docs | CURRENT_STATUS.md |
| http | http://localhost:8000/docs | CURRENT_STATUS.md |
| http | http://localhost:8000/docs` | CURRENT_STATUS.md |
| http | http://localhost:8000/docs` | FITNESS_MODULE_IMPLEMENTATION_SUMMARY.md |
| http | http://localhost:8000/fitness/analyze/pose | FITNESS_MODULE_IMPLEMENTATION_SUMMARY.md |
| http | http://localhost:8000/fitness/health | FITNESS_MODULE_IMPLEMENTATION_SUMMARY.md |
| http | http://localhost:8000/fitness/users/profile | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:8000/fitness/users/profile | FITNESS_MODULE_IMPLEMENTATION_SUMMARY.md |
| http | http://localhost:8000/fitness/users/profile | FITNESS_MODULE_IMPLEMENTATION_SUMMARY.md |
| http | http://localhost:8000/fitness/users/{user_id}/biometrics | FITNESS_MODULE_IMPLEMENTATION_SUMMARY.md |
| http | http://localhost:8000/fitness/users/{user_id}/workouts | FITNESS_MODULE_IMPLEMENTATION_SUMMARY.md |
| http | http://localhost:8000/health | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:8000/health | DOCKER_LOCALHOST_FIX.md |
| http | http://localhost:8000/health | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://localhost:8000/metrics | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:8000/redoc | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:8000/redoc` | FITNESS_MODULE_IMPLEMENTATION_SUMMARY.md |
| http | http://localhost:8001 | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| http | http://localhost:8030 | test_multilang_fix.py |
| http | http://localhost:8030/health | DOCKER_LOCALHOST_FIX.md |
| http | http://localhost:8030/health | docker-compose.lean.yml |
| http | http://localhost:8030/health | DEPLOYMENT_SUMMARY_HETZNER.md |
| http | http://localhost:8030/health | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://localhost:8030/health` | OCEAN_CORE_v2_HETZNER_GUIDE.md |
| http | http://localhost:8035/api/v1/pillars/generate | update_blerina_topics.py |
| http | http://localhost:8888 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:9001 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:9090 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:9090 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:9090 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:9090 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:9090 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:9090 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:9090 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:9090 | INTEGRATION_GUIDE_AI_AGENTS.md |
| http | http://localhost:9999 | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:9999/health | DOCKER_STARTUP_REPORT.md |
| http | http://localhost:PORT/health | OCEAN_CORE_v2_DEPLOYMENT_READY.md |
| http | http://ocean-core:8030 | docker-compose.lean.yml |
| http | http://ollama:11434/api/generate | ocean-core-diagnostic.py |
| http | http://ollama:11434/api/tags | ocean-core-diagnostic.py |
| https | https://api.clisonix.com | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://api.example.com | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://brainflow.readthedocs.io/ | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://clinic-api.example.com | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://clinic-api.example.com | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://clisonix-docs.example.com | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://clisonix.com | DEPLOYMENT_CHECKLIST.md |
| https | https://console.cloud.google.com/apis/library/firestore.googleapis.com | FIREBASE_KEY_SETUP_QUICK.md |
| https | https://console.cloud.google.com/iam-admin/serviceaccounts | FIREBASE_KEY_SETUP_QUICK.md |
| https | https://console.firebase.google.com/ | FIREBASE_KEY_SETUP_QUICK.md |
| https | https://console.firebase.google.com/ | FIREBASE_KEY_SETUP_QUICK.md |
| https | https://console.firebase.google.com/ | FIREBASE_KEY_SETUP_QUICK.md |
| https | https://console.hetzner.cloud | DEPLOYMENT_SUMMARY_HETZNER.md |
| https | https://console.hetzner.com | DEPLOYMENT_CHECKLIST.md |
| https | https://dashboard.stripe.com/test/webhooks | DEPLOYMENT_SUMMARY_HETZNER.md |
| https | https://docs.anthropic.com | INTEGRATION_GUIDE_AI_AGENTS.md |
| https | https://docs.anthropic.com/en/docs/build/tool-use | AI_AGENT_FRAMEWORKS.md |
| https | https://docs.docker.com/compose | DEPLOYMENT_SUMMARY_HETZNER.md |
| https | https://docs.hetzner.cloud | DEPLOYMENT_SUMMARY_HETZNER.md |
| https | https://github.com/LedjanAhmati/clisonix-blog | REPO_AUDIT.md |
| https | https://github.com/Significant-Gravitas/AutoGPT | AI_AGENT_FRAMEWORKS.md |
| https | https://github.com/Web8kameleon-hub/clisonix.com | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://github.com/Web8kameleon-hub/clisonix.com | REPO_AUDIT.md |
| https | https://github.com/Web8kameleon-hub/clisonix.com | DEPLOYMENT_SUMMARY_HETZNER.md |
| https | https://github.com/joaomdmoura/crewai | AI_AGENT_FRAMEWORKS.md |
| https | https://github.com/joaomdmoura/crewai | INTEGRATION_GUIDE_AI_AGENTS.md |
| https | https://github.com/langchain-ai/langchain | AI_AGENT_FRAMEWORKS.md |
| https | https://grafana.com | INTEGRATION_GUIDE_AI_AGENTS.md |
| https | https://mne.tools/ | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://n8n.io | AI_AGENT_FRAMEWORKS.md |
| https | https://openbci.com/ | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| https | https://prometheus.io | INTEGRATION_GUIDE_AI_AGENTS.md |
| https | https://prometheus.io/download/ | INTEGRATION_GUIDE_AI_AGENTS.md |
| https | https://python.langchain.com | INTEGRATION_GUIDE_AI_AGENTS.md |
| https | https://raw.githubusercontent.com/Web8kameleon-hub/clisonix.com/main/deploy-hetzner.sh | DEPLOYMENT_CHECKLIST.md |
| https | https://support.hetzner.com/) | HETZNER_SUPPORT_TEMPLATE.md |
| https | https://www.clisonix.com | DEPLOYMENT_CHECKLIST.md |
| https | https://www.postman.com | INTEGRATION_GUIDE_AI_AGENTS.md |
| https | https://www.strato.de/apps/CustomerService | DEPLOYMENT_CHECKLIST.md |
| redis | redis://:${REDIS_PASSWORD}@redis:6379/0 | docker-compose.lean.yml |
| redis | redis://:${REDIS_PASSWORD}@redis:6379/0 | docker-compose.lean.yml |
| ws | ws://6681/stream/{id} | ALBI_EEG_SETTINGS_TAB_ANALYSIS.md |
| wss | wss://api.clisonix.com/ws | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| wss | wss://api.example.com/ws/clinic/clinic_001/stream | HYBRID_BIOMETRIC_DOCUMENTATION.md |
| wss | wss://clinic-api.example.com/ws | HYBRID_BIOMETRIC_DOCUMENTATION.md |

## CLX Mass Adoption Tracks
### Install Paths
| path |
| --- |
| README.md |
| apps/web/README.md |
| CLX_AI_INSTALLATION_GUIDE.md |
| sdk/python/README.md |
| sdk/typescript/README.md |
| hardware/kloud-soc/README.md |
| scripts/hardware/rust_node_agent/README.md |

### API: AGIMED
_No data found._

### API: IoT Mesh
| method | route | file | line |
| --- | --- | --- | --- |
| POST | /metrics/upload | mesh_hq_receiver.py | 53 |
| GET | /health | mesh_hq_receiver.py | 79 |
| GET | /metrics/latest | mesh_hq_receiver.py | 96 |
| GET | /api/mesh-status | balancer_nodes_3334.py | 278 |
| POST | /mesh/register | asi_api_server.py | 151 |
| POST | /mesh/send | asi_api_server.py | 162 |
| POST | /mesh/register | apps/api/mesh/server.py | 32 |
| POST | /mesh/status | apps/api/mesh/server.py | 38 |
| GET | /mesh/nodes | apps/api/mesh/server.py | 44 |
| GET | /health | apps/api/mesh/server.py | 51 |
| GET | / | apps/api/mesh/server.py | 55 |
| GET | /hardware/mesh/status | services/kloud_bridge/main.py | 1823 |
| POST | /hardware/mesh/ping | services/kloud_bridge/main.py | 1841 |
| POST | /mesh/register | backend/mesh/server.py | 32 |
| POST | /mesh/status | backend/mesh/server.py | 38 |
| GET | /mesh/nodes | backend/mesh/server.py | 44 |
| GET | /health | backend/mesh/server.py | 51 |
| GET | / | backend/mesh/server.py | 55 |
| GET | /mesh/status | backend/layers/layer3-mesh/index.ts | 5 |

### MyMirror Defence
_No data found._

| path |
| --- |
| apps/web/src/lib/mymirror-data-catalog.ts |
| apps/web/app/api/mymirror/export/route.ts |
| apps/web/app/api/mymirror/alert-policy/route.ts |
| apps/web/app/api/mymirror/live-metrics/route.ts |
| apps/web/app/api/mymirror/data-sources/route.ts |
| apps/web/app/api/mymirror/docker-containers/route.ts |
| apps/web/app/api/mymirror/data-sources/[id]/route.ts |
| apps/web/app/modules/mymirror-now/page.tsx |

### CLX Hardware & Chips
| path |
| --- |
| docs/architecture/OCEANCORE_KLOUD_HARDWARE_IMPLEMENTATION_PLAN.md |
| scripts/hardware/oceancore_edge_node.py |
| scripts/hardware/kloud_upstream_stub.py |
| scripts/hardware/rust_node_agent/.dockerignore |
| scripts/hardware/rust_node_agent/Cargo.toml |
| scripts/hardware/rust_node_agent/Cargo.lock |
| scripts/hardware/rust_node_agent/README.md |
| scripts/hardware/rust_node_agent/Dockerfile |
| scripts/hardware/profiles/oceancore_lab_01.json |
| scripts/hardware/profiles/oceancore_lab_02.json |
| scripts/hardware/rust_node_agent/profiles/oceancore_live_01.json |
| scripts/hardware/rust_node_agent/src/main.rs |
| hardware/kloud-soc/RISCV_RELIABILITY_GAP.md |
| hardware/kloud-soc/README.md |
| hardware/kloud-soc/fpga/ulx3s_top.v |
| hardware/kloud-soc/fpga/ulx3s.lpf |
| hardware/kloud-soc/rtl/kloud_bridge_hw.v |
| hardware/kloud-soc/rtl/sync_engine.v |
| hardware/kloud-soc/rtl/picorv32.v |
| hardware/kloud-soc/rtl/pulse_engine.v |
| hardware/kloud-soc/rtl/sram.v |
| hardware/kloud-soc/rtl/uart_tx_core.v |
| hardware/kloud-soc/rtl/soc_top.v |
| hardware/kloud-soc/rtl/rom.v |
| hardware/kloud-soc/scripts/verify.sh |
| hardware/kloud-soc/formal/kloud_bridge_formal.v |
| hardware/kloud-soc/formal/kloud_bridge_formal.ys |
| hardware/kloud-soc/firmware/linker.ld |
| hardware/kloud-soc/firmware/supervisor.c |
| hardware/kloud-soc/firmware/boot_rom.S |
| hardware/kloud-soc/firmware/Makefile |
| hardware/kloud-soc/tests/tb_soc_top_mmio.v |
| hardware/kloud-soc/tests/Makefile |
| hardware/kloud-soc/tests/coverage_report.py |
| hardware/kloud-soc/tests/tb_kloud_soc_engines.v |

### Creator License & Profit Protection
License references:
| path |
| --- |
| LICENSE |
| clx-ai/LICENSE |
| sdk/python/LICENSE |
| sdk/typescript/LICENSE |
| docs/legal/WWWMMM_IP_MEMO.md |

Monetization references:
| path |
| --- |
| docs/API_MONETIZATION_GUIDE.md |
| MONETIZATION_30DAY_PLAN.md |
| docs/BUSINESS_STRATEGY.md |

## npm Snapshot
| name | version | section | file |
| --- | --- | --- | --- |
| @aws-sdk/client-s3 | ^3.893.0 | dependencies | package.json |
| @aws-sdk/s3-request-presigner | ^3.893.0 | dependencies | package.json |
| @clisonix/shared | 1.0.0 | dependencies | packages/ui/package.json |
| @eslint/eslintrc | ^3.3.3 | devDependencies | apps/web/package.json |
| @eslint/eslintrc | ^3 | devDependencies | hello-ai/package.json |
| @eslint/js | ^9.0.0 | devDependencies | apps/web/package.json |
| @fastify/cors | ^11.2.0 | dependencies | package.json |
| @fastify/cors | ^11.0.1 | dependencies | packages/signal-gen/backend/package.json |
| @fastify/rate-limit | ^10.0.0 | dependencies | packages/signal-gen/backend/package.json |
| @fontsource/noto-color-emoji | ^5.2.12 | dependencies | apps/web/package.json |
| @jest/globals | ^30.3.0 | devDependencies | apps/web/package.json |
| @opennextjs/cloudflare | ^1.19.8 | dependencies | hello-ai/package.json |
| @radix-ui/react-avatar | ^1.1.11 | dependencies | apps/web/package.json |
| @radix-ui/react-dialog | ^1.1.15 | dependencies | apps/web/package.json |
| @radix-ui/react-dropdown-menu | ^2.1.16 | dependencies | apps/web/package.json |
| @radix-ui/react-scroll-area | ^1.2.10 | dependencies | apps/web/package.json |
| @radix-ui/react-select | ^2.2.6 | dependencies | apps/web/package.json |
| @radix-ui/react-separator | ^1.1.8 | dependencies | apps/web/package.json |
| @radix-ui/react-slot | ^1.2.3 | dependencies | apps/web/package.json |
| @radix-ui/react-tabs | ^1.1.13 | dependencies | apps/web/package.json |
| @radix-ui/react-tooltip | ^1.2.8 | dependencies | apps/web/package.json |
| @tailwindcss/aspect-ratio | ^0.4.2 | devDependencies | frontend/package.json |
| @tailwindcss/forms | ^0.5.11 | devDependencies | frontend/package.json |
| @tailwindcss/line-clamp | ^0.4.4 | devDependencies | frontend/package.json |
| @tailwindcss/postcss | ^4.1.18 | devDependencies | apps/pwa/package.json |
| @tailwindcss/postcss | ^4.1.18 | devDependencies | apps/web/package.json |
| @tailwindcss/postcss | ^4 | devDependencies | hello-ai/package.json |
| @tailwindcss/postcss | ^4.1.18 | dependencies | package.json |
| @tailwindcss/typography | ^0.5.19 | devDependencies | frontend/package.json |
| @types/bcryptjs | ^2.4.6 | devDependencies | backend/package.json |
| @types/bcryptjs | ^2.4.6 | devDependencies | microservices/package.json |
| @types/bcryptjs | ^2.4.6 | devDependencies | package.json |
| @types/body-parser | ^1.19.6 | devDependencies | apps/alba-collector/package.json |
| @types/body-parser | ^1.19.6 | devDependencies | apps/web/package.json |
| @types/cbor | ^5.0.1 | devDependencies | package.json |
| @types/clamscan | 2.4.1 | devDependencies | package.json |
| @types/compression | ^1.7.5 | devDependencies | microservices/package.json |
| @types/connect | ^3.4.38 | devDependencies | apps/web/package.json |
| @types/convict | ^6.1.6 | devDependencies | backend/package.json |
| @types/cors | ^2.8.19 | devDependencies | apps/alba-collector/package.json |
| @types/cors | ^2.8.17 | devDependencies | backend/package.json |
| @types/cors | ^2.8.17 | devDependencies | microservices/package.json |
| @types/express | ^4.17.25 | devDependencies | apps/alba-collector/package.json |
| @types/express | ^4.17.21 | devDependencies | backend/package.json |
| @types/express | ^5.0.2 | devDependencies | microservices/package.json |
| @types/file-type | 10.6.0 | devDependencies | package.json |
| @types/fluent-ffmpeg | 2.1.27 | devDependencies | package.json |
| @types/hpp | ^0.2.6 | devDependencies | backend/package.json |
| @types/jest | ^30.0.0 | devDependencies | apps/web/package.json |
| @types/jest | ^29.5.5 | devDependencies | backend/package.json |
| @types/jsonwebtoken | ^9.0.5 | devDependencies | backend/package.json |
| @types/jsonwebtoken | ^9.0.9 | devDependencies | microservices/package.json |
| @types/lodash | ^4.17.24 | devDependencies | apps/web/package.json |
| @types/lodash | ^4.17.23 | devDependencies | packages/shared/package.json |
| @types/mime | ^3.0.4 | devDependencies | apps/web/package.json |
| @types/multer | ^1.4.13 | devDependencies | backend/package.json |
| @types/node | ^24.0.0 | devDependencies | apps/pwa/package.json |
| @types/node | ^24.9.2 | devDependencies | apps/web/package.json |
| @types/node | ^20.8.0 | devDependencies | backend/package.json |
| @types/node | ^20.12.7 | dependencies | frontend/package.json |
| @types/node | ^20.19.39 | devDependencies | hello-ai/package.json |
| @types/node | ^22.15.21 | devDependencies | microservices/package.json |
| @types/node | 22.10.2 | devDependencies | package.json |
| @types/node | ^22.10.2 | devDependencies | packages/nanogrid/package.json |
| @types/node | ^20.8.0 | devDependencies | packages/signal-gen/backend/package.json |
| @types/node | ^20.0.0 | devDependencies | sdk/typescript/package.json |
| @types/node-fetch | ^2.6.13 | devDependencies | package.json |
| @types/pg | ^8.10.7 | devDependencies | backend/package.json |
| @types/pg | ^8.16.0 | dependencies | package.json |
| @types/react | 18.3.18 | devDependencies | apps/pwa/package.json |
| @types/react | 18.3.18 | dependencies | apps/web/package.json |
| @types/react | ^18.3.2 | dependencies | frontend/package.json |
| @types/react | ^19.1.5 | devDependencies | hello-ai/package.json |
| @types/react | 18.3.18 | devDependencies | package.json |
| @types/react | ^18.3.27 | devDependencies | packages/ui/package.json |
| @types/react-dom | 18.3.7 | devDependencies | apps/pwa/package.json |
| @types/react-dom | 18.3.7 | dependencies | apps/web/package.json |
| @types/react-dom | ^18.3.0 | dependencies | frontend/package.json |
| @types/react-dom | ^19.1.5 | devDependencies | hello-ai/package.json |
| @types/react-dom | 18.3.7 | devDependencies | package.json |
| @types/react-dom | ^18.3.7 | devDependencies | packages/ui/package.json |
| @types/supertest | ^2.0.16 | devDependencies | backend/package.json |
| @types/uuid | ^9.0.8 | devDependencies | apps/alba-collector/package.json |
| @types/uuid | ^10.0.0 | devDependencies | microservices/package.json |
| @types/ws | ^8.18.1 | devDependencies | apps/alba-collector/package.json |
| @types/ws | ^8.5.8 | devDependencies | backend/package.json |
| @types/ws | ^8.18.1 | devDependencies | microservices/package.json |
| @typescript-eslint/eslint-plugin | ^8.56.0 | dependencies | apps/web/package.json |
| @typescript-eslint/eslint-plugin | ^6.7.4 | devDependencies | backend/package.json |
| @typescript-eslint/eslint-plugin | ^8.0.0 | devDependencies | frontend/package.json |
| @typescript-eslint/eslint-plugin | ^6.0.0 | devDependencies | sdk/typescript/package.json |
| @typescript-eslint/parser | ^8.56.0 | dependencies | apps/web/package.json |
| @typescript-eslint/parser | ^6.7.4 | devDependencies | backend/package.json |
| @typescript-eslint/parser | ^8.0.0 | devDependencies | frontend/package.json |
| @typescript-eslint/parser | ^6.0.0 | devDependencies | sdk/typescript/package.json |
| @vanilla-extract/css | ^1.18.0 | dependencies | apps/web/package.json |
| autoprefixer | ^10.4.20 | devDependencies | apps/pwa/package.json |
| autoprefixer | ^10.4.20 | devDependencies | apps/web/package.json |
| autoprefixer | ^10.4.19 | dependencies | frontend/package.json |
| autoprefixer | 10.4.20 | devDependencies | package.json |
| axios | ^1.16.0 | dependencies | frontend/package.json |
| axios | ^1.16.0 | dependencies | package.json |
| bcryptjs | ^2.4.3 | dependencies | backend/package.json |
| bcryptjs | ^3.0.2 | dependencies | microservices/package.json |
| bcryptjs | ^3.0.3 | dependencies | package.json |
| body-parser | ^1.20.4 | dependencies | apps/alba-collector/package.json |
| body-parser | ^1.20.2 | dependencies | backend/package.json |
| bullmq | ^5.76.5 | dependencies | services/kitchen-worker/package.json |
| cbor | ^10.0.11 | dependencies | apps/web/package.json |
| cbor | ^10.0.11 | dependencies | backend/package.json |
| cbor | ^10.0.11 | dependencies | package.json |
| cbor | ^10.0.11 | dependencies | packages/nanogrid/package.json |
| chart.js | ^4.4.2 | dependencies | frontend/package.json |
| clamscan | 2.4.0 | dependencies | package.json |
| class-variance-authority | ^0.7.1 | dependencies | apps/web/package.json |
| classnames | ^2.3.2 | dependencies | frontend/package.json |
| clsx | ^2.1.1 | dependencies | apps/web/package.json |
| compression | ^1.8.0 | dependencies | microservices/package.json |
| compression | ^1.8.1 | dependencies | package.json |
| concurrently | ^9.2.0 | devDependencies | microservices/package.json |
| concurrently | ^9.2.1 | devDependencies | package.json |
| convict | ^6.2.4 | dependencies | backend/package.json |
| cors | ^2.8.5 | dependencies | apps/alba-collector/package.json |
| cors | ^2.8.5 | dependencies | backend/package.json |
| cors | ^2.8.5 | dependencies | microservices/package.json |
| cors | 2.8.5 | dependencies | package.json |
| cross-env | ^7.0.3 | devDependencies | apps/web/package.json |
| date-fns | ^3.6.0 | dependencies | frontend/package.json |
| date-fns | ^2.30.0 | dependencies | packages/shared/package.json |
| dotenv | ^16.3.1 | dependencies | backend/package.json |
| dotenv | ^16.5.0 | dependencies | microservices/package.json |
| eslint | 9.39.2 | devDependencies | apps/web/package.json |
| eslint | ^8.51.0 | devDependencies | backend/package.json |
| eslint | ^9.0.0 | devDependencies | frontend/package.json |
| eslint | ^9 | devDependencies | hello-ai/package.json |
| eslint | ^9.39.2 | devDependencies | package.json |
| eslint | ^8.55.0 | devDependencies | sdk/typescript/package.json |
| eslint-config-next | 16.3.0-canary.17 | devDependencies | apps/web/package.json |
| eslint-config-next | ^16.1.4 | devDependencies | frontend/package.json |
| eslint-config-next | 16.2.6 | devDependencies | hello-ai/package.json |
| express | ^4.21.1 | dependencies | apps/alba-collector/package.json |
| express | ^4.18.2 | dependencies | backend/package.json |
| express | ^4.21.2 | dependencies | microservices/package.json |
| express | ^5.2.1 | dependencies | package.json |
| express-rate-limit | ^7.1.5 | dependencies | backend/package.json |
| express-rate-limit | ^7.5.0 | dependencies | microservices/package.json |
| express-slow-down | ^2.0.1 | dependencies | backend/package.json |
| express-validator | ^7.0.1 | dependencies | backend/package.json |
| fast-xml-parser | ^5.5.5 | dependencies | package.json |
| fastify | ^5.8.2 | dependencies | package.json |
| fastify | ^5.3.0 | dependencies | packages/signal-gen/backend/package.json |
| ffprobe-static | 3.1.0 | dependencies | package.json |
| file-type | 21.3.2 | dependencies | package.json |
| fluent-ffmpeg | 2.1.3 | dependencies | package.json |
| framer-motion | ^12.30.0 | dependencies | apps/web/package.json |
| helmet | ^7.1.0 | dependencies | backend/package.json |
| helmet | ^8.1.0 | dependencies | microservices/package.json |
| helmet | 8.0.0 | dependencies | package.json |
| hermes-parser | ^0.25.1 | devDependencies | apps/web/package.json |
| hpp | ^0.2.3 | dependencies | backend/package.json |
| http-proxy-middleware | ^3.0.3 | dependencies | microservices/package.json |
| ioredis | ^5.3.2 | dependencies | backend/package.json |
| ioredis | ^5.6.1 | dependencies | microservices/package.json |
| ioredis | ^5.4.1 | dependencies | services/kitchen-worker/package.json |
| jest | ^29.7.0 | devDependencies | backend/package.json |
| jose | ^6.2.2 | dependencies | cloudflare/package.json |
| jsonwebtoken | ^9.0.2 | dependencies | backend/package.json |
| jsonwebtoken | ^9.0.2 | dependencies | microservices/package.json |
| livekit-server-sdk | ^2.15.0 | dependencies | apps/web/package.json |
| lodash | ^4.18.0 | dependencies | packages/shared/package.json |
| lucide-react | ^0.545.0 | dependencies | apps/web/package.json |
| multer | ^2.0.0 | dependencies | backend/package.json |
| newman | ^6.1.0 | dependencies | services/kitchen-worker/package.json |
| newman-reporter-htmlextra | ^1.23.1 | dependencies | services/kitchen-worker/package.json |
| next | 16.3.0-canary.17 | dependencies | apps/pwa/package.json |
| next | 16.3.0-canary.17 | dependencies | apps/web/package.json |
| next | ^16.2.6 | dependencies | frontend/package.json |
| next | 16.2.6 | dependencies | hello-ai/package.json |
| next | 16.3.0-canary.17 | dependencies | package.json |
| next-auth | ^5.0.0-beta.30 | dependencies | apps/web/package.json |
| next-sitemap | ^4.2.3 | dependencies | apps/web/package.json |
| node-fetch | ^3.3.2 | dependencies | backend/package.json |
| node-fetch | ^3.3.2 | dependencies | package.json |
| opossum | ^8.1.3 | dependencies | backend/package.json |
| pg | ^8.11.3 | dependencies | backend/package.json |
| pg | ^8.18.0 | dependencies | package.json |
| pino | ^8.17.2 | dependencies | backend/package.json |
| pino | ^9.0.0 | dependencies | packages/signal-gen/backend/package.json |
| pino-http | ^9.0.0 | dependencies | backend/package.json |
| pino-pretty | ^13.0.0 | dependencies | packages/signal-gen/backend/package.json |
| playwright | ^1.58.2 | devDependencies | apps/web/package.json |
| postcss | ^8.5.10 | dependencies | apps/pwa/package.json |
| postcss | ^8.5.6 | devDependencies | apps/pwa/package.json |
| postcss | ^8.5.14 | devDependencies | apps/web/package.json |
| postcss | ^8.5.14 | dependencies | frontend/package.json |
| postcss | ^8.5.14 | dependencies | hello-ai/package.json |
| postcss | 8.5.14 | devDependencies | package.json |
| react | 18.3.1 | dependencies | apps/pwa/package.json |
| react | 18.3.1 | dependencies | apps/web/package.json |
| react | ^18.3.1 | dependencies | frontend/package.json |
| react | 19.1.5 | dependencies | hello-ai/package.json |
| react | 18.3.1 | dependencies | package.json |
| react | ^18.0.0 | dependencies | packages/ui/package.json |
| react | ^18.0.0 | peerDependencies | packages/ui/package.json |
| react-chartjs-2 | ^5.2.0 | dependencies | frontend/package.json |
| react-dom | 18.3.1 | dependencies | apps/pwa/package.json |
| react-dom | 18.3.1 | dependencies | apps/web/package.json |
| react-dom | ^18.3.1 | dependencies | frontend/package.json |
| react-dom | 19.1.5 | dependencies | hello-ai/package.json |
| react-dom | 18.3.1 | dependencies | package.json |
| react-dom | ^18.0.0 | dependencies | packages/ui/package.json |
| react-dom | ^18.0.0 | peerDependencies | packages/ui/package.json |
| react-is | 18.3.1 | devDependencies | apps/web/package.json |
| recharts | ^3.7.0 | dependencies | apps/web/package.json |
| recharts | ^2.12.7 | dependencies | frontend/package.json |
| redis | ^4.6.10 | dependencies | backend/package.json |
| redis | 4.7.0 | dependencies | package.json |
| redis | ^4.7.0 | dependencies | services/kitchen-worker/package.json |
| rimraf | 6.0.1 | devDependencies | package.json |
| rimraf | ^6.0.1 | devDependencies | packages/nanogrid/package.json |
| rimraf | ^5.0.0 | devDependencies | packages/shared/package.json |
| rimraf | ^5.0.0 | devDependencies | packages/ui/package.json |
| stripe | ^20.3.0 | dependencies | apps/web/package.json |
| supertest | ^6.3.3 | devDependencies | backend/package.json |
| svelte | ^5.53.5 | dependencies | package.json |
| tailwind-merge | ^3.4.0 | dependencies | apps/web/package.json |
| tailwindcss | ^4.1.18 | devDependencies | apps/pwa/package.json |
| tailwindcss | ^4.1.18 | devDependencies | apps/web/package.json |
| tailwindcss | ^3.4.3 | dependencies | frontend/package.json |
| tailwindcss | ^4 | devDependencies | hello-ai/package.json |
| tailwindcss | ^3.4.17 | devDependencies | package.json |
| tsup | ^8.0.0 | devDependencies | sdk/typescript/package.json |
| tsx | ^4.21.0 | devDependencies | apps/alba-collector/package.json |
| tsx | ^4.1.0 | devDependencies | backend/package.json |
| tsx | ^4.20.3 | devDependencies | microservices/package.json |
| tsx | ^4.1.0 | devDependencies | packages/signal-gen/backend/package.json |
| typescript | ^5.6.3 | devDependencies | apps/alba-collector/package.json |
| typescript | ^5.7.0 | devDependencies | apps/pwa/package.json |
| typescript | ^5.0.2 | dependencies | apps/web/package.json |
| typescript | ^5.2.2 | devDependencies | backend/package.json |
| typescript | ^5.4.5 | dependencies | frontend/package.json |
| typescript | ^5.7.4 | devDependencies | hello-ai/package.json |
| typescript | ^5.8.3 | devDependencies | microservices/package.json |
| typescript | 5.7.2 | devDependencies | package.json |
| typescript | ^5.7.2 | devDependencies | packages/nanogrid/package.json |
| typescript | ^5.0.0 | devDependencies | packages/shared/package.json |
| typescript | ^5.2.2 | devDependencies | packages/signal-gen/backend/package.json |
| typescript | ^5.0.0 | devDependencies | packages/ui/package.json |
| typescript | ^5.3.0 | devDependencies | sdk/typescript/package.json |
| uuid | ^14.0.0 | dependencies | apps/alba-collector/package.json |
| uuid | ^14.0.0 | dependencies | apps/web/package.json |
| uuid | ^11.1.0 | dependencies | microservices/package.json |
| uuid | ^14.0.0 | dependencies | package.json |
| vite | ^6.4.2 | devDependencies | package.json |
| vitest | ^1.0.0 | devDependencies | sdk/typescript/package.json |
| winston | ^3.11.0 | dependencies | backend/package.json |
| winston | ^3.17.0 | dependencies | microservices/package.json |
| winston-daily-rotate-file | ^4.7.1 | dependencies | backend/package.json |
| wrangler | ^4.80.0 | devDependencies | cloudflare/package.json |
| wrangler | ^4.80.0 | devDependencies | hello-ai/package.json |
| ws | ^8.19.0 | dependencies | apps/alba-collector/package.json |
| ws | ^8.14.2 | dependencies | backend/package.json |
| ws | ^8.18.1 | dependencies | microservices/package.json |
| ws | ^8.19.0 | dependencies | package.json |
| zod | ^3.22.4 | dependencies | backend/package.json |
| zod | 3.24.1 | dependencies | package.json |
| zustand | ^5.0.11 | dependencies | apps/web/package.json |

## PyPI Snapshot
| name | version | section | file |
| --- | --- | --- | --- |
| Clisonix-cloud | [api,data,ocean,payments,observability] | project.optional-dependencies.full | pyproject.toml |
| Pillow | >=11.1.0 | requirements | apps/api/requirements-excel.txt |
| Pillow | >=11.1.0 | project.optional-dependencies.excel | pyproject.toml |
| Pillow | >=11.0.0 | requirements | services/video-generator/requirements.txt |
| PyJWT | >=2.10.1 | requirements | apps/api/requirements.txt |
| PyJWT | [crypto]>=2.10.1 | project.optional-dependencies.api | pyproject.toml |
| PyJWT | [crypto]>=2.10.1 | project.dependencies | services/api/pyproject.toml |
| SpeechRecognition | >=3.14.0 | requirements | requirements.txt |
| XlsxWriter | >=3.2.9 | requirements | apps/api/requirements-excel.txt |
| XlsxWriter | >=3.2.9 | project.optional-dependencies.excel | pyproject.toml |
| accelerate | >=1.0.0 | requirements | ocean_core/requirements-internal-llm.txt |
| aiofiles | >=24.1.0 | requirements | apps/api/requirements-slim.txt |
| aiofiles | >=24.1.0 | requirements | apps/api/requirements.txt |
| aiofiles | >=23.0.0 | requirements | ocean_core/requirements.txt |
| aiofiles | >=24.1.0 | project.optional-dependencies.api | pyproject.toml |
| aiofiles | >=24.1.0 | requirements | services/lab/requirements.txt |
| aiofiles | >=23.0.0 | requirements | services/video-generator/requirements.txt |
| aiohttp | >=3.11.0 | requirements | ocean_core/requirements-internal-core.txt |
| aiohttp | >=3.11.0 | requirements | ocean_core/requirements.txt |
| aiohttp | >=3.11.0 | requirements | requirements-autolearning.txt |
| aiohttp | >=3.11.0 | requirements | services/content-factory/requirements.txt |
| aiohttp | >=3.9.1 | requirements | services/newsroom/requirements.txt |
| aiohttp | >=3.11.0 | requirements | services/reporting/requirements.txt |
| aioredis | >=2.0.0 | requirements | services/clx_brain/requirements.txt |
| aioredis | >=2.0.0 | requirements | services/redis_core/requirements.txt |
| aiosqlite | >=0.20.0 | requirements | apps/api/requirements.txt |
| alembic | >=1.14.0 | requirements | apps/api/requirements-slim.txt |
| alembic | >=1.14.0 | requirements | apps/api/requirements.txt |
| alembic | >=1.14.0 | project.optional-dependencies.api | pyproject.toml |
| anyio | >=4.0.0 | requirements | ocean_core/requirements.txt |
| apscheduler | >=3.10.4 | requirements | services/dr_albana/requirements.txt |
| asyncpg | >=0.29.0 | requirements | apps/api/requirements.txt |
| asyncpg | >=0.30.0 | project.optional-dependencies.api | pyproject.toml |
| asyncpg | >=0.30.0 | requirements | requirements.txt |
| asyncpg | >=0.28.0 | requirements | services/reporting/requirements.txt |
| bandit | >=1.7.0 | requirements | requirements-dev.txt |
| beautifulsoup4 | ==4.13.5 | requirements | services/crawler/requirements.txt |
| bentoml | >=1.3.0 | requirements | ocean_core/requirements-internal-llm.txt |
| biosppy | >=2.2.2 | requirements | ocean_core/requirements-internal-eeg.txt |
| bitsandbytes | >=0.44.0 | requirements | ocean_core/requirements-internal-llm.txt |
| black | >=24.10.0 | project.optional-dependencies.dev | pyproject.toml |
| black | >=24.0.0 | requirements | requirements-dev.txt |
| black | >=23.0.0 | project.optional-dependencies.dev | sdk/python/clx/pyproject.toml |
| black | >=23.0.0 | project.optional-dependencies.dev | sdk/python/pyproject.toml |
| boto3 | >=1.34.0 | requirements | airflow/requirements.txt |
| boto3 | >=1.36.0 | requirements | requirements.txt |
| braindecode | >=0.8.1 | requirements | ocean_core/requirements-internal-eeg.txt |
| cbor2 | >=5.6.5 | requirements | apps/api/requirements.txt |
| cbor2 | >=5.6.5 | requirements | ocean_core/requirements-internal-core.txt |
| cbor2 | >=5.6.0 | requirements | ocean_core/requirements.txt |
| cbor2 | >=5.6.5 | project.optional-dependencies.ocean | pyproject.toml |
| cbor2 | >=5.6.5 | requirements | requirements-autolearning.txt |
| cbor2 | >=5.6.5 | requirements | requirements-ocean.txt |
| cbor2 | >=5.6.5 | requirements | requirements.txt |
| chromadb | >=0.5.0 | requirements | ocean_core/requirements-internal-llm.txt |
| commitizen | >=3.13.0 | requirements | requirements-dev.txt |
| controlnet_aux | >=0.0.9 | requirements | ocean_core/requirements-internal-multimodal.txt |
| cryptography | >=42.0.0 | requirements | requirements.txt |
| diffusers | >=0.31.0 | requirements | ocean_core/requirements-internal-multimodal.txt |
| docker | >=7.1.0 | requirements | requirements.txt |
| docker | >=7.1.0 | requirements | services/reporting/requirements.txt |
| duckdb | >=1.1.0 | project.optional-dependencies.ocean | pyproject.toml |
| duckdb | >=1.1.0 | requirements | requirements-ocean.txt |
| duckdb-engine | >=0.14.0 | project.optional-dependencies.ocean | pyproject.toml |
| duckdb-engine | >=0.14.0 | requirements | requirements-ocean.txt |
| edge-tts | >=7.0.0 | requirements | ocean_core/requirements-internal-core.txt |
| edge-tts | >=6.1.10 | requirements | ocean_core/requirements.txt |
| edge-tts | >=7.0.0 | requirements | requirements.txt |
| edge-tts | >=6.1.0 | requirements | services/video-generator/requirements.txt |
| elasticsearch | >=8.0.0,<9.0.0 | requirements | ocean_core/requirements-lite.txt |
| email-validator | unspecified | requirements | services/user-management/requirements.txt |
| et-xmlfile | >=2.0.0 | requirements | apps/api/requirements-excel.txt |
| faiss-cpu | >=1.8.0 | requirements | ocean_core/requirements-internal-llm.txt |
| fastapi | >=0.104.0 | requirements | 9999/requirements.txt |
| fastapi | >=0.115.6 | requirements | apps/api/requirements-slim.txt |
| fastapi | >=0.115.6 | requirements | apps/api/requirements.txt |
| fastapi | >=0.104.0 | requirements | excel-core/requirements.txt |
| fastapi | >=0.115.0 | requirements | ocean_core/requirements-internal-core.txt |
| fastapi | >=0.115.0 | requirements | ocean_core/requirements-lite.txt |
| fastapi | >=0.104.0 | requirements | ocean_core/requirements.txt |
| fastapi | >=0.115.6 | requirements | orchestra/requirements.txt |
| fastapi | >=0.115 | requirements | packages/wwwmmm-ndb-stigma-pc/requirements-min.txt |
| fastapi | >=0.115.6 | project.dependencies | pyproject.toml |
| fastapi | >=0.115.0 | requirements | requirements-ocean.txt |
| fastapi | >=0.115.6 | requirements | requirements-test.txt |
| fastapi | >=0.115.6 | requirements | requirements.txt |
| fastapi | ==0.121.0 | requirements | services/ads_core/requirements.txt |
| fastapi | >=0.110.0 | requirements | services/agent-telemetry/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/agiem/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/ai-global-9999/requirements.txt |
| fastapi | >=0.115 | project.dependencies | services/api/pyproject.toml |
| fastapi | >=0.115 | requirements | services/api/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/aviation-weather/requirements.txt |
| fastapi | ==0.121.0 | requirements | services/billing_core/requirements.txt |
| fastapi | >=0.109.0 | requirements | services/blerina/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/blog_api/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/blog_publisher/requirements.txt |
| fastapi | >=0.100.0 | requirements | services/clx_brain/requirements.txt |
| fastapi | unspecified | project.dependencies | services/concept_gap/pyproject.toml |
| fastapi | >=0.115.6 | requirements | services/content-factory/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/core/requirements.txt |
| fastapi | ==0.116.1 | requirements | services/crawler/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/cycle-engine/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/dr_albana/requirements.txt |
| fastapi | >=0.100.0 | requirements | services/excel/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/intelligence-lab/requirements.txt |
| fastapi | ==0.116.1 | requirements | services/kitchen-api/requirements.txt |
| fastapi | >=0.115,<1.0 | requirements | services/kloud_bridge/requirements.txt |
| fastapi | >=0.115,<1.0 | requirements | services/kloud_upstream_runtime/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/lab/requirements.txt |
| fastapi | >=0.109.0,<0.120.0 | requirements | services/lagter/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/reporting/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/user-management/requirements.txt |
| fastapi | >=0.115.6 | requirements | services/video-generator/requirements.txt |
| faster-whisper | >=1.1.0 | requirements | ocean_core/requirements-internal-core.txt |
| faster-whisper | >=1.1.0 | requirements | ocean_core/requirements-internal-multimodal.txt |
| faster-whisper | >=1.1.0 | requirements | ocean_core/requirements-lite.txt |
| faster-whisper | >=1.0.3 | requirements | ocean_core/requirements.txt |
| faster-whisper | >=1.1.0 | requirements | requirements.txt |
| flake8 | >=7.0.0 | requirements | requirements-dev.txt |
| googletrans | ==4.0.2 | requirements | ocean_core/requirements.txt |
| greenlet | unspecified | requirements | apps/api/requirements.txt |
| gtts | >=2.5.0 | requirements | services/video-generator/requirements.txt |
| h2 | >=4.1.0 | requirements | ocean_core/requirements-lite.txt |
| h2 | >=4.1.0 | requirements | requirements-ocean.txt |
| httpx | >=0.25.0 | requirements | 9999/requirements.txt |
| httpx | >=0.28.1 | requirements | apps/api/requirements.txt |
| httpx | >=0.25.0 | requirements | ocean_core/requirements.txt |
| httpx | >=0.27 | requirements | packages/wwwmmm-ndb-stigma-pc/requirements-min.txt |
| httpx | >=0.28.1 | project.dependencies | pyproject.toml |
| httpx | >=0.28.1 | requirements | requirements-dev.txt |
| httpx | >=0.28.1 | requirements | requirements-test.txt |
| httpx | >=0.28.1 | requirements | requirements.txt |
| httpx | >=0.28.1 | requirements | services/ai-global-9999/requirements.txt |
| httpx | unspecified | project.dependencies | services/api/pyproject.toml |
| httpx | unspecified | requirements | services/api/requirements.txt |
| httpx | >=0.28.1 | requirements | services/aviation-weather/requirements.txt |
| httpx | ==0.28.1 | requirements | services/billing_core/requirements.txt |
| httpx | >=0.26.0 | requirements | services/blerina/requirements.txt |
| httpx | ==0.25.1 | requirements | services/blog_api/requirements.txt |
| httpx | >=0.28.1 | requirements | services/blog_publisher/requirements.txt |
| httpx | >=0.28.1 | requirements | services/content-factory/requirements.txt |
| httpx | ==0.28.1 | requirements | services/crawler/requirements.txt |
| httpx | >=0.28.1 | requirements | services/dr_albana/requirements.txt |
| httpx | >=0.24.0 | requirements | services/excel/requirements.txt |
| httpx | >=0.28.1 | requirements | services/intelligence-lab/requirements.txt |
| httpx | >=0.27,<1.0 | requirements | services/kloud_bridge/requirements.txt |
| httpx | >=0.28.1 | requirements | services/lab/requirements.txt |
| httpx | >=0.26.0,<0.30.0 | requirements | services/lagter/requirements.txt |
| httpx | >=0.28.1 | requirements | services/reporting/requirements.txt |
| httpx | >=0.28.1 | requirements | services/user-management/requirements.txt |
| httpx | >=0.28.1 | requirements | services/video-generator/requirements.txt |
| imageio | >=2.34.0 | requirements | 9999/requirements.txt |
| imageio-ffmpeg | >=0.4.9 | requirements | 9999/requirements.txt |
| influxdb-client | unspecified | project.dependencies | services/api/pyproject.toml |
| influxdb-client | unspecified | requirements | services/api/requirements.txt |
| isort | >=5.13.0 | requirements | requirements-dev.txt |
| langdetect | >=1.0.9 | requirements | ocean_core/requirements.txt |
| langgraph | >=0.2.0 | requirements | ocean_core/requirements-internal-llm.txt |
| librosa | >=0.10.2 | project.optional-dependencies.ml | pyproject.toml |
| librosa | >=0.10.2 | requirements | requirements.txt |
| line-profiler | >=4.1.0 | requirements | requirements-dev.txt |
| livekit-api | >=1.0.0 | requirements | apps/api/requirements.txt |
| lxml | >=5.0.0 | requirements | apps/api/requirements-excel.txt |
| lxml | >=5.0.0 | project.optional-dependencies.excel | pyproject.toml |
| memory-profiler | >=0.61.0 | requirements | requirements-dev.txt |
| mkdocs | >=1.5.0 | requirements | requirements-dev.txt |
| mkdocs-material | >=9.4.0 | requirements | requirements-dev.txt |
| mne | >=1.8.0 | requirements | ocean_core/requirements-internal-eeg.txt |
| mne | >=1.8.0 | project.optional-dependencies.ml | pyproject.toml |
| mne | >=1.8.0 | requirements | requirements.txt |
| moviepy | >=1.0.3 | requirements | ocean_core/requirements-internal-multimodal.txt |
| moviepy | >=1.0.3 | requirements | services/video-generator/requirements.txt |
| msgpack | >=1.1.0 | requirements | apps/api/requirements.txt |
| msgpack | >=1.1.0 | requirements | ocean_core/requirements-internal-core.txt |
| msgpack | >=1.0.7 | requirements | ocean_core/requirements.txt |
| msgpack | >=1.1.0 | project.optional-dependencies.ocean | pyproject.toml |
| msgpack | >=1.1.0 | requirements | requirements-ocean.txt |
| msgpack | >=1.1.2 | requirements | requirements.txt |
| mutagen | >=1.47.0 | requirements | services/video-generator/requirements.txt |
| mypy | >=1.13.0 | project.optional-dependencies.dev | pyproject.toml |
| mypy | >=1.8.0 | requirements | requirements-dev.txt |
| mypy | >=1.0.0 | project.optional-dependencies.dev | sdk/python/clx/pyproject.toml |
| mypy | >=1.0.0 | project.optional-dependencies.dev | sdk/python/pyproject.toml |
| neo4j | >=5.22.0 | requirements | airflow/requirements.txt |
| neo4j | unspecified | project.dependencies | services/api/pyproject.toml |
| neo4j | unspecified | requirements | services/api/requirements.txt |
| neurokit2 | >=0.2.10 | requirements | ocean_core/requirements-internal-eeg.txt |
| numpy | >=1.26.0 | requirements | 9999/requirements.txt |
| numpy | >=1.26.4 | requirements | apps/api/requirements.txt |
| numpy | >=1.26.0 | requirements | ocean_core/requirements.txt |
| numpy | >=2.0.0 | project.optional-dependencies.data | pyproject.toml |
| numpy | >=2.0.0 | requirements | requirements-autolearning.txt |
| numpy | >=2.2.0 | requirements | requirements.txt |
| numpy | >=2.0.0 | requirements | services/content-factory/requirements.txt |
| numpy | >=2.0.0 | requirements | services/intelligence-lab/requirements.txt |
| onnxruntime-gpu | >=1.20.0 | requirements | ocean_core/requirements-internal-llm.txt |
| opencv-python | >=4.10.0 | requirements | ocean_core/requirements-internal-multimodal.txt |
| openpyxl | >=3.1.5 | requirements | apps/api/requirements-excel.txt |
| openpyxl | >=3.1.5 | requirements | excel-core/requirements.txt |
| openpyxl | >=3.1.0 | requirements | hybrid_saas_platform/requirements.txt |
| openpyxl | >=3.1.5 | requirements | ocean_core/requirements.txt |
| openpyxl | >=3.1.5 | project.optional-dependencies.excel | pyproject.toml |
| openpyxl | >=3.1.0 | requirements | services/excel/requirements.txt |
| openpyxl | >=3.1.0 | requirements | services/intelligence-lab/requirements.txt |
| openpyxl | >=3.1.0 | requirements | services/reporting/requirements.txt |
| opentelemetry-api | >=1.29.0 | project.optional-dependencies.observability | pyproject.toml |
| opentelemetry-api | >=1.30.0 | requirements | requirements.txt |
| opentelemetry-exporter-otlp | >=1.29.0 | project.optional-dependencies.observability | pyproject.toml |
| opentelemetry-exporter-otlp | >=1.30.0 | requirements | requirements.txt |
| opentelemetry-exporter-otlp-proto-http | >=1.30.0 | requirements | requirements.txt |
| opentelemetry-instrumentation-aiohttp-client | >=0.51b0 | requirements | requirements.txt |
| opentelemetry-instrumentation-fastapi | >=0.50b0 | project.optional-dependencies.observability | pyproject.toml |
| opentelemetry-instrumentation-fastapi | >=0.51b0 | requirements | requirements.txt |
| opentelemetry-instrumentation-httpx | >=0.51b0 | requirements | requirements.txt |
| opentelemetry-instrumentation-logging | >=0.51b0 | requirements | requirements.txt |
| opentelemetry-instrumentation-redis | >=0.50b0 | project.optional-dependencies.observability | pyproject.toml |
| opentelemetry-instrumentation-requests | >=0.51b0 | requirements | requirements.txt |
| opentelemetry-instrumentation-sqlalchemy | >=0.50b0 | project.optional-dependencies.observability | pyproject.toml |
| opentelemetry-sdk | >=1.29.0 | project.optional-dependencies.observability | pyproject.toml |
| opentelemetry-sdk | >=1.30.0 | requirements | requirements.txt |
| orjson | >=3.10.0 | requirements | ocean_core/requirements-internal-core.txt |
| orjson | >=3.9.0 | requirements | ocean_core/requirements.txt |
| orjson | >=3.10.0 | project.optional-dependencies.ocean | pyproject.toml |
| orjson | >=3.10.0 | requirements | requirements-ocean.txt |
| orjson | >=3.10.14 | requirements | requirements.txt |
| pandas | >=2.2.0 | requirements | apps/api/requirements.txt |
| pandas | >=2.2.0 | project.optional-dependencies.data | pyproject.toml |
| pandas | >=2.2.3 | requirements | requirements.txt |
| pandas | >=2.2.0 | requirements | services/content-factory/requirements.txt |
| pandas | >=2.0.0 | requirements | services/excel/requirements.txt |
| pandas | >=2.0.0 | requirements | services/intelligence-lab/requirements.txt |
| passlib | [bcrypt]>=1.7.4 | project.optional-dependencies.api | pyproject.toml |
| paypalrestsdk | >=1.7.1 | requirements | apps/api/requirements.txt |
| paypalrestsdk | >=1.7.1 | project.optional-dependencies.payments | pyproject.toml |
| peft | >=0.13.0 | requirements | ocean_core/requirements-internal-llm.txt |
| pillow | >=10.0.0 | requirements | 9999/requirements.txt |
| pip-audit | >=2.7.0 | project.optional-dependencies.dev | pyproject.toml |
| pre-commit | >=3.6.0 | requirements | requirements-dev.txt |
| prometheus-client | >=0.21.1 | requirements | apps/api/requirements.txt |
| prometheus-client | >=0.21.0 | requirements | ocean_core/requirements-internal-core.txt |
| prometheus-client | >=0.18.0 | requirements | ocean_core/requirements.txt |
| prometheus-client | >=0.20 | requirements | packages/wwwmmm-ndb-stigma-pc/requirements-min.txt |
| prometheus-client | >=0.21.1 | project.optional-dependencies.api | pyproject.toml |
| prometheus-client | >=0.21.1 | requirements | requirements-autolearning.txt |
| prometheus-client | >=0.21.0 | requirements | requirements-ocean.txt |
| psutil | >=6.0.0 | requirements | apps/api/requirements-slim.txt |
| psutil | >=6.0.0 | requirements | apps/api/requirements.txt |
| psutil | >=5.9.0 | requirements | excel-core/requirements.txt |
| psutil | >=6.1.0 | project.optional-dependencies.api | pyproject.toml |
| psutil | >=6.1.0 | requirements | requirements.txt |
| psutil | >=6.1.0 | requirements | services/core/requirements.txt |
| psutil | >=6.1.0 | requirements | services/intelligence-lab/requirements.txt |
| psutil | >=6.1.0 | requirements | services/reporting/requirements.txt |
| psycopg | >=3.2.0 | requirements | apps/api/requirements-slim.txt |
| psycopg2-binary | >=2.9.9 | requirements | airflow/requirements.txt |
| psycopg2-binary | unspecified | project.dependencies | services/api/pyproject.toml |
| psycopg2-binary | unspecified | requirements | services/api/requirements.txt |
| pyOpenSSL | >=26.0.0 | requirements | requirements.txt |
| pydantic | >=2.5.0 | requirements | 9999/requirements.txt |
| pydantic | >=2.10.4 | requirements | apps/api/requirements-slim.txt |
| pydantic | >=2.10.4 | requirements | apps/api/requirements.txt |
| pydantic | >=2.0.0 | requirements | hybrid_saas_platform/requirements.txt |
| pydantic | >=2.10.0 | requirements | ocean_core/requirements-internal-core.txt |
| pydantic | >=2.9.0 | requirements | ocean_core/requirements-lite.txt |
| pydantic | >=2.5.0 | requirements | ocean_core/requirements.txt |
| pydantic | >=2.10.4 | requirements | orchestra/requirements.txt |
| pydantic | >=2.8 | requirements | packages/wwwmmm-ndb-stigma-pc/requirements-min.txt |
| pydantic | >=2.10.4 | project.dependencies | pyproject.toml |
| pydantic | >=2.10.0 | requirements | requirements-ocean.txt |
| pydantic | >=2.10.4 | requirements | requirements.txt |
| pydantic | ==2.10.3 | requirements | services/ads_core/requirements.txt |
| pydantic | >=2.6.0 | requirements | services/agent-telemetry/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/agiem/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/ai-global-9999/requirements.txt |
| pydantic | >=2.8 | project.dependencies | services/api/pyproject.toml |
| pydantic | >=2.8 | requirements | services/api/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/aviation-weather/requirements.txt |
| pydantic | ==2.10.3 | requirements | services/billing_core/requirements.txt |
| pydantic | >=2.5.0 | requirements | services/blerina/requirements.txt |
| pydantic | ==2.5.0 | requirements | services/blog_api/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/blog_publisher/requirements.txt |
| pydantic | >=2.0.0 | requirements | services/clx_brain/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/content-factory/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/cycle-engine/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/dr_albana/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/intelligence-lab/requirements.txt |
| pydantic | >=2.9,<3.0 | requirements | services/kloud_bridge/requirements.txt |
| pydantic | >=2.9,<3.0 | requirements | services/kloud_upstream_runtime/requirements.txt |
| pydantic | >=2.5.0,<3.0.0 | requirements | services/lagter/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/user-management/requirements.txt |
| pydantic | >=2.10.0 | requirements | services/video-generator/requirements.txt |
| pydantic-extra-types | >=2.10.0 | requirements | apps/api/requirements.txt |
| pydantic-extra-types | >=2.10.1 | requirements | requirements.txt |
| pydantic-settings | >=2.7.0 | requirements | apps/api/requirements.txt |
| pydantic-settings | >=2.7.0 | requirements | orchestra/requirements.txt |
| pydantic-settings | >=2.7.0 | project.dependencies | pyproject.toml |
| pydantic-settings | >=2.7.0 | requirements | requirements.txt |
| pydub | >=0.25.1 | requirements | ocean_core/requirements-internal-multimodal.txt |
| pydub | >=0.25.1 | requirements | requirements.txt |
| pyedflib | >=0.1.39 | requirements | ocean_core/requirements-internal-eeg.txt |
| pymilvus | >=2.4.0 | requirements | ocean_core/requirements-internal-llm.txt |
| pypdf | >=4.2.0 | requirements | ocean_core/requirements-internal-core.txt |
| pypdf | >=4.2.0 | requirements | ocean_core/requirements.txt |
| pyriemann | >=0.7 | requirements | ocean_core/requirements-internal-eeg.txt |
| pytest | >=8.3.0 | project.optional-dependencies.dev | pyproject.toml |
| pytest | >=8.0.0 | requirements | requirements-dev.txt |
| pytest | >=8.3.0 | requirements | requirements-dev.txt |
| pytest | >=8.3.0 | requirements | requirements-test.txt |
| pytest | >=7.0.0 | project.optional-dependencies.dev | sdk/python/clx/pyproject.toml |
| pytest | >=7.0.0 | project.optional-dependencies.dev | sdk/python/pyproject.toml |
| pytest | unspecified | project.optional-dependencies.dev | services/api/pyproject.toml |
| pytest-asyncio | >=0.24.0 | project.optional-dependencies.dev | pyproject.toml |
| pytest-asyncio | >=0.23.0 | requirements | requirements-dev.txt |
| pytest-asyncio | >=0.24.0 | requirements | requirements-test.txt |
| pytest-asyncio | >=0.20.0 | project.optional-dependencies.dev | sdk/python/clx/pyproject.toml |
| pytest-asyncio | >=0.20.0 | project.optional-dependencies.dev | sdk/python/pyproject.toml |
| pytest-cov | >=6.0.0 | project.optional-dependencies.dev | pyproject.toml |
| pytest-cov | >=4.1.0 | requirements | requirements-dev.txt |
| python-dateutil | >=2.8.0 | requirements | hybrid_saas_platform/requirements.txt |
| python-docx | >=1.2.0 | requirements | apps/api/requirements-excel.txt |
| python-docx | >=1.1.2 | requirements | ocean_core/requirements.txt |
| python-docx | >=1.1.2 | requirements | services/reporting/requirements.txt |
| python-dotenv | >=1.0.0 | requirements | 9999/requirements.txt |
| python-dotenv | >=1.0.1 | requirements | apps/api/requirements-slim.txt |
| python-dotenv | >=1.0.1 | requirements | apps/api/requirements.txt |
| python-dotenv | >=1.0.1 | requirements | ocean_core/requirements-internal-core.txt |
| python-dotenv | >=1.0.0 | requirements | ocean_core/requirements.txt |
| python-dotenv | >=1.0.1 | project.dependencies | pyproject.toml |
| python-dotenv | >=1.0.1 | requirements | requirements-ocean.txt |
| python-dotenv | ==1.0.1 | requirements | services/ads_core/requirements.txt |
| python-dotenv | >=1.0.0 | requirements | services/ai-global-9999/requirements.txt |
| python-dotenv | >=1.0.0 | requirements | services/aviation-weather/requirements.txt |
| python-dotenv | ==1.0.1 | requirements | services/billing_core/requirements.txt |
| python-dotenv | >=1.0.1 | requirements | services/blog_publisher/requirements.txt |
| python-dotenv | >=1.0.0 | requirements | services/clx_brain/requirements.txt |
| python-dotenv | >=1.0.1 | requirements | services/dr_albana/requirements.txt |
| python-dotenv | >=1.0.0,<2.0.0 | requirements | services/lagter/requirements.txt |
| python-dotenv | >=1.0.0 | requirements | services/newsroom/requirements.txt |
| python-multipart | >=0.0.22 | requirements | apps/api/requirements-slim.txt |
| python-multipart | >=0.0.22 | requirements | apps/api/requirements.txt |
| python-multipart | >=0.0.9 | requirements | ocean_core/requirements-internal-core.txt |
| python-multipart | >=0.0.9 | requirements | ocean_core/requirements.txt |
| python-multipart | >=0.0.22 | project.dependencies | pyproject.toml |
| python-multipart | >=0.0.6 | requirements | services/blerina/requirements.txt |
| python-multipart | >=0.0.22 | requirements | services/blog_api/requirements.txt |
| python-multipart | >=0.0.9 | requirements | services/content-factory/requirements.txt |
| python-multipart | >=0.0.22 | requirements | services/excel/requirements.txt |
| python-multipart | >=0.0.9 | requirements | services/user-management/requirements.txt |
| python-pptx | >=1.0.2 | requirements | apps/api/requirements-excel.txt |
| python-pptx | >=1.0.2 | project.optional-dependencies.excel | pyproject.toml |
| python-pptx | >=0.6.21 | requirements | services/reporting/requirements.txt |
| pyyaml | >=6.0.0 | requirements | ocean_core/requirements-internal-core.txt |
| pyyaml | >=6.0.0 | requirements | ocean_core/requirements.txt |
| redis | >=5.2.0 | requirements | apps/api/requirements.txt |
| redis | >=5.2.0 | requirements | ocean_core/requirements-internal-core.txt |
| redis | >=5.0.0 | requirements | ocean_core/requirements.txt |
| redis | [hiredis]>=5.2.0 | project.optional-dependencies.api | pyproject.toml |
| redis | >=5.2.0 | requirements | requirements-ocean.txt |
| redis | >=5.2.1 | requirements | requirements.txt |
| redis | >=4.5.0 | requirements | services/clx_brain/requirements.txt |
| redis | >=5.0.0 | requirements | services/redis_core/requirements.txt |
| redis | >=5.0.0 | requirements | services/reporting/requirements.txt |
| reportlab | >=4.4.0 | requirements | apps/api/requirements-excel.txt |
| reportlab | >=4.2.5 | requirements | requirements.txt |
| reportlab | >=4.2.2 | requirements | services/reporting/requirements.txt |
| requests | >=2.32.0 | requirements | airflow/requirements.txt |
| requests | >=2.32.3 | requirements | apps/api/requirements-slim.txt |
| requests | >=2.32.3 | requirements | apps/api/requirements.txt |
| requests | >=2.31.0 | requirements | ocean_core/requirements-internal-core.txt |
| requests | >=2.31.0 | requirements | ocean_core/requirements.txt |
| requests | >=2.32.3 | requirements | requirements-autolearning.txt |
| requests | unspecified | requirements | requirements-dev.txt |
| requests | >=2.32.3 | requirements | requirements-dev.txt |
| requests | >=2.32.3 | requirements | requirements-test.txt |
| requests | >=2.32.3 | requirements | requirements.txt |
| ruff | >=0.8.0 | requirements | requirements-dev.txt |
| ruff | >=0.1.0 | project.optional-dependencies.dev | sdk/python/clx/pyproject.toml |
| ruff | >=0.1.0 | project.optional-dependencies.dev | sdk/python/pyproject.toml |
| ruff | unspecified | project.optional-dependencies.dev | services/api/pyproject.toml |
| safety | >=3.0.0 | requirements | requirements-dev.txt |
| scikit-learn | >=1.6.0 | project.optional-dependencies.ml | pyproject.toml |
| scipy | >=1.14.0 | project.optional-dependencies.ml | pyproject.toml |
| sentry-sdk | [fastapi]>=2.19.0 | project.optional-dependencies.observability | pyproject.toml |
| soundfile | >=0.13.0 | requirements | requirements.txt |
| sqlalchemy | >=2.0.36 | requirements | apps/api/requirements-slim.txt |
| sqlalchemy | [asyncio]>=2.0.36 | project.optional-dependencies.api | pyproject.toml |
| sqlalchemy | >=2.0.36 | requirements | requirements.txt |
| sqlalchemy | >=2.0 | project.dependencies | services/api/pyproject.toml |
| sqlalchemy | >=2.0 | requirements | services/api/requirements.txt |
| sqlalchemy | ==2.0.23 | requirements | services/blog_api/requirements.txt |
| starlette | >=0.47.2 | requirements | services/blog_api/requirements.txt |
| stripe | >=12.0.0 | requirements | apps/api/requirements.txt |
| stripe | >=12.0.0 | project.optional-dependencies.payments | pyproject.toml |
| stripe | >=10.0.0 | requirements | requirements.txt |
| stripe | >=12.1.0 | requirements | requirements.txt |
| stripe | ==11.3.0 | requirements | services/billing_core/requirements.txt |
| stripe | ==7.4.0 | requirements | services/blog_api/requirements.txt |
| structlog | >=24.4.0 | requirements | ocean_core/requirements-internal-core.txt |
| structlog | >=23.2.0 | requirements | ocean_core/requirements.txt |
| structlog | >=24.4.0 | project.dependencies | pyproject.toml |
| structlog | >=24.4.0 | requirements | requirements-ocean.txt |
| tenacity | >=9.0.0 | requirements | apps/api/requirements-slim.txt |
| tenacity | >=9.0.0 | requirements | apps/api/requirements.txt |
| tenacity | >=9.0.0 | project.optional-dependencies.api | pyproject.toml |
| torch | >=2.0.0 | requirements | ocean_core/ocean_ai_processes/requirements.txt |
| torch | >=2.4.0 | requirements | ocean_core/requirements-internal-llm.txt |
| transformers | >=4.45.0 | requirements | ocean_core/requirements-internal-llm.txt |
| trl | >=0.11.0 | requirements | ocean_core/requirements-internal-llm.txt |
| tweepy | >=4.14.0 | requirements | services/content-factory/requirements.txt |
| types-all | >=1.0.0 | requirements | requirements-dev.txt |
| typing_extensions | >=4.10.0 | requirements | orchestra/requirements.txt |
| uvicorn | >=0.24.0 | requirements | 9999/requirements.txt |
| uvicorn | >=0.32.1 | requirements | apps/api/requirements-slim.txt |
| uvicorn | >=0.24.0 | requirements | excel-core/requirements.txt |
| uvicorn | >=0.30.0 | requirements | ocean_core/requirements-internal-core.txt |
| uvicorn | >=0.32.0 | requirements | ocean_core/requirements-lite.txt |
| uvicorn | >=0.24.0 | requirements | ocean_core/requirements.txt |
| uvicorn | >=0.30 | requirements | packages/wwwmmm-ndb-stigma-pc/requirements-min.txt |
| uvicorn | [standard]>=0.32.1 | project.dependencies | pyproject.toml |
| uvicorn | >=0.30.0 | requirements | requirements-ocean.txt |
| uvicorn | >=0.32.1 | requirements | requirements-test.txt |
| uvicorn | >=0.34.0 | requirements | requirements.txt |
| uvicorn | >=0.27.0 | requirements | services/agent-telemetry/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/agiem/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/ai-global-9999/requirements.txt |
| uvicorn | [standard] | project.dependencies | services/api/pyproject.toml |
| uvicorn | >=0.32.1 | requirements | services/blog_publisher/requirements.txt |
| uvicorn | >=0.23.0 | requirements | services/clx_brain/requirements.txt |
| uvicorn | [standard] | project.dependencies | services/concept_gap/pyproject.toml |
| uvicorn | >=0.32.1 | requirements | services/content-factory/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/core/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/cycle-engine/requirements.txt |
| uvicorn | >=0.22.0 | requirements | services/excel/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/intelligence-lab/requirements.txt |
| uvicorn | ==0.35.0 | requirements | services/kitchen-api/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/lab/requirements.txt |
| uvicorn | >=0.27.0,<0.35.0 | requirements | services/lagter/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/reporting/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/user-management/requirements.txt |
| uvicorn | >=0.32.1 | requirements | services/video-generator/requirements.txt |
| uvloop | >=0.20.0 | requirements | requirements-ocean.txt |
| vllm | >=0.6.0 | requirements | ocean_core/requirements-internal-llm.txt |
| weaviate-client | >=4.6.4 | requirements | airflow/requirements.txt |
| weaviate-client | >=4.6.4 | project.dependencies | services/api/pyproject.toml |
| weaviate-client | >=4.6.4 | requirements | services/api/requirements.txt |
| weaviate-client | unspecified | project.dependencies | services/concept_gap/pyproject.toml |
| xformers | >=0.0.28 | requirements | ocean_core/requirements-internal-llm.txt |
| xlrd | >=2.0.1 | requirements | ocean_core/requirements.txt |
| xlwings | >=0.30.0 | requirements | hybrid_saas_platform/requirements.txt |

## Cargo/Carter Snapshot
| name | version | section | file |
| --- | --- | --- | --- |
| aes-gcm | 0.9 | dependencies | nanogrid/node/Cargo.toml |
| algebra | unspecified | dependencies | nanogrid/node/Cargo.toml |
| algebra | unspecified | dependencies | nanogrid/protocol/Cargo.toml |
| axum | 0.7 | dependencies | nanogrid/node/Cargo.toml |
| axum | 0.8 | dependencies | services/quantum-rust/Cargo.toml |
| base64 | 0.21 | dependencies | nanogrid/node/Cargo.toml |
| clap | 4.5 | dependencies | scripts/hardware/rust_node_agent/Cargo.toml |
| criterion | 0.5 | dev-dependencies | sdk/rust/Cargo.toml |
| ed25519-dalek | 2 | dependencies | nanogrid/security/Cargo.toml |
| futures-util | 0.3 | dependencies | nanogrid/protocol/Cargo.toml |
| lru | 0.12 | dependencies | nanogrid/protocol/Cargo.toml |
| protocol | unspecified | dependencies | nanogrid/node/Cargo.toml |
| quinn | 0.10 | dependencies | nanogrid/protocol/Cargo.toml |
| rand | 0.8 | dependencies | nanogrid/node/Cargo.toml |
| rand | 0.8 | dependencies | nanogrid/security/Cargo.toml |
| rcgen | 0.11 | dependencies | nanogrid/protocol/Cargo.toml |
| reqwest | 0.12 | dependencies | scripts/hardware/rust_node_agent/Cargo.toml |
| reqwest | 0.12 | dependencies | services/quantum-rust/Cargo.toml |
| rmp-serde | 1.1 | dependencies | nanogrid/protocol/Cargo.toml |
| rustls | 0.21 | dependencies | nanogrid/protocol/Cargo.toml |
| security | unspecified | dependencies | nanogrid/node/Cargo.toml |
| security | unspecified | dependencies | nanogrid/protocol/Cargo.toml |
| serde | 1.0 | dependencies | nanogrid/algebra/Cargo.toml |
| serde | 1.0 | dependencies | nanogrid/node/Cargo.toml |
| serde | 1.0 | dependencies | nanogrid/protocol/Cargo.toml |
| serde | 1.0 | dependencies | nanogrid/security/Cargo.toml |
| serde | 1 | dependencies | scripts/hardware/rust_node_agent/Cargo.toml |
| serde | 1 | dependencies | services/quantum-rust/Cargo.toml |
| serde_cbor | 0.11 | dependencies | nanogrid/protocol/Cargo.toml |
| serde_json | 1.0 | dependencies | nanogrid/node/Cargo.toml |
| serde_json | 1 | dependencies | scripts/hardware/rust_node_agent/Cargo.toml |
| serde_json | 1 | dependencies | services/quantum-rust/Cargo.toml |
| sha3 | 0.10 | dependencies | nanogrid/node/Cargo.toml |
| sha3 | 0.10 | dependencies | nanogrid/protocol/Cargo.toml |
| sha3 | 0.10 | dependencies | nanogrid/security/Cargo.toml |
| tokio | 1 | dependencies | nanogrid/node/Cargo.toml |
| tokio | 1 | dependencies | nanogrid/protocol/Cargo.toml |
| tokio | 1 | dependencies | services/quantum-rust/Cargo.toml |
| tokio-util | 0.7 | dependencies | nanogrid/protocol/Cargo.toml |
| x25519-dalek | 2 | dependencies | nanogrid/security/Cargo.toml |

## Notes
- This report is intentionally package-only for public integration visibility.
- No secret/key scanning is included in this workflow.
- API/protocol sections are auto-extracted via recursive scan from source files.
