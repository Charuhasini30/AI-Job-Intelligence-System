"""Dummy job data for the AI job matcher."""

def get_dummy_jobs():
    """Return a list of dummy job postings with realistic technical requirements."""
    
    jobs = [
        {
            "title": "Senior Python Developer",
            "company": "TechCorp Inc.",
            "location": "San Francisco, CA",
            "experience_level": "Senior (5+ years)",
            "description": "We are seeking a Senior Python Developer to join our backend team. You will be responsible for developing scalable web applications and APIs using modern Python frameworks.",
            "required_skills": [
                "python", "django", "flask", "rest api", "postgresql", "docker", 
                "git", "linux", "sql", "aws", "redis", "celery", "pytest"
            ]
        },
        {
            "title": "Full Stack JavaScript Developer",
            "company": "StartupXYZ",
            "location": "New York, NY",
            "experience_level": "Mid-level (3-5 years)",
            "description": "Join our dynamic team to build modern web applications using cutting-edge JavaScript technologies. Experience with both frontend and backend development required.",
            "required_skills": [
                "javascript", "typescript", "react", "node.js", "express", "mongodb", 
                "html", "css", "git", "docker", "jest", "webpack", "npm"
            ]
        },
        {
            "title": "Data Scientist",
            "company": "DataAnalytics Pro",
            "location": "Boston, MA",
            "experience_level": "Mid-level (2-4 years)",
            "description": "We're looking for a Data Scientist to extract insights from large datasets and build predictive models. Strong background in statistics and machine learning required.",
            "required_skills": [
                "python", "r", "machine learning", "deep learning", "pandas", "numpy", 
                "scikit-learn", "tensorflow", "pytorch", "sql", "statistics", "jupyter", "matplotlib"
            ]
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudSolutions Ltd",
            "location": "Seattle, WA",
            "experience_level": "Senior (4+ years)",
            "description": "Seeking an experienced DevOps Engineer to manage our cloud infrastructure and implement CI/CD pipelines. AWS expertise required.",
            "required_skills": [
                "aws", "docker", "kubernetes", "terraform", "jenkins", "git", "bash", 
                "linux", "python", "ansible", "prometheus", "grafana", "ci/cd"
            ]
        },
        {
            "title": "Frontend React Developer",
            "company": "UX Design Studio",
            "location": "Los Angeles, CA",
            "experience_level": "Junior (1-3 years)",
            "description": "Join our creative team to build beautiful and responsive user interfaces. We're looking for someone passionate about modern frontend technologies.",
            "required_skills": [
                "react", "javascript", "typescript", "html", "css", "sass", "webpack", 
                "git", "responsive design", "redux", "jest", "npm", "bootstrap"
            ]
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Innovations Corp",
            "location": "Austin, TX",
            "experience_level": "Senior (4+ years)",
            "description": "We're seeking an ML Engineer to deploy and scale machine learning models in production. Experience with MLOps and cloud platforms essential.",
            "required_skills": [
                "python", "machine learning", "tensorflow", "pytorch", "docker", "kubernetes", 
                "aws", "mlops", "scikit-learn", "pandas", "sql", "git", "linux"
            ]
        },
        {
            "title": "Java Backend Developer",
            "company": "Enterprise Solutions Inc",
            "location": "Chicago, IL",
            "experience_level": "Mid-level (3-5 years)",
            "description": "Looking for a Java developer to work on enterprise-grade applications. Experience with Spring framework and microservices architecture preferred.",
            "required_skills": [
                "java", "spring", "spring boot", "hibernate", "mysql", "rest api", 
                "microservices", "maven", "git", "junit", "docker", "jenkins"
            ]
        },
        {
            "title": "Mobile App Developer (React Native)",
            "company": "MobileFirst Technologies",
            "location": "Miami, FL",
            "experience_level": "Mid-level (2-4 years)",
            "description": "Develop cross-platform mobile applications using React Native. Experience with both iOS and Android development lifecycle required.",
            "required_skills": [
                "react native", "javascript", "typescript", "react", "redux", "ios", 
                "android", "git", "npm", "expo", "firebase", "rest api"
            ]
        },
        {
            "title": "Cloud Architect",
            "company": "CloudFirst Consulting",
            "location": "Denver, CO",
            "experience_level": "Senior (6+ years)",
            "description": "Design and implement scalable cloud solutions for enterprise clients. Multi-cloud experience with AWS, Azure, and GCP preferred.",
            "required_skills": [
                "aws", "azure", "gcp", "cloud architecture", "terraform", "kubernetes", 
                "docker", "microservices", "security", "networking", "python", "bash"
            ]
        },
        {
            "title": "Cybersecurity Analyst",
            "company": "SecureNet Systems",
            "location": "Washington, DC",
            "experience_level": "Mid-level (3-5 years)",
            "description": "Protect our organization from cyber threats by monitoring security systems and conducting vulnerability assessments.",
            "required_skills": [
                "cybersecurity", "penetration testing", "vulnerability assessment", "firewall", 
                "networking", "linux", "python", "sql", "incident response", "security"
            ]
        },
        {
            "title": "Big Data Engineer",
            "company": "DataStream Analytics",
            "location": "Philadelphia, PA",
            "experience_level": "Senior (4+ years)",
            "description": "Build and maintain large-scale data processing pipelines using modern big data technologies. Experience with Spark and Hadoop required.",
            "required_skills": [
                "big data", "hadoop", "spark", "scala", "python", "kafka", "sql", 
                "hive", "hdfs", "yarn", "linux", "git", "docker"
            ]
        },
        {
            "title": "QA Automation Engineer",
            "company": "QualityFirst Software",
            "location": "Portland, OR",
            "experience_level": "Mid-level (2-4 years)",
            "description": "Develop and maintain automated testing frameworks to ensure software quality. Experience with test automation tools required.",
            "required_skills": [
                "test automation", "selenium", "python", "java", "junit", "testng", 
                "git", "jenkins", "ci/cd", "sql", "rest api", "agile"
            ]
        },
        # Popular internship and entry-level positions from Internshala and similar platforms
        {
            "title": "Web Development Intern",
            "company": "TechStartup India (via Internshala)",
            "location": "Remote",
            "experience_level": "Internship",
            "description": "Build responsive websites and web applications. Perfect for students and fresh graduates looking to gain real-world experience.",
            "required_skills": [
                "html", "css", "javascript", "bootstrap", "git", "responsive design"
            ]
        },
        {
            "title": "Python Developer Intern",
            "company": "DataTech Solutions (via Internshala)",
            "location": "Bangalore, India",
            "experience_level": "Internship",
            "description": "Work on Python-based projects including web development and data analysis. Great opportunity for computer science students.",
            "required_skills": [
                "python", "django", "flask", "sql", "git", "html", "css"
            ]
        },
        {
            "title": "Frontend Developer",
            "company": "Digital Agency Mumbai (via Naukri)",
            "location": "Mumbai, India",
            "experience_level": "Entry Level (0-2 years)",
            "description": "Create engaging user interfaces for web applications using modern frontend technologies.",
            "required_skills": [
                "react", "javascript", "html", "css", "typescript", "git", "npm", "webpack"
            ]
        },
        {
            "title": "Full Stack Developer Intern",
            "company": "EdTech Company (via LinkedIn)",
            "location": "Delhi, India",
            "experience_level": "Internship",
            "description": "Build end-to-end web applications for educational platform. Learn from experienced developers.",
            "required_skills": [
                "javascript", "node.js", "react", "mongodb", "express", "html", "css", "git"
            ]
        },
        {
            "title": "Data Analyst Intern",
            "company": "Analytics Firm (via Internshala)",
            "location": "Pune, India",
            "experience_level": "Internship",
            "description": "Analyze business data and create visualizations. Work with real datasets and learn industry-standard tools.",
            "required_skills": [
                "python", "pandas", "numpy", "matplotlib", "sql", "excel", "statistics"
            ]
        },
        {
            "title": "Mobile App Developer",
            "company": "App Development Studio (via AngelList)",
            "location": "Hyderabad, India",
            "experience_level": "Entry Level (1-2 years)",
            "description": "Develop cross-platform mobile applications for various clients. Work on innovative projects.",
            "required_skills": [
                "react native", "javascript", "typescript", "firebase", "git", "ios", "android"
            ]
        },
        {
            "title": "DevOps Intern",
            "company": "Cloud Solutions (via Internshala)",
            "location": "Chennai, India",
            "experience_level": "Internship",
            "description": "Learn cloud infrastructure management and CI/CD pipeline development. Great for engineering students.",
            "required_skills": [
                "linux", "docker", "git", "bash", "aws", "python", "jenkins"
            ]
        },
        {
            "title": "UI/UX Designer",
            "company": "Design Studio (via Behance Jobs)",
            "location": "Gurgaon, India",
            "experience_level": "Entry Level (0-2 years)",
            "description": "Create user-centered designs for web and mobile applications. Work with product teams.",
            "required_skills": [
                "figma", "adobe xd", "sketch", "html", "css", "javascript", "user research"
            ]
        },
        {
            "title": "Software Developer Trainee",
            "company": "IT Services Company (via Freshersworld)",
            "location": "Kolkata, India",
            "experience_level": "Entry Level (0-1 years)",
            "description": "Join our graduate training program. Learn multiple technologies and work on client projects.",
            "required_skills": [
                "java", "python", "sql", "html", "css", "javascript", "git", "agile"
            ]
        }
    ]
    
    return jobs
