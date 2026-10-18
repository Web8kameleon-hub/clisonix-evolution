/**
 * Time Compression Page - Bend Space-Time for Speed
 * Coming Soon - Requires Monthly Subscription  
 */

'use client';

import Link from 'next/link';
import { ArrowLeft, Clock } from 'lucide-react';

export default function TimeCompressionPage() {
  return (
    <div className="min-h-screen text-white p-8 font-['SF_Pro_Display'] flex flex-col justify-center items-center text-center"
         style={{
           background: `
             radial-gradient(circle at 20% 50%, #ff6b0022 0%, transparent 50%),
             radial-gradient(circle at 80% 20%, #0066ff22 0%, transparent 50%),
             linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)
           `
         }}>
      
      <Link href="/ultra-speed" className="absolute top-8 left-8 flex items-center gap-2 text-orange-500 no-underline text-base">
        <ArrowLeft size={20} />
        Back to Ultra Speed
      </Link>

      <div className="mb-12">
        <div className="text-8xl mb-4">⏰</div>
        
        <h1 className="text-6xl font-black mb-4 bg-gradient-to-r from-orange-500 to-white bg-clip-text text-transparent">
          Time Compression
        </h1>
        
        <p className="text-xl text-gray-400 mb-12 max-w-2xl">
          Bend Space-Time for Speed • Coming Soon
        </p>

        <div className="bg-orange-500/10 border-2 border-orange-500 rounded-3xl p-8 max-w-lg mx-auto">
          <Clock size={48} className="text-orange-500 mb-4 mx-auto" />
          <h3 className="text-xl font-bold text-orange-500 mb-4">
            Premium Service
          </h3>
          <p className="text-gray-300 leading-relaxed">
            This space-time manipulation service requires a monthly subscription. 
            Temporal acceleration technology will be available soon.
          </p>
        </div>
      </div>
    </div>
  );
}
