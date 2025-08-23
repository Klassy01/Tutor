import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  Avatar,
  Divider,
  Alert,
  CircularProgress,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const Profile: React.FC = () => {
  const { user, logout, setUser } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    username: user?.username || '',
    email: user?.email || '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // Call API to update the profile (using demo endpoint for now)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update the user context with new data
      setUser({
        ...user!,
        first_name: profileData.first_name,
        last_name: profileData.last_name,
        username: profileData.username,
        email: profileData.email,
      });
      
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
      
      // Auto-clear success message
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setProfileData({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      username: user?.username || '',
      email: user?.email || '',
    });
    setIsEditing(false);
    setError('');
  };

  const getInitials = () => {
    const first = user?.first_name?.charAt(0)?.toUpperCase() || '';
    const last = user?.last_name?.charAt(0)?.toUpperCase() || '';
    return first + last || user?.username?.charAt(0)?.toUpperCase() || 'U';
  };

  if (!user) {
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
          Profile Settings 👤
        </Typography>
        <Typography variant="h6" sx={{ color: '#64748b', fontWeight: 400 }}>
          Manage your account information
        </Typography>
      </Box>

      {/* Alerts */}
      {success && (
        <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
          {success}
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {/* Profile Card */}
      <Card sx={{ maxWidth: 600, mx: 'auto' }}>
        <CardContent sx={{ p: 4 }}>
          {/* Avatar Section */}
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            alignItems: 'center', 
            mb: 4 
          }}>
            <Avatar
              sx={{
                width: 100,
                height: 100,
                mb: 2,
                fontSize: '2rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              }}
            >
              {getInitials()}
            </Avatar>
            <Typography variant="h5" sx={{ fontWeight: 600, color: '#1e293b' }}>
              {user.first_name} {user.last_name}
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748b' }}>
              @{user.username}
            </Typography>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* Profile Form */}
          <Box component="form" noValidate>
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, 
              gap: 2, 
              mb: 3 
            }}>
              <TextField
                name="first_name"
                label="First Name"
                value={profileData.first_name}
                onChange={handleChange}
                disabled={!isEditing || loading}
                variant="outlined"
                fullWidth
                size={isMobile ? "small" : "medium"}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              />
              <TextField
                name="last_name"
                label="Last Name"
                value={profileData.last_name}
                onChange={handleChange}
                disabled={!isEditing || loading}
                variant="outlined"
                fullWidth
                size={isMobile ? "small" : "medium"}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              />
            </Box>

            <TextField
              name="username"
              label="Username"
              value={profileData.username}
              onChange={handleChange}
              disabled={!isEditing || loading}
              variant="outlined"
              fullWidth
              sx={{ 
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
              size={isMobile ? "small" : "medium"}
            />

            <TextField
              name="email"
              label="Email Address"
              type="email"
              value={profileData.email}
              onChange={handleChange}
              disabled={!isEditing || loading}
              variant="outlined"
              fullWidth
              sx={{ 
                mb: 4,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
              size={isMobile ? "small" : "medium"}
            />

            {/* Action Buttons */}
            <Box sx={{ 
              display: 'flex', 
              gap: 2, 
              justifyContent: 'flex-end',
              flexWrap: 'wrap' 
            }}>
              {!isEditing ? (
                <Button
                  variant="contained"
                  startIcon={<EditIcon />}
                  onClick={() => setIsEditing(true)}
                  sx={{
                    borderRadius: 2,
                    px: 3,
                    py: 1,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5b5bd6 0%, #7c3aed 100%)',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  Edit Profile
                </Button>
              ) : (
                <>
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={handleCancel}
                    disabled={loading}
                    sx={{
                      borderRadius: 2,
                      px: 3,
                      py: 1,
                      borderColor: '#64748b',
                      color: '#64748b',
                      '&:hover': {
                        borderColor: '#475569',
                        backgroundColor: '#f8fafc',
                      },
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <SaveIcon />}
                    onClick={handleSave}
                    disabled={loading}
                    sx={{
                      borderRadius: 2,
                      px: 3,
                      py: 1,
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
                      },
                      '&:disabled': {
                        background: 'rgba(0, 0, 0, 0.12)',
                        transform: 'none',
                        boxShadow: 'none',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </Button>
                </>
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Account Info Card */}
      <Card sx={{ maxWidth: 600, mx: 'auto', mt: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            Account Information
          </Typography>
          
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: 'auto 1fr' }, 
            gap: 2, 
            mb: 2 
          }}>
            <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 500 }}>
              User ID:
            </Typography>
            <Typography variant="body2">
              #{user.id}
            </Typography>
          </Box>
          
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: 'auto 1fr' }, 
            gap: 2, 
            mb: 2 
          }}>
            <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 500 }}>
              Account Status:
            </Typography>
            <Box>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: user.is_active ? '#10b981' : '#ef4444',
                  fontWeight: 500,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 1
                }}
              >
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: user.is_active ? '#10b981' : '#ef4444',
                  }}
                />
                {user.is_active ? 'Active' : 'Inactive'}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />
          
          <Button
            variant="outlined"
            color="error"
            onClick={logout}
            sx={{
              borderRadius: 2,
              px: 3,
              py: 1,
              '&:hover': {
                backgroundColor: '#fee2e2',
              },
            }}
          >
            Sign Out
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Profile;
