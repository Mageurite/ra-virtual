from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from models.user import User

# Blueprint for avatar-related routes
avatar_bp = Blueprint("avatar", __name__)


@avatar_bp.route("/webrtc/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def webrtc_proxy(path):
    """Proxy WebRTC requests to port 8615 (bypass port mapping issue)"""
    webrtc_url = f"http://localhost:8615/{path}"
    
    try:
        # Prepare headers
        headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']}
        
        # Forward request
        if request.method == "POST":
            resp = requests.post(webrtc_url, headers=headers, data=request.get_data(), timeout=30)
        elif request.method == "GET":
            resp = requests.get(webrtc_url, headers=headers, params=request.args, timeout=30)
        else:
            resp = requests.request(request.method, webrtc_url, headers=headers, data=request.get_data(), timeout=30)
        
        # Return response
        return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        return jsonify(msg=f"Proxy error: {str(e)}"), 502


@avatar_bp.route("/avatar/list", methods=["GET"])
@jwt_required()
def fetch_avatars():
    """Fetch list of available avatars from the avatar service."""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    try:
        response = requests.get("http://localhost:8606/avatar/get_avatars", timeout=10)
        data = response.json()
        # 前端期望对象格式：{avatar_name: {clone: bool, description: str, ...}}
        if data.get('status') == 'success' and 'avatars' in data:
            avatar_list = data['avatars']
            # 转换为对象格式
            avatar_dict = {}
            for avatar_name in avatar_list:
                avatar_dict[avatar_name] = {
                    "clone": False,
                    "description": f"Avatar: {avatar_name}",
                    "status": "active",
                    "timbre": "",
                    "tts_model": "",
                    "avatar_model": ""
                }
            return jsonify(avatar_dict), 200
        return jsonify(data), response.status_code
    except requests.RequestException as e:
        return jsonify(msg="Failed to connect to avatar service", error=str(e)), 500


@avatar_bp.route("/avatar/preview", methods=["POST"])
@jwt_required()
def forward_avatar_preview():
    """Request an avatar preview from the avatar service and return the image."""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    avatar_name = request.form.get("avatar_name")
    if not avatar_name:
        return jsonify(msg="Missing avatar_name in form-data"), 400

    try:
        response = requests.post(
            "http://localhost:8606/avatar/preview",
            data={"avatar_name": avatar_name},
            timeout=10
        )

        if response.status_code != 200:
            return jsonify(msg="Failed to get avatar preview", detail=response.text), response.status_code

        # Forward image content directly to the client
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type", "image/png")
        )

    except requests.RequestException as e:
        return jsonify(msg="Error forwarding to avatar service", error=str(e)), 500


@avatar_bp.route("/avatar/add", methods=["POST"])
@jwt_required()
def add_avatar():
    """Forward avatar creation request to the avatar service (tutor only)."""
    admin_email = get_jwt_identity()
    admin = User.query.filter_by(email=admin_email).first()

    if not admin or admin.role.lower() != "tutor":
        return jsonify({"msg": "Permission denied"}), 403

    # Collect form fields
    form_fields = [
        "name", "avatar_blur", "support_clone", "timbre",
        "tts_model", "avatar_model", "description"
    ]
    data = {field: request.form.get(field) for field in form_fields if field in request.form}

    prompt_face = request.files.get("prompt_face")
    prompt_voice = request.files.get("prompt_voice")

    files = {}
    if prompt_face:
        files["prompt_face"] = (prompt_face.filename, prompt_face.stream, prompt_face.mimetype)
    if prompt_voice:
        files["prompt_voice"] = (prompt_voice.filename, prompt_voice.stream, prompt_voice.mimetype)

    try:
        response = requests.post(
            "http://localhost:8606/avatar/add",
            data=data,
            files=files,
            timeout=200
        )

        try:
            response_data = response.json()
        except ValueError:
            return jsonify(msg="Invalid JSON response from avatar service", raw=response.text), 500

        if response_data.get("status") == "success":
            return jsonify(response_data), 200
        else:
            return jsonify(msg="Avatar creation failed", detail=response_data), 400

    except requests.RequestException as e:
        return jsonify(msg="Error forwarding to avatar service", error=str(e)), 500


@avatar_bp.route("/tts/models", methods=["GET"])
@jwt_required()
def get_tts_models():
    """Fetch available TTS models from the avatar service."""
    current_user_email = get_jwt_identity()
    try:
        response = requests.get("http://localhost:8604/tts/models", timeout=10)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify(msg="Failed to fetch TTS models", detail=response.text), response.status_code

    except requests.RequestException as e:
        return jsonify(msg="Error connecting to TTS service", error=str(e)), 500


@avatar_bp.route("avatar/delete", methods=["POST"])
@jwt_required()
def forward_delete_avatar():
    """Forward avatar deletion request to the avatar service."""
    current_user_email = get_jwt_identity()

    avatar_name = request.form.get("name")
    if not avatar_name:
        return jsonify(msg="Missing 'name' in form-data"), 400

    try:
        response = requests.post(
            "http://localhost:8606/avatar/delete",
            data={"name": avatar_name},
            timeout=10
        )

        try:
            response_data = response.json()
        except ValueError:
            return jsonify(msg="Invalid JSON response", raw=response.text), 500

        if response_data.get("status") == "success":
            return jsonify(response_data), 200
        else:
            return jsonify(msg="Avatar deletion failed", detail=response_data), 400

    except requests.RequestException as e:
        return jsonify(msg="Error forwarding to avatar service", error=str(e)), 500


@avatar_bp.route("avatar/start", methods=["POST"])
@jwt_required()
def forward_start_avatar():
    """Forward avatar start request to the avatar service."""
    current_user_email = get_jwt_identity()

    avatar_name = request.form.get("avatar_name")
    if not avatar_name:
        return jsonify(msg="Missing 'avatar_name' in form-data"), 400

    try:
        response = requests.post(
            "http://localhost:8606/avatar/start",
            data={"avatar_name": avatar_name},
            timeout=60
        )

        try:
            response_data = response.json()
        except ValueError:
            return jsonify(msg="Invalid JSON response from avatar service", raw=response.text), 500

        if response_data.get("status") == "success":
            return jsonify(response_data), 200
        else:
            return jsonify(msg="Avatar start failed", detail=response_data), 400

    except requests.RequestException as e:
        return jsonify(msg="Error forwarding to avatar service", error=str(e)), 500
