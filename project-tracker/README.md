A. Problem statement 
- Users log in to see their name, phone, address, project name, and current stage (1–6). 
- When a project’s stage changes (1→2), the user is notified by email or SMS.

B. User stories (each with acceptance criteria)
- As a user, I can log in with username + password.
    - Accept when: wrong password shows an error; correct password takes me to dashboard.
- As a user, I can see my profile (name, phone, address) and project (name, stage 1–6).
    - Accept when: I see exactly those fields on the dashboard.
- As the system, I record stage changes in a history log.
    - Accept when: every update writes old_stage, new_stage, timestamp.

C. Data model (fields only, not SQL yet)
- users: id, username (unique), password_hash, role
- customers: id, name, phone, address
- projects: id, customer_id, name, stage (1–6), updated_at
- project_stage_history: id, project_id, old_stage, new_stage, changed_at


D. Non-functional guardrails
- Passwords are hashed (Argon2/bcrypt).
- Use parameterized queries/ORM.
- Stage is validated (must be 1–6).
- Notifications sent after the DB update (or queued).

E. Tech choices
- Editor: VS Code ✅
- Backend: Flask 
- DB: SQLite for development 
- ORM: SQLAlchemy
- Notifications: Email (SendGrid) to start; SMS (Twilio) optional later.

F. “Definition of done”
- Login works securely.
- Dashboard shows the four fields + project stage.
- Admin page (or quick script) can change stage.
- Stage 1→2 sends an email.
- History rows are created on every change.