import React, { useState, useEffect, useRef } from 'react';
import {
  Typography,
  Box,
  TextField,
  Button,
  Avatar,
  Chip,
  Card,
  CardContent,
  Dialog,
  DialogContent,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  Quiz,
  Lightbulb,
  School,
  Science,
  Calculate,
  History as HistoryIcon
} from '@mui/icons-material';

interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  type?: 'text' | 'quiz' | 'recommendation';
  metadata?: any;
}

interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

interface TutorSuggestion {
  title: string;
  description: string;
  icon: React.ReactNode;
  prompt: string;
  category: string;
}

const AITutor: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: "Hello! I'm your AI Personal Tutor. I'm here to help you learn and understand any topic you're curious about. What would you like to explore today?",
      sender: 'ai',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [activeQuiz, setActiveQuiz] = useState<QuizQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [quizDialogOpen, setQuizDialogOpen] = useState(false);
  const [error, setError] = useState('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestions: TutorSuggestion[] = [
    {
      title: "Explain a Math Concept",
      description: "Get clear explanations for mathematical problems",
      icon: <Calculate color="primary" />,
      prompt: "Can you explain how to solve quadratic equations?",
      category: "Mathematics"
    },
    {
      title: "Science Questions",
      description: "Ask about physics, chemistry, or biology",
      icon: <Science color="secondary" />,
      prompt: "How does photosynthesis work?",
      category: "Science"
    },
    {
      title: "Historical Events",
      description: "Learn about historical events and figures",
      icon: <HistoryIcon color="warning" />,
      prompt: "Tell me about the causes of World War I",
      category: "History"
    },
    {
      title: "Study Tips",
      description: "Get personalized study strategies",
      icon: <School color="success" />,
      prompt: "What are some effective study techniques for memorization?",
      category: "Study Skills"
    },
    {
      title: "Generate Quiz",
      description: "Create practice questions on any topic",
      icon: <Quiz color="error" />,
      prompt: "Create a quiz about basic algebra",
      category: "Practice"
    },
    {
      title: "Problem Solving",
      description: "Step-by-step problem solving help",
      icon: <Lightbulb color="info" />,
      prompt: "Can you help me solve this step by step?",
      category: "Problem Solving"
    }
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async (messageContent?: string) => {
    const content = messageContent || currentMessage.trim();
    if (!content) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsTyping(true);
    setShowSuggestions(false);

    try {
      // Simulate API call to AI tutor
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate processing time
      
      let aiResponse: ChatMessage;
      
      // Check if user is asking for a quiz
      if (content.toLowerCase().includes('quiz') || content.toLowerCase().includes('test me')) {
        // Generate a sample quiz
        const sampleQuiz: QuizQuestion[] = [
          {
            id: '1',
            question: 'What is the capital of France?',
            options: ['London', 'Berlin', 'Paris', 'Madrid'],
            correct_answer: 'Paris',
            explanation: 'Paris is the capital and most populous city of France.'
          },
          {
            id: '2',
            question: 'What is 2 + 2?',
            options: ['3', '4', '5', '6'],
            correct_answer: '4',
            explanation: 'Two plus two equals four in basic arithmetic.'
          }
        ];
        
        setActiveQuiz(sampleQuiz);
        setQuizDialogOpen(true);
        
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: "I've created a practice quiz for you! Click on the quiz dialog to start. The quiz covers the topic we discussed.",
          sender: 'ai',
          timestamp: new Date(),
          type: 'quiz'
        };
      } else {
        // Generate contextual response based on the question
        let responseContent = '';
        
        if (content.toLowerCase().includes('math') || content.toLowerCase().includes('algebra')) {
          responseContent = `Great question about mathematics! Let me help you understand this concept step by step:

1. **Identify the problem type**: First, we need to recognize what kind of mathematical problem we're dealing with.

2. **Apply the right method**: Each type of problem has specific approaches and formulas.

3. **Work through examples**: Let's practice with a concrete example to make it clearer.

Would you like me to create a practice problem for you to work through together?`;
        } else if (content.toLowerCase().includes('science') || content.toLowerCase().includes('physics')) {
          responseContent = `Excellent science question! Let me break this down in a way that's easy to understand:

**Key Concepts:**
- Scientific principles work through observable patterns
- We can understand complex phenomena by breaking them into simpler parts
- Real-world applications help us see why this matters

I'd be happy to explain this topic in more detail or provide some hands-on examples. What specific aspect interests you most?`;
        } else if (content.toLowerCase().includes('history')) {
          responseContent = `That's a fascinating historical topic! Understanding history helps us learn from the past:

**Context is Key:**
- Historical events don't happen in isolation
- Multiple factors often contribute to major changes
- Different perspectives help us understand the full picture

**Why This Matters:**
- Historical patterns can help us understand current events
- Learning about different cultures and time periods broadens our worldview

Would you like me to dive deeper into a specific aspect or time period?`;
        } else {
          responseContent = `I understand you're asking about "${content}". Let me help you with that!

This is a great question that touches on several important concepts. Here's how I'd approach explaining this:

**Main Points:**
- Let's start with the fundamentals
- Build understanding step by step
- Connect it to things you already know
- Practice with examples

Is there a particular aspect you'd like me to focus on? I can adjust my explanation based on what you find most challenging or interesting.`;
        }
        
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: responseContent,
          sender: 'ai',
          timestamp: new Date(),
          type: 'text'
        };
      }
      
      setMessages(prev => [...prev, aiResponse]);
      
    } catch (err) {
      setError('Failed to get response from AI tutor. Please try again.');
      console.error('Error sending message:', err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion: TutorSuggestion) => {
    sendMessage(suggestion.prompt);
  };

  const submitQuizAnswer = () => {
    if (!selectedAnswer || activeQuiz.length === 0) return;

    const currentQuestion = activeQuiz[currentQuestionIndex];
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;

    // Add quiz result message
    const resultMessage: ChatMessage = {
      id: Date.now().toString(),
      content: isCorrect 
        ? `✅ Correct! ${currentQuestion.explanation}`
        : `❌ Not quite. The correct answer is "${currentQuestion.correct_answer}". ${currentQuestion.explanation}`,
      sender: 'ai',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, resultMessage]);

    // Move to next question or end quiz
    if (currentQuestionIndex < activeQuiz.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setSelectedAnswer('');
    } else {
      // Quiz completed
      setQuizDialogOpen(false);
      setActiveQuiz([]);
      setCurrentQuestionIndex(0);
      
      const completionMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "Great job completing the quiz! 🎉 You're making excellent progress. Would you like to try another quiz or explore a different topic?",
        sender: 'ai',
        timestamp: new Date(),
        type: 'text'
      };
      
      setTimeout(() => {
        setMessages(prev => [...prev, completionMessage]);
      }, 1000);
    }
  };

  const MessageBubble = ({ message }: { message: ChatMessage }) => (
    <Box
      display="flex"
      justifyContent={message.sender === 'user' ? 'flex-end' : 'flex-start'}
      mb={3}
    >
      <Box
        display="flex"
        alignItems="flex-start"
        maxWidth="75%"
        flexDirection={message.sender === 'user' ? 'row-reverse' : 'row'}
        gap={2}
      >
        <Avatar sx={{ 
          bgcolor: message.sender === 'user' ? 'transparent' : 'transparent',
          background: message.sender === 'user' 
            ? 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
            : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          width: 36,
          height: 36,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        }}>
          {message.sender === 'user' ? <Person /> : <SmartToy />}
        </Avatar>
        
        <Card
          sx={{
            maxWidth: '100%',
            background: message.sender === 'user' 
              ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
              : 'white',
            color: message.sender === 'user' ? 'white' : '#1e293b',
            borderRadius: 3,
            boxShadow: message.sender === 'user'
              ? '0 4px 12px rgba(99, 102, 241, 0.3)'
              : '0 2px 8px rgba(0, 0, 0, 0.1)',
            border: message.sender === 'user' ? 'none' : '1px solid #e2e8f0'
          }}
        >
          <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
            <Typography 
              variant="body1" 
              sx={{ 
                whiteSpace: 'pre-wrap',
                lineHeight: 1.6,
                fontSize: '0.95rem'
              }}
            >
              {message.content}
            </Typography>
            <Typography 
              variant="caption" 
              sx={{ 
                opacity: 0.8,
                display: 'block', 
                mt: 1,
                color: message.sender === 'user' ? 'rgba(255,255,255,0.8)' : '#64748b',
                fontSize: '0.75rem'
              }}
            >
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700, color: '#1e293b' }}>
          🤖 AI Tutor Chat
        </Typography>
        <Typography variant="h6" sx={{ color: '#64748b', fontWeight: 400 }}>
          Your personal learning assistant is here to help
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 3, height: '75vh' }}>
        {/* Suggestions Panel */}
        {showSuggestions && (
          <Box sx={{ width: '350px', flexShrink: 0 }}>
            <Card sx={{ height: '100%', overflow: 'hidden' }}>
              <Box sx={{ 
                p: 3, 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white'
              }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  💡 How can I help you learn?
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Choose a topic or ask me anything
                </Typography>
              </Box>
              
              <Box sx={{ p: 2, height: 'calc(100% - 120px)', overflowY: 'auto' }}>
                {suggestions.map((suggestion, index) => (
                  <Card 
                    key={index}
                    variant="outlined" 
                    sx={{ 
                      mb: 2,
                      cursor: 'pointer', 
                      transition: 'all 0.3s ease',
                      '&:hover': { 
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 12px rgba(99, 102, 241, 0.15)',
                        borderColor: '#6366f1'
                      } 
                    }}
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    <CardContent sx={{ p: 2.5 }}>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Box sx={{ 
                          p: 1.5, 
                          borderRadius: 2, 
                          backgroundColor: '#f1f5f9',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          {suggestion.icon}
                        </Box>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1e293b' }}>
                            {suggestion.title}
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#64748b', mt: 0.5 }}>
                            {suggestion.description}
                          </Typography>
                          <Chip 
                            label={suggestion.category} 
                            size="small" 
                            sx={{ 
                              mt: 1, 
                              fontSize: '0.75rem',
                              backgroundColor: '#e2e8f0',
                              color: '#475569'
                            }} 
                          />
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Card>
          </Box>
        )}

        {/* Chat Area */}
        <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* Chat Header */}
          <Box sx={{ 
            p: 3, 
            borderBottom: '1px solid #e2e8f0',
            backgroundColor: '#f8fafc'
          }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ 
                  bgcolor: 'transparent', 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  width: 40,
                  height: 40
                }}>
                  <SmartToy />
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    AI Personal Tutor
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    {isTyping ? 'Thinking...' : 'Online • Ready to help'}
                  </Typography>
                </Box>
              </Box>
              
              {!showSuggestions && (
                <Button 
                  variant="outlined" 
                  size="small"
                  onClick={() => setShowSuggestions(true)}
                  sx={{ borderRadius: 2 }}
                >
                  Show Topics
                </Button>
              )}
            </Box>
          </Box>

          {/* Messages */}
          <Box sx={{ 
            flex: 1, 
            overflow: 'auto', 
            p: 3,
            backgroundColor: '#fafafa'
          }}>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            
            {isTyping && (
              <Box display="flex" alignItems="flex-start" gap={2} mb={2}>
                <Avatar sx={{ 
                  bgcolor: 'transparent', 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  width: 36,
                  height: 36
                }}>
                  <SmartToy />
                </Avatar>
                <Card sx={{ 
                  p: 2, 
                  backgroundColor: 'white',
                  borderRadius: 2,
                  maxWidth: '70%',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {[0, 1, 2].map(i => (
                        <Box
                          key={i}
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            backgroundColor: '#6366f1',
                            animation: 'pulse 1.5s ease-in-out infinite',
                            animationDelay: `${i * 0.3}s`,
                            '@keyframes pulse': {
                              '0%, 80%, 100%': { opacity: 0.3 },
                              '40%': { opacity: 1 }
                            }
                          }}
                        />
                      ))}
                    </Box>
                    <Typography variant="body2" sx={{ color: '#64748b', fontStyle: 'italic' }}>
                      AI Tutor is crafting a response...
                    </Typography>
                  </Box>
                </Card>
              </Box>
            )}
            
            <div ref={messagesEndRef} />
          </Box>

          {/* Input Area */}
          <Box sx={{ 
            p: 3, 
            borderTop: '1px solid #e2e8f0',
            backgroundColor: 'white'
          }}>
            <Box display="flex" gap={2} alignItems="end">
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Ask me anything about learning... (Press Enter to send)"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                multiline
                maxRows={4}
                disabled={isTyping}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    backgroundColor: '#f8fafc',
                    '&:hover': {
                      backgroundColor: '#f1f5f9',
                    },
                    '&.Mui-focused': {
                      backgroundColor: 'white',
                    },
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={() => sendMessage()}
                disabled={!currentMessage.trim() || isTyping}
                sx={{ 
                  minWidth: 56,
                  height: 56,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  '&:hover': {
                    transform: 'translateY(-1px)',
                    boxShadow: '0 8px 25px rgba(99, 102, 241, 0.3)',
                  },
                }}
              >
                <Send />
              </Button>
            </Box>

            {/* Quick Actions */}
            <Box mt={2} display="flex" gap={1.5} flexWrap="wrap">
              <Chip 
                label="🧮 Math Help" 
                size="small" 
                onClick={() => sendMessage("Can you help me with a math problem?")}
                sx={{ 
                  backgroundColor: '#e0f2fe',
                  color: '#0277bd',
                  '&:hover': { backgroundColor: '#b3e5fc' }
                }}
              />
              <Chip 
                label="📚 Study Tips" 
                size="small" 
                onClick={() => sendMessage("What are some good study techniques?")}
                sx={{ 
                  backgroundColor: '#e8f5e8',
                  color: '#2e7d32',
                  '&:hover': { backgroundColor: '#c8e6c9' }
                }}
              />
              <Chip 
                label="🎯 Generate Quiz" 
                size="small" 
                onClick={() => sendMessage("Create a quiz for me")}
                sx={{ 
                  backgroundColor: '#fff3e0',
                  color: '#ef6c00',
                  '&:hover': { backgroundColor: '#ffe0b2' }
                }}
              />
              <Chip 
                label="💡 Explain Concept" 
                size="small" 
                onClick={() => sendMessage("Can you explain this concept to me?")}
                sx={{ 
                  backgroundColor: '#f3e5f5',
                  color: '#7b1fa2',
                  '&:hover': { backgroundColor: '#e1bee7' }
                }}
              />
            </Box>
          </Box>
        </Card>
      </Box>

      {/* Quiz Dialog */}
      <Dialog 
        open={quizDialogOpen} 
        onClose={() => setQuizDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, overflow: 'hidden' }
        }}
      >
        <Box sx={{ 
          p: 3, 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            🎯 Practice Quiz
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9, mt: 0.5 }}>
            Question {currentQuestionIndex + 1} of {activeQuiz.length}
          </Typography>
        </Box>
        
        <DialogContent sx={{ p: 4 }}>
          {activeQuiz.length > 0 && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ color: '#1e293b', mb: 3 }}>
                {activeQuiz[currentQuestionIndex]?.question}
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {activeQuiz[currentQuestionIndex]?.options.map((option, index) => (
                  <Card
                    key={index}
                    variant={selectedAnswer === option ? "elevation" : "outlined"}
                    sx={{ 
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      borderColor: selectedAnswer === option ? '#6366f1' : '#e2e8f0',
                      backgroundColor: selectedAnswer === option ? '#eef2ff' : 'white',
                      '&:hover': { 
                        borderColor: '#6366f1',
                        backgroundColor: selectedAnswer === option ? '#eef2ff' : '#f8fafc',
                        transform: 'translateY(-1px)'
                      }
                    }}
                    onClick={() => setSelectedAnswer(option)}
                  >
                    <CardContent sx={{ py: 2 }}>
                      <Typography sx={{ 
                        fontWeight: selectedAnswer === option ? 600 : 400,
                        color: selectedAnswer === option ? '#6366f1' : '#1e293b'
                      }}>
                        {String.fromCharCode(65 + index)}. {option}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </Box>

              <Box mt={4} display="flex" justifyContent="space-between">
                <Button 
                  onClick={() => setQuizDialogOpen(false)}
                  variant="outlined"
                  sx={{ borderRadius: 2, px: 3 }}
                >
                  Cancel Quiz
                </Button>
                <Button 
                  onClick={submitQuizAnswer}
                  variant="contained"
                  disabled={!selectedAnswer}
                  sx={{ 
                    borderRadius: 2, 
                    px: 3,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  }}
                >
                  Submit Answer →
                </Button>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>

      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
      >
        <Alert onClose={() => setError('')} severity="error" sx={{ borderRadius: 2 }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AITutor;
