# Avatar System Quick Start

## Environment Setup

### 1. Environment Variables

Create a `.env` file in `app_backend/`:

```bash
# Database
DATABASE_URL=sqlite:///./virtual_tutor.db

# JWT
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Avatar Services
LIPSYNC_SERVICE_URL=http://localhost:8615
TTS_SERVICE_URL=http://localhost:8604

# CORS
FRONTEND_URL=http://localhost:3000
```

### 2. Install Dependencies

If not already in requirements.txt, add:

```txt
httpx>=0.24.0  # For async HTTP requests (alternative to requests)
```

### 3. Database Migration

```bash
# From app_backend directory
cd /Users/murphyxu/Code/ra/virtual_tutor/app_backend

# Create migration
alembic revision --autogenerate -m "Add avatar table"

# Apply migration
alembic upgrade head
```

## Testing the Avatar API

### 1. Start Services

Terminal 1 - Backend:
```bash
cd /Users/murphyxu/Code/ra/virtual_tutor/app_backend
uvicorn app.main:app --reload --port 8000
```

Terminal 2 - Lip-Sync Service (from mageurite):
```bash
cd /Users/murphyxu/Code/ra/mageurite_virtual_tutor/lip-sync
conda activate nerfstream
python live_server.py
```

### 2. Test API Endpoints

```bash
# Login as admin
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=your_password" \
  | jq -r '.access_token')

# List avatars
curl -X GET "http://localhost:8000/api/avatars/list" \
  -H "Authorization: Bearer $TOKEN"

# Get TTS models
curl -X GET "http://localhost:8000/api/avatars/tts-models" \
  -H "Authorization: Bearer $TOKEN"

# Get avatar models
curl -X GET "http://localhost:8000/api/avatars/avatar-models" \
  -H "Authorization: Bearer $TOKEN"

# Create avatar (example with file)
curl -X POST "http://localhost:8000/api/avatars/create" \
  -H "Authorization: Bearer $TOKEN" \
  -F "tutor_id=1" \
  -F "name=test_avatar_1" \
  -F "display_name=Test Avatar" \
  -F "avatar_model=MuseTalk" \
  -F "tts_model=edge-tts" \
  -F "prompt_face=@/path/to/video.mp4"

# Start avatar
curl -X POST "http://localhost:8000/api/avatars/1/start" \
  -H "Authorization: Bearer $TOKEN"

# Get preview
curl -X GET "http://localhost:8000/api/avatars/1/preview" \
  -H "Authorization: Bearer $TOKEN" \
  --output avatar_preview.png

# Delete avatar
curl -X DELETE "http://localhost:8000/api/avatars/1" \
  -H "Authorization: Bearer $TOKEN"
```

## Frontend Integration Example

### React Component

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function AvatarManager() {
  const [avatars, setAvatars] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Get token from your auth service
  const token = localStorage.getItem('access_token');
  
  const fetchAvatars = async () => {
    try {
      const response = await axios.get('/api/avatars/list', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAvatars(response.data.avatars);
    } catch (error) {
      console.error('Error fetching avatars:', error);
    }
  };
  
  const createAvatar = async (formData) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/avatars/create', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        timeout: 200000 // 200 seconds
      });
      alert(`Avatar created: ${response.data.name}`);
      fetchAvatars();
    } catch (error) {
      console.error('Error creating avatar:', error);
      alert('Failed to create avatar');
    } finally {
      setLoading(false);
    }
  };
  
  const startAvatar = async (avatarId) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `/api/avatars/${avatarId}/start`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
          timeout: 300000 // 5 minutes
        }
      );
      alert(response.data.message);
      fetchAvatars();
    } catch (error) {
      console.error('Error starting avatar:', error);
      alert('Failed to start avatar');
    } finally {
      setLoading(false);
    }
  };
  
  const deleteAvatar = async (avatarId) => {
    if (!confirm('Are you sure you want to delete this avatar?')) return;
    
    try {
      await axios.delete(`/api/avatars/${avatarId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Avatar deleted');
      fetchAvatars();
    } catch (error) {
      console.error('Error deleting avatar:', error);
      alert('Failed to delete avatar');
    }
  };
  
  React.useEffect(() => {
    fetchAvatars();
  }, []);
  
  return (
    <div>
      <h1>Avatar Manager</h1>
      
      {/* Avatar Creation Form */}
      <form onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        createAvatar(formData);
      }}>
        <input name="tutor_id" type="number" required placeholder="Tutor ID" />
        <input name="name" type="text" required placeholder="Avatar Name" />
        <input name="display_name" type="text" placeholder="Display Name" />
        <select name="avatar_model">
          <option value="MuseTalk">MuseTalk</option>
          <option value="wav2lip">Wav2Lip</option>
          <option value="ultralight">UltraLight</option>
        </select>
        <select name="tts_model">
          <option value="edge-tts">Edge TTS</option>
          <option value="cosyvoice">CosyVoice</option>
          <option value="sovits">GPT-SoVITS</option>
        </select>
        <input name="prompt_face" type="file" accept="video/*" required />
        <button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Avatar'}
        </button>
      </form>
      
      {/* Avatar List */}
      <div>
        {avatars.map(avatar => (
          <div key={avatar.id}>
            <h3>{avatar.display_name} ({avatar.name})</h3>
            <p>Status: {avatar.status}</p>
            <p>Model: {avatar.avatar_model}</p>
            <p>TTS: {avatar.tts_model}</p>
            {avatar.preview_image_path && (
              <img 
                src={`/api/avatars/${avatar.id}/preview`} 
                alt="Preview"
                style={{width: '200px'}}
              />
            )}
            <button 
              onClick={() => startAvatar(avatar.id)}
              disabled={loading || avatar.status === 'active'}
            >
              Start
            </button>
            <button 
              onClick={() => deleteAvatar(avatar.id)}
              disabled={loading}
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AvatarManager;
```

## Common Issues

### 1. "Avatar service not responding"
**Solution**: Ensure lip-sync service is running on port 8615
```bash
curl http://localhost:8615/avatar/get_avatars
```

### 2. "Avatar creation timeout"
**Solution**: Increase timeout in frontend request (default should be 200s)

### 3. "Permission denied"
**Solution**: Verify the avatar's tutor belongs to the authenticated admin

### 4. Database migration fails
**Solution**: Drop and recreate database (development only!)
```bash
rm virtual_tutor.db
alembic upgrade head
python -m app.initial_data  # Create initial admin user
```

## Next Steps

1. **Implement frontend UI** using the example above
2. **Add progress indicators** for long-running operations
3. **Implement avatar status polling** to show real-time status
4. **Add file upload validation** (size, format, duration)
5. **Integrate with chat system** to use avatars in conversations

See `AVATAR_SYSTEM.md` for complete documentation.
