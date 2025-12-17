import React, { useEffect, useMemo, useState } from 'react';
import {
  Box, Typography, Button, Paper, Table, TableBody, TableCell,
  TableHead, TableRow, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, Alert, IconButton, MenuItem, 
  FormControlLabel, Checkbox, CircularProgress, LinearProgress
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SettingsIcon from '@mui/icons-material/Settings';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useNavigate } from 'react-router-dom';
import tutorService from '../../services/tutorService';
import { http } from '../../utils/request';

export default function TutorsPage() {
  const navigate = useNavigate();
  const origin = useMemo(() => window.location.origin, []);

  const [tutors, setTutors] = useState([]);
  const [err, setErr] = useState('');
  const [open, setOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [progress, setProgress] = useState('');
  
  const [form, setForm] = useState({ 
    // Tutor fields
    name: '', 
    description: '', 
    target_language: 'en',
    // Avatar fields
    avatar_name: '',
    avatar_model: 'MuseTalk',
    tts_model: 'edge-tts',
    timbre: '',
    ref_text: '',
    avatar_blur: false,
    support_clone: false,
    prompt_face: null,
    prompt_voice: null
  });

  const load = async () => {
    setErr('');
    try {
      const res = await tutorService.list();
      const data = Array.isArray(res) ? res : (res.data || res);
      setTutors(data || []);
    } catch (e) {
      setErr(e?.message || 'Failed to load tutors');
    }
  };

  useEffect(() => { load(); }, []);

  const onCreate = async () => {
    if (!form.name.trim()) {
      setErr('Tutor name is required');
      return;
    }
    if (!form.avatar_name.trim()) {
      setErr('Avatar name is required');
      return;
    }
    if (!form.prompt_face) {
      setErr('Avatar video file is required');
      return;
    }
    if (form.support_clone && !form.prompt_voice) {
      setErr('Voice file is required when voice cloning is enabled');
      return;
    }

    setErr('');
    setCreating(true);
    setProgress('Creating tutor with avatar (this may take 2-5 minutes)...');
    
    try {
      // Unified API call - creates both tutor and avatar
      const formData = new FormData();
      
      // Tutor fields
      formData.append('name', form.name);
      formData.append('description', form.description || '');
      formData.append('target_language', form.target_language);
      
      // Avatar fields
      formData.append('avatar_name', form.avatar_name);
      formData.append('avatar_model', form.avatar_model);
      formData.append('tts_model', form.tts_model);
      formData.append('timbre', form.timbre || '');
      formData.append('avatar_blur', form.avatar_blur);
      formData.append('support_clone', form.support_clone);
      formData.append('ref_text', form.ref_text || '');
      formData.append('prompt_face', form.prompt_face);
      
      if (form.support_clone && form.prompt_voice) {
        formData.append('prompt_voice', form.prompt_voice);
      }
      
      await http.post('/tutors/create-with-avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000 // 5 minutes
      });
      
      setProgress('✅ Tutor and avatar created successfully!');
      
      setTimeout(() => {
        setOpen(false);
        setForm({ 
          name: '', 
          description: '', 
          target_language: 'en',
          avatar_name: '',
          avatar_model: 'MuseTalk',
          tts_model: 'edge-tts',
          timbre: '',
          ref_text: '',
          avatar_blur: false,
          support_clone: false,
          prompt_face: null,
          prompt_voice: null
        });
        load();
      }, 1500);
      
    } catch (e) {
      console.error('Creation error:', e);
      setErr(e?.response?.data?.detail || e?.message || 'Failed to create tutor with avatar');
    } finally {
      setCreating(false);
      setTimeout(() => setProgress(''), 2000);
    }
  };

  const copy = async (text) => {
    await navigator.clipboard.writeText(text);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>Tutors</Typography>
        <Button variant="contained" onClick={() => setOpen(true)}>Create Tutor</Button>
      </Box>

      {err && <Alert severity="error" sx={{ mb: 2 }}>{err}</Alert>}

      <Paper sx={{ overflow: 'hidden' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Target Language</TableCell>
              <TableCell>Student Login URL</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tutors.map((t) => {
              const url = `${origin}/session/${t.id}/login`;
              return (
                <TableRow key={t.id} hover>
                  <TableCell>{t.id}</TableCell>
                  <TableCell>{t.name}</TableCell>
                  <TableCell>{t.target_language || 'en'}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {url}
                      </Typography>
                      <IconButton size="small" onClick={() => copy(url)} title="Copy">
                        <ContentCopyIcon fontSize="inherit" />
                      </IconButton>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      startIcon={<SettingsIcon />}
                      onClick={() => navigate(`/admin/tutors/${t.id}`)}
                    >
                      Manage
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
            {tutors.length === 0 && (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography sx={{ py: 2, textAlign: 'center', color: 'text.secondary' }}>
                    No tutors yet.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Paper>

      <Dialog open={open} onClose={() => !creating && setOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Create Tutor with Avatar</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {err && <Alert severity="error" sx={{ mb: 2 }}>{err}</Alert>}
          {progress && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="primary" sx={{ mb: 1 }}>{progress}</Typography>
              <LinearProgress />
            </Box>
          )}

          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2 }}>
            Tutor Information
          </Typography>
          
          <TextField
            label="Tutor Name" 
            fullWidth 
            required 
            sx={{ mb: 2 }}
            disabled={creating}
            value={form.name} 
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
          
          <TextField
            label="Description" 
            fullWidth 
            multiline
            rows={2}
            sx={{ mb: 2 }}
            disabled={creating}
            value={form.description} 
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          
          <TextField
            label="Target Language" 
            fullWidth
            select
            sx={{ mb: 3 }}
            disabled={creating}
            value={form.target_language} 
            onChange={(e) => setForm({ ...form, target_language: e.target.value })}
          >
            <MenuItem value="en">English</MenuItem>
            <MenuItem value="zh-CN">Chinese (Simplified)</MenuItem>
            <MenuItem value="es">Spanish</MenuItem>
            <MenuItem value="fr">French</MenuItem>
          </TextField>

          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2 }}>
            Avatar Configuration
          </Typography>

          <TextField
            label="Avatar Name" 
            fullWidth 
            required 
            sx={{ mb: 2 }}
            disabled={creating}
            helperText="Unique identifier for this avatar"
            value={form.avatar_name} 
            onChange={(e) => setForm({ ...form, avatar_name: e.target.value })}
          />

          <TextField
            label="Avatar Model" 
            fullWidth
            select
            sx={{ mb: 2 }}
            disabled={creating}
            value={form.avatar_model} 
            onChange={(e) => setForm({ ...form, avatar_model: e.target.value })}
          >
            <MenuItem value="MuseTalk">MuseTalk (Recommended)</MenuItem>
            <MenuItem value="wav2lip">Wav2Lip</MenuItem>
            <MenuItem value="ultralight">UltraLight</MenuItem>
          </TextField>

          <TextField
            label="TTS Model" 
            fullWidth
            select
            sx={{ mb: 2 }}
            disabled={creating}
            value={form.tts_model} 
            onChange={(e) => setForm({ ...form, tts_model: e.target.value })}
          >
            <MenuItem value="edge-tts">Edge TTS (Fast)</MenuItem>
            <MenuItem value="cosyvoice">CosyVoice (Natural)</MenuItem>
            <MenuItem value="sovits">SoVITS (Clone)</MenuItem>
          </TextField>

          <TextField
            label="Voice Timbre" 
            fullWidth
            sx={{ mb: 2 }}
            disabled={creating || form.support_clone}
            helperText="Voice character identifier (e.g., zh-CN-XiaoxiaoNeural for Edge TTS)"
            value={form.timbre} 
            onChange={(e) => setForm({ ...form, timbre: e.target.value })}
          />

          <FormControlLabel
            control={
              <Checkbox 
                checked={form.avatar_blur} 
                disabled={creating}
                onChange={(e) => setForm({ ...form, avatar_blur: e.target.checked })}
              />
            }
            label="Enable Avatar Blur Effect"
            sx={{ mb: 2 }}
          />

          <FormControlLabel
            control={
              <Checkbox 
                checked={form.support_clone} 
                disabled={creating}
                onChange={(e) => setForm({ ...form, support_clone: e.target.checked })}
              />
            }
            label="Enable Voice Cloning"
            sx={{ mb: 2 }}
          />

          {form.support_clone && (
            <TextField
              label="Reference Text" 
              fullWidth
              multiline
              rows={2}
              sx={{ mb: 2 }}
              disabled={creating}
              helperText="Text for voice cloning reference"
              value={form.ref_text} 
              onChange={(e) => setForm({ ...form, ref_text: e.target.value })}
            />
          )}

          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              component="label"
              fullWidth
              disabled={creating}
              startIcon={<CloudUploadIcon />}
              sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
            >
              {form.prompt_face ? `Video: ${form.prompt_face.name}` : 'Upload Avatar Video (Required)'}
              <input
                type="file"
                hidden
                accept="video/*"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) setForm({ ...form, prompt_face: file });
                }}
              />
            </Button>
            <Typography variant="caption" color="text.secondary">
              Upload a short video of the person's face (MP4 recommended)
            </Typography>
          </Box>

          {form.support_clone && (
            <Box sx={{ mb: 2 }}>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                disabled={creating}
                startIcon={<CloudUploadIcon />}
                sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
              >
                {form.prompt_voice ? `Audio: ${form.prompt_voice.name}` : 'Upload Voice Sample (Required for Cloning)'}
                <input
                  type="file"
                  hidden
                  accept="audio/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) setForm({ ...form, prompt_voice: file });
                  }}
                />
              </Button>
              <Typography variant="caption" color="text.secondary">
                Upload a clear audio sample (WAV/MP3, 10-30 seconds recommended)
              </Typography>
            </Box>
          )}

        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={creating}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={onCreate} 
            disabled={!form.name.trim() || !form.avatar_name.trim() || !form.prompt_face || creating}
            startIcon={creating ? <CircularProgress size={20} /> : null}
          >
            {creating ? 'Creating...' : 'Create Tutor & Avatar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
