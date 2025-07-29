import React from 'react';
import { Typography, Box, Paper } from '@mui/material';

const Progress: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Progress Tracking
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Progress tracking component coming soon...
        </Typography>
      </Paper>
    </Box>
  );
};

export default Progress;
