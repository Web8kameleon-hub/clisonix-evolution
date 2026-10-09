FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ffmpeg && rm -rf /var/lib/apt/lists/*

# Kopjo TË GJITHA modulet e nevojshme për Ocean Core Full
COPY ocean_core_full.py ocean_nanogrid.py prompts.py identity_loader.py ./
COPY mega_layer_engine.py real_answer_engine.py service_registry.py ./
COPY knowledge_layer.py albanian_dictionary.py laboratories.py ./
COPY translation_node.py cell_registry.py external_apis.py ./
COPY autolearning_engine.py layer_algebra_integration.py knowledge_router.py ./
COPY module_core_registry.py chat_latency_policy.py ./
COPY xlc_security_runtime.py ./
COPY alphabet_layers.py ./
COPY xlc/ ./xlc/
COPY requirements.txt requirements-lite.txt ./
COPY documents/ ./documents/
COPY knowledge_seeds/ ./knowledge_seeds/
COPY curiosity_algebra/ ./curiosity_algebra/

# Krijo folder për config (do të montohet si volume)
RUN mkdir -p /app/config

# Përdor requirements.txt të plotë (jo lite)
RUN pip install --no-cache-dir -r requirements.txt

ENV OCEAN_PORT=8030
EXPOSE 8030

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8030/health || exit 1

# Përdor ocean_core_full.py me TË GJITHA LAYERS
CMD ["python", "ocean_core_full.py"]
