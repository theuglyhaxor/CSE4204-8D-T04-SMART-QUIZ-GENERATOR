-- =====================================================================
-- SMART QUIZ GENERATOR — Sample / Seed Data
-- CSE4204-8D-T04 | Batch 8D | Team 04
-- =====================================================================
-- Run AFTER the database exists and migrations have been applied:
--     python manage.py migrate
--     mysql -u root -p smart_quiz_generator < database/seed_data.sql
-- =====================================================================

USE smart_quiz_generator;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE quiz_api_quizattempt;
TRUNCATE TABLE quiz_api_question;
TRUNCATE TABLE quiz_api_quiz;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO quiz_api_quiz (
    id,
    title,
    description,
    difficulty,
    duration_minutes,
    is_active,
    created_at,
    updated_at
) VALUES
(1, 'Biology Basics', 'A starter quiz covering cell structure and basic biology.', 'Easy', 5, TRUE, '2026-05-25 08:00:00', '2026-05-25 08:00:00'),
(2, 'Mathematics Warmup', 'A short algebra and arithmetic practice quiz.', 'Medium', 8, TRUE, '2026-05-25 08:05:00', '2026-05-25 08:05:00');

INSERT INTO quiz_api_question (
    id,
    quiz_id,
    prompt,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_option,
    explanation,
    `order`
) VALUES
(1, 1, 'What is the powerhouse of the cell?', 'Nucleus', 'Mitochondria', 'Ribosome', 'Cell wall', 'B', 'Mitochondria generate ATP for the cell.', 1),
(2, 1, 'Which structure controls what enters and leaves the cell?', 'Cell membrane', 'Cytoplasm', 'Vacuole', 'Nucleus', 'A', 'The cell membrane is the selective barrier around the cell.', 2),
(3, 2, 'What is 12 + 8?', '18', '20', '22', '24', 'B', '12 plus 8 equals 20.', 1),
(4, 2, 'Solve: 3x = 12', 'x = 2', 'x = 3', 'x = 4', 'x = 6', 'C', 'Divide both sides by 3 to get x = 4.', 2);

INSERT INTO quiz_api_quizattempt (
    id,
    quiz_id,
    student_name,
    responses,
    score,
    total,
    created_at
) VALUES
(1, 1, 'Alice', JSON_ARRAY(
    JSON_OBJECT('question', 1, 'selected_option', 'B', 'correct_option', 'B', 'is_correct', TRUE),
    JSON_OBJECT('question', 2, 'selected_option', 'A', 'correct_option', 'A', 'is_correct', TRUE)
), 2, 2, '2026-05-25 09:00:00'),
(2, 2, 'Bob', JSON_ARRAY(
    JSON_OBJECT('question', 3, 'selected_option', 'A', 'correct_option', 'B', 'is_correct', FALSE),
    JSON_OBJECT('question', 4, 'selected_option', 'C', 'correct_option', 'C', 'is_correct', TRUE)
), 1, 2, '2026-05-25 09:15:00');
