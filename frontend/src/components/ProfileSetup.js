import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import toast from 'react-hot-toast';
import { 
  UserCircleIcon, 
  MapPinIcon, 
  LanguageIcon,
  MicrophoneIcon,
  HeartIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const schema = yup.object().shape({
  name: yup.string().required('Name is required').min(2, 'Name must be at least 2 characters'),
  age: yup.number().required('Age is required').min(3, 'Age must be at least 3').max(12, 'Age must be at most 12'),
  gender: yup.string().required('Gender is required'),
  location: yup.string().required('Location is required'),
  timezone: yup.string().required('Timezone is required'),
  avatar: yup.string().required('Avatar is required'),
  voice_personality: yup.string().required('Voice personality is required'),
  speech_speed: yup.string().required('Speech speed is required'),
  energy_level: yup.string().required('Energy level is required'),
  language: yup.string().required('Language is required'),
  interests: yup.array().min(1, 'Please select at least one interest'),
  learning_goals: yup.array().min(1, 'Please select at least one learning goal'),
  parent_email: yup.string().email('Invalid email').required('Parent email is required'),
});

const ProfileSetup = ({ isOpen, onClose, onSave, initialData = null }) => {
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { register, handleSubmit, formState: { errors }, watch, setValue, getValues } = useForm({
    resolver: yupResolver(schema),
    defaultValues: initialData || {
      name: '',
      age: 5,
      gender: 'prefer_not_to_say',
      location: '',
      timezone: 'UTC',
      avatar: 'bunny',
      voice_personality: 'friendly_companion',
      speech_speed: 'normal',
      energy_level: 'balanced',
      language: 'english',
      interests: [],
      learning_goals: [],
      parent_email: ''
    }
  });

  const watchedInterests = watch('interests') || [];
  const watchedLearningGoals = watch('learning_goals') || [];
  
  const voicePersonalities = [
    {
      id: 'friendly_companion',
      name: 'Friendly Companion',
      description: 'Warm and encouraging for daily conversations',
      color: 'bg-blue-500'
    },
    {
      id: 'story_narrator',
      name: 'Story Narrator',
      description: 'Engaging voice for bedtime stories',
      color: 'bg-purple-500'
    },
    {
      id: 'learning_buddy',
      name: 'Learning Buddy',
      description: 'Patient teacher for educational content',
      color: 'bg-green-500'
    }
  ];
  
  const interestOptions = [
    { id: 'animals', name: 'Animals', emoji: '🐾' },
    { id: 'stories', name: 'Stories', emoji: '📚' },
    { id: 'music', name: 'Music', emoji: '🎵' },
    { id: 'science', name: 'Science', emoji: '🔬' },
    { id: 'art', name: 'Art', emoji: '🎨' },
    { id: 'sports', name: 'Sports', emoji: '⚽' },
    { id: 'games', name: 'Games', emoji: '🎮' },
    { id: 'nature', name: 'Nature', emoji: '🌱' },
    { id: 'space', name: 'Space', emoji: '🚀' },
    { id: 'dinosaurs', name: 'Dinosaurs', emoji: '🦕' },
    { id: 'cooking', name: 'Cooking', emoji: '👨‍🍳' },
    { id: 'dancing', name: 'Dancing', emoji: '💃' },
  ];

  const avatarOptions = [
    { id: 'bunny', name: 'Bunny', emoji: '🐰' },
    { id: 'lion', name: 'Lion', emoji: '🦁' },
    { id: 'puppy', name: 'Puppy', emoji: '🐶' },
    { id: 'robot', name: 'Robot', emoji: '🤖' },
    { id: 'unicorn', name: 'Unicorn', emoji: '🦄' },
    { id: 'dragon', name: 'Dragon', emoji: '🐉' },
  ];

  const genderOptions = [
    { id: 'boy', name: 'Boy', emoji: '👦' },
    { id: 'girl', name: 'Girl', emoji: '👧' },
    { id: 'prefer_not_to_say', name: 'Prefer not to say', emoji: '😊' },
  ];

  const speechSpeedOptions = [
    { id: 'slow', name: 'Slow', description: 'Calm and clear' },
    { id: 'normal', name: 'Normal', description: 'Regular pace' },
    { id: 'fast', name: 'Fast', description: 'Quick and energetic' },
  ];

  const energyLevelOptions = [
    { id: 'calm', name: 'Calm', description: 'Peaceful and soothing', emoji: '😌' },
    { id: 'balanced', name: 'Balanced', description: 'Just right energy', emoji: '😊' },
    { id: 'hyper', name: 'Hyper', description: 'Exciting and energetic', emoji: '🤗' },
  ];

  const languageOptions = [
    { id: 'english', name: 'English', description: 'Standard English' },
    { id: 'hinglish', name: 'Hinglish', description: 'English with Hindi words' },
  ];

  const learningGoalOptions = [
    { id: 'reading', name: 'Reading', emoji: '📖' },
    { id: 'math', name: 'Math', emoji: '🔢' },
    { id: 'daily_habits', name: 'Daily Habits', emoji: '🗓️' },
    { id: 'social_skills', name: 'Social Skills', emoji: '👥' },
    { id: 'manners', name: 'Manners', emoji: '🤝' },
    { id: 'emotional_learning', name: 'Emotional Learning', emoji: '❤️' },
    { id: 'creativity', name: 'Creativity', emoji: '🎨' },
    { id: 'problem_solving', name: 'Problem Solving', emoji: '🧩' },
  ];

  const handleInterestToggle = (interestId) => {
    const currentInterests = getValues('interests') || [];
    const newInterests = currentInterests.includes(interestId)
      ? currentInterests.filter(id => id !== interestId)
      : [...currentInterests, interestId];
    setValue('interests', newInterests);
  };

  const handleLearningGoalToggle = (goalId) => {
    const currentGoals = getValues('learning_goals') || [];
    const newGoals = currentGoals.includes(goalId)
      ? currentGoals.filter(id => id !== goalId)
      : [...currentGoals, goalId];
    setValue('learning_goals', newGoals);
  };

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      await onSave(data);
      toast.success('Profile saved successfully!');
      onClose();
    } catch (error) {
      toast.error('Failed to save profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          {/* Header */}
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {initialData ? 'Edit Profile' : 'Create Profile'}
                </h2>
                <p className="text-gray-600">Step {step} of 3</p>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                initial={{ width: '33%' }}
                animate={{ width: `${(step / 3) * 100}%` }}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="p-6">
            {/* Step 1: Basic Information */}
            {step === 1 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="text-center">
                  <UserCircleIcon className="w-16 h-16 text-blue-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900">Basic Information</h3>
                  <p className="text-gray-600">Tell us about yourself</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      What's your name?
                    </label>
                    <input
                      {...register('name')}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                      placeholder="Enter your name"
                    />
                    {errors.name && (
                      <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      How old are you?
                    </label>
                    <input
                      {...register('age')}
                      type="number"
                      min="3"
                      max="12"
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                      placeholder="Enter your age"
                    />
                    {errors.age && (
                      <p className="text-red-500 text-sm mt-1">{errors.age.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Where are you from?
                    </label>
                    <input
                      {...register('location')}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                      placeholder="Enter your location"
                    />
                    {errors.location && (
                      <p className="text-red-500 text-sm mt-1">{errors.location.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Parent's Email
                    </label>
                    <input
                      {...register('parent_email')}
                      type="email"
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                      placeholder="parent@example.com"
                    />
                    {errors.parent_email && (
                      <p className="text-red-500 text-sm mt-1">{errors.parent_email.message}</p>
                    )}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Step 2: Voice & Preferences */}
            {step === 2 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="text-center">
                  <MicrophoneIcon className="w-16 h-16 text-purple-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900">Voice Personality</h3>
                  <p className="text-gray-600">Choose how I should sound</p>
                </div>

                <div className="space-y-3">
                  {voicePersonalities.map((personality) => (
                    <label key={personality.id} className="block">
                      <input
                        {...register('voice_personality')}
                        type="radio"
                        value={personality.id}
                        className="sr-only"
                      />
                      <div className="flex items-center p-4 border rounded-xl cursor-pointer hover:bg-gray-50 transition-colors">
                        <div className={`w-4 h-4 rounded-full ${personality.color} mr-4`} />
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{personality.name}</h4>
                          <p className="text-sm text-gray-600">{personality.description}</p>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Step 3: Interests */}
            {step === 3 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="text-center">
                  <HeartIcon className="w-16 h-16 text-pink-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900">What do you love?</h3>
                  <p className="text-gray-600">Select your interests</p>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {interestOptions.map((interest) => (
                    <motion.button
                      key={interest.id}
                      type="button"
                      onClick={() => handleInterestToggle(interest.id)}
                      className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                        watchedInterests.includes(interest.id)
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300 text-gray-700'
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <div className="text-2xl mb-2">{interest.emoji}</div>
                      <div className="text-sm font-medium">{interest.name}</div>
                      {watchedInterests.includes(interest.id) && (
                        <CheckCircleIcon className="w-5 h-5 text-blue-500 mx-auto mt-1" />
                      )}
                    </motion.button>
                  ))}
                </div>

                {errors.interests && (
                  <p className="text-red-500 text-sm text-center">{errors.interests.message}</p>
                )}
              </motion.div>
            )}

            {/* Footer */}
            <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-100">
              <div>
                {step > 1 && (
                  <button
                    type="button"
                    onClick={prevStep}
                    className="px-6 py-3 text-gray-600 hover:text-gray-800 font-medium transition-colors"
                  >
                    Previous
                  </button>
                )}
              </div>
              
              <div>
                {step < 3 ? (
                  <button
                    type="button"
                    onClick={nextStep}
                    className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    Next
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? 'Saving...' : 'Save Profile'}
                  </button>
                )}
              </div>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ProfileSetup;