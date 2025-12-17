import React from 'react';
import { Box, Typography, Alert } from '@mui/material';

export default function AuditLogsPage() {
  return (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 2 }}>Audit Logs</Typography>
      <Alert severity="info">
        Placeholder: later connect to your audit/activity log API (brief requires exportable logs).
      </Alert>
    </Box>
  );
}
