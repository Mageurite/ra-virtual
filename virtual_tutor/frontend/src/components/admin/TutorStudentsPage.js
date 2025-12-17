import React, { useEffect, useMemo, useState } from 'react';
import {
  Box, Typography, Paper, Table, TableHead, TableRow, TableCell, TableBody,
  Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Alert,
  Chip
} from '@mui/material';
import { useParams } from 'react-router-dom';
import adminStudentService from '../../services/adminStudentService';

const PASSWORD_FIELD = 'password'; // 如果你后端是 new_password，就改成 'new_password'

export default function TutorStudentsPage() {
  const { tutorId } = useParams();
  const tid = Number(tutorId);

  const [students, setStudents] = useState([]);
  const [err, setErr] = useState('');

  const [openCreate, setOpenCreate] = useState(false);
  const [createForm, setCreateForm] = useState({ email: '', name: '', password: '' });

  const [openReset, setOpenReset] = useState(false);
  const [resetTarget, setResetTarget] = useState(null);
  const [newPassword, setNewPassword] = useState('');

  const origin = useMemo(() => window.location.origin, []);
  const loginUrl = `${origin}/session/${tid}/login`;

  const load = async () => {
    setErr('');
    try {
      const res = await adminStudentService.list(tid);
      const data = Array.isArray(res) ? res : (res.data || res);
      setStudents(data || []);
    } catch (e) {
      setErr(e?.message || 'Failed to load students');
    }
  };

  useEffect(() => { load(); }, [tid]);

  const createStudent = async () => {
    setErr('');
    try {
      await adminStudentService.create(tid, createForm);
      setOpenCreate(false);
      setCreateForm({ email: '', name: '', password: '' });
      await load();
    } catch (e) {
      setErr(e?.message || 'Failed to create student');
    }
  };

  const toggleActive = async (stu) => {
    setErr('');
    try {
      await adminStudentService.update(tid, stu.id, { is_active: !stu.is_active });
      await load();
    } catch (e) {
      setErr(e?.message || 'Failed to update student status');
    }
  };

  const openResetPwd = (stu) => {
    setResetTarget(stu);
    setNewPassword('');
    setOpenReset(true);
  };

  const doResetPwd = async () => {
    if (!resetTarget) return;
    setErr('');
    try {
      await adminStudentService.update(tid, resetTarget.id, { [PASSWORD_FIELD]: newPassword });
      setOpenReset(false);
      setResetTarget(null);
      setNewPassword('');
      await load();
    } catch (e) {
      setErr(e?.message || 'Failed to reset password');
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, gap: 2, flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>Tutor #{tid}</Typography>
          <Typography variant="body2" color="text.secondary">
            Student login URL: <span style={{ fontFamily: 'monospace' }}>{loginUrl}</span>
          </Typography>
        </Box>
        <Button variant="contained" onClick={() => setOpenCreate(true)}>
          Create Student
        </Button>
      </Box>

      {err && <Alert severity="error" sx={{ mb: 2 }}>{err}</Alert>}

      <Paper sx={{ overflow: 'hidden' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Email / Student ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {students.map((s) => (
              <TableRow key={s.id} hover>
                <TableCell>{s.id}</TableCell>
                <TableCell>{s.email}</TableCell>
                <TableCell>{s.name || '-'}</TableCell>
                <TableCell>
                  {s.is_active
                    ? <Chip size="small" label="active" color="success" />
                    : <Chip size="small" label="disabled" color="default" />
                  }
                </TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={() => toggleActive(s)}>
                    {s.is_active ? 'Disable' : 'Enable'}
                  </Button>
                  <Button size="small" onClick={() => openResetPwd(s)}>
                    Reset Password
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {students.length === 0 && (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography sx={{ py: 2, textAlign: 'center', color: 'text.secondary' }}>
                    No students yet.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Paper>

      {/* Create student */}
      <Dialog open={openCreate} onClose={() => setOpenCreate(false)} fullWidth maxWidth="sm">
        <DialogTitle>Create Student</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <TextField
            label="Email / Student ID" fullWidth required sx={{ mb: 2 }}
            value={createForm.email}
            onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
          />
          <TextField
            label="Display Name" fullWidth sx={{ mb: 2 }}
            value={createForm.name}
            onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
          />
          <TextField
            label="Initial Password" fullWidth required
            value={createForm.password}
            onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreate(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={createStudent}
            disabled={!createForm.email.trim() || !createForm.password.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reset password */}
      <Dialog open={openReset} onClose={() => setOpenReset(false)} fullWidth maxWidth="xs">
        <DialogTitle>Reset Password</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Typography variant="body2" sx={{ mb: 2 }} color="text.secondary">
            Student: {resetTarget?.email}
          </Typography>
          <TextField
            label="New Password"
            fullWidth
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenReset(false)}>Cancel</Button>
          <Button variant="contained" onClick={doResetPwd} disabled={!newPassword.trim()}>
            Reset
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
