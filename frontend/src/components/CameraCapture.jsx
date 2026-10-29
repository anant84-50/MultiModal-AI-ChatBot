import React, { useState, useRef, useEffect } from 'react';
import { Camera, X, RefreshCw, Check, AlertCircle } from 'lucide-react';

export default function CameraCapture({ isOpen, onClose, onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [facingMode, setFacingMode] = useState('user'); // 'user' or 'environment'

  useEffect(() => {
    if (isOpen) {
      startCamera();
    } else {
      stopCamera();
      setCapturedImage(null);
      setErrorMsg(null);
    }
    return () => {
      stopCamera();
    };
  }, [isOpen, facingMode]);

  const startCamera = async () => {
    stopCamera();
    setErrorMsg(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access is not supported by this browser.');
      }
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error('Camera error:', err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setErrorMsg('Camera permission denied. Please allow camera access in browser settings.');
      } else if (err.name === 'NotFoundError') {
        setErrorMsg('No camera device found on this system.');
      } else {
        setErrorMsg(err.message || 'Unable to access camera.');
      }
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  };

  const handleCapture = () => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current || document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    if (facingMode === 'user') {
      // Mirror front camera
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL('image/png');
    setCapturedImage(dataUrl);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `camera_capture_${Date.now()}.png`, { type: 'image/png' });
        // Auto pass to parent or allow confirm
        onCapture(file);
        handleClose();
      }
    }, 'image/png');
  };

  const handleFlipCamera = () => {
    setFacingMode((prev) => (prev === 'user' ? 'environment' : 'user'));
  };

  const handleClose = () => {
    stopCamera();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay camera-modal-overlay">
      <div className="camera-modal-card">
        <div className="camera-modal-header">
          <div className="camera-title-group">
            <Camera size={20} className="text-indigo-400" />
            <span className="camera-title">Take a Photo</span>
          </div>
          <button type="button" onClick={handleClose} className="modal-close-btn">
            <X size={20} />
          </button>
        </div>

        <div className="camera-viewport-wrapper">
          {errorMsg ? (
            <div className="camera-error-box">
              <AlertCircle size={36} className="text-rose-500 mb-2" />
              <p className="camera-error-text">{errorMsg}</p>
              <button type="button" onClick={startCamera} className="camera-retry-btn">
                Retry Permission
              </button>
            </div>
          ) : (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`camera-video-feed ${facingMode === 'user' ? 'mirror' : ''}`}
                onLoadedMetadata={() => videoRef.current?.play()}
              />
              <div className="camera-crosshairs"></div>
            </>
          )}
        </div>

        <canvas ref={canvasRef} style={{ display: 'none' }} />

        {!errorMsg && (
          <div className="camera-controls-bar">
            <button
              type="button"
              onClick={handleFlipCamera}
              className="camera-tool-btn"
              title="Switch Camera (Front/Back)"
            >
              <RefreshCw size={18} />
            </button>

            <button
              type="button"
              onClick={handleCapture}
              className="camera-shutter-btn"
              title="Take Photo"
            >
              <div className="shutter-inner-ring">
                <Camera size={24} />
              </div>
            </button>

            <button
              type="button"
              onClick={handleClose}
              className="camera-tool-btn"
              title="Cancel"
            >
              <X size={18} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
