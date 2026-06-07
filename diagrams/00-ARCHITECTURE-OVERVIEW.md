# Quick Architecture Overview
## CSE4204-8D-T04 Smart Quiz Generator

**Description:** This diagram shows a high-level overview of the Smart Quiz Generator system architecture with all major components and their interactions.

```mermaid
graph TB
    subgraph Frontend["🖥️ FRONTEND LAYER"]
        WEB["Web Browser<br/>React/Vue/Angular"]
    end
    
    subgraph Gateway["🔒 API GATEWAY"]
        LB["Nginx<br/>Load Balancer<br/>HTTPS Termination"]
    end
    
    subgraph AppLayer["⚙️ APPLICATION LAYER"]
        AUTH["🔐 Authentication<br/>Token-Based"]
        QUIZ["📝 Quiz Service<br/>CRUD Operations"]
        QUESTION["❓ Question Service<br/>Management"]
        SCORING["⭐ Scoring Service<br/>Calculate Scores"]
        PARSER["📄 Document Parser<br/>PDF/TXT/MD/CSV/JSON"]
        AI["🤖 AI Client<br/>Gemini Integration"]
    end
    
    subgraph Data["💾 DATA LAYER"]
        DB[("🗄️ MySQL/MariaDB<br/>Primary Database")]
        CACHE[("⚡ Redis<br/>Optional Cache")]
    end
    
    subgraph External["☁️ EXTERNAL SERVICES"]
        GEMINI["🌟 Google Gemini API<br/>AI Question Generation"]
    end
    
    WEB -->|HTTPS/REST API| LB
    
    LB -->|Route| AUTH
    LB -->|Route| QUIZ
    LB -->|Route| QUESTION
    LB -->|Route| SCORING
    LB -->|Route| PARSER
    LB -->|Route| AI
    
    AUTH -->|Verify| DB
    QUIZ -->|Read/Write| DB
    QUESTION -->|Read/Write| DB
    SCORING -->|Update| DB
    PARSER -->|Upload| DB
    AI -->|Call API| GEMINI
    GEMINI -->|Return Questions| AI
    
    AUTH -->|Cache| CACHE
    QUIZ -->|Cache| CACHE
    QUESTION -->|Cache| CACHE
    
    style Frontend fill:#e1f5ff
    style Gateway fill:#fff3e0
    style AppLayer fill:#f3e5f5
    style Data fill:#e8f5e9
    style External fill:#fce4ec
```

## Architecture Layers Explained

### 🖥️ **Frontend Layer**
- Web browser application (React, Vue, or Angular)
- Communicates via HTTPS REST API

### 🔒 **API Gateway Layer**
- Nginx reverse proxy
- Load balancing for scalability
- HTTPS termination and security

### ⚙️ **Application Layer (Django REST Framework)**
- **Authentication Module:** Token-based user authentication
- **Quiz Service:** Create, read, update, delete quizzes
- **Question Service:** Manage questions and options
- **Scoring Service:** Calculate and store quiz scores
- **Document Parser:** Extract text from various formats
- **AI Client:** Interface with Google Gemini API

### 💾 **Data Layer**
- **MySQL/MariaDB:** Primary relational database
- **Redis Cache:** Optional caching layer for performance

### ☁️ **External Services**
- **Google Gemini API:** AI-powered question generation

## Data Flow

```
Student/Teacher Input
        ↓
    Frontend
        ↓
   API Gateway (Nginx)
        ↓
   Application Services
        ↓
   Database & Cache
        ↓
   Response → Frontend → User
```

