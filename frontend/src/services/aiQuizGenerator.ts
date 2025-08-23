export interface Question {
  id: string;
  question: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  correct_answer: string;
  explanation: string;
  subject?: string;
  difficulty?: number;
}

export interface QuizGenerationRequest {
  subject: string;
  topic: string;
  difficulty: number;
  numQuestions: number;
}

export interface AIQuestion extends Question {
  type: 'multiple-choice' | 'true-false' | 'short-answer';
  category?: string;
}

class AIQuizGeneratorService {
  private apiKey: string;
  private apiUrl: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_HUGGINGFACE_API_KEY || '';
    this.apiUrl = 'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium';
  }

  async generateQuiz(request: QuizGenerationRequest): Promise<Question[]> {
    try {
      // For now, return sample questions with AI-like generation
      const questions: Question[] = [];
      
      for (let i = 0; i < request.numQuestions; i++) {
        const question: Question = {
          id: `q_${Date.now()}_${i}`,
          question: this.generateQuestionText(request.subject, request.topic, i + 1),
          options: this.generateOptions(request.subject, request.topic, i + 1),
          correct_answer: ['A', 'B', 'C', 'D'][Math.floor(Math.random() * 4)],
          explanation: `This question tests your understanding of ${request.topic} in ${request.subject}.`,
          subject: request.subject,
          difficulty: request.difficulty
        };
        questions.push(question);
      }
      
      return questions;
    } catch (error) {
      console.error('Failed to generate quiz:', error);
      return this.getFallbackQuestions(request);
    }
  }

  private generateQuestionText(subject: string, topic: string, questionNumber: number): string {
    const questionTemplates = {
      Mathematics: [
        `What is the result of this ${topic} problem?`,
        `Which formula is used for ${topic}?`,
        `How do you solve this ${topic} equation?`,
      ],
      Science: [
        `What is the main principle of ${topic}?`,
        `Which process describes ${topic}?`,
        `What happens during ${topic}?`,
      ],
      History: [
        `When did the ${topic} occur?`,
        `Who was involved in ${topic}?`,
        `What was the cause of ${topic}?`,
      ],
      English: [
        `What is the meaning of this ${topic} concept?`,
        `Which technique is used in ${topic}?`,
        `How does ${topic} affect the text?`,
      ],
    };

    const templates = questionTemplates[subject as keyof typeof questionTemplates] || [
      `What is important about ${topic}?`,
      `How does ${topic} work?`,
      `What are the key features of ${topic}?`,
    ];

    return templates[questionNumber % templates.length];
  }

  private generateOptions(subject: string, topic: string, questionNumber: number): Question['options'] {
    const optionSets = {
      Mathematics: [
        { A: 'x = 5', B: 'x = 10', C: 'x = 15', D: 'x = 20' },
        { A: 'Pythagorean theorem', B: 'Quadratic formula', C: 'Chain rule', D: 'Distance formula' },
      ],
      Science: [
        { A: 'Photosynthesis', B: 'Respiration', C: 'Digestion', D: 'Circulation' },
        { A: 'Newton\'s First Law', B: 'Newton\'s Second Law', C: 'Newton\'s Third Law', D: 'Law of Gravity' },
      ],
      History: [
        { A: '1776', B: '1789', C: '1812', D: '1865' },
        { A: 'George Washington', B: 'Thomas Jefferson', C: 'Abraham Lincoln', D: 'Benjamin Franklin' },
      ],
      English: [
        { A: 'Metaphor', B: 'Simile', C: 'Alliteration', D: 'Personification' },
        { A: 'First person', B: 'Second person', C: 'Third person limited', D: 'Third person omniscient' },
      ],
    };

    const sets = optionSets[subject as keyof typeof optionSets] || [
      { A: 'Option A', B: 'Option B', C: 'Option C', D: 'Option D' },
    ];

    return sets[questionNumber % sets.length];
  }

  private getFallbackQuestions(request: QuizGenerationRequest): Question[] {
    return [
      {
        id: 'fallback_1',
        question: `What is a fundamental concept in ${request.topic}?`,
        options: {
          A: 'Basic principle',
          B: 'Advanced theory',
          C: 'Complex formula',
          D: 'Simple rule'
        },
        correct_answer: 'A',
        explanation: `This is a basic question about ${request.topic} in ${request.subject}.`,
        subject: request.subject,
        difficulty: request.difficulty
      }
    ];
  }

  async generateQuestionsForSubject(subject: string, count: number = 5): Promise<Question[]> {
    const topics = this.getTopicsForSubject(subject);
    const randomTopic = topics[Math.floor(Math.random() * topics.length)];
    
    return this.generateQuiz({
      subject,
      topic: randomTopic,
      difficulty: 0.5,
      numQuestions: count
    });
  }

  private getTopicsForSubject(subject: string): string[] {
    const subjectTopics = {
      Mathematics: ['Algebra', 'Geometry', 'Calculus', 'Statistics', 'Trigonometry'],
      Science: ['Physics', 'Chemistry', 'Biology', 'Earth Science', 'Astronomy'],
      History: ['Ancient History', 'Medieval Period', 'Renaissance', 'Modern History', 'Contemporary'],
      English: ['Grammar', 'Literature', 'Poetry', 'Writing', 'Reading Comprehension'],
    };

    return subjectTopics[subject as keyof typeof subjectTopics] || ['General Topics'];
  }
}

export const aiQuizGenerator = new AIQuizGeneratorService();