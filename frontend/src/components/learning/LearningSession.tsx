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
import { learningAPI } from '../../services/api';
import { aiQuizGenerator, type QuizGenerationRequest } from '../../services/aiQuizGenerator';

interface Question {
  id: string;
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
  difficulty: number;
}

interface LearningSessionData {
  id: number;
  session_type: string;
  subject_area: string;
  topic: string;
  status: string;
  questions_attempted: number;
  questions_correct: number;
  accuracy_rate: number;
  duration_minutes: number;
  started_at: string;
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

  // Create session dialog state
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSessionData, setNewSessionData] = useState({
    subject_area: '',
    topic: '',
    session_type: 'practice'
  });

  // Sample questions for different topics
  const getQuestionsForTopic = (subjectArea: string, topic: string): Question[] => {
    const topicLower = topic.toLowerCase();
    const subjectLower = subjectArea.toLowerCase();
    
    if (subjectLower.includes('artificial intelligence') || subjectLower.includes('ai') || topicLower.includes('machine learning') || topicLower.includes('ml')) {
      return [
        {
          id: '1',
          question: 'What is the primary goal of machine learning?',
          options: [
            'To replace human intelligence completely',
            'To enable computers to learn and make decisions from data',
            'To create robots that look like humans',
            'To store large amounts of data'
          ],
          correct_answer: 'To enable computers to learn and make decisions from data',
          explanation: 'Machine learning aims to enable computers to automatically learn and improve from experience without being explicitly programmed for every task.',
          difficulty: 0.4
        },
        {
          id: '2',
          question: 'What is France in the context of AI development?',
          options: [
            'A country with no AI research',
            'A leading country in AI research with institutions like INRIA',
            'Only focused on traditional computing',
            'Has banned AI research'
          ],
          correct_answer: 'A leading country in AI research with institutions like INRIA',
          explanation: 'France is a major player in AI research, home to institutions like INRIA (French Institute for Research in Computer Science and Automation) and has significant government investment in AI initiatives.',
          difficulty: 0.3
        },
        {
          id: '3',
          question: 'Which of these is a supervised learning algorithm?',
          options: [
            'K-means clustering',
            'Linear regression',
            'Principal Component Analysis',
            'Autoencoders'
          ],
          correct_answer: 'Linear regression',
          explanation: 'Linear regression is a supervised learning algorithm that learns from labeled training data to predict continuous output values.',
          difficulty: 0.5
        },
        {
          id: '4',
          question: 'What does "AI" stand for?',
          options: [
            'Advanced Intelligence',
            'Artificial Intelligence',
            'Automated Information',
            'Algorithmic Innovation'
          ],
          correct_answer: 'Artificial Intelligence',
          explanation: 'AI stands for Artificial Intelligence - the simulation of human intelligence in machines that are programmed to think and learn.',
          difficulty: 0.1
        }
      ];
    }
    
    // Default questions for other topics
    return [
      {
        id: '1',
        question: 'What is the capital of France?',
        options: ['London', 'Berlin', 'Paris', 'Madrid'],
        correct_answer: 'Paris',
        explanation: 'Paris is the capital and most populous city of France.',
        difficulty: 0.3
      },
      {
        id: '2',
        question: 'What is 2 + 2?',
        options: ['3', '4', '5', '6'],
        correct_answer: '4',
        explanation: 'Two plus two equals four in basic arithmetic.',
        difficulty: 0.1
      }
    ];
  };

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
          id: session.id,
          session_type: session.session_type,
          subject_area: session.subject_area || 'General',
          topic: session.topic || 'Mixed Topics',
          status: session.status,
          questions_attempted: session.questions_attempted || 0,
          questions_correct: session.questions_correct || 0,
          accuracy_rate: session.accuracy_rate || 0,
          duration_minutes: session.duration_minutes || 0,
          started_at: session.started_at
        })));
      } else {
        // Single session response, convert to array
        const session = response.data;
        setSessions([{
          id: session.id,
          session_type: session.session_type,
          subject_area: session.subject_area || 'General',
          topic: session.topic || 'Mixed Topics',
          status: session.status,
          questions_attempted: session.questions_attempted || 0,
          questions_correct: session.questions_correct || 0,
          accuracy_rate: session.accuracy_rate || 0,
          duration_minutes: session.duration_minutes || 0,
          started_at: session.started_at
        }]);
      }
    } catch (err) {
      console.error('Error fetching sessions, using demo data:', err);
      // Fallback to demo session for functionality
      setSessions([
        {
          id: 1,
          session_type: 'practice',
          subject_area: 'General Knowledge',
          topic: 'Mixed Topics',
          status: 'active',
          questions_attempted: 0,
          questions_correct: 0,
          accuracy_rate: 0,
          duration_minutes: 0,
          started_at: new Date().toISOString()
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
      const quizRequest: QuizGenerationRequest = {
        subject: newSessionData.subject_area,
        topic: newSessionData.topic,
        difficulty: 0.5, // Convert to number
        numQuestions: 4
      };
      
      const aiQuestions = await aiQuizGenerator.generateQuiz(quizRequest);
      
      // Convert AI questions to local Question format
      const questions: Question[] = aiQuestions.map(q => ({
        id: q.id,
        question: q.question,
        options: [q.options.A, q.options.B, q.options.C, q.options.D],
        correct_answer: q.correct_answer,
        explanation: q.explanation,
        difficulty: q.difficulty || 0.5
      }));
      
      // Create session with backend
      await learningAPI.createSession({
        content_id: 1,
        session_type: newSessionData.session_type
      });
      
      // Create local session with AI-generated questions
      const newSession: LearningSessionData = {
        id: Date.now(),
        ...newSessionData,
        status: 'active',
        questions_attempted: 0,
        questions_correct: 0,
        accuracy_rate: 0,
        duration_minutes: 0,
        started_at: new Date().toISOString()
      };
      
      setSessions(prev => [newSession, ...prev]);
      setActiveSession(newSession);
      
      // Store the AI-generated questions and start with the first one
      setCurrentQuestions(questions);
      if (questions.length > 0) {
        setCurrentQuestion(questions[0]);
      }
      
      setCreateDialogOpen(false);
      setNewSessionData({ subject_area: '', topic: '', session_type: 'practice' });
      setSuccessMessage(`AI-powered quiz created for ${newSessionData.topic}!`);
      
    } catch (err) {
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
    
    // Update session progress
    const updatedSession = {
      ...activeSession,
      questions_attempted: activeSession.questions_attempted + 1,
      questions_correct: activeSession.questions_correct + (isCorrect ? 1 : 0),
      accuracy_rate: ((activeSession.questions_correct + (isCorrect ? 1 : 0)) / (activeSession.questions_attempted + 1)) * 100
    };
    
    setActiveSession(updatedSession);
    
    // Update sessions list
    setSessions(prev => prev.map(session => 
      session.id === activeSession.id ? updatedSession : session
    ));
    
    try {
      // Log interaction with backend
      await learningAPI.logInteraction(activeSession.id, {
        question_id: currentQuestion.id,
        answer: selectedAnswer,
        is_correct: isCorrect,
        time_spent: 30 // You could track actual time spent
      });
    } catch (error) {
      console.error('Error logging interaction:', error);
    }
  };
  
  const handleNextQuestion = () => {
    if (!activeSession || !currentQuestions.length) return;
    
    const currentIndex = currentQuestions.findIndex(q => q.id === currentQuestion?.id);
    
    if (currentIndex < currentQuestions.length - 1) {
      setCurrentQuestion(currentQuestions[currentIndex + 1]);
      setSelectedAnswer('');
      setShowResults(false);
      setExplanation('');
    } else {
      // Session complete
      setCurrentQuestion(null);
      setActiveSession(null);
      setCurrentQuestions([]);
      setSuccessMessage('Session completed! Great job!');
    }
  };

  const startSession = (session: LearningSessionData) => {
    // Generate questions for the session when starting
    const generateQuestionsForSession = async () => {
      try {
        setLoading(true);
        const quizRequest: QuizGenerationRequest = {
          subject: session.subject_area,
          topic: session.topic,
          difficulty: 0.5, // Convert to number
          numQuestions: 4
        };
        
        const aiQuestions = await aiQuizGenerator.generateQuiz(quizRequest);
        
        // Convert AI questions to local Question format
        const questions: Question[] = aiQuestions.map(q => ({
          id: q.id,
          question: q.question,
          options: [q.options.A, q.options.B, q.options.C, q.options.D],
          correct_answer: q.correct_answer,
          explanation: q.explanation,
          difficulty: q.difficulty || 0.5
        }));
        
        setCurrentQuestions(questions);
        setActiveSession(session);
        setCurrentQuestion(questions[0]);
        setSelectedAnswer('');
        setShowResults(false);
        setExplanation('');
      } catch (error) {
        console.error('Error generating questions for session:', error);
        setError('Failed to generate quiz questions');
      } finally {
        setLoading(false);
      }
    };
    
    generateQuestionsForSession();
  };

  const completeSession = async () => {
    if (!activeSession) return;
    
    try {
      // await learningAPI.completeSession(activeSession.id);
      const updatedSession = { ...activeSession, status: 'completed' };
      setSessions(prev => 
        prev.map(s => s.id === updatedSession.id ? updatedSession : s)
      );
      setActiveSession(null);
      setCurrentQuestion(null);
      setSuccessMessage('Learning session completed successfully!');
    } catch (err) {
      setError('Failed to complete session');
    }
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
      {activeSession && currentQuestion ? (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
            <Typography variant="h6">
              {activeSession.subject_area} - {activeSession.topic}
            </Typography>
            <Box display="flex" gap={1}>
              <Chip 
                label={`${activeSession.questions_attempted} Questions`} 
                color="primary" 
                size="small" 
              />
              <Chip 
                label={`${activeSession.accuracy_rate.toFixed(1)}% Accuracy`} 
                color={activeSession.accuracy_rate >= 70 ? "success" : "warning"} 
                size="small" 
              />
            </Box>
          </Box>

          <LinearProgress 
            variant="determinate" 
            value={activeSession && currentQuestions.length > 0 ? ((activeSession.questions_attempted) / currentQuestions.length * 100) : 0}
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
        </Paper>
      ) : (
        /* Session List View */
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
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                      <Typography variant="h6" noWrap>
                        {session.subject_area}
                      </Typography>
                      <Chip 
                        label={session.status} 
                        color={
                          session.status === 'completed' ? 'success' : 
                          session.status === 'active' ? 'primary' : 'default'
                        }
                        size="small"
                      />
                    </Box>

                    <Typography color="textSecondary" gutterBottom>
                      {session.topic}
                    </Typography>

                    <Divider sx={{ my: 1 }} />

                    <Typography variant="body2">
                      Questions: {session.questions_attempted} | 
                      Accuracy: {session.accuracy_rate.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2">
                      Duration: {session.duration_minutes} minutes
                    </Typography>

                    <Box mt={2}>
                      {session.status === 'active' || session.status === 'paused' ? (
                        <Button 
                          variant="contained" 
                          size="small" 
                          onClick={() => startSession(session)}
                        >
                          {session.status === 'paused' ? 'Resume' : 'Continue'}
                        </Button>
                      ) : (
                        <Button 
                          variant="outlined" 
                          size="small" 
                          disabled
                        >
                          Completed
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
