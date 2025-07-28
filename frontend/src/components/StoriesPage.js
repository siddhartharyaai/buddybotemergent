import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BookOpenIcon,
  PlayIcon,
  HeartIcon,
  ClockIcon,
  UserIcon,
  SpeakerWaveIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import toast from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const StoriesPage = ({ user, sessionId }) => {
  const [stories, setStories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [favorites, setFavorites] = useState([]);
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);

  const categories = [
    { id: 'all', name: 'All Stories', emoji: '📚' },
    { id: 'fairy_tales', name: 'Fairy Tales', emoji: '🧚' },
    { id: 'adventures', name: 'Adventures', emoji: '🗺️' },
    { id: 'animals', name: 'Animals', emoji: '🐾' },
    { id: 'educational', name: 'Educational', emoji: '🎓' },
    { id: 'bedtime', name: 'Bedtime', emoji: '🌙' }
  ];

  useEffect(() => {
    fetchStories();
    loadFavorites();
  }, [user?.id]);

  const fetchStories = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/content/stories`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStories(data.stories || []);
      } else {
        throw new Error('Failed to fetch stories');
      }
    } catch (error) {
      console.error('Error fetching stories:', error);
      toast.error('Failed to load stories');
      // Set some default stories for demo
      setStories([
        {
          id: '1',
          title: 'The Little Red Riding Hood',
          description: 'A classic tale of a girl visiting her grandmother',
          category: 'fairy_tales',
          duration: '5 min',
          age_group: '3-8',
          content: `Once upon a time, there was a little girl who lived in a village near the forest. She always wore a red riding cloak, so everyone called her Little Red Riding Hood.

One day, her mother said, "Little Red Riding Hood, take this basket of food to your grandmother. She lives in the cottage in the forest, and she's feeling unwell."

Little Red Riding Hood set off through the forest. Along the way, she met a big, bad wolf. "Where are you going, little girl?" asked the wolf with a sly smile.

"I'm going to my grandmother's cottage to bring her some food," said Little Red Riding Hood innocently.

The wolf had a wicked plan. He ran ahead to the grandmother's cottage and knocked on the door. When the grandmother opened it, he swallowed her up in one gulp! Then he put on her nightgown and cap and got into her bed.

When Little Red Riding Hood arrived, she noticed something strange. "Oh grandmother," she said, "what big eyes you have!"

"All the better to see you with," replied the wolf.

"And grandmother, what big ears you have!"

"All the better to hear you with."

"And grandmother, what big teeth you have!"

"All the better to eat you with!" roared the wolf, jumping out of bed.

Just then, a huntsman who was passing by heard the commotion. He burst into the cottage and saved Little Red Riding Hood and her grandmother.

From that day on, Little Red Riding Hood always stayed on the path and never talked to strangers in the forest.

The End.`
        },
        {
          id: '2',
          title: 'The Three Little Pigs',
          description: 'Three pigs build houses to protect themselves from the big bad wolf',
          category: 'fairy_tales',
          duration: '6 min',
          age_group: '3-7',
          content: `Once upon a time, there were three little pigs who decided to build their own houses.

The first little pig was lazy and built his house out of straw. It was quick and easy, but not very strong.

The second little pig built his house out of sticks. It was a bit stronger than straw, but still not very sturdy.

The third little pig worked hard all day and built his house out of bricks. It was strong and solid.

One day, a big bad wolf came to the first pig's house. "Little pig, little pig, let me come in!" he called.

"Not by the hair on my chinny-chin-chin!" replied the first pig.

"Then I'll huff, and I'll puff, and I'll blow your house in!" The wolf blew down the straw house easily, and the first pig ran to his brother's stick house.

The wolf followed and said, "Little pigs, little pigs, let me come in!"

"Not by the hair on our chinny-chin-chins!"

"Then I'll huff, and I'll puff, and I'll blow your house in!" The wolf blew down the stick house too, and both pigs ran to their brother's brick house.

When the wolf reached the brick house, he huffed and puffed with all his might, but the house was too strong. He couldn't blow it down!

The wolf tried to climb down the chimney, but the clever third pig had a pot of boiling water ready. The wolf fell into the pot and ran away, never to bother the three little pigs again.

The first two pigs learned their lesson and built strong brick houses too.

The End.`
        },
        {
          id: '3',
          title: 'The Tortoise and the Hare',
          description: 'A classic fable about perseverance and determination',
          category: 'educational',
          duration: '4 min',
          age_group: '4-10',
          content: `Once upon a time, in a peaceful meadow, there lived a speedy hare and a slow-moving tortoise.

The hare was very proud of how fast he could run. He would often boast to all the other animals, "I'm the fastest animal in the whole forest! No one can beat me in a race!"

One day, the tortoise, who was tired of listening to the hare's bragging, said quietly, "I challenge you to a race."

All the animals laughed. "You want to race the hare?" they giggled. "But you're so slow!"

The hare laughed the loudest. "This will be the easiest race I've ever won!" he said.

The fox offered to be the judge, and all the animals gathered to watch the race. The fox marked the starting line and the finish line, which was on the other side of the meadow.

"Ready, set, go!" called the fox.

The hare zoomed off like lightning, leaving the tortoise far behind. Soon, the hare was so far ahead that he couldn't even see the tortoise anymore.

"This is too easy," thought the hare. "I have plenty of time. I think I'll take a little nap under this shady tree."

The hare curled up under the tree and fell fast asleep.

Meanwhile, the tortoise kept moving slowly but steadily. Step by step, he made his way across the meadow. He passed the sleeping hare and continued toward the finish line.

When the hare woke up, the sun was setting. He stretched and yawned, then remembered the race. He looked toward the finish line and couldn't believe his eyes. There was the tortoise, just steps away from winning!

The hare ran as fast as he could, but it was too late. The tortoise crossed the finish line first!

All the animals cheered for the tortoise. The hare learned an important lesson that day: "Slow and steady wins the race."

The End.`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFavorites = () => {
    const savedFavorites = localStorage.getItem(`favorites_${user?.id}`);
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  };

  const toggleFavorite = (storyId) => {
    const newFavorites = favorites.includes(storyId)
      ? favorites.filter(id => id !== storyId)
      : [...favorites, storyId];
    
    setFavorites(newFavorites);
    localStorage.setItem(`favorites_${user?.id}`, JSON.stringify(newFavorites));
    
    toast.success(
      favorites.includes(storyId) ? 'Removed from favorites' : 'Added to favorites'
    );
  };

  const playStory = async (story) => {
    try {
      setCurrentlyPlaying(story.id);
      
      const response = await fetch(`${BACKEND_URL}/api/conversations/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: user?.id,
          message: `Please tell me the story "${story.title}" in full detail with good storytelling pace and engaging narration.`,
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.response_audio) {
          // Play the audio
          const audioBlob = new Blob(
            [Uint8Array.from(atob(data.response_audio), c => c.charCodeAt(0))], 
            { type: 'audio/wav' }
          );
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          
          audio.play();
          toast.success(`Playing: ${story.title}`);
          
          audio.onended = () => {
            setCurrentlyPlaying(null);
            URL.revokeObjectURL(audioUrl);
          };
        } else {
          toast.error('Story audio not available');
          setCurrentlyPlaying(null);
        }
      }
    } catch (error) {
      console.error('Error playing story:', error);
      toast.error('Failed to play story');
      setCurrentlyPlaying(null);
    }
  };

  const filteredStories = selectedCategory === 'all' 
    ? stories 
    : stories.filter(story => story.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <BookOpenIcon className="w-12 h-12 text-purple-600 mr-3" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Story Time
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            Discover magical stories tailored just for you, {user?.name}! 📚✨
          </p>
        </motion.div>

        {/* Category Filter */}
        <div className="flex flex-wrap justify-center gap-3 mb-8">
          {categories.map((category) => (
            <motion.button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-full font-medium transition-all duration-200 ${
                selectedCategory === category.id
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-purple-50 border border-gray-200'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="mr-2">{category.emoji}</span>
              {category.name}
            </motion.button>
          ))}
        </div>

        {/* Stories Grid */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading magical stories...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredStories.map((story) => (
              <motion.div
                key={story.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">
                        {story.title}
                      </h3>
                      <p className="text-gray-600 text-sm mb-4">
                        {story.description}
                      </p>
                    </div>
                    
                    <button
                      onClick={() => toggleFavorite(story.id)}
                      className="p-2 rounded-full hover:bg-gray-100 transition-colors"
                    >
                      {favorites.includes(story.id) ? (
                        <HeartSolidIcon className="w-6 h-6 text-red-500" />
                      ) : (
                        <HeartIcon className="w-6 h-6 text-gray-400" />
                      )}
                    </button>
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <div className="flex items-center">
                      <ClockIcon className="w-4 h-4 mr-1" />
                      {story.duration}
                    </div>
                    <div className="flex items-center">
                      <UserIcon className="w-4 h-4 mr-1" />
                      Ages {story.age_group}
                    </div>
                  </div>

                  <motion.button
                    onClick={() => playStory(story)}
                    disabled={currentlyPlaying === story.id}
                    className={`w-full py-3 rounded-xl font-medium flex items-center justify-center transition-all duration-200 ${
                      currentlyPlaying === story.id
                        ? 'bg-gray-400 text-white cursor-not-allowed'
                        : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 shadow-lg hover:shadow-xl'
                    }`}
                    whileHover={{ scale: currentlyPlaying === story.id ? 1 : 1.02 }}
                    whileTap={{ scale: currentlyPlaying === story.id ? 1 : 0.98 }}
                  >
                    {currentlyPlaying === story.id ? (
                      <>
                        <SpeakerWaveIcon className="w-5 h-5 mr-2 animate-pulse" />
                        Playing...
                      </>
                    ) : (
                      <>
                        <PlayIcon className="w-5 h-5 mr-2" />
                        Listen to Story
                      </>
                    )}
                  </motion.button>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {filteredStories.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <BookOpenIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No stories found</h3>
            <p className="text-gray-500">Try selecting a different category</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StoriesPage;