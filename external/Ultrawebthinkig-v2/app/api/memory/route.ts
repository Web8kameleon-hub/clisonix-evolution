import OpenMindMemory from '../../../lib/memorySystem';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json(
        { error: 'Nuk u gjet asnjë fajll për ngarkime' },
        { status: 400 }
      );
    }

    const memory = OpenMindMemory.getInstance();
    const documentId = await memory.storeDocument(file);

    return NextResponse.json({
      success: true,
      documentId,
      message: `Dokumenti "${file.name}" u ruajt me sukses në memorien e OpenMind`,
      size: file.size,
      type: file.type
    });

  } catch (error) {
    console.error('Document upload error:', error);
    return NextResponse.json(
      { error: 'Gabim gjatë ngarkimit të dokumentit' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    
    const memory = OpenMindMemory.getInstance();

    if (action === 'stats') {
      const stats = memory.getMemoryStats();
      return NextResponse.json(stats);
    }

    if (action === 'search') {
      const query = searchParams.get('q') || '';
      const limit = parseInt(searchParams.get('limit') || '10');
      
      const results = memory.search(query, limit);
      return NextResponse.json({
        query,
        results: results.map(r => ({
          id: r.entry.id,
          title: r.entry.title,
          type: r.entry.type,
          relevance: r.relevanceScore,
          timestamp: r.entry.metadata.timestamp,
          fragments: r.matchedFragments
        }))
      });
    }

    return NextResponse.json({
      message: 'OpenMind Memory API',
      endpoints: {
        'POST /api/memory': 'Ngarko dokument',
        'GET /api/memory?action=stats': 'Statistikat e memories',
        'GET /api/memory?action=search&q=query': 'Kërko në memorie'
      }
    });

  } catch (error) {
    console.error('Memory API error:', error);
    return NextResponse.json(
      { error: 'Gabim në API të memories' },
      { status: 500 }
    );
  }
}
