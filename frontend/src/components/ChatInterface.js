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
  EyeIcon,
  EyeSlashIcon,
  SunIcon,
  MoonIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const ChatInterface = ({ user, darkMode, setDarkMode, sessionId, onSendMessage }) => {
  const [isAmbientListening, setIsAmbientListening] = useState(false);
  const [isConversationActive, setIsConversationActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [listeningState, setListeningState] = useState('inactive'); // inactive, ambient, active
  const [wakeWordDetected, setWakeWordDetected] = useState(false);
  const [isBotSpeaking, setIsBotSpeaking] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [botMood, setBotMood] = useState('friendly'); // friendly, excited, calm, thinking
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  const audioRef = useRef(null);
  const ambientRecorderRef = useRef(null);
  const ambientIntervalRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Start ambient listening when component mounts
    startAmbientListening();
    
    // Cleanup on unmount
    return () => {
      stopAmbientListening();
      if (ambientIntervalRef.current) {
        clearInterval(ambientIntervalRef.current);
      }
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startAmbientListening = async () => {
    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Start ambient listening on server
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ambient/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: user.id
        })
      });

      if (response.ok) {
        setIsAmbientListening(true);
        setListeningState('ambient');
        
        // Start continuous audio processing
        startContinuousAudioProcessing(stream);
        
        toast.success('Always listening! Say "Hey Buddy" to start chatting.');
      } else {
        throw new Error('Failed to start ambient listening');
      }
    } catch (error) {
      console.error('Error starting ambient listening:', error);
      toast.error('Microphone access required for voice features');
    }
  };

  const stopAmbientListening = async () => {
    try {
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ambient/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      setIsAmbientListening(false);
      setIsConversationActive(false);
      setListeningState('inactive');
      
      // Stop audio processing
      if (ambientRecorderRef.current) {
        ambientRecorderRef.current.stop();
      }
      
      if (ambientIntervalRef.current) {
        clearInterval(ambientIntervalRef.current);
      }
    } catch (error) {
      console.error('Error stopping ambient listening:', error);
    }
  };

  const startContinuousAudioProcessing = (stream) => {
    const mediaRecorder = new MediaRecorder(stream);
    ambientRecorderRef.current = mediaRecorder;
    
    let audioChunks = [];
    
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      await processAmbientAudio(audioBlob);
      audioChunks = [];
      
      // Continue recording if still in ambient listening mode
      if (isAmbientListening && mediaRecorder.state === 'inactive') {
        setTimeout(() => {
          if (isAmbientListening) {
            mediaRecorder.start();
          }
        }, 100);
      }
    };
    
    // Start recording in chunks
    mediaRecorder.start();
    
    // Process audio every 2 seconds
    ambientIntervalRef.current = setInterval(() => {
      if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        setTimeout(() => {
          if (isAmbientListening) {
            mediaRecorder.start();
          }
        }, 100);
      }
    }, 2000);
  };

  const processAmbientAudio = async (audioBlob) => {
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = reader.result.split(',')[1];
        
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ambient/process`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            audio_base64: base64Audio
          })
        });

        const data = await response.json();
        
        if (response.ok) {
          handleAmbientResponse(data);
        }
      };
      
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error('Error processing ambient audio:', error);
    }
  };

  const handleAmbientResponse = (data) => {
    const { status, transcript, listening_state, conversation_response, has_response } = data;
    
    // Update listening state
    setListeningState(listening_state);
    
    if (status === 'wake_word_detected') {
      setWakeWordDetected(true);
      setIsConversationActive(true);
      
      // Add wake word message
      const wakeWordMessage = {
        id: Date.now(),
        type: 'system',
        content: `Wake word detected: "${transcript}"`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, wakeWordMessage]);
      
      // Add AI response if available
      if (has_response && conversation_response) {
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: conversation_response.response_text,
          audioData: conversation_response.response_audio,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        
        // Play audio response
        if (conversation_response.response_audio) {
          playAudio(conversation_response.response_audio);
        }
      }
      
      // Clear wake word detection after 3 seconds
      setTimeout(() => setWakeWordDetected(false), 3000);
      
    } else if (status === 'conversation_active' && has_response) {
      // Add user message
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: transcript,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: conversation_response.response_text,
        audioData: conversation_response.response_audio,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Play audio response
      if (conversation_response.response_audio) {
        playAudio(conversation_response.response_audio);
      }
      
    } else if (status === 'conversation_ended' || status === 'conversation_timeout') {
      setIsConversationActive(false);
      
      const endMessage = {
        id: Date.now(),
        type: 'system',
        content: status === 'conversation_timeout' ? 'Conversation timed out. Say "Hey Buddy" to start again.' : 'Conversation ended. Say "Hey Buddy" to start again.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, endMessage]);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        sendVoiceMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      toast.error('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64Audio = reader.result.split(',')[1];
      
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: 'Voice message',
        isVoice: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/conversations/voice`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            user_id: user.id,
            audio_base64: base64Audio
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

          setMessages(prev => [...prev, aiMessage]);
          
          // Auto-play AI response
          if (data.response_audio) {
            playAudio(data.response_audio);
          }
        } else {
          throw new Error(data.detail || 'Failed to send voice message');
        }
      } catch (error) {
        toast.error('Failed to send voice message');
        console.error('Voice message error:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    reader.readAsDataURL(audioBlob);
  };

  const sendTextMessage = async (e) => {
    e.preventDefault();
    if (!textInput.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: textInput,
      isVoice: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setTextInput('');
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
          message: textInput
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

        setMessages(prev => [...prev, aiMessage]);
        
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
    
    audioRef.current.onended = () => {
      setIsPlaying(false);
      URL.revokeObjectURL(audioUrl);
    };
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getListeningStateDisplay = () => {
    switch (listeningState) {
      case 'ambient':
        return {
          text: 'Always Listening',
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          icon: EyeIcon
        };
      case 'active':
        return {
          text: 'Conversation Active',
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          icon: MicrophoneIcon
        };
      default:
        return {
          text: 'Not Listening',
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          icon: EyeSlashIcon
        };
    }
  };

  const suggestions = [
    "Tell me a story",
    "Sing a song",
    "What's a fun fact?",
    "Let's play a game",
    "Help me learn something"
  ];

  const listeningDisplay = getListeningStateDisplay();
  const ListeningIcon = listeningDisplay.icon;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex-shrink-0 p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">AI Buddy</h2>
              <p className="text-sm text-gray-600">Your smart companion</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Listening Status */}
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${listeningDisplay.bgColor}`}>
              <ListeningIcon className={`w-4 h-4 ${listeningDisplay.color}`} />
              <span className={`text-sm font-medium ${listeningDisplay.color}`}>
                {listeningDisplay.text}
              </span>
              {wakeWordDetected && (
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-2"></div>
              )}
            </div>
            
            {/* Audio Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={isAmbientListening ? stopAmbientListening : startAmbientListening}
                className={`p-2 rounded-full transition-colors ${
                  isAmbientListening ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'
                }`}
              >
                {isAmbientListening ? <EyeSlashIcon className="w-5 h-5" /> : <EyeIcon className="w-5 h-5" />}
              </button>
              
              <button
                onClick={isPlaying ? stopAudio : null}
                className={`p-2 rounded-full transition-colors ${
                  isPlaying ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-400'
                }`}
                disabled={!isPlaying}
              >
                {isPlaying ? <SpeakerXMarkIcon className="w-5 h-5" /> : <SpeakerWaveIcon className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <ChatBubbleLeftEllipsisIcon className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">I'm always listening!</h3>
            <p className="text-gray-600 mb-2">Say <strong>"Hey Buddy"</strong> to start chatting</p>
            <p className="text-gray-600 mb-6">Or try typing one of these:</p>
            
            <div className="flex flex-wrap justify-center gap-2">
              {suggestions.map((suggestion, index) => (
                <motion.button
                  key={index}
                  onClick={() => setTextInput(suggestion)}
                  className="px-4 py-2 bg-blue-50 text-blue-600 rounded-full text-sm hover:bg-blue-100 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
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
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                      : message.type === 'system'
                      ? 'bg-yellow-50 text-yellow-800 border border-yellow-200'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    {message.type === 'ai' && (
                      <SparklesIcon className="w-4 h-4 text-blue-500" />
                    )}
                    <p className="text-sm">{message.content}</p>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className={`text-xs ${
                      message.type === 'user' ? 'text-blue-100' : 
                      message.type === 'system' ? 'text-yellow-600' : 'text-gray-500'
                    }`}>
                      {formatTime(message.timestamp)}
                    </span>
                    
                    {message.audioData && (
                      <button
                        onClick={() => playAudio(message.audioData)}
                        className="p-1 text-blue-500 hover:text-blue-600 transition-colors"
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
        
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-gray-100 rounded-2xl px-4 py-3 max-w-xs">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-600">Thinking...</span>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 p-6 bg-white border-t border-gray-100">
        <form onSubmit={sendTextMessage} className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Type a message or say 'Hey Buddy'..."
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!textInput.trim() || isLoading}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-blue-500 hover:text-blue-600 disabled:text-gray-400 transition-colors"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
          
          <motion.button
            type="button"
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-4 rounded-full transition-all duration-200 ${
              isRecording
                ? 'bg-red-500 text-white shadow-lg scale-110'
                : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 shadow-lg hover:shadow-xl'
            }`}
            whileHover={{ scale: isRecording ? 1.1 : 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={isLoading}
          >
            {isRecording ? (
              <StopIcon className="w-6 h-6" />
            ) : (
              <MicrophoneIcon className="w-6 h-6" />
            )}
          </motion.button>
        </form>
        
        {isRecording && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 text-center"
          >
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-red-50 text-red-600 rounded-full">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Recording...</span>
            </div>
          </motion.div>
        )}
        
        {wakeWordDetected && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 text-center"
          >
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-green-50 text-green-600 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Wake word detected!</span>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;