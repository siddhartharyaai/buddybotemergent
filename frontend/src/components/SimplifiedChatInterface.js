import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MicrophoneIcon, 
  StopIcon, 
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  SparklesIcon,
  ChatBubbleLeftEllipsisIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const SimplifiedChatInterface = ({ user, darkMode, setDarkMode, sessionId, messages, onAddMessage }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isBotSpeaking, setIsBotSpeaking] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [recordingTimer, setRecordingTimer] = useState(0);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  const audioRef = useRef(null);
  const recordingIntervalRef = useRef(null);
  const streamRef = useRef(null);

  // Voice-only suggestions
  const suggestions = [
    "Tell me a story",
    "Sing me a song", 
    "Ask me a riddle",
    "Let's play a game"
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startRecording = async () => {
    console.log('🎤 Starting recording process...');
    
    try {
      // Reset states
      setCurrentTranscript('');
      setRecordingTimer(0);
      
      console.log('🔍 Checking for media devices support...');
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Media devices not supported on this browser');
      }
      
      console.log('🔍 Checking for MediaRecorder support...');
      if (!window.MediaRecorder) {
        throw new Error('MediaRecorder not supported on this browser');
      }
      
      console.log('🎯 Requesting microphone access...');
      
      // Use the simplest possible audio constraints for maximum compatibility
      const audioConstraints = {
        audio: true
      };

      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia(audioConstraints);
        console.log('✅ Microphone access granted');
      } catch (permissionError) {
        console.error('❌ Microphone permission error:', permissionError);
        let errorMessage = '🎤 Microphone access denied. ';
        
        if (permissionError.name === 'NotAllowedError') {
          errorMessage += 'Please allow microphone permission in your browser settings.';
        } else if (permissionError.name === 'NotFoundError') {
          errorMessage += 'No microphone found on your device.';
        } else if (permissionError.name === 'NotReadableError') {
          errorMessage += 'Microphone is being used by another application.';
        } else {
          errorMessage += 'Please check your microphone settings and try again.';
        }
        
        toast.error(errorMessage);
        return;
      }
      
      streamRef.current = stream;
      
      console.log('🎚️ Creating MediaRecorder with default settings...');
      
      // Use the most basic MediaRecorder setup for maximum compatibility
      let mediaRecorder;
      try {
        mediaRecorder = new MediaRecorder(stream);
        console.log('✅ MediaRecorder created successfully');
      } catch (recorderError) {
        console.error('❌ MediaRecorder creation failed:', recorderError);
        
        // Clean up stream
        stream.getTracks().forEach(track => track.stop());
        streamRef.current = null;
        
        toast.error('🎤 Recording not supported on this device. Please try a different browser.');
        return;
      }
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      console.log('📦 Setting up MediaRecorder events...');

      mediaRecorder.ondataavailable = (event) => {
        console.log('📦 Audio data received:', event.data.size, 'bytes');
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log('✅ Audio chunk added, total chunks:', audioChunksRef.current.length);
        }
      };

      mediaRecorder.onstop = () => {
        console.log('🛑 Recording stopped, processing audio...');
        console.log('📊 Total chunks collected:', audioChunksRef.current.length);
        
        if (audioChunksRef.current.length === 0) {
          console.error('❌ No audio chunks collected');
          toast.error('🎤 Recording failed - no audio captured. Please try speaking louder.');
          return;
        }
        
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: mediaRecorder.mimeType || 'audio/webm'
        });
        console.log('🎵 Audio blob created:', audioBlob.size, 'bytes, type:', audioBlob.type);
        
        if (audioBlob.size === 0) {
          console.error('❌ Audio blob is empty');
          toast.error('🎤 Recording failed - empty audio. Please speak louder and try again.');
          return;
        }
        
        sendVoiceMessage(audioBlob);
        
        // Clean up stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => {
            track.stop();
            console.log('🔇 Audio track stopped');
          });
          streamRef.current = null;
        }
      };

      mediaRecorder.onerror = (error) => {
        console.error('❌ MediaRecorder error:', error);
        toast.error('🎤 Recording error occurred. Please try again.');
      };

      console.log('🎬 Starting recording...');
      
      // Start recording with data collection every 1000ms for stability
      mediaRecorder.start(1000);
      setIsRecording(true);
      
      console.log('✅ Recording started successfully');
      
      // Add a live recording message
      const liveMessage = {
        id: `recording-${Date.now()}`,
        type: 'user',
        content: '🎤 Recording... (hold to continue)',
        isVoice: true,
        isLive: true,
        timestamp: new Date()
      };
      onAddMessage(liveMessage);
      
      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTimer(prev => prev + 1);
      }, 1000);
      
      console.log('🎉 Recording setup complete');
      
    } catch (error) {
      console.error('💥 Critical recording error:', error);
      
      // Clean up any resources
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      
      let errorMessage = '🎤 Recording failed: ';
      if (error.message.includes('not supported')) {
        errorMessage += 'Your browser does not support audio recording.';
      } else if (error.message.includes('permission')) {
        errorMessage += 'Microphone permission required.';
      } else {
        errorMessage += error.message;
      }
      
      toast.error(errorMessage);
    }
  };

  const stopRecording = () => {
    console.log('🛑 Stopping recording...');
    
    try {
      // Clear recording timer
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
      
      // Stop MediaRecorder
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        console.log('⏹️ Stopping MediaRecorder...');
        mediaRecorderRef.current.stop();
      }
      
      setIsRecording(false);
      console.log('✅ Recording stopped successfully');
      
    } catch (error) {
      console.error('❌ Error stopping recording:', error);
      setIsRecording(false);
      toast.error('🎤 Error stopping recording');
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    console.log('🎵 Sending voice message, blob size:', audioBlob.size, 'type:', audioBlob.type);
    
    // Enhanced validation with detailed logging
    if (!audioBlob) {
      console.error('❌ Audio blob is null/undefined');
      toast.error('🎤 Recording failed - no audio captured. Please try again.');
      return;
    }
    
    if (audioBlob.size === 0) {
      console.error('❌ Audio blob size is 0');
      toast.error('🎤 Recording failed - empty audio. Please speak louder and hold the mic button longer.');
      return;
    }

    // More forgiving size threshold for mobile
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const minSize = isMobile ? 500 : 1000; // Lower threshold for mobile
    
    if (audioBlob.size < minSize) {
      console.warn('⚠️ Audio blob very small:', audioBlob.size, 'bytes');
      // Don't block on mobile - try to process anyway
      if (!isMobile) {
        toast.error('Recording too short. Please hold the mic button and speak for at least 1 second.');
        return;
      }
    }
    
    console.log('✅ Audio blob validation passed');
    
    // Create temporary user message for processing
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: '🎤 Processing voice...',
      isVoice: true,
      timestamp: new Date()
    };

    onAddMessage(userMessage);
    setIsLoading(true);

    try {
      // Enhanced mobile-compatible base64 conversion
      console.log('🔄 Converting audio to base64...');
      
      // Method 1: ArrayBuffer conversion (more reliable on mobile)
      let base64Audio;
      try {
        const arrayBuffer = await audioBlob.arrayBuffer();
        console.log('📦 ArrayBuffer size:', arrayBuffer.byteLength);
        
        const uint8Array = new Uint8Array(arrayBuffer);
        base64Audio = btoa(String.fromCharCode(...uint8Array));
        console.log('✅ ArrayBuffer to base64 conversion successful, length:', base64Audio.length);
      } catch (arrayBufferError) {
        console.warn('⚠️ ArrayBuffer method failed, trying FileReader:', arrayBufferError);
        
        // Method 2: FileReader fallback
        try {
          base64Audio = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
              try {
                const result = reader.result;
                if (!result || typeof result !== 'string') {
                  reject(new Error('FileReader result is not a string'));
                  return;
                }
                const base64 = result.split(',')[1];
                if (!base64 || base64.length === 0) {
                  reject(new Error('Base64 extraction failed'));
                  return;
                }
                resolve(base64);
              } catch (error) {
                reject(error);
              }
            };
            reader.onerror = () => reject(new Error('FileReader error'));
            reader.readAsDataURL(audioBlob);
          });
          console.log('✅ FileReader to base64 conversion successful, length:', base64Audio.length);
        } catch (fileReaderError) {
          console.error('❌ Both conversion methods failed:', fileReaderError);
          throw new Error('Audio conversion failed');
        }
      }
      
      if (!base64Audio || base64Audio.length === 0) {
        throw new Error('Base64 conversion resulted in empty string');
      }
      
      console.log('📡 Sending to backend...');
      
      // Create form data with proper content type
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('user_id', user.id);
      formData.append('audio_base64', base64Audio);

      console.log('🌐 Making API call to voice endpoint...');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/voice/process_audio`, {
        method: 'POST',
        body: formData
      });

      console.log('📨 Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API error response:', errorText);
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log('✅ Voice processing response:', data);
      
      if (data.status === 'success') {
        // Add AI response
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response_text || 'I heard you!',
          audioData: data.response_audio,
          contentType: data.content_type,
          metadata: data.metadata,
          timestamp: new Date()
        };

        onAddMessage(aiMessage);
        
        // Auto-play AI response if available
        if (data.response_audio) {
          playAudio(data.response_audio);
        }
        
        toast.success('🎉 Voice message processed!');
      } else {
        throw new Error(data.detail || data.message || 'Voice processing failed');
      }
      
    } catch (error) {
      console.error('💥 Voice message error:', error);
      
      // More specific error messages
      let errorMessage = '🎤 Voice processing failed. ';
      if (error.message.includes('conversion failed')) {
        errorMessage += 'Audio format issue - please try again.';
      } else if (error.message.includes('Server error')) {
        errorMessage += 'Server issue - please check your connection.';
      } else if (error.message.includes('fetch')) {
        errorMessage += 'Network error - please check your internet connection.';
      } else {
        errorMessage += 'Please try speaking louder and holding the mic button longer.';
      }
      
      toast.error(errorMessage);
      
      // Add error message since we can't update existing message
      const errorMsg = {
        id: Date.now() + 1,
        type: 'system',
        content: '❌ Voice processing failed - try again',
        timestamp: new Date()
      };
      onAddMessage(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  // Voice-only interface - no text messaging functionality

  const playAudio = (base64Audio) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    
    const audioBlob = new Blob([Uint8Array.from(atob(base64Audio), c => c.charCodeAt(0))], { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(audioBlob);
    
    audioRef.current = new Audio(audioUrl);
    audioRef.current.play();
    setIsPlaying(true);
    setIsBotSpeaking(true);
    
    audioRef.current.onended = () => {
      setIsPlaying(false);
      setIsBotSpeaking(false);
      URL.revokeObjectURL(audioUrl);
    };
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setIsBotSpeaking(false);
    }
  };

  const formatTime = (timestamp) => {
    // Ensure timestamp is a Date object
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
    // Handle invalid dates
    if (isNaN(date.getTime())) {
      return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleMicPress = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('🎤 Mic button pressed, type:', e.type);
    
    // Prevent any focus changes that might trigger mobile keyboard
    if (e.target && typeof e.target.blur === 'function') {
      e.target.blur();
    }
    
    // Prevent document focus and text selection
    if (typeof document !== 'undefined') {
      const activeElement = document.activeElement;
      if (activeElement && activeElement !== e.target && typeof activeElement.blur === 'function') {
        activeElement.blur();
      }
    }
    
    console.log('🎯 Mic state check - isBotSpeaking:', isBotSpeaking, 'isRecording:', isRecording, 'isLoading:', isLoading);
    
    // BARGE-IN FEATURE: If bot is speaking, immediately interrupt and start recording
    if (isBotSpeaking) {
      console.log('🔀 Barge-in detected: Interrupting bot speech and starting recording');
      
      // Immediately stop all audio playback
      stopAudio();
      
      // Stop any TTS that might be playing
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        audioRef.current.src = '';
      }
      
      // Clear bot speaking state
      setIsBotSpeaking(false);
      setIsPlaying(false);
      
      // Seamlessly switch to recording mode (no acknowledgment needed)
      startRecording();
      return;
    }
    
    // Normal mic button behavior when bot is not speaking
    if (!isRecording && !isLoading) {
      console.log('▶️ Starting normal recording');
      startRecording();
    } else {
      console.log('⏸️ Cannot start recording - isRecording:', isRecording, 'isLoading:', isLoading);
    }
  };

  const handleMicRelease = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('🛑 Mic button released, type:', e.type);
    
    console.log('⏹️ Recording state check - isRecording:', isRecording);
    if (isRecording) {
      console.log('🔴 Stopping recording...');
      stopRecording();
    } else {
      console.log('ℹ️ Not recording, nothing to stop');
    }
  };

  // Handle keyboard interactions
  const handleMicKeyDown = (e) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handleMicPress(e);
    }
  };

  const handleMicKeyUp = (e) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handleMicRelease(e);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Dynamic background based on bot speaking
  const getBackgroundClass = () => {
    const base = darkMode 
      ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900'
      : 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50';
    
    if (isBotSpeaking) {
      return darkMode 
        ? 'bg-gradient-to-br from-purple-900 via-pink-900 to-orange-900'
        : 'bg-gradient-to-br from-yellow-100 via-orange-100 to-pink-100';
    }
    
    return base;
  };

  return (
    <div className={`h-full ${getBackgroundClass()} transition-all duration-1000`}>
      {/* Full Height Chat Interface - No more split panel layout */}
      <div className="h-full flex flex-col">
        
        {/* Header */}
        <div className={`flex-shrink-0 p-4 border-b ${darkMode ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-50'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ChatBubbleLeftEllipsisIcon className={`w-6 h-6 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
              <h3 className="text-lg font-semibold">Chat with Buddy 🤖</h3>
              
              {/* Recording Status Indicator */}
              {isRecording && (
                <motion.div 
                  className="flex items-center space-x-2 text-red-500"
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm font-medium">Recording {recordingTimer}s</span>
                </motion.div>
              )}
              
              {/* Bot Speaking Indicator */}
              {isBotSpeaking && (
                <motion.div 
                  className="flex items-center space-x-2 text-blue-500"
                  animate={{ opacity: [1, 0.7, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                >
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-sm font-medium">Speaking...</span>
                </motion.div>
              )}
            </div>
            
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2 rounded-full transition-colors ${
                darkMode ? 'bg-gray-700 text-yellow-400 hover:bg-gray-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {darkMode ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Messages Area - Full Height */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              {/* Animated Bot Avatar - Smaller and Centered */}
              <motion.div
                className={`mx-auto w-32 h-32 rounded-full flex items-center justify-center mb-6 ${
                  darkMode ? 'bg-gradient-to-br from-blue-600 to-purple-700' : 'bg-gradient-to-br from-blue-500 to-purple-600'
                }`}
                animate={{
                  scale: isBotSpeaking ? [1, 1.05, 1] : [1, 1.02, 1],
                }}
                transition={{
                  scale: { duration: 2, repeat: Infinity, ease: "easeInOut" },
                }}
              >
                {/* Eyes */}
                <div className="flex space-x-4">
                  <motion.div 
                    className="w-4 h-8 bg-white rounded-full"
                    animate={{
                      scaleY: isBotSpeaking ? [1, 0.3, 1] : [1, 0.8, 1]
                    }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                  />
                  <motion.div 
                    className="w-4 h-8 bg-white rounded-full"
                    animate={{
                      scaleY: isBotSpeaking ? [1, 0.3, 1] : [1, 0.8, 1]
                    }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.1 }}
                  />
                </div>
              </motion.div>
              
              <h4 className={`text-xl font-semibold mb-2 ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                Hi {user?.name || 'there'}! 👋
              </h4>
              <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-6 text-lg`}>
                {isRecording ? `Recording ${recordingTimer}s...` : 
                 isBotSpeaking ? '🔴 Tap mic to interrupt and speak' :
                 'Press and hold the microphone button below to start talking!'}
              </p>
              
              <div className="flex flex-col space-y-2 max-w-md mx-auto">
                <p className={`text-center text-sm mb-3 ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                  Try saying:
                </p>
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className={`px-4 py-2 rounded-full text-sm text-center ${
                      darkMode 
                        ? 'bg-blue-900 text-blue-200' 
                        : 'bg-blue-50 text-blue-600'
                    }`}
                  >
                    "{suggestion}"
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className="max-w-sm">
                    <div
                      className={`px-4 py-3 rounded-2xl ${
                        message.type === 'user'
                          ? darkMode 
                            ? 'bg-gradient-to-r from-blue-600 to-purple-700 text-white'
                            : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                          : darkMode
                          ? 'bg-gray-700 text-gray-100'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.type === 'ai' && (
                          <span className="text-xl">🤖</span>
                        )}
                        {message.type === 'user' && (
                          <span className="text-xl">👶</span>
                        )}
                        <p className="text-sm leading-relaxed">{message.content}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between mt-1 px-2">
                      <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        {formatTime(message.timestamp)}
                      </span>
                      
                      {message.audioData && (
                        <button
                          onClick={() => playAudio(message.audioData)}
                          className={`p-1 rounded transition-colors ${
                            darkMode 
                              ? 'text-blue-400 hover:text-blue-300 hover:bg-gray-700' 
                              : 'text-blue-500 hover:text-blue-600 hover:bg-blue-50'
                          }`}
                        >
                          <SpeakerWaveIcon className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
          
          {/* Loading Animation */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className={`px-4 py-3 rounded-2xl ${
                darkMode ? 'bg-gray-700' : 'bg-gray-100'
              }`}>
                <div className="flex items-center space-x-2">
                  <span className="text-xl">🤖</span>
                  <div className="flex space-x-1">
                    <div className={`w-2 h-2 rounded-full animate-bounce ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    }`}></div>
                    <div className={`w-2 h-2 rounded-full animate-bounce ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    }`} style={{ animationDelay: '0.1s' }}></div>
                    <div className={`w-2 h-2 rounded-full animate-bounce ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    }`} style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Thinking...
                  </span>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Voice-Only Interface - No Text Input */}
        <div className={`flex-shrink-0 border-t ${darkMode ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-50'}`}>
          
          {/* Large Centered Microphone Button - Voice Only */}
          <div className="px-4 py-8">
            <div className="flex flex-col items-center">
              <motion.button
                onMouseDown={handleMicPress}
                onMouseUp={handleMicRelease}
                onMouseLeave={handleMicRelease}
                onTouchStart={handleMicPress}
                onTouchEnd={handleMicRelease}
                onTouchCancel={handleMicRelease}
                onContextMenu={(e) => e.preventDefault()}
                className={`relative w-24 h-24 rounded-full transition-all duration-200 select-none shadow-lg flex items-center justify-center touch-manipulation z-50 ${
                  isRecording 
                    ? 'bg-gradient-to-br from-red-500 to-red-600 text-white scale-110 shadow-red-500/50' 
                    : isBotSpeaking
                    ? 'bg-gradient-to-br from-orange-500 to-orange-600 text-white animate-pulse shadow-orange-500/50'
                    : darkMode
                    ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white hover:from-blue-500 hover:to-blue-600 shadow-blue-600/30'
                    : 'bg-gradient-to-br from-blue-500 to-blue-600 text-white hover:from-blue-400 hover:to-blue-500 shadow-blue-500/30'
                } ${isLoading ? 'opacity-50' : ''}`}
                disabled={isLoading}
                type="button"
                tabIndex="-1"
                aria-label="Press and hold to record voice message"
                style={{ 
                  WebkitUserSelect: 'none',
                  WebkitTouchCallout: 'none',
                  WebkitTapHighlightColor: 'transparent',
                  touchAction: 'manipulation',
                  userSelect: 'none',
                  outline: 'none',
                  position: 'relative',
                  zIndex: 50
                }}
                whileHover={{ scale: isLoading ? 1 : 1.05 }}
                whileTap={{ scale: isLoading ? 1 : 0.95 }}
                animate={{
                  boxShadow: isRecording 
                    ? ['0 0 0 0 rgba(239, 68, 68, 0.4)', '0 0 0 30px rgba(239, 68, 68, 0)', '0 0 0 0 rgba(239, 68, 68, 0.4)']
                    : ['0 0 0 0 rgba(59, 130, 246, 0.3)', '0 0 0 15px rgba(59, 130, 246, 0)', '0 0 0 0 rgba(59, 130, 246, 0.3)']
                }}
                transition={{
                  boxShadow: { duration: isRecording ? 1 : 2, repeat: Infinity, ease: "easeOut" }
                }}
              >
                {isRecording ? (
                  <div className="flex flex-col items-center justify-center">
                    <StopIcon className="w-10 h-10 mb-1" />
                    <span className="text-sm font-bold">{recordingTimer}s</span>
                  </div>
                ) : (
                  <MicrophoneIcon className="w-10 h-10" />
                )}
                
                {/* Enhanced Pulsing Animation Ring */}
                <AnimatePresence>
                  {!isLoading && (
                    <motion.div
                      className={`absolute inset-0 rounded-full border-4 ${
                        isRecording ? 'border-red-300' : 'border-blue-300'
                      }`}
                      initial={{ scale: 1, opacity: 0.8 }}
                      animate={{ scale: 2, opacity: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ 
                        duration: isRecording ? 1 : 2, 
                        repeat: Infinity, 
                        ease: "easeOut" 
                      }}
                    />
                  )}
                </AnimatePresence>
              </motion.button>
              
              {/* Voice-Only Instructions */}
              <div className="text-center mt-4">
                <p className={`text-lg font-medium mb-2 ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                  {isRecording 
                    ? `🎤 Recording ${recordingTimer}s - Release to send` 
                    : isBotSpeaking
                    ? '🔴 Tap to interrupt and speak'
                    : '🎤 Press and hold to speak'}
                </p>
                <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  {!isRecording && !isBotSpeaking && 'Voice-only AI companion - just speak naturally!'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimplifiedChatInterface;