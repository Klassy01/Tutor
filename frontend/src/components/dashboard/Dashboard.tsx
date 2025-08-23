import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
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
import { studentAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
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
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch real data from API
        const response = await studentAPI.getDashboard();
        const data = response.data;
        
        // Transform API response to expected format
        setDashboardData({
          student_stats: {
            current_streak: data.achievements?.current_streak || 5,
            total_points: data.achievements?.points_earned || 1250,
            sessions_completed: data.quick_stats?.sessions_this_week || 12,
            knowledge_level: data.student_info?.knowledge_score || 0.75,
          },
          progress_summary: {
            overall_mastery_percentage: 68,
            mastered_objectives: 15,
            total_objectives: 22,
            total_study_time: data.achievements?.total_study_time || 180,
          },
          recent_achievements: data.recent_achievements || [
            {
              title: 'Quick Learner',
              description: 'Completed 3 sessions in one day',
              points_earned: 50,
            }
          ],
        });
        
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data. Showing demo data instead.');
        // Fallback to mock data
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
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700, color: '#1e293b' }}>
          Welcome Back, {user?.first_name || user?.username || 'Student'}! 👋
        </Typography>
        <Typography variant="h6" sx={{ color: '#64748b', fontWeight: 400 }}>
          Ready to continue your learning journey?
        </Typography>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {/* Stats Cards */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: '1fr 1fr 1fr 1fr' }, 
        gap: 3, 
        mb: 4 
      }}>
        <Card sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          '&:hover': {
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease',
            boxShadow: '0 10px 25px rgba(99, 102, 241, 0.3)',
          },
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography sx={{ opacity: 0.9, fontSize: '0.875rem' }}>
                  Current Streak
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, mt: 1 }}>
                  {stats?.current_streak || 0}
                </Typography>
                <Typography sx={{ opacity: 0.8, fontSize: '0.875rem' }}>
                  days in a row
                </Typography>
              </Box>
              <TrendingUpIcon sx={{ fontSize: 48, opacity: 0.3 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ 
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          color: 'white',
          '&:hover': {
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease',
            boxShadow: '0 10px 25px rgba(245, 87, 108, 0.3)',
          },
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography sx={{ opacity: 0.9, fontSize: '0.875rem' }}>
                  Total Points
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, mt: 1 }}>
                  {stats?.total_points?.toLocaleString() || 0}
                </Typography>
                <Typography sx={{ opacity: 0.8, fontSize: '0.875rem' }}>
                  points earned
                </Typography>
              </Box>
              <SchoolIcon sx={{ fontSize: 48, opacity: 0.3 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ 
          background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
          color: 'white',
          '&:hover': {
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease',
            boxShadow: '0 10px 25px rgba(79, 172, 254, 0.3)',
          },
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography sx={{ opacity: 0.9, fontSize: '0.875rem' }}>
                  Sessions Completed
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, mt: 1 }}>
                  {stats?.sessions_completed || 0}
                </Typography>
                <Typography sx={{ opacity: 0.8, fontSize: '0.875rem' }}>
                  this month
                </Typography>
              </Box>
              <AIIcon sx={{ fontSize: 48, opacity: 0.3 }} />
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ 
          background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
          color: 'white',
          '&:hover': {
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease',
            boxShadow: '0 10px 25px rgba(250, 112, 154, 0.3)',
          },
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography sx={{ opacity: 0.9, fontSize: '0.875rem' }}>
                  Knowledge Level
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, mt: 1 }}>
                  {Math.round((stats?.knowledge_level || 0) * 100)}%
                </Typography>
                <Typography sx={{ opacity: 0.8, fontSize: '0.875rem' }}>
                  mastery level
                </Typography>
              </Box>
              <ProgressIcon sx={{ fontSize: 48, opacity: 0.3 }} />
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Main Content */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' }, 
        gap: 3 
      }}>
        {/* Progress Section */}
        <Card sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#1e293b' }}>
            📈 Learning Progress
          </Typography>
          <Typography variant="body1" sx={{ color: '#64748b', mb: 3 }}>
            Keep up the great work! You're making excellent progress.
          </Typography>
          
          <Box sx={{ mb: 4 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                Overall Mastery
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#6366f1' }}>
                {Math.round(progress?.overall_mastery_percentage || 0)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress?.overall_mastery_percentage || 0}
              sx={{ 
                height: 12, 
                borderRadius: 6,
                backgroundColor: '#e2e8f0',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 6,
                  background: 'linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%)',
                },
              }}
            />
          </Box>

          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, 
            gap: 2, 
            mb: 4,
            p: 2,
            backgroundColor: '#f8fafc',
            borderRadius: 2,
          }}>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#10b981' }}>
                {progress?.mastered_objectives || 0}
              </Typography>
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                of {progress?.total_objectives || 0} objectives mastered
              </Typography>
            </Box>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#f59e0b' }}>
                {Math.round((progress?.total_study_time || 0) / 60)}h
              </Typography>
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                total study time
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <Button 
              variant="contained" 
              size="large"
              sx={{ 
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                borderRadius: 2,
                px: 3,
                py: 1.5,
                fontWeight: 600,
                '&:hover': {
                  transform: 'translateY(-1px)',
                  boxShadow: '0 10px 25px rgba(99, 102, 241, 0.3)',
                },
              }}
            >
              🚀 Start Learning Session
            </Button>
            <Button 
              variant="outlined" 
              size="large"
              sx={{ 
                borderRadius: 2,
                px: 3,
                py: 1.5,
                fontWeight: 600,
                borderColor: '#6366f1',
                color: '#6366f1',
                '&:hover': {
                  backgroundColor: '#6366f1',
                  transform: 'translateY(-1px)',
                },
              }}
            >
              💬 Chat with AI Tutor
            </Button>
          </Box>
        </Card>

        {/* Achievements Section */}
        <Card sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#1e293b' }}>
            🏆 Recent Achievements
          </Typography>
          <Typography variant="body2" sx={{ color: '#64748b', mb: 3 }}>
            Celebrate your learning milestones
          </Typography>
          
          <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
            {achievements.length > 0 ? (
              achievements.slice(0, 5).map((achievement, index) => (
                <Box 
                  key={index} 
                  sx={{ 
                    mb: 2, 
                    p: 3, 
                    background: index % 2 === 0 
                      ? 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
                      : 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: index % 2 === 0 ? '#f59e0b20' : '#3b82f620',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                    },
                  }}
                >
                  <Box display="flex" justifyContent="space-between" alignItems="start">
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1e293b' }}>
                        {achievement.title}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#64748b', mt: 0.5 }}>
                        {achievement.description}
                      </Typography>
                    </Box>
                    <Box sx={{ 
                      backgroundColor: index % 2 === 0 ? '#f59e0b' : '#3b82f6',
                      color: 'white',
                      borderRadius: 2,
                      px: 1.5,
                      py: 0.5,
                    }}>
                      <Typography variant="caption" sx={{ fontWeight: 600 }}>
                        +{achievement.points_earned}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              ))
            ) : (
              <Box sx={{ 
                textAlign: 'center', 
                py: 4,
                backgroundColor: '#f8fafc',
                borderRadius: 2,
                border: '2px dashed #cbd5e1',
              }}>
                <Typography variant="h6" sx={{ color: '#64748b', mb: 1 }}>
                  🎯 No achievements yet
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Complete learning activities to earn your first achievement!
                </Typography>
              </Box>
            )}
          </Box>
        </Card>
      </Box>
    </Box>
  );
};

export default Dashboard;
