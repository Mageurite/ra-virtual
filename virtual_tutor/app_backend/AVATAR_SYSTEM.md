# Avatar System for Virtual Tutor

This document describes the Avatar management system implemented for the Virtual Tutor application.

## Overview

The Avatar system enables tutors to create and manage virtual avatars for AI-powered video conversations. Based on the mageurite_virtual_tutor implementation, this system integrates:

- **Digital Avatar Creation**: Upload video files to create lifelike avatars
- **Multi-Model Support**: MuseTalk, Wav2Lip, UltraLight models
- **Voice Cloning**: TTS with multiple voice models (Edge-TTS, CosyVoice, GPT-SoVITS, Tacotron2)
- **Real-time Video**: WebRTC streaming for low-latency communication
- **Multi-Tenant Architecture**: Each avatar belongs to a specific tutor

## Architecture

### Database Model

**Avatar Table**:
```python
class Avatar(Base):
    id: int                        # Primary key
    tutor_id: int                  # Foreign key to tutors table
    name: str                      # Unique avatar identifier
    display_name: str              # Human-readable name
    avatar_model: str              # MuseTalk, wav2lip, ultralight
    tts_model: str                 # edge-tts, cosyvoice, sovits, tacotron
    timbre: str                    # Voice timbre identifier
    avatar_blur: bool              # Apply blur effect
    support_clone: bool            # Voice cloning support
    status: str                    # active, inactive, processing, error
    preview_image_path: str        # Path to preview image
    video_path: str                # Source video path
    audio_path: str                # Reference audio path
    engine_url: str                # WebRTC service URL
    created_at: datetime
    updated_at: datetime
```

### API Endpoints

**Base URL**: `/api/avatars`

#### 1. List Avatars
```
GET /api/avatars/list?tutor_id={tutor_id}
```
Returns all avatars for the authenticated admin, optionally filtered by tutor.

**Response**:
```json
{
  "avatars": [
    {
      "id": 1,
      "name": "avatar_john",
      "display_name": "John's Avatar",
      "status": "active",
      "avatar_model": "MuseTalk",
      "tts_model": "edge-tts",
      ...
    }
  ],
  "total": 1
}
```

#### 2. Create Avatar
```
POST /api/avatars/create
Content-Type: multipart/form-data
```

**Form Data**:
- `tutor_id`: int (required)
- `name`: str (required, unique identifier)
- `display_name`: str (optional)
- `description`: str (optional)
- `avatar_model`: str (default: "MuseTalk")
- `tts_model`: str (default: "edge-tts")
- `timbre`: str (optional, voice character)
- `avatar_blur`: bool (default: false)
- `support_clone`: bool (default: false)
- `prompt_face`: File (required, video file)
- `prompt_voice`: File (optional, audio file)

**Response**:
```json
{
  "id": 1,
  "name": "avatar_john",
  "display_name": "John's Avatar",
  "status": "inactive",
  "preview_image_path": "/data/avatars/avatar_john/full_imgs/00000000.png",
  ...
}
```

#### 3. Start Avatar
```
POST /api/avatars/{avatar_id}/start
```

Starts the WebRTC service for the avatar. Can take up to 5 minutes.

**Body** (optional):
```json
{
  "ref_file": "ref_audio/silence.wav"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Avatar 'avatar_john' started successfully",
  "engine_url": "http://localhost:8615"
}
```

#### 4. Get Avatar Preview
```
GET /api/avatars/{avatar_id}/preview
```

Returns the preview image for the avatar.

**Response**: Image file (PNG)

#### 5. Delete Avatar
```
DELETE /api/avatars/{avatar_id}
```

Deletes the avatar from both the service and database.

**Response**:
```json
{
  "status": "success",
  "message": "Avatar 'avatar_john' deleted successfully"
}
```

#### 6. Update Avatar
```
PATCH /api/avatars/{avatar_id}
```

Updates avatar metadata (not video/audio files).

**Body**:
```json
{
  "display_name": "New Display Name",
  "description": "Updated description",
  "status": "active"
}
```

#### 7. WebRTC Proxy
```
GET/POST /api/avatars/webrtc/{path}
```

Proxies WebRTC requests to the lip-sync service for real-time video communication.

#### 8. Get TTS Models
```
GET /api/avatars/tts-models
```

Returns list of available TTS models.

#### 9. Get Avatar Models
```
GET /api/avatars/avatar-models
```

Returns list of supported avatar models.

## Integration with Services

The Avatar system integrates with external microservices:

### 1. Lip-Sync Service (Port 8615)
- **Avatar Creation**: Processes video files to create avatar assets
- **Avatar Management**: Stores avatar data (images, coordinates, latents)
- **WebRTC Streaming**: Provides real-time video stream
- **Avatar Lifecycle**: Start, stop, delete operations

### 2. TTS Service (Port 8604)
- **Voice Models**: Edge-TTS, CosyVoice, GPT-SoVITS, Tacotron2
- **Voice Cloning**: Custom voice generation
- **Audio Streaming**: Real-time TTS for avatar speech

## Configuration

Environment variables:

```bash
# Service URLs
LIPSYNC_SERVICE_URL=http://localhost:8615
TTS_SERVICE_URL=http://localhost:8604

# Database (configured in app.core.config)
DATABASE_URL=sqlite:///./virtual_tutor.db
```

## Usage Example

### Python Client Example

```python
import httpx

# Login as admin
response = httpx.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin@example.com", "password": "password"}
)
token = response.json()["access_token"]

# Create avatar
files = {
    "prompt_face": ("video.mp4", open("avatar_video.mp4", "rb"), "video/mp4"),
}
data = {
    "tutor_id": 1,
    "name": "avatar_teacher1",
    "display_name": "Teacher Avatar",
    "avatar_model": "MuseTalk",
    "tts_model": "edge-tts",
}

response = httpx.post(
    "http://localhost:8000/api/avatars/create",
    headers={"Authorization": f"Bearer {token}"},
    data=data,
    files=files,
    timeout=200.0
)
avatar = response.json()
print(f"Avatar created: {avatar['id']}")

# Start avatar
response = httpx.post(
    f"http://localhost:8000/api/avatars/{avatar['id']}/start",
    headers={"Authorization": f"Bearer {token}"},
    timeout=300.0
)
print(f"Avatar started: {response.json()}")
```

### Frontend Integration

```javascript
// Create avatar
const formData = new FormData();
formData.append('tutor_id', tutorId);
formData.append('name', 'avatar_teacher1');
formData.append('display_name', 'Teacher Avatar');
formData.append('prompt_face', videoFile);

const response = await fetch('/api/avatars/create', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const avatar = await response.json();

// Start avatar
await fetch(`/api/avatars/${avatar.id}/start`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Multi-Tenant Security

- **Ownership Verification**: All endpoints verify that the avatar belongs to a tutor owned by the authenticated admin
- **Cascade Deletion**: Deleting a tutor automatically deletes all associated avatars
- **Isolation**: Admins can only access avatars for their own tutors

## Deployment Considerations

### 1. File Storage
- Avatar assets (images, videos, audio) are stored by the lip-sync service
- Consider using shared storage (NFS, S3) for multi-instance deployments

### 2. Service Dependencies
- Lip-sync service must be running before creating/starting avatars
- TTS service must be accessible for voice model queries

### 3. Performance
- Avatar creation can take 30-60 seconds depending on video length
- Avatar startup can take 1-5 minutes (model loading)
- Consider implementing job queues for async processing

### 4. Database Migration
```bash
# Generate migration for Avatar table
cd app_backend
alembic revision --autogenerate -m "Add avatar table"
alembic upgrade head
```

## Troubleshooting

### Avatar Creation Fails
- Check lip-sync service is running: `curl http://localhost:8615/avatar/get_avatars`
- Verify video format is supported: .mp4, .avi, .mov, .mkv
- Check service logs for detailed errors

### Avatar Won't Start
- Ensure avatar was created successfully (check preview image)
- Verify sufficient GPU memory for model loading
- Check lip-sync service conda environment is activated

### WebRTC Connection Issues
- Verify port 8615 is accessible from frontend
- Check browser console for WebRTC errors
- Ensure proper CORS configuration

## Future Enhancements

1. **Async Processing**: Implement Celery/RQ for long-running avatar creation
2. **Progress Tracking**: Add progress updates during avatar creation
3. **Avatar Templates**: Pre-configured avatar setups for common use cases
4. **Batch Operations**: Create multiple avatars from template
5. **Resource Limits**: Set limits on number of avatars per tutor
6. **Analytics**: Track avatar usage statistics
7. **Preview Generation**: Automatic preview video generation
8. **Avatar Sharing**: Allow avatars to be shared across tutors (with permissions)

## References

- Mageurite Virtual Tutor: `/Users/murphyxu/Code/ra/mageurite_virtual_tutor/backend/routes/avatar.py`
- MuseTalk: https://github.com/TMElyralab/MuseTalk
- LiveTalking: https://github.com/lipku/LiveTalking
