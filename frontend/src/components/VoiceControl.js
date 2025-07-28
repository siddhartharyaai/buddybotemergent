import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { MicrophoneIcon } from '@heroicons/react/24/outline';

const VoiceControl = ({ onStartAmbientListening, onStopAmbientListening, darkMode }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      console.log('🎤 Starting simple voice recording...');
      
      // Request microphone permission - simple approach like ChatGPT/Gemini
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      
      console.log('✅ Microphone access granted');
      
      // Create MediaRecorder - use webm like other voice bots
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = async () => {
        console.log('🎤 Recording stopped, processing...');
        setIsProcessing(true);
        
        try {
          // Create audio blob and send to backend
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          await processVoiceInput(audioBlob);
        } catch (error) {
          console.error('❌ Error processing voice:', error);
        } finally {
          setIsProcessing(false);
        }
      };
      
      // Start recording
      mediaRecorderRef.current.start();
      setIsRecording(true);
      
      console.log('🎤 Recording started');
      
    } catch (error) {
      console.error('❌ Microphone error:', error);
      alert('Please allow microphone access and try again. Make sure no other app is using your microphone.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      console.log('🎤 Stopping recording...');
      mediaRecorderRef.current.stop();
      
      // Stop all tracks to release microphone
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      
      setIsRecording(false);
    }
  };

  const processVoiceInput = async (audioBlob) => {
    try {
      // Convert to base64 for API transmission
      const base64Audio = await blobToBase64(audioBlob);
      
      // Send to backend for STT + conversation processing
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/conversations/voice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: Date.now().toString(), // Simple session ID
          user_id: 'test_user',
          audio_base64: base64Audio
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Voice response received:', data.response_text);
        
        // Play TTS audio if available
        if (data.response_audio) {
          playTTSAudio(data.response_audio);
        }
      } else {
        console.error('❌ Voice API error:', response.status);
        alert('Voice processing failed. Please try again.');
      }
      
    } catch (error) {
      console.error('❌ Voice processing error:', error);
      alert('Voice processing failed. Please try again.');
    }
  };

  const blobToBase64 = (blob) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.readAsDataURL(blob);
    });
  };

  const playTTSAudio = (base64Audio) => {
    try {
      // Create audio element and play - simple like other voice bots
      const audio = new Audio(`data:audio/wav;base64,${base64Audio}`);
      audio.play().catch(console.error);
      console.log('🔊 Playing TTS audio');
    } catch (error) {
      console.error('❌ TTS playback error:', error);
    }
  };

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else if (!isProcessing) {
      startRecording();
    }
  };

  const getButtonStyle = () => {
    if (isProcessing) {
      return 'bg-yellow-500 text-white shadow-lg shadow-yellow-500/25 animate-pulse';
    } else if (isRecording) {
      return 'bg-red-500 text-white shadow-lg shadow-red-500/25 animate-pulse';
    } else {
      return darkMode 
        ? 'bg-gray-700 text-gray-300 hover:bg-blue-600 hover:text-white' 
        : 'bg-blue-500 text-white hover:bg-blue-600';
    }
  };

  const getStatusText = () => {
    if (isProcessing) return 'Processing...';
    if (isRecording) return 'Recording - Click to stop';
    return 'Click to record';
  };

  const getButtonText = () => {
    if (isProcessing) return 'Processing...';
    if (isRecording) return 'Stop';
    return 'Record';
  };

  return (
    <div className="flex flex-col items-center space-y-2">
      <motion.button
        type="button"
        onClick={handleClick}
        disabled={isProcessing}
        whileHover={{ scale: isProcessing ? 1 : 1.05 }}
        whileTap={{ scale: isProcessing ? 1 : 0.95 }}
        className={`p-4 rounded-full transition-all duration-300 ${getButtonStyle()}`}
        title={getStatusText()}
      >
        <MicrophoneIcon className="w-6 h-6" />
      </motion.button>
      
      <div className={`text-xs px-3 py-1 rounded-full ${
        isRecording 
          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          : isProcessing
          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          : 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-200'
      }`}>
        {getStatusText()}
      </div>

      <div className={`text-xs text-center max-w-xs ${
        darkMode ? 'text-gray-400' : 'text-gray-500'
      }`}>
        {!isRecording && !isProcessing && 'Click to record your message'}
        {isRecording && 'Speak now, click again to stop'}
        {isProcessing && 'Processing your voice...'}
      </div>
    </div>
  );
};

export default VoiceControl;