import dynamic from 'next/dynamic';
import { Suspense } from 'react';

// Dynamic import to avoid SSR issues
const AdvancedChatSystem = dynamic(() => import('../components/chat/AdvancedChatSystem'), {
  ssr: false,
  loading: () => (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-500 mx-auto mb-4"></div>
        <h2 className="text-2xl font-bold text-white mb-2">🚀 Sistemin e Diskutimit të Avancuar</h2>
        <p className="text-gray-300">Duke ngarkuar platformën për diskutime të lira...</p>
      </div>
    </div>
  )
});

export default function AdvancedChat() {
  return (
    <div className="min-h-screen">
      <Suspense fallback={
        <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-pulse text-6xl mb-4">🧠</div>
            <h2 className="text-2xl font-bold text-white mb-2">Sistemi i Diskutimit të Avancuar</h2>
            <p className="text-gray-300">Gati për diskutime të thella...</p>
          </div>
        </div>
      }>
        <AdvancedChatSystem />
      </Suspense>
    </div>
  );
}
