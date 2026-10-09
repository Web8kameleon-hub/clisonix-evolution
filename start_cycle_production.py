#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 COMPLETE CYCLE PRODUCTION STARTER
Inicion dhe nis prodhimin e cycles të reja për të gjithë sistemin Clisonix Cloud

Përfshin:
- ALBA: EEG nga burime të hapura falas
- ALBI: Inteligjencë dhe analytics (më shumë se 20 min)
- JONA: Mbikëqyrje etike dhe koordinim (më shumë se 20 min)
- ASI: Inteligjencë e avancuar (më shumë se 20 min)
- AGIEM: Menaxhim ekosistemi AGI (më shumë se 20 min)
- LABORATORË: Të dhëna nga shumë laboratorë kërkimorë (më shumë se 20 min)
"""

import asyncio
import json
from cycle_engine import CycleEngine, CycleType

async def start_complete_cycle_production():
    """Nis prodhimin e cycles të reja për të gjithë sistemin"""

    print("🔁 Inicializimi i Cycle Engine për sistemin e plotë...")
    engine = CycleEngine()

    print("📋 Krijimi i cycles të prodhimit për të gjithë modulet...")

    # ==================== ALBA MODULE ====================
    print("\n🧠 ALBA - EEG nga burime të hapura falas:")

    # ALBA: EEG nga Open Source Links (çdo 30 min)
    cycle_alba_eeg_open = engine.create_cycle(
        domain="neuro",
        source="open_eeg_sources",  # EEG nga burime të hapura
        agent="ALBA",
        task="eeg_collection",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="strict"
    )
    print(f"✅ Krijuar: {cycle_alba_eeg_open.cycle_id} - ALBA EEG Open Sources (çdo 30min)")

    # ALBA: Signal Processing (çdo 45 min)
    cycle_alba_processing = engine.create_cycle(
        domain="neuro",
        source="alba.signals",
        agent="ALBA",
        task="signal_processing",
        cycle_type=CycleType.INTERVAL,
        interval=2700.0,  # 45 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_alba_processing.cycle_id} - ALBA Signal Processing (çdo 45min)")

    # ==================== ALBI MODULE ====================
    print("\n🧠 ALBI - Inteligjencë dhe Analytics:")

    # ALBI: Pattern Learning (çdo 25 min)
    cycle_albi_learning = engine.create_cycle(
        domain="intelligence",
        source="albi.patterns",
        agent="ALBI",
        task="pattern_learning",
        cycle_type=CycleType.INTERVAL,
        interval=1500.0,  # 25 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_albi_learning.cycle_id} - ALBI Pattern Learning (çdo 25min)")

    # ALBI: Anomaly Detection (çdo 35 min)
    cycle_albi_anomalies = engine.create_cycle(
        domain="analytics",
        source="albi.anomalies",
        agent="ALBI",
        task="anomaly_detection",
        cycle_type=CycleType.INTERVAL,
        interval=2100.0,  # 35 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_albi_anomalies.cycle_id} - ALBI Anomaly Detection (çdo 35min)")

    # ALBI: Knowledge Synthesis (çdo 40 min)
    cycle_albi_synthesis = engine.create_cycle(
        domain="intelligence",
        source="albi.knowledge",
        agent="ALBI",
        task="knowledge_synthesis",
        cycle_type=CycleType.INTERVAL,
        interval=2400.0,  # 40 minuta
        alignment="strict"
    )
    print(f"✅ Krijuar: {cycle_albi_synthesis.cycle_id} - ALBI Knowledge Synthesis (çdo 40min)")

    # ==================== JONA MODULE ====================
    print("\n⚖️ JONA - Mbikëqyrje Etike dhe Koordinim:")

    # JONA: Ethical Oversight (çdo 30 min)
    cycle_jona_ethics = engine.create_cycle(
        domain="ethics",
        source="jona.oversight",
        agent="JONA",
        task="ethical_review",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="ethical_guard"
    )
    print(f"✅ Krijuar: {cycle_jona_ethics.cycle_id} - JONA Ethical Oversight (çdo 30min)")

    # JONA: Alignment Monitoring (çdo 25 min)
    cycle_jona_alignment = engine.create_cycle(
        domain="alignment",
        source="jona.monitoring",
        agent="JONA",
        task="alignment_check",
        cycle_type=CycleType.INTERVAL,
        interval=1500.0,  # 25 minuta
        alignment="ethical_guard"
    )
    print(f"✅ Krijuar: {cycle_jona_alignment.cycle_id} - JONA Alignment Monitoring (çdo 25min)")

    # JONA: Neural Audio Generation (çdo 45 min)
    cycle_jona_audio = engine.create_cycle(
        domain="neural_audio",
        source="jona.audio",
        agent="JONA",
        task="audio_generation",
        cycle_type=CycleType.INTERVAL,
        interval=2700.0,  # 45 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_jona_audio.cycle_id} - JONA Neural Audio (çdo 45min)")

    # ==================== ASI MODULE ====================
    print("\n🚀 ASI - Inteligjencë e Avancuar:")

    # ASI: Advanced Reasoning (çdo 35 min)
    cycle_asi_reasoning = engine.create_cycle(
        domain="advanced_ai",
        source="asi.reasoning",
        agent="ASI",
        task="advanced_reasoning",
        cycle_type=CycleType.INTERVAL,
        interval=2100.0,  # 35 minuta
        alignment="strict"
    )
    print(f"✅ Krijuar: {cycle_asi_reasoning.cycle_id} - ASI Advanced Reasoning (çdo 35min)")

    # ASI: Real-time Engine (çdo 40 min)
    cycle_asi_realtime = engine.create_cycle(
        domain="realtime_ai",
        source="asi.realtime",
        agent="ASI",
        task="realtime_processing",
        cycle_type=CycleType.INTERVAL,
        interval=2400.0,  # 40 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_asi_realtime.cycle_id} - ASI Real-time Engine (çdo 40min)")

    # ==================== AGIEM MODULE ====================
    print("\n🌐 AGIEM - Menaxhim Ekosistemi AGI:")

    # AGIEM: Ecosystem Management (çdo 30 min)
    cycle_agiem_ecosystem = engine.create_cycle(
        domain="agi_ecosystem",
        source="agiem.management",
        agent="AGIEM",
        task="ecosystem_management",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="strict"
    )
    print(f"✅ Krijuar: {cycle_agiem_ecosystem.cycle_id} - AGIEM Ecosystem Management (çdo 30min)")

    # AGIEM: Agent Coordination (çdo 35 min)
    cycle_agiem_coordination = engine.create_cycle(
        domain="agent_coordination",
        source="agiem.agents",
        agent="AGIEM",
        task="agent_coordination",
        cycle_type=CycleType.INTERVAL,
        interval=2100.0,  # 35 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_agiem_coordination.cycle_id} - AGIEM Agent Coordination (çdo 35min)")

    # ==================== LABORATORY MODULES ====================
    print("\n🔬 LABORATORË - Të dhëna nga shumë laboratorë kërkimorë:")

    # Laboratory: PubMed Research (çdo 60 min)
    cycle_lab_pubmed = engine.create_cycle(
        domain="laboratory",
        source="pubmed.api",
        agent="RESEARCH",
        task="pubmed_ingest",
        cycle_type=CycleType.INTERVAL,
        interval=3600.0,  # 60 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_lab_pubmed.cycle_id} - Lab PubMed Research (çdo 60min)")

    # Laboratory: ArXiv Papers (çdo 45 min)
    cycle_lab_arxiv = engine.create_cycle(
        domain="laboratory",
        source="arxiv.api",
        agent="RESEARCH",
        task="arxiv_ingest",
        cycle_type=CycleType.INTERVAL,
        interval=2700.0,  # 45 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_lab_arxiv.cycle_id} - Lab ArXiv Papers (çdo 45min)")

    # Laboratory: CrossRef Citations (çdo 50 min)
    cycle_lab_crossref = engine.create_cycle(
        domain="laboratory",
        source="crossref.api",
        agent="RESEARCH",
        task="crossref_ingest",
        cycle_type=CycleType.INTERVAL,
        interval=3000.0,  # 50 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_lab_crossref.cycle_id} - Lab CrossRef Citations (çdo 50min)")

    # Laboratory: Open Data Portals (çdo 40 min)
    cycle_lab_open_data = engine.create_cycle(
        domain="laboratory",
        source="open_data_portals",
        agent="RESEARCH",
        task="open_data_ingest",
        cycle_type=CycleType.INTERVAL,
        interval=2400.0,  # 40 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_lab_open_data.cycle_id} - Lab Open Data Portals (çdo 40min)")

    # Laboratory: Environmental Data (çdo 30 min)
    cycle_lab_environment = engine.create_cycle(
        domain="laboratory",
        source="environmental_data",
        agent="RESEARCH",
        task="environment_monitoring",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_lab_environment.cycle_id} - Lab Environmental Data (çdo 30min)")

    # SCALABILITY: Open Data Discovery & Integration (çdo 2 orë)
    cycle_scalability_engine = engine.create_cycle(
        domain="scalability",
        source="global_open_data",
        agent="SCALABILITY_ENGINE",
        task="discover_and_integrate",
        cycle_type=CycleType.INTERVAL,
        interval=7200.0,  # 2 orë
        alignment="ethical_guard"
    )
    print(f"✅ Krijuar: {cycle_scalability_engine.cycle_id} - Scalability Engine (çdo 2 orë)")

    # ==================== SPECIFIC CITY LABORATORIES ====================
    print("\n🏛️ LABORATORË SPECIFIKE NGA QYTETE - Elbasan, Tirana, Durrës, Vlorë, Shkodër, Korçë, Sarandë, Prishtina, Kostur, Athina, Roma, Zyrih:")

    # Albania Laboratories
    cycle_lab_elbasan = engine.create_cycle(
        domain="laboratory",
        source="elbasan.university.lab",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Elbasan",
        country="Albania"
    )
    print(f"✅ Krijuar: {cycle_lab_elbasan.cycle_id} - Lab Elbasan University (çdo 30min)")

    cycle_lab_tirana = engine.create_cycle(
        domain="laboratory",
        source="tirana.medical.center",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Tirana",
        country="Albania"
    )
    print(f"✅ Krijuar: {cycle_lab_tirana.cycle_id} - Lab Tirana Medical Center (çdo 30min)")

    cycle_lab_durres = engine.create_cycle(
        domain="laboratory",
        source="durres.research.institute",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Durrës",
        country="Albania"
    )
    print(f"✅ Krijuar: {cycle_lab_durres.cycle_id} - Lab Durrës Research Institute (çdo 30min)")

    cycle_lab_vlore = engine.create_cycle(
        domain="laboratory",
        source="vlore.marine.lab",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Vlorë",
        country="Albania"
    )
    print(f"✅ Krijuar: {cycle_lab_vlore.cycle_id} - Lab Vlorë Marine Lab (çdo 30min)")

    cycle_lab_shkoder = engine.create_cycle(
        domain="laboratory",
        source="shkoder.university.lab",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Shkodër",
        country="Albania"
    )
    print(f"✅ Krijuar: {cycle_lab_shkoder.cycle_id} - Lab Shkodër University (çdo 30min)")

    cycle_lab_korce = engine.create_cycle(
        domain="laboratory",
        source="korce.agricultural.lab",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Korçë",
        country="Albania"
    )
    print(f"✅ Krijuar: {cycle_lab_korce.cycle_id} - Lab Korçë Agricultural (çdo 30min)")

    cycle_lab_saranda = engine.create_cycle(
        domain="laboratory",
        source="saranda.ecological.lab",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Sarandë",
        country="Albania"
    )
    print(f"✅ Krijuar: {cycle_lab_saranda.cycle_id} - Lab Sarandë Ecological (çdo 30min)")

    # Kosovo Laboratory
    cycle_lab_prishtina = engine.create_cycle(
        domain="laboratory",
        source="prishtina.university.hospital",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Prishtina",
        country="Kosovo"
    )
    print(f"✅ Krijuar: {cycle_lab_prishtina.cycle_id} - Lab Prishtina University Hospital (çdo 30min)")

    # North Macedonia Laboratory
    cycle_lab_kostur = engine.create_cycle(
        domain="laboratory",
        source="kostur.medical.center",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Kostur",
        country="North_Macedonia"
    )
    print(f"✅ Krijuar: {cycle_lab_kostur.cycle_id} - Lab Kostur Medical Center (çdo 30min)")

    # Greece Laboratory
    cycle_lab_athens = engine.create_cycle(
        domain="laboratory",
        source="athens.national.lab",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Athens",
        country="Greece"
    )
    print(f"✅ Krijuar: {cycle_lab_athens.cycle_id} - Lab Athens National Lab (çdo 30min)")

    # Italy Laboratory
    cycle_lab_rome = engine.create_cycle(
        domain="laboratory",
        source="rome.research.center",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Rome",
        country="Italy"
    )
    print(f"✅ Krijuar: {cycle_lab_rome.cycle_id} - Lab Rome Research Center (çdo 30min)")

    # Switzerland Laboratory
    cycle_lab_zurich = engine.create_cycle(
        domain="laboratory",
        source="zurich.tech.university",
        agent="RESEARCH",
        task="city_laboratory_data",
        cycle_type=CycleType.INTERVAL,
        interval=1800.0,  # 30 minuta
        alignment="moderate",
        city="Zurich",
        country="Switzerland"
    )
    print(f"✅ Krijuar: {cycle_lab_zurich.cycle_id} - Lab Zurich Tech University (çdo 30min)")
    print("\n📅 CYCLES TË PRODHIMIT DITOR - API të Reja, Dokumenta, Koncepte, Kërkime, AI/AGI:")

    # Daily API Generation (çdo 24 orë)
    cycle_api_generation = engine.create_cycle(
        domain="api_generation",
        source="asi.saas",
        agent="ASI",
        task="daily_api_generation",
        cycle_type=CycleType.INTERVAL,
        interval=86400.0,  # 24 orë
        alignment="strict"
    )
    print(f"✅ Krijuar: {cycle_api_generation.cycle_id} - Daily API Generation (çdo 24h)")

    # Daily Document Production (çdo 24 orë)
    cycle_document_production = engine.create_cycle(
        domain="documentation",
        source="laboratory.research",
        agent="RESEARCH",
        task="daily_document_generation",
        cycle_type=CycleType.INTERVAL,
        interval=86400.0,  # 24 orë
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_document_production.cycle_id} - Daily Document Production (çdo 24h)")

    # Daily Concept Generation (çdo 24 orë)
    cycle_concept_generation = engine.create_cycle(
        domain="concept_birth",
        source="born_concepts",
        agent="ALBI",
        task="daily_concept_creation",
        cycle_type=CycleType.INTERVAL,
        interval=86400.0,  # 24 orë
        alignment="ethical_guard"
    )
    print(f"✅ Krijuar: {cycle_concept_generation.cycle_id} - Daily Concept Generation (çdo 24h)")

    # Daily Research Production (çdo 24 orë)
    cycle_research_production = engine.create_cycle(
        domain="research",
        source="laboratory.data",
        agent="RESEARCH",
        task="daily_research_generation",
        cycle_type=CycleType.INTERVAL,
        interval=86400.0,  # 24 orë
        alignment="strict"
    )
    print(f"✅ Krijuar: {cycle_research_production.cycle_id} - Daily Research Production (çdo 24h)")

    # Daily AI/AGI Advancement (çdo 24 orë)
    cycle_ai_agi_advancement = engine.create_cycle(
        domain="agi_advancement",
        source="asi.agiem",
        agent="AGIEM",
        task="daily_ai_agi_evolution",
        cycle_type=CycleType.INTERVAL,
        interval=86400.0,  # 24 orë
        alignment="ethical_guard"
    )
    print(f"✅ Krijuar: {cycle_ai_agi_advancement.cycle_id} - Daily AI/AGI Advancement (çdo 24h)")

    # ==================== ALIGNMENT & INTEGRATION CYCLES ====================
    print("\n🔗 CYCLES TË ALIGMENT DHE INTEGRIMIT:")

    # Alignment Synchronization (çdo 6 orë)
    cycle_alignment_sync = engine.create_cycle(
        domain="alignment",
        source="jona.alignment",
        agent="JONA",
        task="alignment_synchronization",
        cycle_type=CycleType.INTERVAL,
        interval=21600.0,  # 6 orë
        alignment="ethical_guard"
    )
    print(f"✅ Krijuar: {cycle_alignment_sync.cycle_id} - Alignment Synchronization (çdo 6h)")

    # Cross-Module Integration (çdo 12 orë)
    cycle_cross_integration = engine.create_cycle(
        domain="integration",
        source="orchestrator.integration",
        agent="ORCHESTRATOR",
        task="cross_module_integration",
        cycle_type=CycleType.INTERVAL,
        interval=43200.0,  # 12 orë
        alignment="strict"
    )
    print(f"✅ Krijuar: {cycle_cross_integration.cycle_id} - Cross-Module Integration (çdo 12h)")

    # Knowledge Graph Update (çdo 8 orë)
    cycle_knowledge_update = engine.create_cycle(
        domain="knowledge",
        source="albi.knowledge_graph",
        agent="ALBI",
        task="knowledge_graph_update",
        cycle_type=CycleType.INTERVAL,
        interval=28800.0,  # 8 orë
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_knowledge_update.cycle_id} - Knowledge Graph Update (çdo 8h)")

    # ==================== CROSS-MODULE COORDINATION ====================
    print("\n🔄 CROSS-MODULE COORDINATION:")

    # System Health Check (çdo 20 min)
    cycle_health_check = engine.create_cycle(
        domain="system",
        source="health.monitor",
        agent="ORCHESTRATOR",
        task="health_check",
        cycle_type=CycleType.INTERVAL,
        interval=1200.0,  # 20 minuta
        alignment="strict"
    )
    print(f"✅ Krijuar: {cycle_health_check.cycle_id} - System Health Check (çdo 20min)")

    # Data Synchronization (çdo 25 min)
    cycle_data_sync = engine.create_cycle(
        domain="data",
        source="sync.orchestrator",
        agent="ORCHESTRATOR",
        task="data_synchronization",
        cycle_type=CycleType.INTERVAL,
        interval=1500.0,  # 25 minuta
        alignment="moderate"
    )
    print(f"✅ Krijuar: {cycle_data_sync.cycle_id} - Data Synchronization (çdo 25min)")

    # ==================== START ALL CYCLES ====================
    print("\n▶️  Nisja e të gjithë cycles...")

    all_cycles = [
        cycle_alba_eeg_open, cycle_alba_processing,
        cycle_albi_learning, cycle_albi_anomalies, cycle_albi_synthesis,
        cycle_jona_ethics, cycle_jona_alignment, cycle_jona_audio,
        cycle_asi_reasoning, cycle_asi_realtime,
        cycle_agiem_ecosystem, cycle_agiem_coordination,
        cycle_lab_pubmed, cycle_lab_arxiv, cycle_lab_crossref, cycle_lab_open_data, cycle_lab_environment, cycle_scalability_engine,
        cycle_lab_elbasan, cycle_lab_tirana, cycle_lab_durres, cycle_lab_vlore, cycle_lab_shkoder, cycle_lab_korce, cycle_lab_saranda,
        cycle_lab_prishtina, cycle_lab_kostur, cycle_lab_athens, cycle_lab_rome, cycle_lab_zurich,
        cycle_api_generation, cycle_document_production, cycle_concept_generation, cycle_research_production, cycle_ai_agi_advancement,
        cycle_alignment_sync, cycle_cross_integration, cycle_knowledge_update,
        cycle_health_check, cycle_data_sync
    ]

    cycles_started = []
    for cycle in all_cycles:
        try:
            execution = await engine.start_cycle(cycle.cycle_id)
            cycles_started.append({
                "cycle_id": cycle.cycle_id,
                "domain": cycle.domain,
                "agent": cycle.agent,
                "task": cycle.task,
                "interval_min": cycle.interval / 60 if cycle.interval else None,
                "execution_id": execution.execution_id
            })
            print(f"🚀 Nisur: {cycle.cycle_id} ({cycle.agent}/{cycle.domain}) - çdo {cycle.interval/60:.0f}min")
        except Exception as e:
            print(f"❌ Dështoi të niset {cycle.cycle_id}: {e}")

    print(f"\n🎯 Prodhimi i cycles ka filluar! {len(cycles_started)} cycles aktive nga të gjithë modulet.")

    # Shfaq statusin përfundimtar
    status = engine.get_status()
    print("\n📊 Statusi i Sistemit të Plotë:")
    print(json.dumps(status, indent=2, ensure_ascii=False))

    # Lista e cycles aktive
    print("\n🔄 Lista e Cycles Aktive:")
    for cycle_info in cycles_started:
        interval = f"{cycle_info['interval_min']:.0f}min" if cycle_info['interval_min'] else "N/A"
        print(f"  • {cycle_info['agent']}: {cycle_info['task']} ({interval}) - {cycle_info['domain']}")

    print("\n⏳ Sistemi i plotë është aktiv. Shtypni Ctrl+C për të ndaluar...")

    try:
        # Mbaj sistemin aktiv për monitorim
        while True:
            await asyncio.sleep(60)  # Kontrollo çdo minutë
            current_status = engine.get_status()
            active_count = current_status.get("active_cycles", 0)

            if active_count != len(cycles_started):
                print(f"⚠️  Numri i cycles aktive ka ndryshuar: {active_count}/{len(cycles_started)}")

    except KeyboardInterrupt:
        print("\n🛑 Ndërprer nga përdoruesi. Duke mbyllur cycles...")
        await engine.stop_all_cycles()
        print("✅ Të gjithë cycles u mbyllën.")

if __name__ == "__main__":
    asyncio.run(start_complete_cycle_production())
