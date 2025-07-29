import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MicrophoneIcon, 
  StopIcon, 
  PaperAirplaneIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  SparklesIcon,
  ChatBubbleLeftEllipsisIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import TextInput from './TextInput';

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

  const suggestions = [
    "Tell me a story",
    "Sing a song", 
    "What's a fun fact?",
    "Let's play a game",
    "Help me learn something"
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startRecording = async () => {
    try {
      console.log('🎤 Starting recording...');
      
      // Reset states
      setCurrentTranscript('');
      setRecordingTimer(0);
      
      // Detect mobile device
      const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      console.log('📱 Is mobile device:', isMobile);
      
      // Simplified audio constraints for better mobile compatibility
      const audioConstraints = isMobile ? {
        audio: {
          // Simplified constraints for mobile
          sampleRate: { ideal: 44100, min: 8000 },
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      } : {
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          latency: 0,
          volume: 1.0
        }
      };

      console.log('🔧 Audio constraints:', audioConstraints);

      // Request microphone permission with timeout
      let stream;
      try {
        console.log('🎯 Requesting microphone access...');
        stream = await Promise.race([
          navigator.mediaDevices.getUserMedia(audioConstraints),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))
        ]);
        console.log('✅ Microphone access granted');
      } catch (permissionError) {
        console.error('❌ Microphone permission error:', permissionError);
        if (permissionError.name === 'NotAllowedError') {
          toast.error('🎤 Please allow microphone access in your browser settings and try again.');
        } else if (permissionError.name === 'NotFoundError') {
          toast.error('🎤 No microphone found. Please check your device settings.');
        } else {
          toast.error('🎤 Microphone access failed. Please refresh and try again.');
        }
        return;
      }
      
      streamRef.current = stream;
      
      // Enhanced mobile-compatible MediaRecorder options
      let options = {};
      
      if (isMobile) {
        // Mobile-first approach - try most compatible formats first
        const mobileFormats = [
          'audio/webm',
          'audio/ogg',
          'audio/mp4',
          'audio/wav',
          '' // Default format
        ];
        
        for (const format of mobileFormats) {
          if (!format || MediaRecorder.isTypeSupported(format)) {
            if (format) {
              options.mimeType = format;
              console.log('📱 Using mobile format:', format);
            } else {
              console.log('📱 Using default mobile format');
            }
            break;
          }
        }
        
        // Lower bitrate for mobile stability
        options.audioBitsPerSecond = 64000;
      } else {
        // Desktop options
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          options.mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
          options.mimeType = 'audio/webm';
        }
        options.audioBitsPerSecond = 128000;
      }

      console.log('🎚️ MediaRecorder options:', options);
      
      try {
        mediaRecorderRef.current = new MediaRecorder(stream, options);
        console.log('✅ MediaRecorder created successfully');
      } catch (recorderError) {
        console.error('❌ MediaRecorder creation failed:', recorderError);
        // Fallback: try with no options
        try {
          mediaRecorderRef.current = new MediaRecorder(stream);
          console.log('✅ MediaRecorder created with default options');
        } catch (fallbackError) {
          console.error('❌ MediaRecorder fallback failed:', fallbackError);
          toast.error('🎤 Recording not supported on this device/browser');
          return;
        }
      }
      
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        console.log('📦 Data available event:', event.data.size, 'bytes');
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log('✅ Audio chunk added, total chunks:', audioChunksRef.current.length);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        console.log('🛑 Recording stopped, processing audio...');
        console.log('📊 Total chunks collected:', audioChunksRef.current.length);
        
        if (audioChunksRef.current.length === 0) {
          console.error('❌ No audio chunks collected');
          toast.error('🎤 Recording failed - no audio captured. Please try again.');
          return;
        }
        
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: mediaRecorderRef.current.mimeType || 'audio/webm'
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

      mediaRecorderRef.current.onerror = (error) => {
        console.error('❌ MediaRecorder error:', error);
        toast.error('🎤 Recording error. Please try again.');
      };

      // Start recording with frequent data collection for mobile
      const timeslice = isMobile ? 250 : 100; // More frequent on mobile
      mediaRecorderRef.current.start(timeslice);
      setIsRecording(true);
      
      console.log('🎬 Recording started with timeslice:', timeslice + 'ms');
      
      // Add a live transcript message
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
      
      console.log('✅ Recording setup complete');
      
    } catch (error) {
      console.error('💥 Start recording error:', error);
      toast.error(`🎤 Recording failed: ${error.message}`);
    }
  };

  const stopRecording = () => {
    console.log('Stopping recording...');
    
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setRecordingTimer(0);
      
      // Clear recording timer
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
      
      // Remove live recording message by filtering it from current messages
      // Since we can't modify the messages directly, we'll need to update the approach
      // For now, we'll add a cleanup mechanism in the parent component
      
      console.log('Recording stop initiated');
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    console.log('Sending voice message, blob size:', audioBlob.size, 'type:', audioBlob.type);
    
    // Enhanced mobile audio blob validation
    if (!audioBlob || audioBlob.size === 0) {
      console.error('Invalid audio blob - size:', audioBlob?.size, 'type:', audioBlob?.type);
      
      // Mobile-specific error handling
      const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      if (isMobile) {
        toast.error('Mobile recording failed. Please try holding the mic button longer and speaking clearly.');
      } else {
        toast.error('Recording failed - no audio data. Please check microphone permissions.');
      }
      return;
    }

    // Mobile browser blob size threshold
    if (audioBlob.size < 1000) {
      console.warn('Audio blob very small, might be empty recording');
      toast.error('Recording too short. Please hold the mic button and speak for at least 1 second.');
      return;
    }
    
    // Mobile-optimized base64 conversion
    const convertToBase64 = (blob) => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          try {
            // Remove data URL prefix for base64
            const base64 = reader.result.split(',')[1];
            if (!base64 || base64.length === 0) {
              reject(new Error('Base64 conversion failed'));
              return;
            }
            resolve(base64);
          } catch (error) {
            reject(error);
          }
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    };

    let audioBase64;
    try {
      audioBase64 = await convertToBase64(audioBlob);
      console.log('Base64 conversion successful, length:', audioBase64.length);
    } catch (conversionError) {
      console.error('Base64 conversion failed:', conversionError);
      toast.error('Audio processing failed. Please try again.');
      return;
    }
    
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
      // Convert audio blob to ArrayBuffer first for better handling
      const arrayBuffer = await audioBlob.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      const base64Audio = btoa(String.fromCharCode(...uint8Array));
      
      console.log('Audio converted to base64, length:', base64Audio.length);
      
      // Create form data with proper content type
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('user_id', user.id);
      formData.append('audio_base64', base64Audio);

      console.log('Sending request to voice endpoint...');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/voice/process_audio`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      console.log('Voice processing response:', data);
      
      if (response.ok && data.status === 'success') {
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
        
        toast.success('Voice message processed!');
      } else {
        throw new Error(data.detail || data.message || 'Voice processing failed');
      }
      
    } catch (error) {
      console.error('Voice message error:', error);
      toast.error(`Voice processing failed: ${error.message}`);
      
      // Add error message since we can't update existing message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'system',
        content: '❌ Voice processing failed - try again',
        timestamp: new Date()
      };
      onAddMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const sendTextMessage = async (messageText) => {
    if (!messageText || !messageText.trim() || isLoading) return;

    const messageContent = messageText.trim();
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageContent,
      isVoice: false,
      timestamp: new Date()
    };

    onAddMessage(userMessage);
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/conversations/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: user.id,
          message: messageContent
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response_text,
          audioData: data.response_audio,
          contentType: data.content_type,
          metadata: data.metadata,
          timestamp: new Date()
        };

        onAddMessage(aiMessage);
        
        // Auto-play AI response
        if (data.response_audio) {
          playAudio(data.response_audio);
        }
      } else {
        throw new Error(data.detail || 'Failed to send message');
      }
    } catch (error) {
      toast.error('Failed to send message');
      console.error('Text message error:', error);
    } finally {
      setIsLoading(false);
    }
  };

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
    
    // Prevent any focus changes that might trigger mobile keyboard
    if (e.target) {
      e.target.blur();
    }
    
    // Prevent touch events from bubbling up
    if (e.type === 'touchstart') {
      e.preventDefault();
    }
    
    console.log('Mic button pressed, isBotSpeaking:', isBotSpeaking, 'isRecording:', isRecording);
    
    // BARGE-IN FEATURE: If bot is speaking, immediately interrupt and start recording
    if (isBotSpeaking) {
      console.log('Barge-in detected: Interrupting bot speech and starting recording');
      
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
      startRecording();
    }
  };

  const handleMicRelease = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Prevent touch events from bubbling up
    if (e.type === 'touchend') {
      e.preventDefault();
    }
    
    console.log('Mic button released');
    if (isRecording) {
      stopRecording();
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
                 isBotSpeaking ? '🔴 Tap to interrupt and speak' :
                 'Start talking with the big microphone button below!'}
              </p>
              
              <div className="flex flex-col space-y-2 max-w-md mx-auto">
                {suggestions.map((suggestion, index) => (
                  <motion.button
                    key={index}
                    onClick={() => sendTextMessage(suggestion)}
                    className={`px-4 py-2 rounded-full text-sm transition-colors ${
                      darkMode 
                        ? 'bg-blue-900 text-blue-200 hover:bg-blue-800' 
                        : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {suggestion}
                  </motion.button>
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

        {/* Bottom Input Area with Large Mic Button */}
        <div className={`flex-shrink-0 border-t ${darkMode ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-50'}`}>
          
          {/* Text Input Row */}
          <div className="px-4 py-3">
            <div className="flex items-center space-x-3">
              <div className="flex-1">
                <TextInput 
                  onSendMessage={sendTextMessage} 
                  isLoading={isLoading}
                  darkMode={darkMode}
                />
              </div>
            </div>
          </div>

          {/* Large Centered Microphone Button */}
          <div className="px-4 pb-6 pt-2">
            <div className="flex flex-col items-center">
              <motion.button
                onMouseDown={handleMicPress}
                onMouseUp={handleMicRelease}
                onMouseLeave={handleMicRelease}
                onTouchStart={handleMicPress}
                onTouchEnd={handleMicRelease}
                onKeyDown={handleMicKeyDown}
                onKeyUp={handleMicKeyUp}
                className={`relative w-20 h-20 rounded-full transition-all duration-200 select-none shadow-lg flex items-center justify-center touch-manipulation ${
                  isRecording 
                    ? 'bg-gradient-to-br from-red-500 to-red-600 text-white scale-110 shadow-red-500/50' 
                    : isBotSpeaking
                    ? 'bg-gradient-to-br from-orange-500 to-orange-600 text-white animate-pulse shadow-orange-500/50'  // Barge-in mode
                    : darkMode
                    ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white hover:from-blue-500 hover:to-blue-600 shadow-blue-600/30'
                    : 'bg-gradient-to-br from-blue-500 to-blue-600 text-white hover:from-blue-400 hover:to-blue-500 shadow-blue-500/30'
                } ${isLoading ? 'opacity-50' : ''}`}
                disabled={isLoading}
                style={{ 
                  WebkitUserSelect: 'none',
                  WebkitTouchCallout: 'none',
                  WebkitTapHighlightColor: 'transparent',
                  touchAction: 'manipulation'
                }}
                whileHover={{ scale: isLoading ? 1 : 1.05 }}
                whileTap={{ scale: isLoading ? 1 : 0.95 }}
                animate={{
                  boxShadow: isRecording 
                    ? ['0 0 0 0 rgba(239, 68, 68, 0.4)', '0 0 0 20px rgba(239, 68, 68, 0)', '0 0 0 0 rgba(239, 68, 68, 0.4)']
                    : ['0 0 0 0 rgba(59, 130, 246, 0.3)', '0 0 0 10px rgba(59, 130, 246, 0)', '0 0 0 0 rgba(59, 130, 246, 0.3)']
                }}
                transition={{
                  boxShadow: { duration: isRecording ? 1 : 2, repeat: Infinity, ease: "easeOut" }
                }}
              >
                {isRecording ? (
                  <div className="flex flex-col items-center justify-center">
                    <StopIcon className="w-8 h-8 mb-1" />
                    <span className="text-xs font-bold">{recordingTimer}s</span>
                  </div>
                ) : (
                  <MicrophoneIcon className="w-8 h-8" />
                )}
                
                {/* Pulsing Animation Ring */}
                <AnimatePresence>
                  {!isLoading && (
                    <motion.div
                      className={`absolute inset-0 rounded-full border-2 ${
                        isRecording ? 'border-red-300' : 'border-blue-300'
                      }`}
                      initial={{ scale: 1, opacity: 0.6 }}
                      animate={{ scale: 1.8, opacity: 0 }}
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
              
              {/* Instructions */}
              <p className={`text-center text-sm mt-3 font-medium ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                {isRecording 
                  ? `🎤 Recording ${recordingTimer}s - Release to send` 
                  : '🎤 Press and hold to speak'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimplifiedChatInterface;