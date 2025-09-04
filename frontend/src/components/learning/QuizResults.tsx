import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  LinearProgress,
  Chip,
  Divider,
  Grid,
  IconButton
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Timer,
  Quiz,
  TrendingUp,
  EmojiEvents,
  Close,
  Refresh
} from '@mui/icons-material';

interface QuizResultsProps {
  results: {
    totalQuestions: number;
    correctAnswers: number;
    accuracy: number;
    timeSpent: number;
  };
  onRetake: () => void;
  onClose: () => void;
}

const QuizResults: React.FC<QuizResultsProps> = ({
  results,
  onRetake,
  onClose
}) => {
  const { totalQuestions, correctAnswers, accuracy, timeSpent } = results;
  const incorrectAnswers = totalQuestions - correctAnswers;

  const getPerformanceLevel = (accuracy: number) => {
    if (accuracy >= 90) return { level: 'Excellent', color: 'success', emoji: '🏆' };
    if (accuracy >= 80) return { level: 'Great', color: 'success', emoji: '🎉' };
    if (accuracy >= 70) return { level: 'Good', color: 'warning', emoji: '👍' };
    if (accuracy >= 60) return { level: 'Fair', color: 'warning', emoji: '📚' };
    return { level: 'Needs Improvement', color: 'error', emoji: '💪' };
  };

  const performance = getPerformanceLevel(accuracy);

  const getEncouragementMessage = (accuracy: number) => {
    if (accuracy >= 90) return "Outstanding work! You've mastered this topic!";
    if (accuracy >= 80) return "Great job! You have a solid understanding!";
    if (accuracy >= 70) return "Good work! You're on the right track!";
    if (accuracy >= 60) return "Not bad! Keep practicing to improve!";
    return "Don't give up! Practice makes perfect!";
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 2 }}>
      {/* Results Header */}
      <Paper sx={{ 
        p: 4, 
        mb: 3, 
        background: 'linear-gradient(135deg, #1976d2, #42a5f5)',
        textAlign: 'center'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <EmojiEvents sx={{ color: 'white', fontSize: 40 }} />
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
              Quiz Complete!
            </Typography>
          </Box>
          <IconButton onClick={onClose} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </Box>
        
        <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.9)' }}>
          {getEncouragementMessage(accuracy)}
        </Typography>
      </Paper>

      {/* Performance Overview */}
      <Card sx={{ mb: 3, boxShadow: 3 }}>
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h2" sx={{ mb: 2, fontSize: '4rem' }}>
            {performance.emoji}
          </Typography>
          
          <Typography variant="h4" sx={{ mb: 2, fontWeight: 600 }}>
            {performance.level}
          </Typography>
          
          <Typography variant="h3" sx={{ 
            mb: 3, 
            fontWeight: 700,
            color: `${performance.color}.main`
          }}>
            {accuracy.toFixed(1)}%
          </Typography>
          
          <LinearProgress
            variant="determinate"
            value={accuracy}
            sx={{
              height: 12,
              borderRadius: 6,
              mb: 3,
              '& .MuiLinearProgress-bar': {
                bgcolor: `${performance.color}.main`
              }
            }}
          />
          
          <Typography variant="body1" color="text.secondary">
            Overall Performance
          </Typography>
        </CardContent>
      </Card>

      {/* Detailed Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={6}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <CheckCircle sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
              {correctAnswers}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Correct Answers
            </Typography>
          </Card>
        </Grid>
        
        <Grid item xs={6}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Cancel sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
            <Typography variant="h4" sx={{ fontWeight: 600, color: 'error.main' }}>
              {incorrectAnswers}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Incorrect Answers
            </Typography>
          </Card>
        </Grid>
      </Grid>

      {/* Additional Stats */}
      <Card sx={{ mb: 3, boxShadow: 2 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            Quiz Statistics
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Quiz sx={{ color: 'primary.main' }} />
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {totalQuestions}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Questions
                  </Typography>
                </Box>
              </Box>
            </Grid>
            
            <Grid item xs={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Timer sx={{ color: 'info.main' }} />
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {timeSpent}m
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Time Spent
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 2 }} />
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <TrendingUp sx={{ color: 'success.main' }} />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {(correctAnswers / totalQuestions * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Success Rate
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          onClick={onRetake}
          variant="outlined"
          size="large"
          startIcon={<Refresh />}
          sx={{ px: 4 }}
        >
          Retake Quiz
        </Button>
        
        <Button
          onClick={onClose}
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
          Continue Learning
        </Button>
      </Box>

      {/* Performance Tips */}
      {accuracy < 80 && (
        <Card sx={{ mt: 3, bgcolor: 'info.50', border: '1px solid', borderColor: 'info.200' }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: 'info.main' }}>
              💡 Tips for Improvement
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              • Review the explanations for incorrect answers
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              • Take your time to read questions carefully
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              • Practice with more quizzes on this topic
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Consider reviewing the lesson material first
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default QuizResults;
