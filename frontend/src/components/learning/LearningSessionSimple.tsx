import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Button,
  Card,
  CardContent,
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
  CircularProgress
} from '@mui/material';
import { quizAPI, lessonAPI } from '../../services/api';

const LearningSession: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState<any[]>([]);
  const [activeSession, setActiveSession] = useState<any>(null);
  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [currentQuestions, setCurrentQuestions] = useState<any[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [showResults, setShowResults] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newSessionData, setNewSessionData] = useState({
    subject_area: '',
    topic: '',
    session_type: 'lesson'
  });

  useEffect(() => {
    // Initialize with demo sessions
    setSessions([
      {
        id: '1',
        session_type: 'lesson',
        subject_area: 'Mathematics',
        topic: 'Linear Algebra',
        status: 'active',
        difficulty_level: 0.5,
        created_at: new Date().toISOString()
      },
      {
        id: '2', 
        session_type: 'quiz',
        subject_area: 'Computer Science',
        topic: 'Machine Learning',
        status: 'active',
        difficulty_level: 0.6,
        created_at: new Date().toISOString()
      }
    ]);
  }, []);

  const createNewSession = async () => {
    if (!newSessionData.subject_area || !newSessionData.topic) return;

    try {
      setLoading(true);
      
      if (newSessionData.session_type === 'lesson') {
        // Generate AI lesson
        const response = await lessonAPI.generateLesson({
          subject: newSessionData.subject_area,
          topic: newSessionData.topic,
          difficulty_level: 'medium'
        });
        
        if (response.data) {
          const newSession = {
            id: Date.now().toString(),
            ...newSessionData,
            status: 'active',
            lesson_content: response.data,
            created_at: new Date().toISOString()
          };
          
          setSessions(prev => [newSession, ...prev]);
          setActiveSession(newSession);
          setSuccessMessage('AI Lesson created successfully!');
        }
      } else {
        // Generate AI quiz
        const response = await quizAPI.generateQuiz({
          subject: newSessionData.subject_area,
          topic: newSessionData.topic,
          difficulty_level: 'medium',
          num_questions: 5
        });
        
        if (response.data && response.data.questions) {
          const newSession = {
            id: Date.now().toString(),
            ...newSessionData,
            status: 'active',
            created_at: new Date().toISOString()
          };
          
          setSessions(prev => [newSession, ...prev]);
          setActiveSession(newSession);
          setCurrentQuestions(response.data.questions);
          setCurrentQuestion(response.data.questions[0]);
          setSuccessMessage('AI Quiz created successfully!');
        }
      }
      
      setCreateDialogOpen(false);
      setNewSessionData({ subject_area: '', topic: '', session_type: 'lesson' });
      
    } catch (err) {
      console.error('Error creating session:', err);
      setError('Failed to create AI session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = () => {
    if (!currentQuestion || !selectedAnswer) return;
    
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;
    setIsCorrect(isCorrect);
    setShowResults(true);
    setExplanation(currentQuestion.explanation || 'Good attempt!');
  };

  const handleNextQuestion = () => {
    const currentIndex = currentQuestions.findIndex(q => q.id === currentQuestion?.id);
    
    if (currentIndex < currentQuestions.length - 1) {
      setCurrentQuestion(currentQuestions[currentIndex + 1]);
      setSelectedAnswer('');
      setShowResults(false);
      setExplanation('');
    } else {
      // Quiz complete
      setCurrentQuestion(null);
      setActiveSession(null);
      setCurrentQuestions([]);
      setSuccessMessage('Quiz completed! Great job!');
    }
  };

  const startSession = async (session: any) => {
    setActiveSession(session);
    
    if (session.session_type === 'quiz') {
      try {
        const response = await quizAPI.generateQuiz({
          subject: session.subject_area,
          topic: session.topic,
          difficulty_level: 'medium',
          num_questions: 5
        });
        
        if (response.data && response.data.questions) {
          setCurrentQuestions(response.data.questions);
          setCurrentQuestion(response.data.questions[0]);
        }
      } catch (error) {
        console.error('Error generating quiz:', error);
        setError('Failed to generate quiz questions');
      }
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: '1200px', margin: '0 auto', p: 2 }}>
      {/* Header */}
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
            }}
          >
            🚀 Create AI Learning Session
          </Button>
        )}
      </Box>

      {/* Active Session View */}
      {activeSession && (
        <Paper sx={{ 
          p: 4, 
          mb: 4, 
          borderRadius: 4,
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
        }}>
          {activeSession.session_type === 'lesson' ? (
            // Lesson View
            <Box>
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: 'primary.main' }}>
                📚 {activeSession.subject_area} - {activeSession.topic}
              </Typography>
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    AI-Generated Lesson Content
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Welcome to your personalized lesson on <strong>{activeSession.topic}</strong> in {activeSession.subject_area}.
                  </Typography>
                  {activeSession.lesson_content && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'rgba(25,118,210,0.05)', borderRadius: 2 }}>
                      <Typography variant="body1">
                        {typeof activeSession.lesson_content === 'string' 
                          ? activeSession.lesson_content 
                          : JSON.stringify(activeSession.lesson_content, null, 2)}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
              <Button
                variant="contained"
                onClick={() => setActiveSession(null)}
                sx={{ mr: 2 }}
              >
                ✅ Complete Lesson
              </Button>
              <Button
                variant="outlined"
                onClick={() => setActiveSession(null)}
              >
                📚 Back to Sessions
              </Button>
            </Box>
          ) : (
            // Quiz View
            <Box>
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: 'warning.main' }}>
                📝 {activeSession.subject_area} - {activeSession.topic}
              </Typography>
              
              {currentQuestion && !showResults ? (
                <Card>
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      Question {currentQuestions.findIndex(q => q.id === currentQuestion.id) + 1} of {currentQuestions.length}
                    </Typography>
                    <Typography variant="h5" paragraph>
                      {currentQuestion.question}
                    </Typography>
                    
                    <RadioGroup 
                      value={selectedAnswer} 
                      onChange={(e) => setSelectedAnswer(e.target.value)}
                    >
                      {currentQuestion.options?.map((option: string, index: number) => (
                        <FormControlLabel
                          key={index}
                          value={option}
                          control={<Radio />}
                          label={option}
                          sx={{ mb: 1 }}
                        />
                      ))}
                    </RadioGroup>
                    
                    <Button
                      variant="contained"
                      onClick={handleAnswerSubmit}
                      disabled={!selectedAnswer}
                      sx={{ mt: 2 }}
                    >
                      Submit Answer
                    </Button>
                  </CardContent>
                </Card>
              ) : showResults ? (
                <Card>
                  <CardContent sx={{ p: 4 }}>
                    <Alert severity={isCorrect ? "success" : "error"} sx={{ mb: 3 }}>
                      {isCorrect ? "Correct! Well done!" : "Not quite right, but good effort!"}
                    </Alert>
                    
                    <Typography variant="h6" gutterBottom>
                      Explanation:
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {explanation}
                    </Typography>
                    
                    {currentQuestions.findIndex(q => q.id === currentQuestion?.id) < currentQuestions.length - 1 ? (
                      <Button variant="contained" onClick={handleNextQuestion}>
                        Next Question
                      </Button>
                    ) : (
                      <Button variant="contained" color="success" onClick={handleNextQuestion}>
                        Complete Quiz
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ) : (
                <Typography>Loading questions...</Typography>
              )}
            </Box>
          )}
        </Paper>
      )}

      {/* Session List */}
      {!activeSession && (
        <Grid container spacing={3}>
          {sessions.map((session) => (
            <Grid size={{ xs: 12, md: 6, lg: 4 }} key={session.id}>
              <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {session.subject_area}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {session.topic}
                  </Typography>
                  <Chip 
                    label={session.session_type.toUpperCase()} 
                    color={session.session_type === 'lesson' ? 'primary' : 'secondary'}
                    size="small"
                    sx={{ mb: 2 }}
                  />
                  <Box>
                    <Button
                      variant="contained"
                      fullWidth
                      onClick={() => startSession(session)}
                      sx={{ borderRadius: 2 }}
                    >
                      {session.session_type === 'lesson' ? '📚 Start Lesson' : '📝 Take Quiz'}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Session Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New AI Learning Session</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Subject Area"
            value={newSessionData.subject_area}
            onChange={(e) => setNewSessionData(prev => ({ ...prev, subject_area: e.target.value }))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Topic"
            value={newSessionData.topic}
            onChange={(e) => setNewSessionData(prev => ({ ...prev, topic: e.target.value }))}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Session Type</InputLabel>
            <Select
              value={newSessionData.session_type}
              onChange={(e) => setNewSessionData(prev => ({ ...prev, session_type: e.target.value }))}
            >
              <MenuItem value="lesson">📚 Interactive Lesson</MenuItem>
              <MenuItem value="quiz">📝 Knowledge Quiz</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={createNewSession} 
            variant="contained"
            disabled={!newSessionData.subject_area || !newSessionData.topic}
          >
            Create Session
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Messages */}
      <Snackbar
        open={!!successMessage}
        autoHideDuration={4000}
        onClose={() => setSuccessMessage('')}
      >
        <Alert severity="success">{successMessage}</Alert>
      </Snackbar>

      <Snackbar
        open={!!error}
        autoHideDuration={4000}
        onClose={() => setError('')}
      >
        <Alert severity="error">{error}</Alert>
      </Snackbar>
    </Box>
  );
};

export default LearningSession;
