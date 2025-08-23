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
  Grid,
  Alert,
  Snackbar,
  RadioGroup,
  FormControlLabel,
  Radio,
  CircularProgress,
  Divider
} from '@mui/material';
import { learningAPI, quizAPI, lessonAPI } from '../../services/api';

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
  // Lesson-specific properties
  content?: LessonContent;
  duration_estimate?: number;
  // Quiz-specific properties  
  questions?: Question[];
  total_questions?: number;
  time_limit_minutes?: number;
  // Common properties
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

  // State for quiz tracking
  const [activeQuizAttempt, setActiveQuizAttempt] = useState<any>(null);
  const [questionStartTime, setQuestionStartTime] = useState<Date | null>(null);

  // Create session dialog state
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSessionData, setNewSessionData] = useState({
    subject_area: '',
    topic: '',
    session_type: 'practice'
  });

  // Sample questions for different topics (fallback only)
  

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      
      // Try to get real sessions from backend
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
        // Single session response, convert to array
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
      console.error('Error fetching sessions, using demo data:', err);
      // Fallback to demo session for functionality
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
      
      // Generate AI-powered quiz based on selected topic
      const quizRequest = {
        subject: newSessionData.subject_area,
        topic: newSessionData.topic,
        difficulty_level: 'medium',
        num_questions: 4
      };
      
      const quizResponse = await quizAPI.generateQuiz(quizRequest);
      const quizData = quizResponse.data;
      
      // Convert quiz questions to local Question format
      const questions: Question[] = quizData.questions.map((q: any, index: number) => ({
        id: `q_${index}`,
        question: q.question,
        options: q.options || [q.option_a, q.option_b, q.option_c, q.option_d],
        correct_answer: q.correct_answer,
        explanation: q.explanation || 'No explanation available.',
        difficulty: q.difficulty_level || 0.5
      }));
      
      // Create session with backend
      const sessionResponse = await learningAPI.createSession({
        content_id: 1,
        session_type: newSessionData.session_type
      });
      
      // Create local session with AI-generated questions
      const newSession: LearningSessionData = {
        id: sessionResponse.data.id || Date.now().toString(),
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
      
      setSessions(prev => [newSession, ...prev]);
      setActiveSession(newSession);
      
      // Store the AI-generated questions and start with the first one
      setCurrentQuestions(questions);
      if (questions.length > 0) {
        setCurrentQuestion(questions[0]);
        setQuestionStartTime(new Date()); // Start timing the first question
      }
      
      setCreateDialogOpen(false);
      setNewSessionData({ subject_area: '', topic: '', session_type: 'practice' });
      setSuccessMessage(`AI-powered quiz created for ${newSessionData.topic}!`);
      
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
    
    // Calculate response time if we tracked question start
    const responseTime = questionStartTime 
      ? (new Date().getTime() - questionStartTime.getTime()) / 1000 
      : undefined;
    
    // Update session progress
    const updatedSession = {
      ...activeSession,
      questions_attempted: (activeSession.questions_attempted || 0) + 1,
      questions_correct: (activeSession.questions_correct || 0) + (isCorrect ? 1 : 0),
      accuracy_rate: (((activeSession.questions_correct || 0) + (isCorrect ? 1 : 0)) / ((activeSession.questions_attempted || 0) + 1)) * 100
    };
    
    setActiveSession(updatedSession);
    
    // Update sessions list
    setSessions(prev => prev.map(session => 
      session.id === activeSession.id ? updatedSession : session
    ));
    
    try {
      // Submit answer to quiz API if we have a quiz attempt
      if (activeQuizAttempt && activeQuizAttempt.id) {
        await quizAPI.submitQuiz({
          quiz_data: activeQuizAttempt,
          answers: { [currentQuestion.id]: selectedAnswer },
          time_spent_minutes: responseTime ? Math.round(responseTime / 60) : 1
        });
      }
      
      // Log interaction with backend
      if (activeSession.id && parseInt(activeSession.id)) {
        await learningAPI.logInteraction(parseInt(activeSession.id), {
          question_id: currentQuestion.id,
          answer: selectedAnswer,
          is_correct: isCorrect,
          time_spent: responseTime || 30
        });
      }
    } catch (error) {
      console.error('Error logging interaction:', error);
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
      setQuestionStartTime(new Date()); // Track start time for new question
    } else {
      // Session complete
      if (activeQuizAttempt && activeQuizAttempt.id) {
        try {
          await quizAPI.submitQuiz({
            quiz_data: activeQuizAttempt,
            answers: {}, // All answers have been submitted individually
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
    // Generate questions for the session when starting
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
        
        // Convert quiz questions to local Question format
        const questions: Question[] = quizData.questions.map((q: any, index: number) => ({
          id: `q_${index}`,
          question: q.question,
          options: q.options || [q.option_a, q.option_b, q.option_c, q.option_d],
          correct_answer: q.correct_answer,
          explanation: q.explanation || 'No explanation available.',
          difficulty: q.difficulty_level || 0.5
        }));
        
        setActiveQuizAttempt({ id: quizData.quiz_id, ...quizData });
        setCurrentQuestions(questions);
        setActiveSession(session);
        setCurrentQuestion(questions[0]);
        setSelectedAnswer('');
        setShowResults(false);
        setExplanation('');
        setQuestionStartTime(new Date()); // Start timing the first question
      } catch (error) {
        console.error('Error generating questions for session:', error);
        setError('Failed to generate quiz questions');
      } finally {
        setLoading(false);
      }
    };
    
    generateQuestionsForSession();
  };

  const pauseSession = async () => {
    if (!activeSession) return;
    
    try {
      // await learningAPI.pauseSession(activeSession.id);
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
    <Box>
      <Typography variant="h4" gutterBottom>
        Learning Session
      </Typography>

      {/* Active Session View */}
      {activeSession && (
        <Paper sx={{ p: 3, mb: 3 }}>
          {activeSession.session_type === 'lesson' ? (
            // Lesson View
            <Box>
              <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
                <Typography variant="h5">
                  📖 {activeSession.subject_area} - {activeSession.topic}
                </Typography>
                <Box display="flex" gap={1}>
                  <Chip label="LESSON" color="info" size="small" />
                  <Chip 
                    label={`~${activeSession.duration_estimate || 20} min`} 
                    color="primary" 
                    size="small" 
                  />
                </Box>
              </Box>

              {activeSession.content && (
                <Box>
                  <Typography variant="h6" gutterBottom color="primary">
                    {activeSession.content.title}
                  </Typography>
                  
                  <Card sx={{ mb: 3, bgcolor: '#f8f9ff' }}>
                    <CardContent>
                      <Typography variant="body1" paragraph>
                        {activeSession.content.introduction}
                      </Typography>
                    </CardContent>
                  </Card>

                  <Typography variant="h6" gutterBottom>
                    🔑 Key Concepts
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    {activeSession.content.key_concepts.map((concept, index) => (
                      <Grid key={index} size={{ xs: 12, md: 6 }}>
                        <Card sx={{ height: '100%', bgcolor: '#fff3e0' }}>
                          <CardContent>
                            <Typography variant="body2">
                              <strong>{index + 1}.</strong> {concept}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>

                  <Typography variant="h6" gutterBottom>
                    💡 Examples
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 4 }}>
                    {activeSession.content.examples.map((example, index) => (
                      <Grid key={index} size={{ xs: 12 }}>
                        <Card sx={{ bgcolor: '#f3e5f5' }}>
                          <CardContent>
                            <Typography variant="body1" paragraph>
                              <strong>Example {index + 1}:</strong>
                            </Typography>
                            {Object.entries(example).map(([key, value]) => (
                              <Typography key={key} variant="body2" sx={{ ml: 2 }}>
                                <strong>{key.charAt(0).toUpperCase() + key.slice(1)}:</strong> {
                                  Array.isArray(value) ? (
                                    <ul>
                                      {value.map((item, i) => <li key={i}>{item}</li>)}
                                    </ul>
                                  ) : (
                                    String(value)
                                  )
                                }
                              </Typography>
                            ))}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>

                  <Box display="flex" gap={2} justifyContent="center">
                    <Button 
                      variant="outlined" 
                      onClick={() => setActiveSession(null)}
                    >
                      📚 Back to Sessions
                    </Button>
                    <Button 
                      variant="contained" 
                      color="success"
                      onClick={() => {
                        // Mark lesson as completed and maybe start related quiz
                        const quizSession = sessions.find(s => 
                          s.session_type === 'quiz' && 
                          s.topic === activeSession.topic &&
                          s.subject_area === activeSession.subject_area
                        );
                        if (quizSession) {
                          setActiveSession(quizSession);
                        } else {
                          setActiveSession(null);
                          // Could trigger a success message here
                        }
                      }}
                    >
                      ✅ Complete Lesson & Take Quiz
                    </Button>
                  </Box>
                </Box>
              )}
            </Box>
          ) : activeSession && currentQuestion ? (
            // Quiz View (existing code)
            <Box>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  📝 {activeSession.subject_area} - {activeSession.topic}
                </Typography>
                <Box display="flex" gap={1}>
                  <Chip label="QUIZ" color="warning" size="small" />
                  <Chip 
                    label={`${activeSession.questions_attempted || 0} Questions`} 
                    color="primary" 
                    size="small" 
                  />
                  <Chip 
                    label={`${(activeSession.accuracy_rate || 0).toFixed(1)}% Accuracy`} 
                    color={(activeSession.accuracy_rate || 0) >= 70 ? "success" : "warning"} 
                    size="small" 
                  />
            </Box>
          </Box>

          <LinearProgress 
            variant="determinate" 
            value={activeSession && currentQuestions.length > 0 ? ((activeSession.questions_attempted || 0) / currentQuestions.length * 100) : 0}
            sx={{ mb: 3 }}
          />

          {!showResults ? (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Question {currentQuestions.length > 0 ? (currentQuestions.findIndex(q => q.id === currentQuestion?.id) + 1) : 1} of {currentQuestions.length || 1}
                </Typography>
                <Typography variant="body1" paragraph>
                  {currentQuestion.question}
                </Typography>

                <RadioGroup value={selectedAnswer} onChange={(e) => setSelectedAnswer(e.target.value)}>
                  {currentQuestion.options.map((option, index) => (
                    <FormControlLabel
                      key={index}
                      value={option}
                      control={<Radio />}
                      label={option}
                    />
                  ))}
                </RadioGroup>

                <Box mt={2} display="flex" gap={2}>
                  <Button 
                    variant="contained" 
                    onClick={handleAnswerSubmit}
                    disabled={!selectedAnswer}
                  >
                    Submit Answer
                  </Button>
                  <Button variant="outlined" onClick={pauseSession}>
                    Pause Session
                  </Button>
                </Box>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent>
                <Alert severity={isCorrect ? "success" : "error"} sx={{ mb: 2 }}>
                  {isCorrect ? "Correct!" : "Incorrect"}
                </Alert>

                <Typography variant="body1" paragraph>
                  <strong>Your Answer:</strong> {selectedAnswer}
                </Typography>
                <Typography variant="body1" paragraph>
                  <strong>Correct Answer:</strong> {currentQuestion.correct_answer}
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>Explanation:</strong> {explanation}
                </Typography>

                <Box mt={2}>
                  {activeSession && currentQuestions.length > 0 && (currentQuestions.findIndex(q => q.id === currentQuestion?.id) < currentQuestions.length - 1) ? (
                    <Button variant="contained" onClick={handleNextQuestion}>
                      Next Question
                    </Button>
                  ) : (
                    <Button variant="contained" color="success" onClick={handleNextQuestion}>
                      Complete Session
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          )}
            </Box>
          ) : null}
        </Paper>
      )}
      
      {/* Session List View */}
      {!activeSession && (
        <Box>
          <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
            <Typography variant="h6">Your Learning Sessions</Typography>
            <Button 
              variant="contained" 
              onClick={() => setCreateDialogOpen(true)}
            >
              Start New Session
            </Button>
          </Box>

          <Grid container spacing={3}>
            {sessions.map((session) => (
              <Grid key={session.id} size={{ xs: 12, md: 6, lg: 4 }}>
                <Card 
                  sx={{ 
                    height: '100%',
                    border: session.session_type === 'lesson' ? '2px solid #2196f3' : 
                           session.session_type === 'quiz' ? '2px solid #ff9800' : '1px solid #e0e0e0',
                    '&:hover': { transform: 'translateY(-2px)', transition: 'transform 0.2s' }
                  }}
                >
                  <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                      <Typography variant="h6" noWrap>
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
                        />
                        <Chip 
                          label={session.status} 
                          color={
                            session.status === 'completed' ? 'success' : 
                            session.status === 'active' ? 'primary' : 'default'
                          }
                          size="small"
                        />
                      </Box>
                    </Box>

                    <Typography color="textSecondary" gutterBottom>
                      {session.topic}
                    </Typography>

                    <Divider sx={{ my: 1 }} />

                    {/* Session type specific information */}
                    {session.session_type === 'lesson' ? (
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="body2" paragraph>
                          📖 <strong>Lesson Content:</strong> Interactive learning material
                        </Typography>
                        <Typography variant="body2" paragraph>
                          ⏱️ <strong>Duration:</strong> ~{session.duration_estimate || 20} minutes
                        </Typography>
                        <Typography variant="body2" paragraph>
                          🎯 <strong>Difficulty:</strong> {Math.round(session.difficulty_level * 100)}%
                        </Typography>
                        {session.content && (
                          <Typography variant="body2" color="text.secondary">
                            📋 {session.content.key_concepts?.length || 3} key concepts covered
                          </Typography>
                        )}
                      </Box>
                    ) : (
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="body2" paragraph>
                          📝 <strong>Questions:</strong> {session.total_questions || session.questions_attempted || 0}
                        </Typography>
                        {session.accuracy_rate && (
                          <Typography variant="body2" paragraph>
                            🎯 <strong>Accuracy:</strong> {session.accuracy_rate.toFixed(1)}%
                          </Typography>
                        )}
                        <Typography variant="body2" paragraph>
                          ⏱️ <strong>Time Limit:</strong> {session.time_limit_minutes || session.duration_minutes || 15} minutes
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          📊 Difficulty: {Math.round(session.difficulty_level * 100)}%
                        </Typography>
                      </Box>
                    )}

                    <Box mt={2}>
                      {session.status === 'active' || session.status === 'paused' ? (
                        <Button 
                          variant="contained" 
                          size="small" 
                          fullWidth
                          onClick={() => startSession(session)}
                        >
                          {session.status === 'paused' ? 'Resume' : 'Continue'}
                        </Button>
                      ) : session.status === 'completed' ? (
                        <Button 
                          variant="outlined" 
                          size="small" 
                          fullWidth
                          disabled
                        >
                          ✅ Completed
                        </Button>
                      ) : (
                        <Button 
                          variant="contained" 
                          size="small" 
                          fullWidth
                          onClick={() => startSession(session)}
                          color={session.session_type === 'lesson' ? 'info' : 'warning'}
                        >
                          {session.session_type === 'lesson' ? '📖 Start Lesson' : '📝 Take Quiz'}
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

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

      {/* Create Session Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Learning Session</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Subject Area"
              value={newSessionData.subject_area}
              onChange={(e) => setNewSessionData(prev => ({ ...prev, subject_area: e.target.value }))}
              margin="normal"
              placeholder="e.g., Mathematics, Science, History"
            />
            
            <TextField
              fullWidth
              label="Topic"
              value={newSessionData.topic}
              onChange={(e) => setNewSessionData(prev => ({ ...prev, topic: e.target.value }))}
              margin="normal"
              placeholder="e.g., Algebra, Physics, World War II"
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>Session Type</InputLabel>
              <Select
                value={newSessionData.session_type}
                onChange={(e) => setNewSessionData(prev => ({ ...prev, session_type: e.target.value }))}
              >
                <MenuItem value="practice">Practice</MenuItem>
                <MenuItem value="quiz">Quiz</MenuItem>
                <MenuItem value="review">Review</MenuItem>
                <MenuItem value="lesson">Lesson</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={createNewSession} 
            variant="contained"
            disabled={!newSessionData.subject_area || !newSessionData.topic}
          >
            Start Session
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Messages */}
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
    </Box>
  );
};

export default LearningSession;
