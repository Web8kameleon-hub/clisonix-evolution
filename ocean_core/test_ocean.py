import asyncio

async def test():
    print('🌊 Testing Ocean Core 8030...\n')
    
    try:
        from data_sources import get_data_sources_manager
        from external_apis import get_external_apis_manager
        from query_processor import get_query_processor
        from knowledge_engine import get_knowledge_engine
        print('✅ All imports successful')
    except Exception as e:
        print(f'❌ Import error: {e}')
        return
    
    try:
        print('\n🔄 Initializing managers...')
        data_sources = await get_data_sources_manager()
        external_apis = await get_external_apis_manager()
        query_proc = await get_query_processor()
        knowledge_eng = await get_knowledge_engine(data_sources, external_apis)
        print('✅ All managers initialized')
    except Exception as e:
        print(f'❌ Init error: {e}')
        import traceback
        traceback.print_exc()
        return
    
    try:
        print('\n🧠 Processing queries...')
        queries = [
            'What labs do we have?',
            'How are ALBA and ALBI performing?',
            'What is consciousness?'
        ]
        for q in queries:
            proc = await query_proc.process(q)
            print(f'✅ "{q}" -> intent={proc.intent.value}')
        
    except Exception as e:
        print(f'❌ Query error: {e}')
        import traceback
        traceback.print_exc()
        return
    
    try:
        print('\n📝 Testing knowledge engine...')
        proc = await query_proc.process('What is our lab status?')
        response = await knowledge_eng.answer_query('What is our lab status?', proc)
        print(f'✅ Response: {response.processing_time_ms}ms, confidence={response.confidence_score}')
        print(f'✅ Findings: {len(response.key_findings)} items')
        print(f'✅ Curiosity threads: {len(response.curiosity_threads)}')
    except Exception as e:
        print(f'❌ Engine error: {e}')
        import traceback
        traceback.print_exc()
        return
    
    print('\n✅ Ocean Core 8030 READY!')

asyncio.run(test())
