import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Check, X, Loader2, AlertCircle, Volume2 } from 'lucide-react';
import { api } from '../services/api';

export default function VoiceInput({ onTranscript, isRecording, setIsRecording }) {
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordSeconds, setRecordSeconds] = useState(0);
  const [interimSpeech, setInterimSpeech] = useState('');
  const [errorMessage, setErrorMessage] = useState(null);

  const mediaStreamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const recognitionRef = useRef(null);
  const finalTranscriptRef = useRef('');

  // Clear timers and streams on unmount
  useEffect(() => {
    return () => {
      cleanupAudio();
    };
  }, []);

  const cleanupAudio = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onresult = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.onend = null;
        recognitionRef.current.stop();
      } catch (e) {
        // Ignore
      }
      recognitionRef.current = null;
    }
    if (mediaStreamRef.current) {
      try {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      } catch (e) {
        // Ignore
      }
      mediaStreamRef.current = null;
    }
  };

  // Start Voice Recording
  const startRecording = async () => {
    setErrorMessage(null);
    setInterimSpeech('');
    finalTranscriptRef.current = '';
    chunksRef.current = [];

    // 1. Request microphone access explicitly
    let stream = null;
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Your browser does not support microphone audio capture.');
      }
      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;
    } catch (err) {
      console.error('Microphone permission error:', err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setErrorMessage(
          'Microphone permission was denied. Please allow microphone access in your browser settings (click the lock/tune icon near your address bar).'
        );
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setErrorMessage('No microphone device found. Please connect a microphone or headset.');
      } else {
        setErrorMessage(`Microphone error: ${err.message || 'Unable to access microphone'}`);
      }
      setIsRecording(false);
      return;
    }

    // 2. Setup MediaRecorder for universal audio recording
    try {
      let mimeType = 'audio/webm;codecs=opus';
      if (typeof MediaRecorder !== 'undefined') {
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = 'audio/webm';
          if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'audio/mp4';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
              mimeType = '';
            }
          }
        }
      }

      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start(200); // 200ms slice
      setIsRecording(true);
      setRecordSeconds(0);

      // Start elapsed timer
      timerRef.current = setInterval(() => {
        setRecordSeconds((s) => s + 1);
      }, 1000);
    } catch (err) {
      console.error('Failed to start MediaRecorder:', err);
      setErrorMessage('Could not initialize audio recorder: ' + err.message);
      cleanupAudio();
      setIsRecording(false);
      return;
    }

    // 3. Fast-path: Start Browser SpeechRecognition concurrently if available
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      try {
        const recog = new SpeechRecognition();
        recog.continuous = true;
        recog.interimResults = true;
        recog.lang = navigator.language || 'en-US';

        recog.onresult = (event) => {
          let accumulated = '';
          for (let i = 0; i < event.results.length; i++) {
            accumulated += event.results[i][0].transcript + ' ';
          }
          const cleaned = accumulated.trim();
          if (cleaned) {
            finalTranscriptRef.current = cleaned;
            setInterimSpeech(cleaned);
          }
        };

        recog.onerror = (e) => {
          // 'no-speech' is normal during pauses; do not abort recording!
          if (e.error !== 'no-speech') {
            console.warn('SpeechRecognition warning:', e.error);
          }
        };

        recog.start();
        recognitionRef.current = recog;
      } catch (recogErr) {
        console.warn('Browser SpeechRecognition not active; falling back to Gemini audio:', recogErr);
      }
    }
  };

  // Stop Recording & Transcribe
  const stopRecording = () => {
    if (!isRecording) return;

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // Stop SpeechRecognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        // Ignore
      }
      recognitionRef.current = null;
    }

    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== 'inactive') {
      recorder.onstop = async () => {
        // Release mic stream immediately so browser red dot disappears
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((t) => t.stop());
          mediaStreamRef.current = null;
        }

        const capturedText = finalTranscriptRef.current.trim();

        // If Web Speech API captured text with high fidelity, use it!
        if (capturedText && capturedText.length > 2) {
          onTranscript(capturedText);
          setIsRecording(false);
          setInterimSpeech('');
          return;
        }

        // Otherwise (or in Brave/Firefox/silence), transcribe with Gemini Flash!
        const mimeType = recorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(chunksRef.current, { type: mimeType });

        if (audioBlob.size < 500) {
          setErrorMessage('No voice detected. Please speak into your microphone and try again.');
          setIsRecording(false);
          setInterimSpeech('');
          return;
        }

        try {
          setIsTranscribing(true);
          const res = await api.transcribeAudio(audioBlob);
          if (res && res.transcript && res.transcript.trim()) {
            onTranscript(res.transcript.trim());
          } else {
            setErrorMessage('No clear speech was detected. Please try again.');
          }
        } catch (apiErr) {
          console.error('Gemini audio transcription error:', apiErr);
          setErrorMessage('Transcription error. Please check backend connection and retry.');
        } finally {
          setIsTranscribing(false);
          setIsRecording(false);
          setInterimSpeech('');
        }
      };

      try {
        recorder.stop();
      } catch (e) {
        console.error('Error stopping recorder:', e);
        cleanupAudio();
        setIsRecording(false);
      }
    } else {
      cleanupAudio();
      setIsRecording(false);
    }
  };

  // Cancel Recording without transcribing
  const cancelRecording = () => {
    cleanupAudio();
    setIsRecording(false);
    setIsTranscribing(false);
    setInterimSpeech('');
    chunksRef.current = [];
  };

  const formatTimer = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="voice-input-wrapper">
      {/* Mic Button */}
      <button
        type="button"
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isTranscribing}
        className={`voice-record-btn ${isRecording ? 'recording-active' : ''} ${
          isTranscribing ? 'transcribing-active' : ''
        }`}
        title={
          isTranscribing
            ? 'Transcribing audio...'
            : isRecording
            ? 'Click to Stop & Finish'
            : 'Voice Input (Click to speak)'
        }
      >
        {isTranscribing ? (
          <Loader2 size={16} className="spin-icon" />
        ) : isRecording ? (
          <Square size={13} className="stop-square-icon" />
        ) : (
          <Mic size={17} />
        )}
      </button>

      {/* Floating Active Recording Pill */}
      {isRecording && (
        <div className="voice-live-floating-banner">
          <div className="voice-live-pulse-indicator">
            <span className="live-red-dot" />
            <span className="live-timer-text">{formatTimer(recordSeconds)}</span>
          </div>

          <div className="voice-wave-bars">
            <span className="wave-bar bar-1" />
            <span className="wave-bar bar-2" />
            <span className="wave-bar bar-3" />
            <span className="wave-bar bar-4" />
          </div>

          <div className="voice-live-text-preview">
            {interimSpeech ? `"${interimSpeech}"` : 'Listening... Speak now'}
          </div>

          <div className="voice-live-actions">
            <button
              type="button"
              onClick={stopRecording}
              className="voice-action-btn voice-confirm-btn"
              title="Done speaking (Transcribe)"
            >
              <Check size={14} />
              <span>Done</span>
            </button>
            <button
              type="button"
              onClick={cancelRecording}
              className="voice-action-btn voice-cancel-btn"
              title="Cancel recording"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Transcribing Indicator Banner */}
      {isTranscribing && (
        <div className="voice-live-floating-banner voice-transcribing-banner">
          <Loader2 size={15} className="spin-icon text-amber-400" />
          <span className="voice-transcribing-text">AI is transcribing your voice...</span>
        </div>
      )}

      {/* Error Tooltip Banner */}
      {errorMessage && (
        <div className="voice-error-toast">
          <AlertCircle size={15} className="voice-error-icon" />
          <span className="voice-error-text">{errorMessage}</span>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            className="voice-error-close"
            title="Dismiss"
          >
            <X size={13} />
          </button>
        </div>
      )}
    </div>
  );
}
