import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
  LinearProgress,
  Chip,
  Paper,
  IconButton
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Timer,
  Quiz,
  ArrowForward,
  ArrowBack
} from '@mui/icons-material';

interface Question {
  id: string;
  question: string;
  options: string[];
  correct_answer: string | number;
  explanation: string;
  difficulty?: number;
}

interface QuizDisplayProps {
  questions: Question[];
  quizId: string;
  onComplete: (results: {
    totalQuestions: number;
    correctAnswers: number;
    accuracy: number;
    timeSpent: number;
  }) => void;
  onClose: () => void;
}

const QuizDisplay: React.FC<QuizDisplayProps> = ({
  questions,
  quizId,
  onComplete,
  onClose
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [timeSpent, setTimeSpent] = useState(0);

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);


  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: answer
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      // Quiz completed
      const correctAnswers = questions.filter(q => 
        selectedAnswers[q.id] === q.correct_answer.toString()
      ).length;
      
      const accuracy = (correctAnswers / questions.length) * 100;
      
      onComplete({
        totalQuestions: questions.length,
        correctAnswers,
        accuracy,
        timeSpent: Math.round(timeSpent / 60) // Convert to minutes
      });
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getDifficultyColor = (difficulty?: number) => {
    if (!difficulty) return 'default';
    if (difficulty < 0.3) return 'success';
    if (difficulty < 0.7) return 'warning';
    return 'error';
  };

  const getDifficultyLabel = (difficulty?: number) => {
    if (!difficulty) return 'Medium';
    if (difficulty < 0.3) return 'Easy';
    if (difficulty < 0.7) return 'Medium';
    return 'Hard';
  };

  if (!currentQuestion) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6">Loading quiz...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      {/* Quiz Header */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #1976d2, #42a5f5)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Quiz sx={{ color: 'white', fontSize: 32 }} />
            <Box>
              <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
                AI Practice Quiz
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                Quiz ID: {quizId}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              icon={<Timer />}
              label={formatTime(timeSpent)}
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.2)', 
                color: 'white',
                '& .MuiChip-icon': { color: 'white' }
              }}
            />
            <IconButton onClick={onClose} sx={{ color: 'white' }}>
              <Cancel />
            </IconButton>
          </Box>
        </Box>
        
        <LinearProgress
          variant="determinate"
          value={progress}
          sx={{
            height: 8,
            borderRadius: 4,
            bgcolor: 'rgba(255,255,255,0.2)',
            '& .MuiLinearProgress-bar': {
              bgcolor: 'white'
            }
          }}
        />
      </Paper>

      {/* Question Card */}
      <Card sx={{ mb: 3, boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          {/* Question Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
              Question {currentQuestionIndex + 1} of {questions.length}
            </Typography>
            <Chip
              label={getDifficultyLabel(currentQuestion.difficulty)}
              color={getDifficultyColor(currentQuestion.difficulty) as any}
              size="small"
            />
          </Box>

          {/* Question Text */}
          <Typography variant="h5" sx={{ mb: 4, lineHeight: 1.6 }}>
            {currentQuestion.question}
          </Typography>

          {/* Answer Options */}
          <RadioGroup
            value={selectedAnswers[currentQuestion.id] || ''}
            onChange={(e) => handleAnswerSelect(e.target.value)}
            sx={{ mb: 4 }}
          >
            {currentQuestion.options.map((option, index) => (
              <FormControlLabel
                key={index}
                value={option}
                control={<Radio size="medium" />}
                label={
                  <Typography variant="body1" sx={{ ml: 1 }}>
                    {option}
                  </Typography>
                }
                sx={{
                  p: 2,
                  mb: 1,
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: selectedAnswers[currentQuestion.id] === option 
                    ? 'primary.main' 
                    : 'divider',
                  bgcolor: selectedAnswers[currentQuestion.id] === option 
                    ? 'primary.50' 
                    : 'transparent',
                  '&:hover': {
                    bgcolor: 'action.hover'
                  }
                }}
              />
            ))}
          </RadioGroup>

          {/* Navigation Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Button
              onClick={handlePreviousQuestion}
              disabled={currentQuestionIndex === 0}
              startIcon={<ArrowBack />}
              variant="outlined"
            >
              Previous
            </Button>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {selectedAnswers[currentQuestion.id] && (
                <Chip
                  icon={<CheckCircle />}
                  label="Answered"
                  color="success"
                  size="small"
                />
              )}
              
              <Button
                onClick={handleNextQuestion}
                disabled={!selectedAnswers[currentQuestion.id]}
                endIcon={currentQuestionIndex === questions.length - 1 ? <CheckCircle /> : <ArrowForward />}
                variant="contained"
                size="large"
                sx={{
                  px: 4,
                  background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1565c0, #1976d2)',
                  }
                }}
              >
                {currentQuestionIndex === questions.length - 1 ? 'Complete Quiz' : 'Next Question'}
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Progress Info */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, mb: 2 }}>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 600 }}>
            {currentQuestionIndex + 1}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Current
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" sx={{ color: 'success.main', fontWeight: 600 }}>
            {Object.keys(selectedAnswers).length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Answered
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" sx={{ color: 'warning.main', fontWeight: 600 }}>
            {questions.length - Object.keys(selectedAnswers).length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Remaining
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default QuizDisplay;
