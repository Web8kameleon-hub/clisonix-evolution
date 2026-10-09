import { Camera, RefreshCw, X } from 'lucide-react';
import type { RefObject } from 'react';
import { CuriosityUiStrings } from '../../../lib/i18n/curiosity-ocean';

interface CameraOverlayProps {
  showCamera: boolean;
  videoRef: RefObject<HTMLVideoElement>;
  switchCamera: () => void | Promise<void>;
  capturePhoto: () => void | Promise<void>;
  toggleCamera: () => void | Promise<void>;
  t: CuriosityUiStrings;
}

export function CameraOverlay({ showCamera, videoRef, switchCamera, capturePhoto, toggleCamera, t }: CameraOverlayProps) {
  if (!showCamera) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl overflow-hidden shadow-2xl max-w-sm w-full">
        <div className="px-4 py-2 border-b border-gray-200 bg-gray-50 text-[11px] font-semibold tracking-wide text-gray-700">
          CLISONIX ZEISS VISION ULTRA • 2450px+
        </div>
        <video ref={videoRef} autoPlay playsInline className="w-full aspect-[4/3] bg-gray-900 object-cover" />
        <div className="flex items-center justify-center gap-4 p-5">
          <button onClick={switchCamera} className="p-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors text-gray-600" title={t.switchCam}>
            <RefreshCw className="w-5 h-5" />
          </button>
          <button onClick={capturePhoto} className="p-5 bg-emerald-500 hover:bg-emerald-600 rounded-full transition-all text-white shadow-lg shadow-emerald-500/30 active:scale-95">
            <Camera className="w-6 h-6" />
          </button>
          <button onClick={toggleCamera} className="p-3 bg-gray-100 hover:bg-red-50 rounded-full transition-colors text-gray-600 hover:text-red-500" title={t.close}>
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
