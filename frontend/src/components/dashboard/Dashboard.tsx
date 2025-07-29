import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  LinearProgress,
  Button,
  Alert,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
  Psychology as AIIcon,
  Timeline as ProgressIcon,
} from '@mui/icons-material';
import { studentAPI, progressAPI } from '../../services/api';
import Loading from '../common/Loading';

interface DashboardData {
  student_stats: {
    current_streak: number;
    total_points: number;
    sessions_completed: number;
    knowledge_level: number;
  };
  progress_summary: {
    overall_mastery_percentage: number;
    mastered_objectives: number;
    total_objectives: number;
    total_study_time: number;
  };
  recent_achievements: Array<{
    title: string;
    description: string;
    points_earned: number;
  }>;
}

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Mock data for now since backend might not be fully connected
        setDashboardData({
          student_stats: {
            current_streak: 5,
            total_points: 1250,
            sessions_completed: 12,
            knowledge_level: 0.75,
          },
          progress_summary: {
            overall_mastery_percentage: 68,
            mastered_objectives: 15,
            total_objectives: 22,
            total_study_time: 180,
          },
          recent_achievements: [
            {
              title: 'Quick Learner',
              description: 'Completed 3 sessions in one day',
              points_earned: 50,
            },
            {
              title: '5-Day Streak',
              description: 'Maintained learning for 5 consecutive days',
              points_earned: 100,
            },
          ],
        });
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) return <Loading message="Loading your dashboard..." />;

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  const stats = dashboardData?.student_stats;
  const progress = dashboardData?.progress_summary;
  const achievements = dashboardData?.recent_achievements || [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to Your Learning Dashboard
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Track your progress and continue your learning journey
      </Typography>

      {/* Stats Cards */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 4 }}>
        <Card sx={{ minWidth: 200, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <TrendingUpIcon color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Current Streak
                </Typography>
                <Typography variant="h5">
                  {stats?.current_streak || 0} days
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 200, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <SchoolIcon color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Points
                </Typography>
                <Typography variant="h5">
                  {stats?.total_points || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 200, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <AIIcon color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Sessions Completed
                </Typography>
                <Typography variant="h5">
                  {stats?.sessions_completed || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ minWidth: 200, flex: 1 }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <ProgressIcon color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Knowledge Level
                </Typography>
                <Typography variant="h5">
                  {Math.round((stats?.knowledge_level || 0) * 100)}%
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Progress Overview */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        <Paper sx={{ p: 3, flex: 2, minWidth: 300 }}>
          <Typography variant="h6" gutterBottom>
            Learning Progress
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="textSecondary">
              Overall Mastery: {Math.round(progress?.overall_mastery_percentage || 0)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={progress?.overall_mastery_percentage || 0}
              sx={{ height: 10, borderRadius: 5, mt: 1 }}
            />
          </Box>
          <Box display="flex" justifyContent="space-between" sx={{ mt: 2 }}>
            <Typography variant="body2">
              Mastered: {progress?.mastered_objectives || 0} / {progress?.total_objectives || 0} objectives
            </Typography>
            <Typography variant="body2">
              Study Time: {Math.round((progress?.total_study_time || 0) / 60)} hours
            </Typography>
          </Box>
          
          <Box sx={{ mt: 3 }}>
            <Button variant="contained" color="primary" sx={{ mr: 2 }}>
              Start Learning Session
            </Button>
            <Button variant="outlined" color="primary">
              Chat with AI Tutor
            </Button>
          </Box>
        </Paper>

        <Paper sx={{ p: 3, flex: 1, minWidth: 250 }}>
          <Typography variant="h6" gutterBottom>
            Recent Achievements
          </Typography>
          {achievements.length > 0 ? (
            achievements.slice(0, 3).map((achievement, index) => (
              <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="subtitle2" color="primary">
                  {achievement.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {achievement.description}
                </Typography>
                <Typography variant="caption" color="primary">
                  +{achievement.points_earned} points
                </Typography>
              </Box>
            ))
          ) : (
            <Typography variant="body2" color="textSecondary">
              Complete learning activities to earn achievements!
            </Typography>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default Dashboard;
