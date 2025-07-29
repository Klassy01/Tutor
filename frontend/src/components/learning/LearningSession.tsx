import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const LearningSession: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Learning Session
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Learning session component coming soon...
        </Typography>
      </Paper>
    </Box>
  );
};

export default LearningSession;
