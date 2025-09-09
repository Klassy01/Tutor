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

// Lessons API calls
export const lessonAPI = {
  getSubjects: () => api.get('/lessons/subjects'),
  
  getTopics: (subject: string) => api.get(`/lessons/topics/${subject}`),
  
  generateLesson: (data: { 
    subject: string; 
    topic: string; 
    difficulty_level?: string;
    learning_objectives?: string[];
  }) => api.post('/lessons/generate', data),
  
  completeLesson: (data: {
    lesson_data: any;
    time_spent_minutes: number;
  }) => api.post('/lessons/complete', data),
  
  getLessonHistory: (limit?: number) => 
    api.get(`/lessons/history${limit ? `?limit=${limit}` : ''}`),
  
  getRecommendations: () => api.get('/lessons/recommendations'),
};

// Quiz API calls
export const quizAPI = {
  generateQuiz: (data: { 
    subject: string; 
    topic: string; 
    difficulty_level?: string; 
    num_questions?: number;
    quiz_type?: string;
  }) => api.post('/quizzes/generate', data),
  
  submitQuiz: (data: {
    quiz_data: any;
    answers: Record<string, string>;
    time_spent_minutes: number;
  }) => api.post('/quizzes/submit', data),
  
  getQuizHistory: (limit?: number) => 
    api.get(`/quizzes/history${limit ? `?limit=${limit}` : ''}`),
  
  getStatistics: () => api.get('/quizzes/statistics'),
  
  generatePracticeQuiz: (data: {
    subject?: string;
    topic?: string;
    num_questions?: number;
  }) => api.post('/quizzes/practice-mode', data),
};

// AI Tutor API calls
export const aiTutorAPI = {
  startChatSession: (data: {
    subject: string;
    learning_goal?: string;
  }) => api.post('/ai-tutor/start-session', data),
  
  sendMessage: (data: {
    session_id: string;
    message: string;
  }) => api.post('/ai-tutor/send-message', data),
  
  getChatHistory: (sessionId: string) => 
    api.get(`/ai-tutor/session/${sessionId}/history`),
  
  getChatSessions: () => api.get('/ai-tutor/sessions'),
  
  deleteChatSession: (sessionId: string) => 
    api.delete(`/ai-tutor/session/${sessionId}`),
  
  askQuickQuestion: (data: {
    question: string;
    subject?: string;
  }) => api.post('/ai-tutor/ask-quick', data),
  
  explainConcept: (data: {
    concept: string;
    subject?: string;
    level?: string;
  }) => api.post('/ai-tutor/explain-concept', data),
};

// Dashboard API calls
export const dashboardAPI = {
  getOverview: () => api.get('/dashboard/overview'),
  
  getProgressChart: (timeframe?: string) => 
    api.get(`/dashboard/progress-chart${timeframe ? `?timeframe=${timeframe}` : ''}`),
  
  getSubjectBreakdown: () => api.get('/dashboard/subject-breakdown'),
  
  getAchievements: () => api.get('/dashboard/achievements'),
  
  getLearningStreaks: () => api.get('/dashboard/learning-streaks'),
};

// Legacy API calls for backward compatibility (will be gradually replaced)
export const studentAPI = {
  getProfile: () => authAPI.getCurrentUser(),
  updateProfile: (data: any) => api.put('/auth/profile', data),
  getDashboard: () => dashboardAPI.getOverview(),
  getAchievements: () => dashboardAPI.getAchievements(),
  getStats: () => dashboardAPI.getOverview(),
};

export const contentAPI = {
  getCategories: () => lessonAPI.getSubjects(),
  searchContent: (query: string) => api.get(`/lessons/search?q=${query}`),
  getRecommendations: () => lessonAPI.getRecommendations(),
  getContent: (id: number) => api.get(`/lessons/${id}`),
  markComplete: (id: number) => api.post(`/lessons/${id}/complete`),
};

export const learningAPI = {
  createSession: (data: { 
    content_id?: number; 
    session_type: string;
    subject_area?: string;
    topic?: string;
  }) => api.post('/learning/sessions', data),
  
  generateLesson: (data: { subject: string; topic: string; difficulty_level?: string }) =>
    lessonAPI.generateLesson(data),
  
  getSession: (id: number) => api.get(`/learning/sessions/${id}`),
  getSessions: () => lessonAPI.getLessonHistory(),
  
  logInteraction: (sessionId: number, data: any) =>
    api.post(`/learning/sessions/${sessionId}/interactions`, data),
  
  completeSession: (id: number, data?: any) =>
    api.post(`/learning/sessions/${id}/complete`, data),
  
  getAnalytics: () => dashboardAPI.getProgressChart(),
};

export const progressAPI = {
  getOverview: () => dashboardAPI.getOverview(),
  getDetailed: () => dashboardAPI.getProgressChart(),
  getSubjectProgress: () => dashboardAPI.getSubjectBreakdown(),
  getMasteryMap: () => dashboardAPI.getOverview(),
  getLearningPath: () => lessonAPI.getRecommendations(),
  getAnalytics: (period: string = 'week') =>
    dashboardAPI.getProgressChart(period),
};

export default api;
