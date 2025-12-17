import { http } from "../utils/request";

const tutorService = {
  // GET /api/tutors/
  list: () => http.get("/tutors/"),

  // POST /api/tutors/
  create: (payload) => http.post("/tutors/", payload),
};

export default tutorService;
