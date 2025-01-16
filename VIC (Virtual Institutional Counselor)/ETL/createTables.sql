-- Drop existing tables if they exist
DROP TABLE IF EXISTS sections CASCADE;
DROP TABLE IF EXISTS classrooms CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS meeting_times CASCADE;

-- Table for courses
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    department VARCHAR(100),
    course_code VARCHAR(20),
    course_name VARCHAR(200),
    director_approval BOOLEAN DEFAULT FALSE,
    syllabus_link TEXT,
    year INT CHECK (year >= 1900),
    semester VARCHAR(20) CHECK (semester IN ('Fall', 'Spring', 'Summer', 'Any')),
    course_type VARCHAR(20) CHECK (course_type IN ('Regular', 'OnDemand')),
    CONSTRAINT valid_semester_for_course_type CHECK (
        (course_type = 'Regular' AND semester IN ('Fall', 'Spring')) OR
        (course_type = 'OnDemand' AND semester = 'Any')
    )
);

-- Sequence to start course_id from 2
ALTER SEQUENCE courses_course_id_seq RESTART WITH 2;

-- Table for classrooms
CREATE TABLE classrooms (
    classroom_id SERIAL PRIMARY KEY,
    classroom_name VARCHAR(50),
    capacity INT CHECK (capacity > 0)
);

-- Table for sections
CREATE TABLE sections (
    section_id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(course_id),
    section_code VARCHAR(10),
    classroom_id INT REFERENCES classrooms(classroom_id),
    meeting_days VARCHAR(5) CHECK (meeting_days IN ('LMV', 'MJ')),
    start_time TIME,
    end_time TIME,
    capacity INT CHECK (capacity > 0),
    year INT CHECK (year >= 1900),
    semester VARCHAR(20) CHECK (semester IN ('Fall', 'Spring', 'Summer')),
    CONSTRAINT no_overlapping_sections CHECK (start_time < end_time),
    CONSTRAINT unique_section_per_course UNIQUE (course_id, section_code, start_time),
    CONSTRAINT no_overlapping_classroom_use UNIQUE (classroom_id, meeting_days, start_time),
    CONSTRAINT valid_mj_times CHECK (
        meeting_days != 'MJ' OR
        (
            (start_time >= '07:30' AND end_time <= '10:15') OR
            (start_time >= '12:30' AND end_time <= '19:45')
        )
    ),
    CONSTRAINT valid_lmv_times CHECK (
        meeting_days != 'LMV' OR
        (start_time >= '07:30' AND end_time <= '21:20')
    ),
    CONSTRAINT valid_meeting_duration CHECK (
        (meeting_days = 'LMV' AND EXTRACT(EPOCH FROM (end_time - start_time))/60 = 50) OR
        (meeting_days = 'MJ' AND EXTRACT(EPOCH FROM (end_time - start_time))/60 = 75)
    )
);

-- Table for defining valid meeting times for each meeting type
CREATE TABLE meeting_times (
    meeting_id SERIAL PRIMARY KEY,
    meeting_type VARCHAR(5) CHECK (meeting_type IN ('LMV', 'MJ')),
    start_time TIME,
    end_time TIME,
    duration INT CHECK (duration > 0)
);

-- Insert dummy record for courses requiring director approval
INSERT INTO courses (department, course_code, course_name, director_approval, syllabus_link, year, semester)
VALUES ('Authorization from the Director of the Department', NULL, NULL, TRUE, NULL, 1900, 'Any');