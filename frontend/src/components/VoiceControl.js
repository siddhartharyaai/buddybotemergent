import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MicrophoneIcon } from '@heroicons/react/24/outline';

const VoiceControl = ({ onStartAmbientListening, onStopAmbientListening, darkMode }) => {
  const [micStatus, setMicStatus] = useState('offline'); // 'offline', 'requesting', 'ready', 'listening'

  const handleStartVoice = async () => {
    console.log('🎤 User clicked Start Voice button');
    setMicStatus('requesting');
    
    try {
      console.log('🎤 Requesting microphone permission...');
      
      // Request microphone permission with explicit user gesture
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      console.log('✅ Microphone permission granted!');
      
      // Permission granted: proceed with ambient listening
      const success = await onStartAmbientListening(stream);
      
      if (success) {
        setMicStatus('listening');
        console.log('🎤 Ambient listening started - ready for "Hey Buddy"');
      } else {
        setMicStatus('offline');
        console.error('❌ Failed to start ambient listening');
      }
      
    } catch (error) {
      console.error('❌ Microphone permission denied:', error);
      setMicStatus('offline');
      
      // Provide user guidance
      if (error.name === 'NotAllowedError') {
        alert('🎤 Microphone access denied. Please:\n1. Click the microphone icon in your browser address bar\n2. Select "Allow"\n3. Refresh the page and try again');
      } else {
        alert('🎤 Could not access microphone. Please check your device settings and try again.');
      }
    }
  };

  const handleStopVoice = () => {
    console.log('🔇 User clicked Stop Voice button');
    onStopAmbientListening();
    setMicStatus('offline');
  };

  const getButtonStyle = () => {
    switch (micStatus) {
      case 'ready':
      case 'listening':
        return 'bg-green-500 text-white shadow-lg shadow-green-500/25 hover:bg-green-600';
      case 'requesting':
        return 'bg-yellow-500 text-white shadow-lg shadow-yellow-500/25 animate-pulse';
      case 'offline':
      default:
        return darkMode 
          ? 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white' 
          : 'bg-gray-200 text-gray-600 hover:bg-gray-300';
    }
  };

  const getStatusText = () => {
    switch (micStatus) {
      case 'requesting':
        return 'Requesting permission...';
      case 'ready':
        return 'Voice ready - waiting for wake word';
      case 'listening':
        return 'Always On - Say "Hey Buddy"';
      case 'offline':
      default:
        return 'Offline';
    }
  };

  const getButtonText = () => {
    switch (micStatus) {
      case 'requesting':
        return 'Starting...';
      case 'ready':
      case 'listening':
        return 'Voice Active';
      case 'offline':
      default:
        return 'Start Voice';
    }
  };

  return (
    <div className="flex flex-col items-center space-y-2">
      <motion.button
        type="button"
        onClick={micStatus === 'offline' || micStatus === 'requesting' ? handleStartVoice : handleStopVoice}
        disabled={micStatus === 'requesting'}
        whileHover={{ scale: micStatus !== 'requesting' ? 1.05 : 1 }}
        whileTap={{ scale: micStatus !== 'requesting' ? 0.95 : 1 }}
        className={`p-4 rounded-full transition-all duration-300 ${getButtonStyle()}`}
        title={getStatusText()}
      >
        <MicrophoneIcon className="w-6 h-6" />
      </motion.button>
      
      {/* Status indicator */}
      <div className={`text-xs px-3 py-1 rounded-full ${
        micStatus === 'listening' || micStatus === 'ready' 
          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
          : micStatus === 'requesting'
          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
      }`}>
        {getStatusText()}
      </div>

      {/* Instructions for first-time users */}
      {micStatus === 'offline' && (
        <div className={`text-xs text-center max-w-xs ${
          darkMode ? 'text-gray-400' : 'text-gray-500'
        }`}>
          Click to grant microphone permission and start voice chat
        </div>
      )}
      
      {micStatus === 'listening' && (
        <div className={`text-xs text-center max-w-xs ${
          darkMode ? 'text-green-400' : 'text-green-600'
        }`}>
          🎤 Ready! Say "Hey Buddy" to start talking
        </div>
      )}
    </div>
  );
};

export default VoiceControl;