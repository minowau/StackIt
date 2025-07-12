import React, { useState, useEffect } from 'react';
import { Search, Bell, User, Plus, ChevronUp, ChevronDown, Check, Eye, MessageSquare, Calendar, Tag, Bold, Italic, Underline, List, ListOrdered, Link, Image, AlignLeft, AlignCenter, AlignRight, Smile, X, Edit, Trash2, LogOut, Settings } from 'lucide-react';
import axios from 'axios';

const App = () => {
  // State management
  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState('home');
  const [questions, setQuestions] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);

  // Mock data
  const mockUsers = [
    { id: 1, username: 'john_doe', email: 'john@example.com', role: 'user', avatar: '👨‍💻' },
    { id: 2, username: 'jane_smith', email: 'jane@example.com', role: 'admin', avatar: '👩‍💼' },
    { id: 3, username: 'alex_dev', email: 'alex@example.com', role: 'user', avatar: '👨‍🎨' }
  ];

  const mockQuestions = [
    {
      id: 1,
      title: "How to implement JWT authentication in React?",
      description: "I'm trying to implement JWT authentication in my React application. What's the best practice for storing tokens and handling authentication state?",
      author: mockUsers[0],
      tags: ['React', 'JWT', 'Authentication'],
      votes: 15,
      answers: 3,
      views: 127,
      createdAt: '2025-01-10',
      answers: [
        {
          id: 1,
          content: "You can store JWT tokens in memory or httpOnly cookies. Here's a comprehensive approach:\n\n1. Store tokens in memory for security\n2. Use refresh tokens for persistence\n3. Implement auto-logout on token expiry",
          author: mockUsers[1],
          votes: 8,
          isAccepted: true,
          createdAt: '2025-01-10'
        },
        {
          id: 2,
          content: "I'd recommend using a state management library like Redux or Context API to handle authentication state globally.",
          author: mockUsers[2],
          votes: 3,
          isAccepted: false,
          createdAt: '2025-01-11'
        }
      ]
    },
    {
      id: 2,
      title: "Best practices for responsive design in 2025?",
      description: "What are the current best practices for creating responsive websites? Should I use CSS Grid, Flexbox, or a combination?",
      author: mockUsers[2],
      tags: ['CSS', 'Responsive', 'Design'],
      votes: 8,
      answers: 2,
      views: 89,
      createdAt: '2025-01-09',
      answers: []
    }
  ];

  const mockNotifications = [
    { id: 1, type: 'answer', message: 'Jane Smith answered your question about JWT authentication', time: '2 hours ago', read: false },
    { id: 2, type: 'mention', message: 'Alex Dev mentioned you in a comment', time: '1 day ago', read: false },
    { id: 3, type: 'vote', message: 'Your answer received 5 upvotes', time: '2 days ago', read: true }
  ];

  const availableTags = ['React', 'JavaScript', 'CSS', 'HTML', 'Node.js', 'Python', 'JWT', 'Authentication', 'Design', 'Responsive'];

  // Initialize data
// useEffect(() => {
//   const fetchData = async () => {
//     try {
//       const questionsRes = await axios.get('http://localhost:5000/api/questions'); // Replace with your real API
//       const notificationsRes = await axios.get('http://localhost:5000/api/notifications');

//       setQuestions(questionsRes.data);
//       setNotifications(notificationsRes.data);
//     } catch (error) {
//       console.error("API failed, falling back to mock data:", error);
//       setQuestions(mockQuestions);
//       setNotifications(mockNotifications);
//     }
//   };

//   fetchData();
// }, []);

  // Authentication functions
  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:5000/api/auth/login', {
        username,
        password
      });

      const { access_token, refresh_token, user } = response.data;

      // Store tokens securely (localStorage or secure cookie)
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      console.log(access_token)
      // Optionally store user info (if needed)
      localStorage.setItem('user', JSON.stringify(user));

      // Set user in app state
      setCurrentUser(user);

      // Set default authorization header for future axios requests
      // axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      return { success: true };
    } catch (error) {
      console.error('Login failed:', error.response?.data?.error || error.message);
      return { success: false, error: error.response?.data?.error || 'Login failed' };
    }
  };

  const logout = () => {
    setCurrentUser(null);
    setCurrentView('home');
  };

  const register = async (username, email, password) => {
    try {
      const response = await axios.post('http://localhost:5000/api/auth/register', {
        username,
        email,
        password
      });

      const newUser = response.data;
      setCurrentUser(newUser); // Assuming this sets the logged-in user in state
      return true;
    } catch (error) {
      console.error('Registration failed:', error.response?.data?.error || error.message);
      return false;
    }
  };

  // Rich Text Editor Component
  const RichTextEditor = ({ content, onChange, placeholder = "Write your content here..." }) => {
    const [editorContent, setEditorContent] = useState(content || '');
    const [showEmojiPicker, setShowEmojiPicker] = useState(false);

    const emojis = ['😀', '😊', '😍', '🤔', '😎', '🔥', '👍', '👎', '❤', '💯'];

    const handleFormatting = (command, value = null) => {
      document.execCommand(command, false, value);
    };

    const insertEmoji = (emoji) => {
      const newContent = editorContent + emoji;
      setEditorContent(newContent);
      onChange(newContent);
      setShowEmojiPicker(false);
    };

    return (
      <div className="border rounded-lg overflow-hidden">
        {/* Toolbar */}
        <div className="bg-gray-50 border-b p-2 flex flex-wrap gap-1">
          <button onClick={() => handleFormatting('bold')} className="p-2 hover:bg-gray-200 rounded">
            <Bold size={16} />
          </button>
          <button onClick={() => handleFormatting('italic')} className="p-2 hover:bg-gray-200 rounded">
            <Italic size={16} />
          </button>
          <button onClick={() => handleFormatting('underline')} className="p-2 hover:bg-gray-200 rounded">
            <Underline size={16} />
          </button>
          <div className="w-px bg-gray-300 mx-1"></div>
          <button onClick={() => handleFormatting('insertUnorderedList')} className="p-2 hover:bg-gray-200 rounded">
            <List size={16} />
          </button>
          <button onClick={() => handleFormatting('insertOrderedList')} className="p-2 hover:bg-gray-200 rounded">
            <ListOrdered size={16} />
          </button>
          <div className="w-px bg-gray-300 mx-1"></div>
          <button onClick={() => handleFormatting('justifyLeft')} className="p-2 hover:bg-gray-200 rounded">
            <AlignLeft size={16} />
          </button>
          <button onClick={() => handleFormatting('justifyCenter')} className="p-2 hover:bg-gray-200 rounded">
            <AlignCenter size={16} />
          </button>
          <button onClick={() => handleFormatting('justifyRight')} className="p-2 hover:bg-gray-200 rounded">
            <AlignRight size={16} />
          </button>
          <div className="w-px bg-gray-300 mx-1"></div>
          <button onClick={() => {
            const url = prompt('Enter URL:');
            if (url) handleFormatting('createLink', url);
          }} className="p-2 hover:bg-gray-200 rounded">
            <Link size={16} />
          </button>
          <div className="relative">
            <button onClick={() => setShowEmojiPicker(!showEmojiPicker)} className="p-2 hover:bg-gray-200 rounded">
              <Smile size={16} />
            </button>
            {showEmojiPicker && (
              <div className="absolute top-full left-0 mt-1 bg-white border rounded-lg shadow-lg p-2 z-10">
                <div className="grid grid-cols-5 gap-1">
                  {emojis.map((emoji, index) => (
                    <button
                      key={index}
                      onClick={() => insertEmoji(emoji)}
                      className="p-1 hover:bg-gray-100 rounded text-lg"
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Editor Content */}
        <div
          contentEditable
          className="p-4 min-h-32 focus:outline-none"
          onInput={(e) => {
            const content = e.target.innerHTML;
            setEditorContent(content);
            onChange(content);
          }}
          dangerouslySetInnerHTML={{ __html: editorContent }}
          style={{ minHeight: '120px' }}
        />
      </div>
    );
  };

  // Login Component
  const LoginForm = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({ username: '', email: '', password: '' });

    const handleSubmit = () => {
      if (isLogin) {
        login(formData.username, formData.password);
      } else {
        register(formData.username, formData.email, formData.password);
      }
    };

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
          <h2 className="text-3xl font-bold text-center mb-6 text-gray-800">
            {isLogin ? 'Sign In' : 'Sign Up'} to StackIt
          </h2>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Username"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            {!isLogin && (
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            )}
            <input
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <button
              onClick={handleSubmit}
              className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {isLogin ? 'Sign In' : 'Sign Up'}
            </button>
          </div>
          <p className="text-center mt-4 text-gray-600">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 hover:underline font-medium"
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
          <div className="mt-6 pt-4 border-t text-center text-sm text-gray-500">
            <p>Demo credentials:</p>
            <p><strong>Username:</strong> john_doe <strong>Password:</strong> any</p>
          </div>
        </div>
      </div>
    );
  };

  // Ask Question Form
  const AskQuestionForm = () => {
    const [questionData, setQuestionData] = useState({
      title: '',
      description: '',
      tags: []
    });
    const [tagInput, setTagInput] = useState('');

    const addTag = (tag) => {
      if (tag && !questionData.tags.includes(tag)) {
        setQuestionData({...questionData, tags: [...questionData.tags, tag]});
      }
      setTagInput('');
    };

    const removeTag = (tagToRemove) => {
      setQuestionData({
        ...questionData,
        tags: questionData.tags.filter(tag => tag !== tagToRemove)
      });
    };

    const submitQuestion = async () => {
      if (questionData.title && questionData.description && questionData.tags.length > 0) {
        try {
          const token = localStorage.getItem('token'); // Assuming token is stored here after login

          const response = await axios.post(
            'http://localhost:5000/api/questions',
            {
              title: questionData.title,
              description: questionData.description,
              tags: questionData.tags
            },
            {
              headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
          );

          const newQuestion = response.data;

          setQuestions([newQuestion, ...questions]); // Add the new question to state
          setCurrentView('home'); // Navigate back to home
        } catch (error) {
          console.error('Error posting question:', error.response?.data?.error || error.message);
          alert('Failed to post question. Please try again.');
        }
      } else {
        alert('Please fill all required fields.');
      }
    };

    return (
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Ask a Question</h1>
        <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input
              type="text"
              value={questionData.title}
              onChange={(e) => setQuestionData({...questionData, title: e.target.value})}
              placeholder="What's your programming question? Be specific."
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <RichTextEditor
              content={questionData.description}
              onChange={(content) => setQuestionData({...questionData, description: content})}
              placeholder="Provide more details about your question. Include what you've tried and any error messages."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
            <div className="flex flex-wrap gap-2 mb-3">
              {questionData.tags.map((tag, index) => (
                <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center gap-1">
                  {tag}
                  <button onClick={() => removeTag(tag)} className="hover:text-blue-600">
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addTag(tagInput)}
                placeholder="Add tags (press Enter)"
                className="flex-1 p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="mt-2 flex flex-wrap gap-1">
              {availableTags.filter(tag => !questionData.tags.includes(tag)).map((tag, index) => (
                <button
                  key={index}
                  onClick={() => addTag(tag)}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded transition-colors"
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={submitQuestion}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Post Question
            </button>
            <button
              onClick={() => setCurrentView('home')}
              className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Question Card Component
  const QuestionCard = ({ question }) => {
    const [userVote, setUserVote] = useState(0);

    const handleVote = (voteType) => {
      if (!currentUser) return;
      
      let newVote = 0;
      if (voteType === 'up' && userVote !== 1) newVote = 1;
      else if (voteType === 'down' && userVote !== -1) newVote = -1;
      
      setUserVote(newVote);
    };

    return (
      <div 
        className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-l-blue-500"
        onClick={() => {
          setSelectedQuestion(question);
          setCurrentView('question');
        }}
      >
        <div className="flex gap-4">
          <div className="flex flex-col items-center space-y-2 min-w-0">
            <div className="text-center">
              <div className="text-lg font-bold text-gray-700">{question.votes + userVote}</div>
              <div className="text-xs text-gray-500">votes</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">{question.answers?.length || 0}</div>
              <div className="text-xs text-gray-500">answers</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-gray-500">{question.views}</div>
              <div className="text-xs text-gray-500">views</div>
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-semibold text-gray-800 mb-2 hover:text-blue-600">
              {question.title}
            </h3>
            <div className="text-gray-600 mb-3 line-clamp-2">
              <div dangerouslySetInnerHTML={{ __html: question.description.slice(0, 150) + '...' }} />
            </div>
            <div className="flex flex-wrap gap-2 mb-3">
              {question.tags.map((tag, index) => (
                <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                  {tag}
                </span>
              ))}
            </div>
            <div className="flex items-center justify-between text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <span className="text-lg">{question.author.avatar}</span>
                <span>{question.author.username}</span>
                <span>•</span>
                <span>{question.createdAt}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Question Detail View
  const QuestionDetail = ({ question }) => {
    const [newAnswer, setNewAnswer] = useState('');
    const [answers, setAnswers] = useState(question.answers || []);

  const submitAnswer = async () => {
    if (newAnswer && currentUser) {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.post(
          `http://localhost:5000/api/questions/${question.id}/answers`,
          { content: newAnswer },
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );

        const createdAnswer = response.data;
        setAnswers([...answers, createdAnswer]);
        setNewAnswer('');
      } catch (error) {
        console.error('Failed to post answer:', error.response?.data?.error || error.message);
        alert('Failed to submit answer.');
      }
    }
  };


  const voteAnswer = async (answerId, voteType) => {
    try {
      const token = localStorage.getItem('access_token');

      const response = await axios.post(
        `http://localhost:5000/api/answers/${answerId}/vote`,
        { vote: voteType },  // "up", "down", or "remove"
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const { vote_score } = response.data;

      // Update the vote count in state
      setAnswers(prevAnswers =>
        prevAnswers.map(ans =>
          ans.id === answerId ? { ...ans, votes: vote_score } : ans
        )
      );
    } catch (error) {
      console.error('Vote failed:', error.response?.data?.error || error.message);
      alert('Vote could not be registered.');
    }
  };


  const acceptAnswer = async (answerId) => {
    if (currentUser.id === question.author.id) {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.post(
          `http://localhost:5000/api/answers/${answerId}/accept`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        // Update UI: mark accepted answer
        setAnswers(answers.map(ans => ({
          ...ans,
          isAccepted: ans.id === answerId
        })));
      } catch (error) {
        console.error('Failed to accept answer:', error.response?.data?.error || error.message);
        alert('Could not accept the answer.');
      }
    }
  };
  //   useEffect(() => {
  //   const fetchAnswers = async () => {
  //     try {
  //       const response = await axios.get(`http://localhost:5000/api/questions/${question.id}/answers`);
  //       setAnswers(response.data);
  //     } catch (err) {
  //       console.error("Failed to load answers:", err);
  //     }
  //   };

  //   fetchAnswers();
  // }, [question.id]);

    return (
      <div className="max-w-4xl mx-auto p-6">
        <button
          onClick={() => setCurrentView('home')}
          className="mb-4 text-blue-600 hover:text-blue-800 font-medium"
        >
          ← Back to Questions
        </button>

        {/* Question */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-4">{question.title}</h1>
          <div className="flex gap-4 mb-4">
            <div className="flex flex-col items-center space-y-2">
              <button className="p-1 hover:bg-gray-100 rounded">
                <ChevronUp size={24} className="text-gray-600" />
              </button>
              <span className="text-xl font-bold">{question.votes}</span>
              <button className="p-1 hover:bg-gray-100 rounded">
                <ChevronDown size={24} className="text-gray-600" />
              </button>
            </div>
            <div className="flex-1">
              <div className="prose max-w-none mb-4">
                <div dangerouslySetInnerHTML={{ __html: question.description }} />
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                {question.tags.map((tag, index) => (
                  <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center gap-2">
                  <Eye size={16} />
                  <span>{question.views} views</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg">{question.author.avatar}</span>
                  <span>{question.author.username}</span>
                  <span>•</span>
                  <span>{question.createdAt}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Answers */}
        <div className="space-y-4 mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {answers.length} {answers.length === 1 ? 'Answer' : 'Answers'}
          </h2>
        {answers.map((answer) => (
          <div
            key={answer.id}
            className={`bg-white rounded-lg shadow-md p-6 ${
              answer.isAccepted ? 'border-l-4 border-l-green-500' : ''
            }`}
          >
            <div className="flex gap-4">
              <div className="flex flex-col items-center space-y-2">
                <button onClick={() => voteAnswer(answer.id, 'up')} className="p-1 hover:bg-gray-100 rounded">
                  <ChevronUp size={20} className="text-gray-600" />
                </button>
                <span className="font-bold">{answer.votes}</span>
                <button onClick={() => voteAnswer(answer.id, 'down')} className="p-1 hover:bg-gray-100 rounded">
                  <ChevronDown size={20} className="text-gray-600" />
                </button>
                {currentUser?.id === question.author.id && !answer.isAccepted && (
                  <button
                    onClick={() => acceptAnswer(answer.id)}
                    className="p-1 hover:bg-green-100 rounded text-green-600"
                    title="Accept this answer"
                  >
                    <Check size={20} />
                  </button>
                )}
                {answer.isAccepted && (
                  <div className="p-1 bg-green-100 rounded text-green-600">
                    <Check size={20} />
                  </div>
                )}
              </div>
              <div className="flex-1">
                <div className="prose max-w-none mb-4">
                  <div dangerouslySetInnerHTML={{ __html: answer.content }} />
                </div>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    {answer.isAccepted && (
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                        ✓ Accepted Answer
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{answer.author.avatar}</span>
                    <span>{answer.author.username}</span>
                    <span>•</span>
                    <span>{answer.createdAt}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}

        </div>

        {/* Add Answer */}
        {currentUser && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Your Answer</h3>
            <RichTextEditor
              content={newAnswer}
              onChange={setNewAnswer}
              placeholder="Share your knowledge and help the community..."
            />
            <button
              onClick={submitAnswer}
              className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Post Answer
            </button>
          </div>
        )}
      </div>
    );
  };

  // Main App Layout
  const MainLayout = () => {
    const filteredQuestions = questions.filter(q => {
      const matchesSearch = searchQuery === '' || 
        q.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      
      const matchesTags = selectedTags.length === 0 || 
        selectedTags.some(tag => q.tags.includes(tag));
      
      return matchesSearch && matchesTags;
    });
      useEffect(() => {
        if (questions.length > 0) return;
        const token = localStorage.getItem('access_token'); 
        console.log(token)
        console.log("UseEffect Running");
    const fetchData = async () => {

      try {
        const questionsRes = await axios.get('http://localhost:5000/api/questions',{headers:{Authorization:`Bearer ${token}`}}); 
        const notificationsRes = await axios.get('http://localhost:5000/api/notifications',{headers:{Authorization:`Bearer ${token}`}});

        setQuestions(questionsRes.data);
        setNotifications(notificationsRes.data);
      } catch (error) {
        console.error("API failed, falling back to mock data:", error);
        setQuestions(mockQuestions);
        setNotifications(mockNotifications);
      }
    };

    fetchData();
  }, []);
    console.log("MainLayout rendered");


    const unreadCount = notifications.filter(n => !n.read).length;

    return (
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-lg border-b">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold text-blue-600 cursor-pointer" onClick={() => setCurrentView('home')}>
                  StackIt
                </h1>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    placeholder="Search questions..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setCurrentView('ask')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 font-medium"
                >
                  <Plus size={20} />
                  Ask Question
                </button>

                <div className="relative">
                  <button
                    onClick={() => setShowNotifications(!showNotifications)}
                    className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <Bell size={20} className="text-gray-600" />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                        {unreadCount}
                      </span>
                    )}
                  </button>

                  {showNotifications && (
                    <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-50">
                      <div className="p-4 border-b">
                        <h3 className="font-semibold">Notifications</h3>
                      </div>
                      <div className="max-h-96 overflow-y-auto">
                        {notifications.length === 0 ? (
                          <div className="p-4 text-gray-500 text-center">No notifications</div>
                        ) : (
                          notifications.map((notification) => (
                            <div
                              key={notification.id}
                              className={`p-4 border-b hover:bg-gray-50 ${
                                !notification.read ? 'bg-blue-50' : ''
                              }`}
                            >
                              <div className="text-sm">{notification.message}</div>
                              <div className="text-xs text-gray-500 mt-1">{notification.time}</div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  )}

                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{currentUser.avatar}</span>
                  <span className="font-medium text-gray-700">{currentUser.username}</span>
                  {currentUser.role === 'admin' && (
                    <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs font-medium">
                      Admin
                    </span>
                  )}
                  <button
                    onClick={logout}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <LogOut size={16} className="text-gray-600" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 py-6">
          {currentView === 'home' && (
            <div>
              {/* Filters */}
              <div className="mb-6">
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="text-sm font-medium text-gray-700">Filter by tags:</span>
                  {availableTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => {
                        if (selectedTags.includes(tag)) {
                          setSelectedTags(selectedTags.filter(t => t !== tag));
                        } else {
                          setSelectedTags([...selectedTags, tag]);
                        }
                      }}
                      className={`px-3 py-1 rounded-full text-sm transition-colors ${
                        selectedTags.includes(tag)
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                  {selectedTags.length > 0 && (
                    <button
                      onClick={() => setSelectedTags([])}
                      className="px-3 py-1 rounded-full text-sm bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
                    >
                      Clear filters
                    </button>
                  )}
                </div>
              </div>

              {/* Questions List */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-2xl font-bold text-gray-800">
                    {filteredQuestions.length} Questions
                  </h2>
                </div>
                
                {filteredQuestions.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-gray-500 text-lg mb-4">No questions found</div>
                    <button
                      onClick={() => setCurrentView('ask')}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Ask the first question
                    </button>
                  </div>
                ) : (
                  filteredQuestions.map((question) => (
                    <QuestionCard key={question.id} question={question} />
                  ))
                )}
              </div>
            </div>
          )}

          {currentView === 'ask' && <AskQuestionForm />}
          {currentView === 'question' && selectedQuestion && <QuestionDetail question={selectedQuestion} />}
        </div>
      </div>
    );
  };

  // Render based on authentication state
  if (!currentUser) {
    return <LoginForm />;
  }

  return <MainLayout />;
};

export default App;
