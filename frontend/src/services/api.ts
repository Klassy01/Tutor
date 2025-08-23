import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  
  register: (userData: {
    email: string;
    username: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) => api.post('/auth/register', userData),
  
  getCurrentUser: () => api.get('/auth/me'),
  
  refreshToken: () => api.post('/auth/refresh'),
};

// Student API calls
export const studentAPI = {
  getProfile: () => api.get('/students/profile'),
  
  updateProfile: (data: any) => api.put('/students/profile', data),
  
  getDashboard: () => api.get('/demo/dashboard'), // Using demo endpoint for immediate functionality
  
  getAchievements: () => api.get('/students/achievements'),
  
  getStats: () => api.get('/students/stats'),
};

// Content API calls
export const contentAPI = {
  getCategories: () => api.get('/content/categories'),
  
  searchContent: (query: string) => api.get(`/content/search?q=${query}`),
  
  getRecommendations: () => api.get('/content/recommendations'),
  
  getContent: (id: number) => api.get(`/content/${id}`),
  
  markComplete: (id: number) => api.post(`/content/${id}/complete`),
};

// Learning session API calls
export const learningAPI = {
  createSession: (data: { content_id?: number; session_type: string }) =>
    api.post('/demo/learning/sessions', data), // Using demo endpoint
  
  generateLesson: (data: { subject: string; topic: string; difficulty_level?: string }) =>
    api.post('/demo/learning/generate-lesson', data), // New AI lesson generation
  
  getSession: (id: number) => api.get(`/learning/sessions/${id}`),
  
  getSessions: () => api.get('/demo/learning/sessions'), // Using demo endpoint
  
  logInteraction: (sessionId: number, data: any) =>
    api.post(`/learning/sessions/${sessionId}/interactions`, data),
  
  completeSession: (id: number, data?: any) =>
    api.post(`/learning/sessions/${id}/complete`, data),
  
  getAnalytics: () => api.get('/learning/analytics'),
};

// Progress API calls
export const progressAPI = {
  getOverview: () => api.get('/demo/progress/overview'), // Using demo endpoint
  
  getDetailed: (params?: any) => api.get('/progress/detailed', { params }),
  
  getSubjectProgress: () => api.get('/progress/subjects'),
  
  getMasteryMap: () => api.get('/progress/mastery-map'),
  
  getLearningPath: () => api.get('/progress/learning-path'),
  
  getAnalytics: (period: string = 'week') =>
    api.get(`/progress/analytics?period=${period}`),
};

// AI Tutor API calls
export const aiTutorAPI = {
  chat: (message: string, sessionId?: number) =>
    api.post('/demo/ai-tutor/chat', { message, session_id: sessionId }), // Using demo endpoint
  
  generateExercises: (topic: string, difficulty?: string) =>
    api.post('/ai-tutor/exercises', { topic, difficulty }),
  
  submitAnswer: (exerciseId: number, answer: string) =>
    api.post('/ai-tutor/submit-answer', { exercise_id: exerciseId, answer }),
  
  getRecommendations: () => api.get('/ai-tutor/recommendations'),
  
  getSuggestions: () => api.get('/demo/ai-tutor/suggestions'), // Using demo endpoint
};

// Quiz API calls
export const quizAPI = {
  generateQuiz: (data: { subject: string; topic: string; difficulty_level?: string; num_questions?: number }) =>
    api.post('/demo/quiz/generate', data), // New AI quiz generation
  
  createAttempt: (quizData: {
    quiz_title: string;
    subject_area?: string;
    topic?: string;
    difficulty_level?: number;
    questions: Array<{
      question_id: string;
      question_text: string;
      answer_options: string[];
      correct_answer: string;
      explanation?: string;
      difficulty_level?: number;
    }>;
  }) => api.post('/demo/quiz/quiz-attempts', quizData), // Using demo endpoint
  
  getAttempts: () => api.get('/demo/quiz/quiz-attempts'), // Using demo endpoint
  
  getAttempt: (attemptId: number) => api.get(`/demo/quiz/quiz-attempts/${attemptId}`), // Using demo endpoint
  
  submitAnswer: (attemptId: number, answerData: {
    question_id: string;
    student_answer: string;
    response_time_seconds?: number;
  }) => api.post(`/demo/quiz/quiz-attempts/${attemptId}/submit-answer`, answerData), // Using demo endpoint
  
  completeAttempt: (attemptId: number) => api.post(`/demo/quiz/quiz-attempts/${attemptId}/complete`), // Using demo endpoint
  
  getResults: (attemptId: number) => api.get(`/demo/quiz/quiz-attempts/${attemptId}/results`), // Using demo endpoint
};

export default api;
