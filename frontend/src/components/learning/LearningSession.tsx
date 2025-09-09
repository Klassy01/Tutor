import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
  RadioGroup,
  FormControlLabel,
  Radio,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import { learningAPI, quizAPI, lessonAPI } from '../../services/api';
import QuizDisplay from './QuizDisplay';
import QuizResults from './QuizResults';

interface Question {
  id: string;
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
  difficulty?: number;
}

interface LessonContent {
  title: string;
  full_content?: string;
  introduction: string;
  key_concepts: string[];
  examples: Array<{
    [key: string]: any;
  }>;
}

interface LearningSessionData {
  id: string;
  session_type: 'lesson' | 'quiz' | 'practice';
  subject_area: string;
  topic: string;
  status: string;
  content?: LessonContent;
  duration_estimate?: number;
  questions?: Question[];
  total_questions?: number;
  time_limit_minutes?: number;
  questions_attempted?: number;
  questions_correct?: number;
  accuracy_rate?: number;
  duration_minutes?: number;
  started_at?: string;
  difficulty_level: number;
  created_at: string;
}

const LearningSession: React.FC = () => {
  const [sessions, setSessions] = useState<LearningSessionData[]>([]);
  const [activeSession, setActiveSession] = useState<LearningSessionData | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [currentQuestions, setCurrentQuestions] = useState<Question[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [showResults, setShowResults] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [activeQuizAttempt, setActiveQuizAttempt] = useState<any>(null);
  const [questionStartTime, setQuestionStartTime] = useState<Date | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSessionData, setNewSessionData] = useState({
    subject_area: '',
    topic: '',
    session_type: 'practice'
  });
  const [showQuizResults, setShowQuizResults] = useState(false);
  const [quizResults, setQuizResults] = useState<any>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await learningAPI.getSessions();
      
      if (response.data && Array.isArray(response.data)) {
        setSessions(response.data.map((session: any) => ({
          ...session,
          id: session.id || Date.now().toString(),
          session_type: session.session_type || 'practice',
          subject_area: session.subject_area || 'General',
          topic: session.topic || 'Mixed Topics',
          status: session.status || 'active',
          difficulty_level: session.difficulty_level || 0.5,
          created_at: session.created_at || new Date().toISOString(),
          questions_attempted: session.questions_attempted || 0,
          questions_correct: session.questions_correct || 0,
          accuracy_rate: session.accuracy_rate || 0
        })));
      } else {
        const session = response.data;
        setSessions([{
          id: session.id || Date.now().toString(),
          session_type: session.session_type || 'practice',
          subject_area: session.subject_area || 'General',
          topic: session.topic || 'Mixed Topics',
          status: session.status || 'active',
          questions_attempted: session.questions_attempted || 0,
          questions_correct: session.questions_correct || 0,
          accuracy_rate: session.accuracy_rate || 0,
          duration_minutes: session.duration_minutes || 0,
          started_at: session.started_at || new Date().toISOString(),
          difficulty_level: session.difficulty_level || 0.5,
          created_at: session.created_at || new Date().toISOString()
        }]);
      }
    } catch (err) {
      console.error('Error fetching sessions:', err);
      setSessions([
        {
          id: '1',
          session_type: 'practice',
          subject_area: 'General Knowledge',
          topic: 'Mixed Topics',
          status: 'active',
          questions_attempted: 0,
          questions_correct: 0,
          accuracy_rate: 0,
          duration_minutes: 0,
          started_at: new Date().toISOString(),
          difficulty_level: 0.5,
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      setLoading(true);
      
      let newSession: LearningSessionData;
      
      if (newSessionData.session_type === 'lesson') {
        const lessonRequest = {
          subject: newSessionData.subject_area,
          topic: newSessionData.topic,
          difficulty_level: 'medium'
        };
        
        const lessonResponse = await lessonAPI.generateLesson(lessonRequest);
        const lessonData = lessonResponse.data;
        
        newSession = {
          id: lessonData.lesson?.id || Date.now().toString(),
          subject_area: newSessionData.subject_area,
          topic: newSessionData.topic,
          session_type: 'lesson' as const,
          status: 'active',
          content: lessonData.lesson?.content ? {
            title: lessonData.lesson.title || `${newSessionData.topic} - ${newSessionData.subject_area}`,
            full_content: typeof lessonData.lesson.content === 'string' 
              ? lessonData.lesson.content
              : lessonData.lesson.content.full_content || lessonData.lesson.content.introduction || `Welcome to this comprehensive lesson on ${newSessionData.topic}.`,
            introduction: typeof lessonData.lesson.content === 'string' 
              ? lessonData.lesson.content.substring(0, 300) + '...'
              : lessonData.lesson.content.introduction || `Welcome to this comprehensive lesson on ${newSessionData.topic}.`,
            key_concepts: lessonData.lesson.key_concepts || lessonData.lesson.content.key_concepts || [
              "Foundation principles",
              "Practical applications", 
              "Problem-solving strategies"
            ],
            examples: lessonData.lesson.content.examples || [
              { "Basic Application": `How ${newSessionData.topic} applies in real-world scenarios` },
              { "Advanced Implementation": `Complex applications of ${newSessionData.topic}` }
            ]
          } : {
            title: `${newSessionData.topic} - ${newSessionData.subject_area}`,
            full_content: `Welcome to this comprehensive lesson on ${newSessionData.topic}.`,
            introduction: `Welcome to this comprehensive lesson on ${newSessionData.topic}.`,
            key_concepts: ["Foundation principles", "Practical applications", "Problem-solving strategies"],
            examples: [
              { "Basic Application": `How ${newSessionData.topic} applies in real-world scenarios` },
              { "Advanced Implementation": `Complex applications of ${newSessionData.topic}` }
            ]
          },
          duration_estimate: lessonData.lesson?.estimated_duration || 20,
          questions_attempted: 0,
          questions_correct: 0,
          accuracy_rate: 0,
          duration_minutes: 0,
          started_at: new Date().toISOString(),
          difficulty_level: 0.5,
          created_at: new Date().toISOString()
        };
        
        setSuccessMessage(`AI-powered lesson created for ${newSessionData.topic}!`);
      } else {
        const quizRequest = {
          subject: newSessionData.subject_area,
          topic: newSessionData.topic,
          difficulty_level: 'medium',
          num_questions: 4
        };
        
        const quizResponse = await quizAPI.generateQuiz(quizRequest);
        const quizData = quizResponse.data;
        
        // Handle the response structure: { success: true, quiz: { questions: [...] } }
        const questionsData = quizData.quiz?.questions || quizData.questions || [];
        
        if (!questionsData || questionsData.length === 0) {
          throw new Error('No questions generated');
        }
        
        const questions: Question[] = questionsData.map((q: any, index: number) => ({
          id: `q_${index}`,
          question: q.question,
          options: q.options || [q.option_a, q.option_b, q.option_c, q.option_d],
          correct_answer: q.correct_answer,
          explanation: q.explanation || 'No explanation available.',
          difficulty: q.difficulty_level || 0.5
        }));
        
        // Try to create learning session, but don't fail if it doesn't work
        let sessionId = Date.now().toString();
        try {
          const sessionResponse = await learningAPI.createSession({
            session_type: newSessionData.session_type,
            subject_area: newSessionData.subject_area,
            topic: newSessionData.topic
          });
          sessionId = sessionResponse.data.id || sessionId;
        } catch (sessionError) {
          console.warn('Learning session creation failed, continuing with quiz:', sessionError);
        }
        
        newSession = {
          id: sessionId,
          subject_area: newSessionData.subject_area,
          topic: newSessionData.topic,
          session_type: newSessionData.session_type as 'lesson' | 'quiz' | 'practice',
          status: 'active',
          questions_attempted: 0,
          questions_correct: 0,
          accuracy_rate: 0,
          duration_minutes: 0,
          started_at: new Date().toISOString(),
          difficulty_level: 0.5,
          created_at: new Date().toISOString()
        };
        
        setCurrentQuestions(questions);
        if (questions.length > 0) {
          setCurrentQuestion(questions[0]);
          setQuestionStartTime(new Date());
        }
        
        setSuccessMessage(`AI-powered quiz created for ${newSessionData.topic}!`);
      }
      
      setSessions(prev => [newSession, ...prev]);
      setActiveSession(newSession);
      
      setCreateDialogOpen(false);
      setNewSessionData({ subject_area: '', topic: '', session_type: 'practice' });
      
    } catch (err) {
      console.error('Error creating session:', err);
      setError('Failed to create AI-powered learning session');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = async () => {
    if (!currentQuestion || !selectedAnswer || !activeSession) return;
    
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;
    setIsCorrect(isCorrect);
    setShowResults(true);
    setExplanation(currentQuestion.explanation);
    
    const responseTime = questionStartTime 
      ? (new Date().getTime() - questionStartTime.getTime()) / 1000 
      : undefined;
    
    const updatedSession = {
      ...activeSession,
      questions_attempted: (activeSession.questions_attempted || 0) + 1,
      questions_correct: (activeSession.questions_correct || 0) + (isCorrect ? 1 : 0),
      accuracy_rate: (((activeSession.questions_correct || 0) + (isCorrect ? 1 : 0)) / ((activeSession.questions_attempted || 0) + 1)) * 100
    };
    
    setActiveSession(updatedSession);
    setSessions(prev => prev.map(session => 
      session.id === activeSession.id ? updatedSession : session
    ));
    
    try {
      if (activeQuizAttempt && activeQuizAttempt.id) {
        try {
          await quizAPI.submitQuiz({
            quiz_data: activeQuizAttempt,
            answers: { [currentQuestion.id]: selectedAnswer },
            time_spent_minutes: responseTime ? Math.round(responseTime / 60) : 1
          });
        } catch (quizError) {
          console.warn('Quiz submission failed, continuing:', quizError);
        }
      }
      
      if (activeSession.id && parseInt(activeSession.id)) {
        try {
          await learningAPI.logInteraction(parseInt(activeSession.id), {
            question_id: currentQuestion.id,
            answer: selectedAnswer,
            is_correct: isCorrect,
            time_spent: responseTime || 30
          });
        } catch (interactionError) {
          console.warn('Interaction logging failed, continuing:', interactionError);
        }
      }
    } catch (error) {
      console.error('Error in answer submission:', error);
    }
  };
  
  const handleNextQuestion = async () => {
    if (!activeSession || !currentQuestions.length) return;
    
    const currentIndex = currentQuestions.findIndex(q => q.id === currentQuestion?.id);
    
    if (currentIndex < currentQuestions.length - 1) {
      setCurrentQuestion(currentQuestions[currentIndex + 1]);
      setSelectedAnswer('');
      setShowResults(false);
      setExplanation('');
      setQuestionStartTime(new Date());
    } else {
      if (activeQuizAttempt && activeQuizAttempt.id) {
        try {
          await quizAPI.submitQuiz({
            quiz_data: activeQuizAttempt,
            answers: {},
            time_spent_minutes: Math.round((new Date().getTime() - new Date(activeSession.started_at || '').getTime()) / 60000)
          });
        } catch (error) {
          console.error('Error completing quiz attempt:', error);
        }
      }
      
      setCurrentQuestion(null);
      setActiveSession(null);
      setCurrentQuestions([]);
      setActiveQuizAttempt(null);
      setSuccessMessage('Session completed! Great job!');
    }
  };

  const startSession = async (session: LearningSessionData) => {
    const generateQuestionsForSession = async () => {
      try {
        setLoading(true);
        const quizRequest = {
          subject: session.subject_area,
          topic: session.topic,
          difficulty_level: 'medium',
          num_questions: 4
        };
        
        const quizResponse = await quizAPI.generateQuiz(quizRequest);
        const quizData = quizResponse.data;
        
        // Handle the response structure: { success: true, quiz: { questions: [...] } }
        const questionsData = quizData.quiz?.questions || quizData.questions || [];
        
        if (!questionsData || questionsData.length === 0) {
          throw new Error('No questions generated');
        }
        
        const questions: Question[] = questionsData.map((q: any, index: number) => ({
          id: `q_${index}`,
          question: q.question,
          options: q.options || [q.option_a, q.option_b, q.option_c, q.option_d],
          correct_answer: q.correct_answer,
          explanation: q.explanation || 'No explanation available.',
          difficulty: q.difficulty_level || 0.5
        }));
        
        setActiveQuizAttempt({ 
          id: quizData.quiz?.quiz_id || quizData.quiz_id || `quiz_${Date.now()}`, 
          ...quizData.quiz || quizData,
          questions: questions
        });
        setCurrentQuestions(questions);
        setActiveSession(session);
        setCurrentQuestion(questions[0]);
        setSelectedAnswer('');
        setShowResults(false);
        setExplanation('');
        setQuestionStartTime(new Date());
      } catch (error) {
        console.error('Error generating questions for session:', error);
        setError('Failed to generate quiz questions');
      } finally {
        setLoading(false);
      }
    };
    
    generateQuestionsForSession();
  };

  const handleQuizComplete = (results: any) => {
    setQuizResults(results);
    setShowQuizResults(true);
    setActiveSession(null);
    setCurrentQuestions([]);
    setCurrentQuestion(null);
    setActiveQuizAttempt(null);
  };

  const handleQuizRetake = () => {
    setShowQuizResults(false);
    setQuizResults(null);
    // Restart the quiz with the same questions
    if (activeQuizAttempt) {
      setCurrentQuestions(activeQuizAttempt.questions || []);
      setCurrentQuestion(activeQuizAttempt.questions?.[0] || null);
      setActiveSession(activeQuizAttempt);
    }
  };

  const handleQuizClose = () => {
    setShowQuizResults(false);
    setQuizResults(null);
    setActiveSession(null);
    setCurrentQuestions([]);
    setCurrentQuestion(null);
    setActiveQuizAttempt(null);
  };

  const pauseSession = async () => {
    if (!activeSession) return;
    
    try {
      const updatedSession = { ...activeSession, status: 'paused' };
      setSessions(prev => 
        prev.map(s => s.id === updatedSession.id ? updatedSession : s)
      );
      setActiveSession(null);
      setCurrentQuestion(null);
      setActiveQuizAttempt(null);
      setSuccessMessage('Session paused successfully!');
    } catch (err) {
      setError('Failed to pause session');
    }
  };

  if (loading && sessions.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: '1200px', margin: '0 auto', p: 2 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700, color: 'primary.main' }}>
          🎓 AI Learning Studio
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
          Personalized learning powered by advanced AI technology
        </Typography>
        {!activeSession && (
          <Button 
            variant="contained" 
            size="large"
            onClick={() => setCreateDialogOpen(true)}
            sx={{ 
              px: 4, 
              py: 1.5, 
              borderRadius: 3,
              background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
              boxShadow: '0 4px 20px rgba(25,118,210,0.3)',
              '&:hover': {
                background: 'linear-gradient(45deg, #1565c0, #1976d2)',
                boxShadow: '0 6px 24px rgba(25,118,210,0.4)',
              }
            }}
          >
            🚀 Start Learning Journey
          </Button>
        )}
      </Box>

      {activeSession && (
        <Paper sx={{ 
          p: 4, 
          mb: 4, 
          borderRadius: 4,
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
        }}>
          {activeSession.session_type === 'lesson' ? (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  📖 {activeSession.subject_area} - {activeSession.topic}
                </Typography>
                <Box display="flex" gap={1}>
                  <Chip 
                    label="📚 LESSON" 
                    color="info" 
                    size="medium"
                    sx={{ 
                      fontWeight: 600,
                      px: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Chip 
                    label={`⏱️ ${activeSession.duration_estimate || 20} min`} 
                    color="primary" 
                    size="medium"
                    sx={{ 
                      fontWeight: 600,
                      px: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                  />
                </Box>
              </Box>

              {activeSession.content && (
                <Card sx={{ 
                  borderRadius: 3,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                  border: '1px solid rgba(0,0,0,0.05)',
                  mb: 3
                }}>
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: 'text.primary', mb: 3 }}>
                      {activeSession.content.title}
                    </Typography>
                    
                    {/* Full Lesson Content */}
                    {activeSession.content.full_content && (
                      <Box sx={{ mb: 4 }}>
                        <Typography variant="body1" sx={{ 
                          lineHeight: 1.8, 
                          whiteSpace: 'pre-line',
                          fontSize: '1rem',
                          color: 'text.primary'
                        }}>
                          {activeSession.content.full_content}
                        </Typography>
                      </Box>
                    )}

                    <Divider sx={{ my: 3 }} />

                    {/* Key Concepts */}
                    {activeSession.content.key_concepts && activeSession.content.key_concepts.length > 0 && (
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                          🎯 Key Concepts
                        </Typography>
                        <List>
                          {activeSession.content.key_concepts.map((concept: string, index: number) => (
                            <ListItem key={index} sx={{ py: 0.5 }}>
                              <ListItemIcon>
                                <Typography variant="h6" color="primary.main">•</Typography>
                              </ListItemIcon>
                              <ListItemText primary={concept} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}

                    <Divider sx={{ my: 3 }} />

                    {/* Examples */}
                    {activeSession.content.examples && activeSession.content.examples.length > 0 && (
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                          💡 Examples
                        </Typography>
                        {activeSession.content.examples.map((example: any, index: number) => (
                          <Card key={index} sx={{ mb: 2, bgcolor: 'grey.50' }}>
                            <CardContent sx={{ p: 2 }}>
                              {Object.entries(example).map(([key, value]) => (
                                <Box key={key}>
                                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                                    {key}
                                  </Typography>
                                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                                    {value as string}
                                  </Typography>
                                </Box>
                              ))}
                            </CardContent>
                          </Card>
                        ))}
                      </Box>
                    )}

                    <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
                      <Button 
                        variant="contained" 
                        size="large"
                        onClick={() => {
                          setActiveSession(null);
                          setSuccessMessage("Lesson completed successfully! 🎉");
                        }}
                        sx={{ 
                          px: 5,
                          py: 1.5,
                          borderRadius: 3,
                          fontWeight: 600,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          fontSize: '1.1rem',
                          textTransform: 'none',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                          }
                        }}
                      >
                        ✅ Complete Lesson
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>
          ) : (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" sx={{ fontWeight: 700, color: 'warning.main' }}>
                  📝 {activeSession.subject_area} - {activeSession.topic}
                </Typography>
                <Box display="flex" gap={1}>
                  <Chip 
                    label="🧠 AI QUIZ" 
                    color="warning" 
                    size="medium"
                    sx={{ 
                      fontWeight: 600,
                      px: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Chip 
                    label={`📊 ${activeSession.questions_attempted || 0} Questions`} 
                    color="primary" 
                    size="medium"
                    sx={{ 
                      fontWeight: 600,
                      px: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Chip 
                    label={`🎯 ${(activeSession.accuracy_rate || 0).toFixed(1)}% Accuracy`} 
                    color={(activeSession.accuracy_rate || 0) >= 70 ? "success" : "warning"} 
                    size="medium"
                    sx={{ 
                      fontWeight: 600,
                      px: 2,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                  />
                </Box>
              </Box>

              <LinearProgress 
                variant="determinate" 
                value={activeSession && currentQuestions.length > 0 ? ((activeSession.questions_attempted || 0) / currentQuestions.length * 100) : 0}
                sx={{ 
                  mb: 4, 
                  height: 8, 
                  borderRadius: 4,
                  backgroundColor: 'rgba(0,0,0,0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                    background: 'linear-gradient(45deg, #00c853, #4caf50)',
                  }
                }}
              />

              {!showResults ? (
                <Card sx={{ 
                  borderRadius: 3,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                  border: '1px solid rgba(0,0,0,0.05)'
                }}>
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: 'text.primary', mb: 3 }}>
                      ❓ Question {currentQuestions.length > 0 && currentQuestion ? (currentQuestions.findIndex(q => q.id === currentQuestion.id) + 1) : 1} of {currentQuestions.length || 1}
                    </Typography>
                    <Typography variant="h6" paragraph sx={{ lineHeight: 1.6, mb: 4 }}>
                      {currentQuestion?.question || 'Loading question...'}
                    </Typography>

                    <RadioGroup 
                      value={selectedAnswer} 
                      onChange={(e) => setSelectedAnswer(e.target.value)}
                      sx={{ mb: 4 }}
                    >
                      {currentQuestion?.options.map((option, index) => (
                        <FormControlLabel
                          key={index}
                          value={option}
                          control={<Radio size="medium" />}
                          label={
                            <Typography variant="body1" sx={{ fontSize: '1.1rem', py: 1 }}>
                              {option}
                            </Typography>
                          }
                          sx={{
                            py: 1,
                            px: 2,
                            margin: '8px 0',
                            borderRadius: 2,
                            border: '1px solid transparent',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              backgroundColor: 'rgba(25,118,210,0.05)',
                              borderColor: 'rgba(25,118,210,0.2)',
                            },
                            '&.Mui-checked': {
                              backgroundColor: 'rgba(25,118,210,0.1)',
                              borderColor: 'primary.main',
                            }
                          }}
                        />
                      ))}
                    </RadioGroup>

                    <Box display="flex" gap={2}>
                      <Button 
                        variant="contained" 
                        size="large"
                        onClick={handleAnswerSubmit}
                        disabled={!selectedAnswer}
                        sx={{ 
                          px: 4,
                          py: 1.5,
                          borderRadius: 2,
                          background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
                          '&:hover': {
                            background: 'linear-gradient(45deg, #1565c0, #1976d2)',
                          },
                          '&:disabled': {
                            background: 'rgba(0,0,0,0.12)',
                          }
                        }}
                      >
                        ✓ Submit Answer
                      </Button>
                      <Button 
                        variant="outlined" 
                        size="large"
                        onClick={pauseSession}
                        sx={{ 
                          px: 3,
                          py: 1.5,
                          borderRadius: 2,
                          borderWidth: 2,
                          '&:hover': {
                            borderWidth: 2,
                          }
                        }}
                      >
                        ⏸️ Pause Session
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              ) : (
                <Card sx={{ 
                  borderRadius: 3,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                  border: '1px solid rgba(0,0,0,0.05)'
                }}>
                  <CardContent sx={{ p: 4 }}>
                    <Alert 
                      severity={isCorrect ? "success" : "error"} 
                      sx={{ 
                        mb: 3,
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        borderRadius: 2,
                        '& .MuiAlert-icon': {
                          fontSize: '1.5rem'
                        }
                      }}
                      icon={isCorrect ? '🎉' : '💡'}
                    >
                      {isCorrect ? "Excellent! Correct answer!" : "Not quite right, but great effort!"}
                    </Alert>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                        📝 Your Answer:
                      </Typography>
                      <Typography variant="body1" paragraph sx={{ 
                        p: 2, 
                        bgcolor: isCorrect ? 'success.light' : 'error.light',
                        borderRadius: 2,
                        color: 'white'
                      }}>
                        {selectedAnswer}
                      </Typography>
                    </Box>

                    {!isCorrect && (
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                          ✅ Correct Answer:
                        </Typography>
                        <Typography variant="body1" paragraph sx={{ 
                          p: 2, 
                          bgcolor: 'success.light',
                          borderRadius: 2,
                          color: 'white'
                        }}>
                          {currentQuestion?.correct_answer}
                        </Typography>
                      </Box>
                    )}

                    <Box sx={{ mb: 4 }}>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                        💡 Explanation:
                      </Typography>
                      <Typography variant="body1" sx={{ 
                        p: 3, 
                        bgcolor: 'rgba(25,118,210,0.05)',
                        borderRadius: 2,
                        lineHeight: 1.6,
                        border: '1px solid rgba(25,118,210,0.1)'
                      }}>
                        {explanation}
                      </Typography>
                    </Box>

                    <Box>
                      {activeSession && currentQuestions.length > 0 && currentQuestion && (currentQuestions.findIndex(q => q.id === currentQuestion.id) < currentQuestions.length - 1) ? (
                        <Button 
                          variant="contained" 
                          size="large"
                          onClick={handleNextQuestion}
                          sx={{ 
                            px: 4,
                            py: 1.5,
                            borderRadius: 2,
                            background: 'linear-gradient(45deg, #00c853, #4caf50)',
                            '&:hover': {
                              background: 'linear-gradient(45deg, #00a84f, #00c853)',
                            }
                          }}
                        >
                          ➡️ Next Question
                        </Button>
                      ) : (
                        <Button 
                          variant="contained" 
                          color="success" 
                          size="large"
                          onClick={handleNextQuestion}
                          sx={{ 
                            px: 4,
                            py: 1.5,
                            borderRadius: 2,
                            background: 'linear-gradient(45deg, #00c853, #4caf50)',
                            '&:hover': {
                              background: 'linear-gradient(45deg, #00a84f, #00c853)',
                            }
                          }}
                        >
                          🎉 Complete Session
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>
          )}
        </Paper>
      )}
      
      {!activeSession && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
                📚 Your Learning Sessions
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Continue your learning journey or start a new session
              </Typography>
            </Box>
          </Box>

          <Box 
            sx={{ 
              display: 'grid', 
              gridTemplateColumns: {
                xs: '1fr',
                md: 'repeat(2, 1fr)',
                lg: 'repeat(3, 1fr)'
              },
              gap: 3 
            }}
          >
            {sessions.map((session) => (
              <Card 
                key={session.id}
                sx={{ 
                  height: '100%',
                  borderRadius: 3,
                  border: session.session_type === 'lesson' ? '2px solid #2196f3' : 
                         session.session_type === 'quiz' ? '2px solid #ff9800' : '2px solid #e0e0e0',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                  transition: 'all 0.3s ease',
                  '&:hover': { 
                    transform: 'translateY(-4px)', 
                    boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
                  }
                }}
              >
                <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 3 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" noWrap sx={{ fontWeight: 700 }}>
                      {session.subject_area}
                    </Typography>
                    <Box display="flex" gap={0.5}>
                      <Chip 
                        label={session.session_type ? session.session_type.toUpperCase() : 'PRACTICE'} 
                        color={
                          session.session_type === 'lesson' ? 'info' :
                          session.session_type === 'quiz' ? 'warning' : 'default'
                        }
                        size="small"
                        sx={{ fontWeight: 600 }}
                      />
                      <Chip 
                        label={session.status} 
                        color={
                          session.status === 'completed' ? 'success' : 
                          session.status === 'active' ? 'primary' : 'default'
                        }
                        size="small"
                        sx={{ fontWeight: 600 }}
                      />
                    </Box>
                  </Box>

                  <Typography color="text.secondary" gutterBottom sx={{ fontWeight: 500 }}>
                    📖 {session.topic}
                  </Typography>

                  <Divider sx={{ my: 2 }} />

                  {session.session_type === 'lesson' ? (
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2" paragraph sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        📖 <strong>Interactive Lesson</strong> 
                      </Typography>
                      <Typography variant="body2" paragraph sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        ⏱️ <strong>Duration:</strong> ~{session.duration_estimate || 20} minutes
                      </Typography>
                      <Typography variant="body2" paragraph sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        🎯 <strong>Difficulty:</strong> {Math.round(session.difficulty_level * 100)}%
                      </Typography>
                      {session.content && (
                        <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          📋 <strong>{session.content.key_concepts?.length || 3} concepts</strong>
                        </Typography>
                      )}
                    </Box>
                  ) : (
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2" paragraph sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        📝 <strong>Questions:</strong> {session.total_questions || session.questions_attempted || 4}
                      </Typography>
                      {session.accuracy_rate ? (
                        <Typography variant="body2" paragraph sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          🎯 <strong>Accuracy:</strong> {session.accuracy_rate.toFixed(1)}%
                        </Typography>
                      ) : null}
                      <Typography variant="body2" paragraph sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        ⏱️ <strong>Time Limit:</strong> {session.time_limit_minutes || session.duration_minutes || 15} min
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        📊 <strong>Difficulty:</strong> {Math.round(session.difficulty_level * 100)}%
                      </Typography>
                    </Box>
                  )}

                  <Box mt={3}>
                    {session.status === 'active' || session.status === 'paused' ? (
                      <Button 
                        variant="contained" 
                        size="large" 
                        fullWidth
                        onClick={() => startSession(session)}
                        sx={{ 
                          py: 1.5,
                          borderRadius: 2,
                          fontWeight: 600,
                          background: session.status === 'paused' ? 
                            'linear-gradient(45deg, #ff9800, #ffb74d)' :
                            'linear-gradient(45deg, #1976d2, #42a5f5)',
                          '&:hover': {
                            background: session.status === 'paused' ? 
                              'linear-gradient(45deg, #f57c00, #ff9800)' :
                              'linear-gradient(45deg, #1565c0, #1976d2)',
                          }
                        }}
                      >
                        {session.status === 'paused' ? '▶️ Resume Session' : '🚀 Continue Learning'}
                      </Button>
                    ) : session.status === 'completed' ? (
                      <Button 
                        variant="outlined" 
                        size="large" 
                        fullWidth
                        disabled
                        sx={{ 
                          py: 1.5,
                          borderRadius: 2,
                          fontWeight: 600,
                          borderWidth: 2,
                        }}
                      >
                        ✅ Completed
                      </Button>
                    ) : (
                      <Button 
                        variant="contained" 
                        size="large" 
                        fullWidth
                        onClick={() => startSession(session)}
                        color={session.session_type === 'lesson' ? 'info' : 'warning'}
                        sx={{ 
                          py: 1.5,
                          borderRadius: 2,
                          fontWeight: 600,
                          background: session.session_type === 'lesson' ? 
                            'linear-gradient(45deg, #2196f3, #64b5f6)' :
                            'linear-gradient(45deg, #ff9800, #ffb74d)',
                          '&:hover': {
                            background: session.session_type === 'lesson' ? 
                              'linear-gradient(45deg, #1976d2, #2196f3)' :
                              'linear-gradient(45deg, #f57c00, #ff9800)',
                          }
                        }}
                      >
                        {session.session_type === 'lesson' ? '📖 Start Lesson' : '🧠 Take AI Quiz'}
                      </Button>
                    )}
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>

          {sessions.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No learning sessions yet
              </Typography>
              <Typography color="textSecondary" paragraph>
                Start your first learning session to begin your educational journey!
              </Typography>
              <Button 
                variant="contained" 
                onClick={() => setCreateDialogOpen(true)}
              >
                Create Your First Session
              </Button>
            </Paper>
          )}
        </Box>
      )}

      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
          }
        }}
      >
        <DialogTitle sx={{ 
          pb: 2,
          background: 'linear-gradient(135deg, #1976d2, #42a5f5)',
          color: 'white',
          textAlign: 'center'
        }}>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            🚀 Create AI Learning Session
          </Typography>
          <Typography variant="body1" sx={{ mt: 1, opacity: 0.9 }}>
            Generate personalized content using advanced AI models
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ p: 4 }}>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Subject Area"
              value={newSessionData.subject_area}
              onChange={(e) => setNewSessionData(prev => ({ ...prev, subject_area: e.target.value }))}
              margin="normal"
              placeholder="e.g., Mathematics, Computer Science, Physics"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />
            
            <TextField
              fullWidth
              label="Learning Topic"
              value={newSessionData.topic}
              onChange={(e) => setNewSessionData(prev => ({ ...prev, topic: e.target.value }))}
              margin="normal"
              placeholder="e.g., Linear Algebra, Machine Learning, Quantum Physics"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>Session Type</InputLabel>
              <Select
                value={newSessionData.session_type}
                onChange={(e) => setNewSessionData(prev => ({ ...prev, session_type: e.target.value }))}
                sx={{
                  borderRadius: 2,
                }}
              >
                <MenuItem value="practice">🧠 AI Practice Quiz</MenuItem>
                <MenuItem value="quiz">📝 Knowledge Assessment</MenuItem>
                <MenuItem value="review">🔄 Review & Reinforcement</MenuItem>
                <MenuItem value="lesson">📖 Interactive Lesson</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ 
              mt: 3, 
              p: 2, 
              bgcolor: 'rgba(25,118,210,0.05)', 
              borderRadius: 2,
              border: '1px solid rgba(25,118,210,0.1)'
            }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                🤖 AI-Powered Features:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Personalized content generation using Qwen Coder, Llama 3, and Mistral models<br/>
                • Adaptive difficulty based on your performance<br/>
                • Comprehensive explanations for every question<br/>
                • Real-time progress tracking and analytics
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, gap: 2 }}>
          <Button 
            onClick={() => setCreateDialogOpen(false)}
            size="large"
            sx={{ px: 3 }}
          >
            Cancel
          </Button>
          <Button 
            onClick={createNewSession} 
            variant="contained"
            size="large"
            disabled={!newSessionData.subject_area || !newSessionData.topic}
            sx={{ 
              px: 4,
              borderRadius: 2,
              background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
              '&:hover': {
                background: 'linear-gradient(45deg, #1565c0, #1976d2)',
              },
              '&:disabled': {
                background: 'rgba(0,0,0,0.12)',
              }
            }}
          >
            🎯 Generate AI Session
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={() => setSuccessMessage('')}
      >
        <Alert onClose={() => setSuccessMessage('')} severity="success">
          {successMessage}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
      >
        <Alert onClose={() => setError('')} severity="error">
          {error}
        </Alert>
      </Snackbar>

      {/* Quiz Display Overlay */}
      {activeSession && activeSession.session_type === 'quiz' && currentQuestions.length > 0 && (
        <Box sx={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          bgcolor: 'rgba(0,0,0,0.8)', 
          zIndex: 9999,
          overflow: 'auto',
          py: 2
        }}>
          <QuizDisplay
            questions={currentQuestions}
            quizId={activeQuizAttempt?.id || 'quiz_1'}
            onComplete={handleQuizComplete}
            onClose={handleQuizClose}
          />
        </Box>
      )}

      {/* Quiz Results Overlay */}
      {showQuizResults && quizResults && (
        <Box sx={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          bgcolor: 'rgba(0,0,0,0.8)', 
          zIndex: 9999,
          overflow: 'auto',
          py: 2
        }}>
          <QuizResults
            results={quizResults}
            onRetake={handleQuizRetake}
            onClose={handleQuizClose}
          />
        </Box>
      )}
    </Box>
  );
};

export default LearningSession;
