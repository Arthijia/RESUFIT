# ============================================================
# RESUFIT — Skills Taxonomy
# Canonical skill -> list of synonyms/variations that should match it
# ============================================================

SKILLS_TAXONOMY = {
    # Programming Languages
    "python": ["python", "python3", "py"],
    "java": ["java"],
    "javascript": ["javascript", "js", "es6", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "c++": ["c++", "cpp"],
    "c": ["c programming", "c language"],
    "c#": ["c#", "csharp", ".net"],
    "sql": ["sql", "structured query language"],
    "r": ["r programming", "r language"],
    "go": ["golang", "go language"],
    "php": ["php"],
    "swift": ["swift"],
    "kotlin": ["kotlin"],

    # Web / Frontend
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular", "angular.js", "angularjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "node.js": ["node.js", "nodejs", "node"],
    "next.js": ["next.js", "nextjs"],
    "tailwind": ["tailwind", "tailwind css"],
    "bootstrap": ["bootstrap"],

    # Backend / Frameworks
    "flask": ["flask"],
    "django": ["django"],
    "spring boot": ["spring boot", "spring"],
    "express.js": ["express.js", "express", "expressjs"],
    "fastapi": ["fastapi"],
    "rest api": ["rest api", "restful api", "rest apis", "api development"],
    "graphql": ["graphql"],

    # Data / ML / AI
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "data science": ["data science"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "cv", "opencv"],
    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data viz"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "statistics": ["statistics", "statistical analysis"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "ms excel", "microsoft excel"],

    # Cloud / DevOps
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "cloud computing": ["cloud computing", "cloud"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
    "terraform": ["terraform"],
    "linux": ["linux", "unix"],

    # Databases
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo"],
    "database management": ["database management", "dbms"],
    "firebase": ["firebase"],

    # Tools
    "git": ["git", "version control"],
    "github": ["github"],
    "jira": ["jira"],
    "figma": ["figma"],
    "postman": ["postman"],

    # Soft Skills
    "communication": ["communication", "communication skills"],
    "teamwork": ["teamwork", "team player", "collaboration"],
    "leadership": ["leadership", "team lead", "leadership skills"],
    "problem solving": ["problem solving", "problem-solving", "analytical thinking"],
    "project management": ["project management"],
    "time management": ["time management"],
    "critical thinking": ["critical thinking"],
    "adaptability": ["adaptability", "flexibility"],
    "presentation skills": ["presentation skills", "public speaking"],

    # Mobile
    "android development": ["android development", "android"],
    "ios development": ["ios development", "ios"],
    "flutter": ["flutter"],
    "react native": ["react native"],
}


def get_all_skill_variants():
    """Returns a flat dict mapping every variant phrase -> canonical skill name."""
    variant_map = {}
    for canonical, variants in SKILLS_TAXONOMY.items():
        for v in variants:
            variant_map[v.lower()] = canonical
    return variant_map
