import { http } from "../utils/request";

const adminStudentService = {
  // GET /api/admin/students/?tutor_id=1
  list: (tutorId) => http.get("/admin/students/", { tutor_id: tutorId }),

  // POST /api/admin/students/?tutor_id=1
  create: (tutorId, payload) =>
    http.post("/admin/students/", payload, { params: { tutor_id: tutorId } }),

  // PATCH /api/admin/students/{student_id}?tutor_id=1
  update: (tutorId, studentId, payload) =>
    http.patch(`/admin/students/${studentId}`, payload, { params: { tutor_id: tutorId } }),
};

export default adminStudentService;
