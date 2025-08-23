import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  Timer,
  Star,
  EmojiEvents,
  Assessment
} from '@mui/icons-material';
import { progressAPI } from '../../services/api';

interface SubjectProgress {
  subject_name: string;
  total_objectives: number;
  mastered_count: number;
  average_mastery: number;
  completion_percentage: number;
  study_time_minutes: number;
}

interface ProgressOverview {
  total_objectives: number;
  mastered_objectives: number;
  in_progress_objectives: number;
  overall_mastery_percentage: number;
  total_study_time: number;
}

interface Achievement {
  title: string;
  description: string;
  points_earned: number;
  date: string;
  type: string;
}

const Progress: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [timeRange, setTimeRange] = useState('week');
  const [loading, setLoading] = useState(false);
  const [overview, setOverview] = useState<ProgressOverview>({
    total_objectives: 24,
    mastered_objectives: 15,
    in_progress_objectives: 6,
    overall_mastery_percentage: 68,
    total_study_time: 480
  });

  const [subjectProgress, setSubjectProgress] = useState<SubjectProgress[]>([
    {
      subject_name: 'Mathematics',
      total_objectives: 8,
      mastered_count: 6,
      average_mastery: 0.8,
      completion_percentage: 75,
      study_time_minutes: 180
    },
    {
      subject_name: 'Science',
      total_objectives: 6,
      mastered_count: 4,
      average_mastery: 0.7,
      completion_percentage: 67,
      study_time_minutes: 120
    },
    {
      subject_name: 'History',
      total_objectives: 5,
      mastered_count: 3,
      average_mastery: 0.6,
      completion_percentage: 60,
      study_time_minutes: 100
    },
    {
      subject_name: 'English',
      total_objectives: 5,
      mastered_count: 2,
      average_mastery: 0.5,
      completion_percentage: 40,
      study_time_minutes: 80
    }
  ]);

  const achievements: Achievement[] = [
    {
      title: '7-Day Streak',
      description: 'Maintained learning for 7 consecutive days',
      points_earned: 100,
      date: '2025-08-22',
      type: 'streak'
    },
    {
      title: 'Quick Learner',
      description: 'Completed 3 sessions in one day',
      points_earned: 50,
      date: '2025-08-21',
      type: 'milestone'
    },
    {
      title: 'Math Master',
      description: 'Achieved 80% mastery in Mathematics',
      points_earned: 150,
      date: '2025-08-20',
      type: 'subject'
    }
  ];

  useEffect(() => {
    fetchProgressData();
  }, [timeRange]);

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      
      // Try to get real progress data
      const response = await progressAPI.getOverview();
      const apiData = response.data;
      
      // Transform API data to component format
      if (apiData.subject_progress && Array.isArray(apiData.subject_progress)) {
        setSubjectProgress(apiData.subject_progress.map((subject: any) => ({
          subject_name: subject.subject_name || subject.name || 'Unknown',
          total_objectives: subject.total_objectives || 10,
          mastered_count: subject.mastered_count || 0,
          average_mastery: subject.average_mastery || 0,
          completion_percentage: subject.completion_percentage || 0,
          study_time_minutes: subject.study_time_minutes || 0
        })));
      }
      
      if (apiData.overview) {
        setOverview({
          total_objectives: apiData.overview.total_objectives || 50,
          mastered_objectives: apiData.overview.mastered_objectives || 25,
          in_progress_objectives: apiData.overview.in_progress_objectives || 15,
          overall_mastery_percentage: apiData.overview.overall_mastery_percentage || 68,
          total_study_time: apiData.overview.total_study_time || 180
        });
      }
      
    } catch (error) {
      console.error('Error fetching progress data, using defaults:', error);
      // Keep the existing default data that's already set
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ 
    title, 
    value, 
    unit = '', 
    icon, 
    color = 'primary' 
  }: {
    title: string;
    value: number;
    unit?: string;
    icon: React.ReactNode;
    color?: 'primary' | 'secondary' | 'success' | 'warning';
  }) => {
    const gradients = {
      primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      secondary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      success: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      warning: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    };

    return (
      <Card sx={{ 
        height: '100%',
        background: gradients[color],
        color: 'white',
        '&:hover': {
          transform: 'translateY(-4px)',
          transition: 'all 0.3s ease',
          boxShadow: '0 12px 28px rgba(0, 0, 0, 0.2)',
        },
      }}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography sx={{ opacity: 0.9, fontSize: '0.875rem', mb: 1 }}>
                {title}
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700, mb: 0.5 }}>
                {value}{unit}
              </Typography>
            </Box>
            <Box sx={{ opacity: 0.3, fontSize: 48 }}>
              {icon}
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  const OverviewTab = () => (
    <Box>
      {/* Key Statistics */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: '1fr 1fr 1fr 1fr' }, 
        gap: 3, 
        mb: 4 
      }}>
        <StatCard
          title="Overall Mastery"
          value={overview.overall_mastery_percentage}
          unit="%"
          icon={<Assessment />}
          color="primary"
        />
        <StatCard
          title="Objectives Mastered"
          value={overview.mastered_objectives}
          unit={` of ${overview.total_objectives}`}
          icon={<EmojiEvents />}
          color="success"
        />
        <StatCard
          title="Study Time"
          value={Math.round(overview.total_study_time / 60)}
          unit="h"
          icon={<Timer />}
          color="warning"
        />
        <StatCard
          title="In Progress"
          value={overview.in_progress_objectives}
          unit=" objectives"
          icon={<TrendingUp />}
          color="secondary"
        />
      </Box>

      {/* Subject Progress */}
      <Card sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#1e293b', mb: 3 }}>
          📚 Subject Progress
        </Typography>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
          gap: 3 
        }}>
          {subjectProgress.map((subject, index) => (
            <Card key={index} variant="outlined" sx={{ 
              '&:hover': { 
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                transform: 'translateY(-2px)',
                transition: 'all 0.3s ease'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {subject.subject_name}
                  </Typography>
                  <Chip 
                    label={`${subject.completion_percentage}%`}
                    color={subject.completion_percentage >= 70 ? 'success' : 
                           subject.completion_percentage >= 50 ? 'warning' : 'default'}
                    sx={{ fontWeight: 600 }}
                  />
                </Box>
                
                <LinearProgress 
                  variant="determinate" 
                  value={subject.completion_percentage} 
                  sx={{ 
                    mb: 2, 
                    height: 10, 
                    borderRadius: 5,
                    backgroundColor: '#e2e8f0',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 5,
                      background: subject.completion_percentage >= 70 ? 
                        'linear-gradient(90deg, #10b981 0%, #34d399 100%)' : 
                        subject.completion_percentage >= 50 ? 
                        'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)' :
                        'linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%)',
                    }
                  }}
                />
                
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    ✅ Mastered: {subject.mastered_count}/{subject.total_objectives}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    ⏱️ {Math.round(subject.study_time_minutes / 60)}h
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      </Card>

      {/* Learning Streak */}
      <Card sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#1e293b', mb: 3 }}>
          🔥 Learning Streak & Consistency
        </Typography>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: 'auto auto 1fr' }, 
          gap: 4,
          alignItems: 'center'
        }}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h2" sx={{ 
              fontWeight: 700, 
              background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>
              5
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748b', fontWeight: 600 }}>
              Current Streak
            </Typography>
          </Box>
          
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h2" sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>
              12
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748b', fontWeight: 600 }}>
              Longest Streak
            </Typography>
          </Box>
          
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                Weekly Consistency
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#6366f1' }}>
                85%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={85} 
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
        </Box>
      </Card>
    </Box>
  );

  const DetailedTab = () => (
    <Paper sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">
          Detailed Progress Report
        </Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <MenuItem value="week">Last Week</MenuItem>
            <MenuItem value="month">Last Month</MenuItem>
            <MenuItem value="quarter">Last Quarter</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Subject</TableCell>
              <TableCell>Objectives</TableCell>
              <TableCell>Mastery Level</TableCell>
              <TableCell>Study Time</TableCell>
              <TableCell>Last Activity</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {subjectProgress.map((subject, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Typography variant="subtitle2">
                    {subject.subject_name}
                  </Typography>
                </TableCell>
                <TableCell>
                  {subject.mastered_count}/{subject.total_objectives}
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <LinearProgress 
                      variant="determinate" 
                      value={subject.average_mastery * 100} 
                      sx={{ width: 100, height: 6 }}
                    />
                    <Typography variant="body2">
                      {Math.round(subject.average_mastery * 100)}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  {Math.round(subject.study_time_minutes / 60)}h
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="textSecondary">
                    2 days ago
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={subject.completion_percentage >= 70 ? 'Excellent' : 
                           subject.completion_percentage >= 50 ? 'Good' : 'Needs Work'}
                    color={subject.completion_percentage >= 70 ? 'success' : 
                           subject.completion_percentage >= 50 ? 'warning' : 'default'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );

  const AchievementsTab = () => (
    <Box>
      <Card sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#1e293b', mb: 3 }}>
          🏆 Recent Achievements
        </Typography>
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: '1fr 1fr 1fr' }, 
          gap: 3 
        }}>
          {achievements.map((achievement, index) => (
            <Card 
              key={index} 
              variant="outlined" 
              sx={{ 
                background: index % 3 === 0 
                  ? 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
                  : index % 3 === 1
                  ? 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)'
                  : 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
                border: '1px solid',
                borderColor: index % 3 === 0 ? '#f59e0b20' : index % 3 === 1 ? '#3b82f620' : '#10b98120',
                '&:hover': { 
                  transform: 'translateY(-4px)',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)',
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Box sx={{ 
                    p: 2, 
                    borderRadius: 2,
                    backgroundColor: 'rgba(255, 215, 0, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <EmojiEvents sx={{ color: '#f59e0b', fontSize: 28 }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
                      {achievement.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      {achievement.description}
                    </Typography>
                  </Box>
                </Box>
                
                <Divider sx={{ mb: 2 }} />
                
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Star sx={{ color: '#f59e0b', fontSize: 18 }} />
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      +{achievement.points_earned} points
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    {new Date(achievement.date).toLocaleDateString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      </Card>

      <Card sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#1e293b', mb: 3 }}>
          🎯 Achievement Progress
        </Typography>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, 
          gap: 3 
        }}>
          <Card 
            variant="outlined" 
            sx={{ 
              '&:hover': { 
                transform: 'translateY(-2px)',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Box sx={{ 
                  p: 1.5, 
                  borderRadius: 2,
                  backgroundColor: '#e0f2fe',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Timer sx={{ color: '#0277bd', fontSize: 24 }} />
                </Box>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Dedicated Learner
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    Complete 50 learning sessions
                  </Typography>
                </Box>
              </Box>
              
              <LinearProgress 
                variant="determinate" 
                value={60} 
                sx={{ 
                  mb: 1,
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: '#e2e8f0',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                    background: 'linear-gradient(90deg, #0277bd 0%, #03a9f4 100%)',
                  },
                }}
              />
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                30/50 sessions completed
              </Typography>
            </CardContent>
          </Card>
          
          <Card 
            variant="outlined"
            sx={{ 
              '&:hover': { 
                transform: 'translateY(-2px)',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Box sx={{ 
                  p: 1.5, 
                  borderRadius: 2,
                  backgroundColor: '#e8f5e8',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <TrendingUp sx={{ color: '#2e7d32', fontSize: 24 }} />
                </Box>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Knowledge Seeker
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    Master 20 different topics
                  </Typography>
                </Box>
              </Box>
              
              <LinearProgress 
                variant="determinate" 
                value={75} 
                sx={{ 
                  mb: 1,
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: '#e2e8f0',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                    background: 'linear-gradient(90deg, #2e7d32 0%, #4caf50 100%)',
                  },
                }}
              />
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                15/20 topics mastered
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Card>
    </Box>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700, color: '#1e293b' }}>
          📊 Progress Tracking
        </Typography>
        <Typography variant="h6" sx={{ color: '#64748b', fontWeight: 400 }}>
          Monitor your learning journey and celebrate achievements
        </Typography>
      </Box>

      {/* Tabs */}
      <Card sx={{ mb: 4, overflow: 'hidden' }}>
        <Tabs 
          value={activeTab} 
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{
            '& .MuiTab-root': {
              fontWeight: 600,
              textTransform: 'none',
              fontSize: '1rem',
            },
            '& .Mui-selected': {
              color: '#6366f1 !important',
            },
          }}
        >
          <Tab label="📈 Overview" />
          <Tab label="📋 Detailed Report" />
          <Tab label="🏆 Achievements" />
        </Tabs>
      </Card>

      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
        </Box>
      )}

      {!loading && activeTab === 0 && <OverviewTab />}
      {!loading && activeTab === 1 && <DetailedTab />}
      {!loading && activeTab === 2 && <AchievementsTab />}
    </Box>
  );
};

export default Progress;
