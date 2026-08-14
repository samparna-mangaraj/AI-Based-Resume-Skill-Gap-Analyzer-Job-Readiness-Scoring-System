// ============================================
// JOB CATEGORIES DATA MODULE
// ============================================
// Contains all 15 IT job categories with tiered skills
// (core, secondary, bonus) and personalized recommendations.

const JOB_CATEGORIES = {
  "Software Development": {
    roles: ["Frontend", "Backend", "Full Stack", "Software Engineer"],
    core: ["javascript", "python", "java", "c++", "react", "node.js", "django", "spring boot", "dsa", "oop"],
    secondary: ["sql", "mongodb", "apis", "git"],
    bonus: ["deployment", "system design"],
    icon: "💻",
    color: "#00f5ff",
    recommendations: {
      projects: "Build 3 real-world projects (e.g., SaaS, management systems)",
      dsa: "Practice DSA daily",
      deployment: "Deploy projects online",
      "system design": "Learn basic system design",
      oop: "Master object-oriented programming principles"
    }
  },

  "Web Development": {
    roles: ["Web Developer", "UI Developer", "Web Designer"],
    core: ["html", "css", "javascript"],
    secondary: ["bootstrap", "tailwind", "responsive design"],
    bonus: ["seo"],
    icon: "🌐",
    color: "#bf00ff",
    recommendations: {
      portfolio: "Create a portfolio website",
      clients: "Work with small businesses (real clients)",
      performance: "Optimize speed & performance",
      ui: "Focus on UI attractiveness"
    }
  },

  "Mobile Development": {
    roles: ["Android", "iOS", "Flutter Developer"],
    core: ["kotlin", "java", "swift", "flutter", "react native"],
    secondary: ["firebase", "apis"],
    bonus: ["notifications", "authentication"],
    icon: "📱",
    color: "#00ff88",
    recommendations: {
      apps: "Publish at least 1 live app on Play Store or App Store",
      auth: "Learn authentication & notifications",
      ui: "Focus on smooth UI/UX with fluid animations",
      features: "Add real-world features (payments, chat, etc.)"
    }
  },

  "UI/UX Design": {
    roles: ["UI Designer", "UX Designer", "Product Designer"],
    core: ["figma", "adobe xd"],
    secondary: ["wireframing", "prototyping", "user research"],
    bonus: ["design principles"],
    icon: "🎨",
    color: "#ff00a8",
    recommendations: {
      portfolio: "Build a strong design portfolio on Dribbble or Behance",
      case_study: "Create detailed design case studies showing your process",
      redesign: "Redesign popular apps for practice",
      ux: "Focus on user experience (psychology & usability)"
    }
  },

  "Data Science": {
    roles: ["Data Analyst", "Data Scientist"],
    core: ["python", "r", "statistics"],
    secondary: ["sql", "excel", "power bi", "tableau"],
    bonus: ["machine learning"],
    icon: "📊",
    color: "#0080ff",
    recommendations: {
      kaggle: "Work on Kaggle datasets",
      dashboard: "Build interactive dashboards (Power BI / Tableau)",
      insights: "Focus on insights, not just code",
      problems: "Solve real business problems",
      storytelling: "Learn storytelling with data"
    }
  },

  "AI/ML": {
    roles: ["ML Engineer", "AI Engineer"],
    core: ["python", "tensorflow", "pytorch"],
    secondary: ["nlp", "deep learning"],
    bonus: ["deployment"],
    icon: "🤖",
    color: "#ff6b00",
    recommendations: {
      projects: "Build small ML projects first",
      deployment: "Learn model deployment (Flask / FastAPI)",
      apis: "Use AI APIs in real apps",
      tools: "Create AI-based SaaS tools",
      cases: "Focus on practical use-cases"
    }
  },

  "Cloud Computing": {
    roles: ["Cloud Engineer", "DevOps Engineer"],
    core: ["aws", "azure", "gcp"],
    secondary: ["docker", "kubernetes", "ci/cd"],
    bonus: ["linux"],
    icon: "☁️",
    color: "#00d4ff",
    recommendations: {
      certs: "Get cloud certifications (AWS/Azure/GCP)",
      deploy: "Deploy real projects on cloud platforms",
      containers: "Learn containerization (Docker & Kubernetes)",
      scaling: "Understand scaling & cost optimization",
      architecture: "Study cloud architecture basics"
    }
  },

  "Cybersecurity": {
    roles: ["Security Analyst", "Ethical Hacker"],
    core: ["networking", "cryptography"],
    secondary: ["kali linux", "metasploit"],
    bonus: ["penetration testing"],
    icon: "🔒",
    color: "#ff4444",
    recommendations: {
      practice: "Practice on TryHackMe / Hack The Box",
      pentest: "Learn penetration testing",
      vuln: "Study real-world vulnerabilities",
      bounty: "Join bug bounty programs",
      lab: "Build a security lab setup"
    }
  },

  "Data Engineering": {
    roles: ["DBA", "Data Engineer"],
    core: ["sql", "database design"],
    secondary: ["etl", "hadoop", "spark"],
    bonus: ["optimization"],
    icon: "🗄️",
    color: "#9b59b6",
    recommendations: {
      sql: "Master advanced SQL (window functions, CTEs, optimization)",
      large: "Work with large datasets",
      etl: "Build end-to-end ETL pipelines",
      perf: "Optimize database performance",
      warehouse: "Learn data warehousing"
    }
  },

"DevOps": {
    roles: ["DevOps Engineer", "SRE"],
    core: ["ci/cd", "docker", "kubernetes"],
    secondary: ["bash", "python"],
    bonus: ["terraform"],
    icon: "🔄",
    color: "#27ae60",
    recommendations: {
      pipelines: "Build CI/CD deployment pipelines",
      auto: "Automate infrastructure provisioning & workflows",
      docker: "Learn Docker & Kubernetes deeply",
      monitor: "Monitor applications (logs, metrics, alerts)",
      projects: "Work on real DevOps projects"
    }
  },

  "IT Support": {
    roles: ["System Admin", "Network Engineer"],
    core: ["networking", "linux", "windows"],
    secondary: ["troubleshooting"],
    bonus: ["security basics"],
    icon: "🌍",
    color: "#e67e22",
    recommendations: {
      practice: "Practice troubleshooting systems",
      linux: "Learn Linux administration deeply",
      lab: "Set up home lab environments",
      network: "Understand networking practically",
      hands: "Gain hands-on experience"
    }
  },

"Game Development": {
    roles: ["Game Developer"],
    core: ["unity", "unreal"],
    secondary: ["c#", "c++"],
    bonus: ["game physics"],
    icon: "🎮",
    color: "#e74c3c",
    recommendations: {
      games: "Build small playable games",
      gameplay: "Focus on gameplay experience",
      physics: "Learn physics & animations",
      publish: "Publish games online (itch.io, Steam)",
      skills: "Improve creativity & design skills"
    }
  },

"QA Testing": {
    roles: ["QA Engineer", "Automation Tester"],
    core: ["manual testing"],
    secondary: ["selenium", "cypress"],
    bonus: ["jira"],
    icon: "📊",
    color: "#2ecc71",
    recommendations: {
      both: "Learn both manual & automation testing",
      tools: "Practice Selenium / Cypress / Playwright",
      cases: "Write proper test cases with edge coverage",
      real: "Test real-world applications",
      sdlc: "Understand the SDLC process"
    }
  },

  "Project Management": {
    roles: ["Project Manager", "Scrum Master"],
    core: ["agile", "scrum"],
    secondary: ["jira", "trello"],
    bonus: ["communication"],
    icon: "📋",
    color: "#3498db",
    recommendations: {
      agile: "Learn Agile & Scrum methodologies",
      manage: "Manage small projects/teams",
      comm: "Improve communication & leadership skills",
      tools: "Use tools like Jira/Trello effectively",
      real: "Handle real-world project scenarios"
    }
  },

  "Emerging Fields": {
    roles: ["Blockchain Dev", "AR/VR Dev", "IoT Engineer"],
    core: ["solidity", "web3", "embedded systems"],
    secondary: ["unity"],
    bonus: ["innovation"],
    icon: "🚀",
    color: "#f39c12",
    recommendations: {
      niche: "Choose ONE niche and become a specialist",
      projects: "Build 1–2 strong portfolio projects",
      trends: "Stay updated with emerging trends",
      innovate: "Focus on innovation and practical use-cases"
    }
  }
};

// Skill synonyms for normalization
const SKILL_SYNONYMS = {
  "js": "javascript",
  "ts": "typescript",
  "ml": "machine learning",
  "ai": "artificial intelligence",
  "dl": "deep learning",
  "ds": "data structures",
  "algo": "algorithms",
  "py": "python",
  "rb": "ruby",
  "rn": "react native",
  "rjs": "react",
  "reactjs": "react",
  "react.js": "react",
  "nodejs": "node.js",
  "node": "node.js",
  "nextjs": "next.js",
  "next": "next.js",
  "vuejs": "vue.js",
  "vue": "vue.js",
  "angular.js": "angular",
  "angularjs": "angular",
  "expressjs": "express",
  "express.js": "express",
  "springboot": "spring boot",
  "spring": "spring boot",
  "k8s": "kubernetes",
  "kube": "kubernetes",
  "ci cd": "ci/cd",
  "cicd": "ci/cd",
  "continuous integration": "ci/cd",
  "aws cloud": "aws",
  "amazon web services": "aws",
  "google cloud": "gcp",
  "google cloud platform": "gcp",
  "microsoft azure": "azure",
  "mongo": "mongodb",
  "postgres": "postgresql",
  "mysql": "sql",
  "tf": "tensorflow",
  "pt": "pytorch",
  "ux": "user research",
  "html5": "html",
  "css3": "css",
  "tailwindcss": "tailwind",
  "tailwind css": "tailwind",
  "tw": "tailwind",
  "bs": "bootstrap",
  "oop concepts": "oop",
  "object oriented": "oop",
  "data structures": "dsa",
  "data structures and algorithms": "dsa",
  "algorithms": "dsa",
  "rest api": "apis",
  "rest apis": "apis",
  "restful": "apis",
  "graphql": "apis",
  "api": "apis",
  "github": "git",
  "gitlab": "git",
  "version control": "git",
  "kali": "kali linux",
  "pen testing": "penetration testing",
  "pentest": "penetration testing",
  "pentesting": "penetration testing",
  "responsive": "responsive design",
  "responsive web design": "responsive design",
  "rwd": "responsive design",
  "search engine optimization": "seo",
  "c sharp": "c#",
  "csharp": "c#",
  "cpp": "c++",
  "cplusplus": "c++",
  "ue": "unreal",
  "unreal engine": "unreal",
  "unity3d": "unity",
  "unity 3d": "unity",
  "manual qa": "manual testing",
  "test cases": "manual testing",
  "project management": "agile",
  "db design": "database design",
  "database": "database design",
  "extract transform load": "etl",
  "apache spark": "spark",
  "apache hadoop": "hadoop",
  "smart contracts": "solidity",
  "blockchain": "solidity",
  "web 3": "web3",
  "web 3.0": "web3",
  "iot": "embedded systems",
  "internet of things": "embedded systems"
};

// Make available globally
if (typeof window !== 'undefined') {
  window.JOB_CATEGORIES = JOB_CATEGORIES;
  window.SKILL_SYNONYMS = SKILL_SYNONYMS;
}
