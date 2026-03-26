# PRD Example (Input)

## Product

TaskFlow Lite

## Goal

Enable small teams to manage tasks, attach files, and receive deadline reminders.

## Features

### F-01 User Sign-In

- Users can sign in with email and password.
- System returns a session token.

### F-02 Task CRUD API

- Authenticated users can create, edit, list, and delete tasks.
- Each task has title, description, due date, and status.

### F-03 File Attachments

- Users can upload files to tasks.
- Files are shown in task detail view.

### F-04 Activity Feed

- Show latest task events for each project.
- Events include task updates and file uploads.

### F-05 Reminder Notifications

- Send reminder email 24 hours before due date.
- Users can disable reminders per project.

## Non-Functional Requirements

- API response time should be under 500 ms for common operations.
- System should support 5,000 active users.
