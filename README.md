# Agro Service Track
🌾 Offline Field Service Management System

🚧 In development

Offline-first project created from the observation of a real pain point in the agricultural equipment maintenance sector.
In field operations, the lack of connectivity makes it difficult to digitize processes such as equipment intake,
maintenance tracking, and delivery checklists, generating legal insecurity and conflicts between involved parties.

Agro Service Track proposes a structured digital flow for data collection, persistence, and synchronization,
increasing process reliability even in environments without internet access.

## 🖥️ System Overview

Agro Service Track is composed of two main applications:

- **Web Application**  
  Used by administrative staff to manage customers, create work orders,
  register equipment data, and monitor service progress.

- **Mobile Application**  
  Used by field technicians to execute checklists, perform maintenance tasks,
  collect signatures, and synchronize data in offline-first environments.

### 🌐 Mobile Application Access
🔗 [Mobile Application Repository](https://github.com/Deiner-S/AgroSeriviceTrackApp.git)

## 📌 Project Stages

### 🧱 Stage 1 – Base Structure (completed)
- System requirements gathering
- Data flow mapping and logical data modeling
- Definition of tools and technologies
- Evaluation and validation of chosen tools
- Definition of the overall system architecture
- Core backend structuring
- Authentication flow configuration
- Mobile application organization into responsibility layers
- Commit standardization and repository organization

### 🔄 Stage 2 – Offline Flow and Synchronization (in progress)
- Local data persistence on the mobile application
- Checklist execution in offline environments
- Data synchronization with the server when connectivity is available
- Work order status management

### 🛠️ Stage 3 – Service Execution and Delivery (planned)
- Equipment maintenance workflow
- Service execution report
- Delivery checklist with final validation
- Work order finalization

### 🧪 Stage 4 – Stability and Reliability (planned)
- Data validation
- Exception handling
- Basic logging and audit trail
- Performance improvements

### 📦 Stage 5 – Documentation and Packaging (planned)
- Technical documentation
- Docker containerization
- Project preparation for controlled deployment

## 🧱 Project Structure

Agro Service Track is composed of **two independent applications**, organized within a
client–server macro architecture:

- **Mobile Application (App)**: responsible for executing service orders in the field,
  managing the local data state, and orchestrating synchronization, operating with an *offline-first* approach.
- **Web Application / Backend**: responsible for initializing the workflow by generating service orders, central data persistence,
  authentication, validation, and exposing endpoints for sending and receiving synchronization data, in addition to monitoring and closing the workflow.

### 📱 Mobile Application
- **Technology**: Expo / React Native
- **Approach**: Offline-first
- **Micro-architecture**: Layered architecture
- **Responsibilities**:
  - Local persistence
  - Synchronization with the Web system
  - API communication

### 🌐 Backend / Web
- **Technology**: Django + Django Rest Framework
- **Micro-architecture**: Layered architecture
- **Responsibilities**:
  - Workflow initialization and closure
  - Workflow monitoring
  - Authentication and access control
  - Central data persistence  
  - REST API exposure

## 🧩 System Modules

- Equipment intake and delivery checklist (core)
- Post-service tracking (planned)
- Business analysis and performance (planned)
- Financial management (planned)
- Customer process tracking (planned)

## 🚀 Possible Evolution Horizons

- Project structuring for a future SaaS model
