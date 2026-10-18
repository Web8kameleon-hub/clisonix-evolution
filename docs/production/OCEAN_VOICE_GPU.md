# Ocean voice conversation

## Ligjet e detyrueshme të zërit — gemma-only-v1

1. Modeli i vetëm i lejuar për përgjigjet e bisedës me zë është `huihui_ai/gemma-4-abliterated:12b`. Llama, Qwen dhe çdo model tjetër ndalohen në këtë rrugë.
2. Klienti nuk mund të zgjedhë model tjetër. Një override i ndryshëm nga konfigurimi i serverit ndalon shërbimin me gabim; nuk ndryshon modelin.
3. Gemma duhet të raportohet plotësisht në GPU. CPU dhe GPU e pjesshme refuzohen me HTTP 503; nuk ka fallback.
4. Konteksti është 4096, përgjigjja maksimumi 192 tokenë, `think=false`, `num_gpu=999`. Parametrat e klientit nuk i ndryshojnë këto kufij.
5. Çdo rekord nga modeli duhet të identifikojë Gemma-n e aprovuar. Rekordet nga modele të tjera refuzohen para se teksti të dërgohet për shqiptim.
6. Në mungesë kapaciteti, kërkesa pret brenda timeout-it ose dështon qartë. Nuk vret kërkesat aktive të moduleve të tjera dhe nuk kalon te model tjetër.
7. Këto rregulla i nënshtrohen testeve të regresionit: `node scripts/verify-ocean-voice-route.mjs`.

Kjo politikë përcakton modelin e bisedës; transkriptimi vazhdon me Whisper dhe shqiptimi me shërbimin ekzistues TTS. Ollama aktualisht ndan GPU-në me module të tjera: politika nuk rezervon VRAM dhe nuk garanton disponueshmëri kur ato e zënë GPU-në.

Open `/modules/curiosity-ocean/voice`, sign in, choose Albanian, German or English, and press **Fillo bisedën**. Allow microphone access. Speak normally; a 650 ms pause submits the turn. Speaking again interrupts playback and generation. **Ndalo bisedën** releases the microphone. Headphones reduce echo. Each recording is limited to 30 seconds.

The voice page uses the private GPU Whisper `large-v3-turbo` service for transcription and the installed Gemma 4 12B model for conversation. The chat route requires GPU residency and disables thinking for speech latency. Conversation history accompanies later turns. Neural speech is prepared sentence by sentence while the model continues generating. Transcription accuracy and interruption sensitivity still depend on language, microphone and ambient noise; validate with real speakers, especially Albanian.

Microphone audio is processed on the production server; response text is sent to the Microsoft neural speech service. Voice endpoints require a signed-in session. Ollama publishes no host port, the multi-model API binds only to `127.0.0.1:4444`, and the speech service publishes no host port. Audio files are temporary and removed after transcription. These changes cover the voice path, not a full audit of every platform service.

The deployment lives under `/opt/clisonix-releases/20261011-natural-voice-v1`. Its `.runtime/rollback.json` preserves the previous web container configuration. Keep these runtime snapshots private because they contain environment settings.

To start the existing private services and warm the voice model on the production host:

```bash
cd /opt/clisonix.com
bash scripts/hetzner/start_private_voice.sh
```

The script requires working NVIDIA drivers and the already-built voice image. It preserves `clisonix_ollama_data` and does not remove containers or volumes. Apply `compose.ollama-private.yml` last when operating the full Compose stack. Build the speech service with `docker compose -p clisonixcom -f compose.voice-gpu.yml build voice-stt` if needed.
