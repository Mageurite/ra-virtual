# Frontend Module

## Introduction

The Frontend Module serves as the user interface for the Intelligent Digital Human Mentor System, developed using the React framework. This module provides a friendly graphical interface that allows users to converse with digital humans, upload learning materials, manage personal profiles, and more. The system supports two roles - users and administrators - each with their own specialized interface.

## Key Features

- **User Interaction Interface**: Provides an interface for dialoguing with digital humans, supporting both text and voice input
- **User Management**: Registration, login, and profile management
- **Material Upload**: Support for uploading user-level and global-level RAG knowledge base materials
- **Digital Human Management**: Create and customize digital human appearances
- **Session History**: View and manage conversation history
- **Admin Console**: User management, system monitoring, and data analysis

## Technology Stack

- React 19
- Material UI 7
- WebSocket/WebRTC (for real-time communication)
- Axios (HTTP client)
- Web Speech API (speech recognition)

## Environment Requirements

- Node.js ≥ 18 (LTS version recommended)
- Npm ≥ 9 or pnpm/yarn
- Browser:
  Chrome/Edge latest version (better support for voice recognition and WebRTC)

## Installation Steps

```bash
# Install dependencies
$ npm install

# Start development server
$ npm start

# Build production version
$ npm run build
```




## Browser Support

- Chrome/Edge (latest version, recommended)
- Firefox (latest version)
- Safari (latest version)

Note: Voice recognition and WebRTC features perform best in Chrome and Edge.

