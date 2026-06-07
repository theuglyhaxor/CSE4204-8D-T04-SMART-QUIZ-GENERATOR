# Software Requirements Specification (SRS)
## Smart Quiz Generator

---

## 1. INTRODUCTION

### 1.1 Project Title
**Smart Quiz Generator**

### 1.2 Project Overview

The **Smart Quiz Generator** is an intelligent, role-based quiz management system designed to streamline the process of creating, administering, and evaluating quizzes. The system leverages AI technology to automatically generate quiz questions from various document formats while providing a secure, user-friendly platform for educators and students to collaborate on assessment activities.

The platform consists of a robust backend API built with Django and a modern frontend interface. Teachers can create quizzes, upload learning materials, and leverage AI to automatically generate questions. Students can take quizzes securely, receive immediate feedback, and track their learning progress.

### 1.3 Problem Statement

Traditional quiz creation and administration processes are time-consuming and resource-intensive. Educators spend significant time manually creating questions and managing student assessments. Additionally, there is no centralized, secure platform for modern educational institutions to manage the complete quiz lifecycle—from creation to evaluation—with intelligent automation.

The lack of AI-powered question generation forces educators to create questions manually from course materials, increasing workload and time-to-deployment. Without proper role-based access control and secure authentication, institutions risk data security breaches and unauthorized access to sensitive assessment information.

### 1.4 Objectives

The Smart Quiz Generator aims to:

- **Enable efficient quiz creation** through both manual input and AI-powered automatic generation from uploaded documents
- **Implement secure role-based access control** with distinct teacher and student workflows
- **Provide intelligent question generation** using Gemini AI to extract and formulate questions from various document formats (PDF, TXT, Markdown, CSV, JSON)
- **Facilitate secure student assessment** with real-time scoring and performance tracking
- **Support multiple file formats** for document-based question generation, including PDF, text files, and structured data formats
- **Deliver comprehensive API endpoints** for seamless integration with frontend applications, mobile apps, and third-party services
- **Maintain data integrity and security** through token-based authentication, encrypted credentials, and proper permission management

### 1.5 Scope of the Project

#### In Scope:
- Backend API for quiz management (CRUD operations)
- Teacher-specific functionality for quiz creation, question management, and student submission review
- Student-specific functionality for answering quizzes and receiving scores
- AI-powered quiz generation using Gemini API
- Document parsing and upload capabilities (PDF, TXT, MD, CSV, JSON)
- Role-based access control (Teacher/Student roles)
- Token-based authentication and authorization
- Quiz attempt tracking and scoring system
- RESTful API endpoints for frontend and third-party integrations
- Database design with proper relationships and constraints

#### Out of Scope:
- Frontend application (standalone; can be developed separately)
- Production-grade message queue or background job scheduling (e.g., Celery)
- Mobile app (can consume the API independently)
- Real-time notifications or WebSocket features
- Payment processing or subscription management
- Analytics dashboard (future enhancement)
- Multi-language support (initial version)

---

## 2. FUNCTIONAL REQUIREMENTS

### 2.1 Authentication and Authorization

**FR-01:** Users shall be able to register with a valid email and password.  
**FR-02:** The system shall authenticate users using token-based authentication (Django REST Framework Token).  
**FR-03:** The system shall assign users to either the "Teacher" or "Student" role during account creation.  
**FR-04:** Teachers shall have access to all quiz management endpoints (create, read, update, delete).  
**FR-05:** Students shall have access only to student-safe endpoints (view questions without answers, submit answers, view scores).  
**FR-06:** The system shall invalidate tokens upon logout.  
**FR-07:** The system shall enforce password encryption for all stored credentials.  

### 2.2 Quiz Management (Teacher Features)

**FR-08:** Teachers shall be able to create new quizzes with a title, description, difficulty level, and duration.  
**FR-09:** Teachers shall be able to view all quizzes they have created.  
**FR-10:** Teachers shall be able to update quiz details (title, description, difficulty, duration, active status).  
**FR-11:** Teachers shall be able to delete quizzes.  
**FR-12:** Teachers shall be able to set a quiz as active or inactive to control student access.  
**FR-13:** The system shall automatically timestamp all quiz creation and modification events.  
**FR-14:** Teachers shall be able to view all quiz attempts and student submissions.  

### 2.3 Question Management (Teacher Features)

**FR-15:** Teachers shall be able to add questions to a quiz, including prompt text, four multiple-choice options (A, B, C, D), and the correct answer.  
**FR-16:** Teachers shall be able to provide an explanation for each question's correct answer.  
**FR-17:** Teachers shall be able to define the order of questions within a quiz.  
**FR-18:** Teachers shall be able to view, update, and delete questions within a quiz.  
**FR-19:** Teachers shall be able to bulk import questions from AI-generated content or manual uploads.  

### 2.4 AI-Powered Question Generation

**FR-20:** Teachers shall be able to upload documents (PDF, TXT, Markdown, CSV, JSON) to generate quiz questions.  
**FR-21:** The system shall parse uploaded documents and extract relevant content.  
**FR-22:** The system shall call the Gemini AI API to generate quiz questions from document content.  
**FR-23:** The system shall return generated questions in a structured format with prompt, options, and correct answer.  
**FR-24:** Teachers shall be able to review AI-generated questions before adding them to a quiz.  
**FR-25:** The system shall support multiple document formats: PDF, TXT, MD, CSV, JSON.  

### 2.5 Student Quiz Taking (Student Features)

**FR-26:** Students shall be able to view a list of active quizzes available to them.  
**FR-27:** Students shall be able to retrieve quiz questions without seeing the correct answers.  
**FR-28:** Students shall be able to submit their answers for a quiz.  
**FR-29:** Students shall be able to enter their name when submitting a quiz attempt.  
**FR-30:** The system shall store student responses in a structured JSON format.  

### 2.6 Scoring and Results

**FR-31:** The system shall automatically calculate scores based on correct answers submitted by students.  
**FR-32:** The system shall store the final score, total questions, and percentage score for each attempt.  
**FR-33:** Students shall be able to view their score after submitting a quiz.  
**FR-34:** Teachers shall be able to view detailed scoring data for all students across quizzes.  
**FR-35:** The system shall store attempt history with timestamps for audit and progress tracking.  

### 2.7 API Endpoints

**FR-36:** The system shall provide RESTful API endpoints following REST conventions (GET, POST, PUT, DELETE).  
**FR-37:** The system shall return JSON responses with appropriate HTTP status codes.  
**FR-38:** The system shall provide pagination for list endpoints to handle large datasets.  
**FR-39:** The system shall include proper error messages and validation feedback in API responses.  
**FR-40:** The system shall document all API endpoints with request/response examples.  

---

## 3. NON-FUNCTIONAL REQUIREMENTS

### 3.1 Performance

**NFR-01:** API endpoints shall respond within 3 seconds for typical quiz operations (create, list, retrieve).  
**NFR-02:** Document parsing and AI question generation shall complete within 10 seconds for documents up to 5MB.  
**NFR-03:** The system shall handle concurrent requests from multiple users without performance degradation.  
**NFR-04:** List endpoints shall support pagination with a default page size of 20 items and maximum of 100 items per page.  

### 3.2 Security

**NFR-05:** All user passwords shall be stored using industry-standard hashing algorithms (e.g., PBKDF2, bcrypt).  
**NFR-06:** Authentication tokens shall expire after 24 hours of inactivity (configurable).  
**NFR-07:** The system shall enforce HTTPS for all API communications in production.  
**NFR-08:** The system shall validate and sanitize all user inputs to prevent injection attacks.  
**NFR-09:** File uploads shall be scanned for malware and validated for file type authenticity.  
**NFR-10:** The system shall implement rate limiting to prevent abuse (e.g., max 100 requests per minute per user).  
**NFR-11:** Teacher endpoints shall verify user role before granting access to sensitive operations.  
**NFR-12:** All database queries shall use parameterized statements to prevent SQL injection.  

### 3.3 Reliability and Availability

**NFR-13:** The system shall achieve 99.5% uptime during operational hours.  
**NFR-14:** The system shall implement proper error handling with meaningful error messages.  
**NFR-15:** The system shall log all critical operations for audit and debugging purposes.  
**NFR-16:** The system shall implement database backups daily with retention for at least 30 days.  
**NFR-17:** The system shall gracefully handle network timeouts and retry failed operations where appropriate.  

### 3.4 Scalability

**NFR-18:** The database schema shall support at least 10,000 quizzes, 100,000 questions, and 1,000,000 student attempts without performance degradation.  
**NFR-19:** The backend API shall be horizontally scalable through stateless design and load balancing.  
**NFR-20:** The system shall support concurrent quiz-taking by 500+ students simultaneously.  

### 3.5 Usability

**NFR-21:** All API endpoints shall follow consistent naming conventions and response formats.  
**NFR-22:** The system shall provide comprehensive API documentation with examples for each endpoint.  
**NFR-23:** Error messages shall be clear, actionable, and include guidance for resolution.  
**NFR-24:** The frontend application shall be responsive and work on desktop, tablet, and mobile devices.  

### 3.6 Maintainability

**NFR-25:** The codebase shall follow PEP 8 style guidelines and Python best practices.  
**NFR-26:** All code shall include unit tests with a minimum coverage of 80%.  
**NFR-27:** The system shall maintain comprehensive documentation for setup, deployment, and API usage.  
**NFR-28:** Database migrations shall be properly versioned and reversible.  

### 3.7 Compatibility

**NFR-29:** The system shall support MySQL 5.7+ and MariaDB 10.3+.  
**NFR-30:** The system shall work with Python 3.9+.  
**NFR-31:** The system shall be compatible with popular frontend frameworks (React, Vue, Angular, etc.).  

---

## 4. USER ROLES AND RESPONSIBILITIES

### 4.1 Teacher/Educator

**Responsibilities:**
- Create and manage quizzes for their courses
- Add questions manually or generate questions using AI
- Upload course materials in various formats (PDF, TXT, etc.)
- Set quiz difficulty levels and duration
- Activate/deactivate quizzes
- Review student submissions and attempts
- Analyze student performance
- Manage quiz content updates and revisions
- Delete quizzes and questions as needed

**Permissions:**
- Full CRUD access to quizzes and questions
- Access to document upload and parsing endpoints
- Access to AI question generation
- View all student attempts and scores
- Cannot access other teachers' quizzes (unless shared)

### 4.2 Student/Learner

**Responsibilities:**
- Register and maintain their account
- Browse and take available quizzes
- Submit quiz responses within the time limit
- Review their scores and feedback
- Track their progress over time
- Request help or clarification if needed

**Permissions:**
- View list of active quizzes
- Retrieve questions without answers
- Submit quiz responses
- View their own scores and attempts
- Cannot modify quiz content
- Cannot view other students' scores or responses
- Cannot access teacher-only endpoints

### 4.3 System Administrator (Future Role)

**Responsibilities:**
- Monitor system health and performance
- Manage user accounts (create, suspend, delete)
- Configure system settings and parameters
- Generate reports and analytics
- Handle data backups and recovery

**Permissions:**
- Full system access
- User management capabilities
- System configuration access
- Access to logs and monitoring dashboards

---

## 5. USE CASES

### Use Case 1: Teacher Creates a Quiz Manually

**Actor:** Teacher  
**Precondition:** Teacher is logged in and authenticated  
**Main Flow:**
1. Teacher navigates to "Create Quiz"
2. Teacher enters quiz title, description, difficulty level, and duration
3. System validates input and creates the quiz
4. System returns quiz ID and confirmation
5. Teacher proceeds to add questions

**Postcondition:** Quiz is created and ready for question addition

**Alternative Flow:**
- If validation fails, system displays error message and prompts teacher to correct input

---

### Use Case 2: Teacher Generates Questions from Document

**Actor:** Teacher  
**Precondition:** Teacher is logged in, quiz exists, and document is available  
**Main Flow:**
1. Teacher navigates to "Generate Questions from Document"
2. Teacher uploads a document (PDF, TXT, MD, CSV, or JSON)
3. System validates file type and size
4. System parses the document content
5. System sends content to Gemini AI API
6. Gemini generates quiz questions with explanations
7. System returns generated questions to teacher for review
8. Teacher reviews questions and selects which ones to add to the quiz
9. System adds selected questions to the quiz

**Postcondition:** Questions are added to the quiz and available for students

**Alternative Flow:**
- If file is invalid or too large, system returns error
- If AI generation fails, system suggests retry or manual question creation

---

### Use Case 3: Student Takes a Quiz

**Actor:** Student  
**Precondition:** Student is logged in and quiz is active  
**Main Flow:**
1. Student views available quizzes
2. Student selects a quiz to take
3. System retrieves questions without correct answers
4. Student reads each question and selects an answer
5. System stores each response
6. Student submits the completed quiz
7. System calculates the score based on responses
8. System displays the score and result to the student
9. System stores the attempt record with timestamp

**Postcondition:** Quiz attempt is recorded, score is calculated, and result is displayed

**Alternative Flow:**
- If student closes the quiz without submitting, responses are discarded
- If student exceeds time limit, system may auto-submit based on configuration

---

### Use Case 4: Teacher Reviews Student Submissions

**Actor:** Teacher  
**Precondition:** Teacher is logged in and students have submitted quiz attempts  
**Main Flow:**
1. Teacher navigates to "Quiz Submissions"
2. Teacher selects a specific quiz
3. System displays list of all student attempts for that quiz
4. Teacher selects a student's submission
5. System displays student responses, scores, and comparison with correct answers
6. Teacher can provide additional feedback or notes (future enhancement)

**Postcondition:** Teacher has reviewed the submission and can make decisions based on performance data

---

### Use Case 5: Student Views Score and Feedback

**Actor:** Student  
**Precondition:** Student has submitted a quiz attempt  
**Main Flow:**
1. Student navigates to "My Attempts" or "Quiz Results"
2. System displays a list of all completed quiz attempts
3. Student selects a completed attempt
4. System displays detailed results including score, percentage, and explanation for correct answers
5. Student can identify weak areas and plan further study

**Postcondition:** Student has access to their performance data and can use it for learning improvement

---

## 6. SYSTEM CONSTRAINTS

### 6.1 Technical Constraints

- **Backend Framework:** Django (Python web framework)
- **Database:** MySQL 5.7+ or MariaDB 10.3+
- **API:** Django REST Framework (DRF)
- **Authentication:** Token-based (Django REST Framework Token)
- **AI Integration:** Gemini API (Google)
- **File Parsing:** Support for PDF, TXT, MD, CSV, JSON formats

### 6.2 Performance Constraints

- Maximum document size for upload: 5MB
- Maximum concurrent users: 500+
- API response time target: < 3 seconds

### 6.3 Functional Constraints

- Quiz duration: configurable, typically 5-120 minutes
- Question options: exactly 4 (A, B, C, D)
- File upload quota: configurable per institution

### 6.4 Security Constraints

- All communications must use HTTPS in production
- Passwords must meet minimum security requirements
- Token expiration: 24 hours (configurable)
- Rate limiting: 100 requests per minute per user

---

## 7. ASSUMPTIONS AND DEPENDENCIES

### 7.1 Assumptions

- Teachers are responsible for creating accurate and appropriate quiz content
- Gemini API will be available and functional
- Database will be properly configured and accessible
- Users have internet connectivity to access the platform
- File uploads are genuine educational materials

### 7.2 Dependencies

- **Google Gemini API:** For AI-powered question generation
- **Django Framework:** Core backend framework
- **Django REST Framework:** API development
- **MySQL/MariaDB:** Database backend
- **Frontend Application:** For user interface (developed separately)
- **PDF Parsing Library:** For document extraction


