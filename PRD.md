# Project Requirements Document (PRD) for Regression Auto-Remediation Syst### Daily Regression Data Sources
1. **regression database Table**: Database table containing test programs enabled for daily execution
2. **Regression Text Files**: Daily regression results from V93K test program executions  
3. **Datalog Files**: Detailed test execution logs and measurement data from Linux terminals
4. **Build Logs**: Compilation errors, warnings, and build process information
5. **Module Baseline Information**: Latest baseline versions and change tracking
6. **Historical Solution Database**: Oracle database storage of confirmed fixes and patternsGoal

Develop an intelligent auto-remediation system that continuously monitors V93K SMT7/8 test program regression results from daily integration cycles using latest baselines of different modules. The system analyzes regression data from text files and logs, learns issue-solution patterns through domain-specific machine learning models, and automatically applies fixes when similar issues are detected. The system performs continuous learning by comparing baseline differences when issues are resolved, informs users about updates, and evolves its knowledge base. The goal is to reduce manual regression issue resolution effort by 70-80% while maintaining V93K test program expertise.

## Technology Stack

### Core AI Framework
- **Domain-Specific ML Models** using Hugging Face Transformers for V93K issue-solution pattern learning
- **V93K Knowledge Model** for test program domain expertise and code analysis
- **LangChain** for RAG (Retrieval Augmented Generation) and tool integration (file parsers, email, build tools)
- **scikit-learn** for classification and pattern recognition
- **OpenAI GPT-4** (optional) for complex code analysis when domain models need assistance

### Code Analysis & Processing
- **Tree-sitter** for parsing V93K test program syntax and generating Abstract Syntax Trees (AST)
- **Custom V93K Parsers** for regression log files, datalog files, and baseline comparison
- **diff utilities** for baseline source code comparison and change detection
- **regex** for pattern matching in log files and error messages

### Backend Infrastructure
- **Python 3.12+** for core system development
- **FastAPI** for REST API development (dashboard communication)
- **Oracle Database** for structured data storage (regression results, solutions, learned patterns)
- **File-based Storage** for raw logs and temporary data (text files, JSON for structured data)
- **Asyncio** for concurrent processing of multiple regression sessions

### Database Configuration
Oracle database configured via environment variables in `../.env`:
```env
DBDRIVER=Oracle
DBNAME=<DATABASE_NAME>
DBHOST=<DATABASE_HOST>
DBUSER=<DATABASE_USER>
DBPASSWD=<DATABASE_PASSWORD>
SID=<DATABASE_SID>
PORT=<DATABASE_PORT>
```
Key database tables:
- **REGRESSION_DAILY**: Regression test programs enabled for daily execution
- **REGRESSION_RESULTS**: Daily regression outcomes and analysis
- **LEARNED_PATTERNS**: ML model learned issue-solution patterns
- **APPLIED_SOLUTIONS**: History of automatically applied fixes

### Machine Learning & Analytics
- **Hugging Face Transformers** for training domain-specific models on V93K patterns
- **PyTorch** for custom model development and fine-tuning
- **pandas** and **NumPy** for regression data analysis and manipulation
- **spaCy** for natural language processing of error messages and logs

### Integration & Communication
- **Email or Dashboard Integration** (SMTP) for notifications to module owners and regression teams
- **Git Integration** for baseline comparison and code updates
- **V93K Build Tools Integration** for automated testing after code fixes
- **File Monitoring** for real-time regression data processing
- **Configuration Management** for module owner contacts and system settings

### Frontend & Visualization (Windows Compatible)
- **React.js** with TypeScript for web dashboard (accessible from Windows laptops)
- **Material-UI** for consistent UI components
- **Web-based Interface** for cross-platform access (Linux backend, Windows client)
- **Real-time Updates** via WebSocket for live regression monitoring
- **Baseline Comparison Viewer** for visualizing code differences

### Deployment & Infrastructure
- **Linux Red Hat 7/8** compatibility for V93K Advantest tester environment
- **Docker** for containerization and easy deployment
- **File-based Data Storage** with NFS/shared drives for multiple sites access
- **Systemd Services** for background process management
- **Web Server** (Nginx) for dashboard hosting and cross-platform access

## Data Sources and Learning Process

### Daily Regression Data Sources
1. **Regression Text Files**: Daily regression results from V93K test program executions
2. **Datalog Files**: Detailed test execution logs and measurement data
3. **Build Logs**: Compilation errors, warnings, and build process information
4. **Module Baseline Information**: different module's baseline versions
5. **Historical Issue-Solution Database**: File-based storage of confirmed fixes
6. **Configuration Files**: Module owner contacts, tool owner emails, system settings

### Automated Learning Process
1. **Issue Detection**: Analyze daily regression data for failures and patterns
2. **Baseline Comparison**: When issues resolve in new baselines, compare source code differences
3. **Solution Generation**: Create proposed fixes based on learned patterns and baseline analysis
4. **Automated Application**: Apply solutions and run validation tests
5. **User Notification**: Inform users about applied changes and validation results
6. **Knowledge Base Update**: Store successful solutions in Oracle database for future use

### Data Storage Structure
```
Database Tables (Oracle):
- REGRESSION_DAILY          # Test programs enabled for regression
- REGRESSION_RESULTS        # Daily regression outcomes
- LEARNED_PATTERNS         # ML model learned patterns (JSON format)
- APPLIED_SOLUTIONS        # History of applied fixes
- BASELINE_CHANGES         # Tracked baseline modifications

File Storage:
├── regression_logs/            # Raw regression text files and logs
├── datalog_files/             # Detailed test execution data
├── models/                    # ML models directory
│   ├── trained/               # Trained model files (pickle/joblib)
│   └── training_data/         # Training datasets
└── temp/                      # Temporary processing files
```

## Directory Structure

```
regression_auto_remediation/
├── src/
│   ├── core/                     # Core system logic and orchestration
│   ├── parsers/                  # Regression data and log file parsers
│   ├── learning/                 # Continuous learning and baseline comparison
│   ├── solutions/                # Solution application and validation
│   ├── database/                 # Oracle database integration and queries
│   ├── api/                      # REST API for dashboard communication
│   └── utils/                    # Utilities and configuration management
├── models/                       # ML models - both code and trained files
│   ├── src/                      # ML model classes and training code
│   │   ├── issue_solution_model.py    # Issue-solution pattern model
│   │   ├── v93k_knowledge_model.py    # V93K domain expertise model
│   │   └── model_trainer.py           # Training utilities
│   ├── trained/                  # Trained model files (pickle/joblib)
│   │   ├── issue_solution.pkl    # Trained issue-solution model
│   │   ├── v93k_knowledge.pkl    # Trained V93K knowledge model
│   │   └── model_metadata.json   # Model version and performance info
│   └── training_data/            # Training datasets
├── frontend/                     # React dashboard for cross-platform access
├── data/                         # File-based temporary storage
│   ├── regression_logs/          # Raw regression text files
│   ├── datalog_files/           # Test execution data
│   └── temp/                    # Temporary processing files
├── tests/                        # Test suites
├── scripts/                      # Setup and utility scripts
├── docker/                       # Container configurations
└── docs/                         # Documentation
```

## Core System Architecture

### Two-Model Approach
1. **Issue-Solution Learning Model**: Learns patterns between regression issues and their solutions
2. **V93K Domain Knowledge Model**: Understands V93K test program structure, syntax, and best practices

### Single Intelligent System (No Multi-Agent)
- **Unified Processing Engine**: Single system that orchestrates all operations
- **Modular Components**: Separate modules for parsing, learning, solution application, and communication
- **Streamlined Workflow**: Linear process from issue detection to solution application

## Core Capabilities

### Daily Regression Monitoring
- **Database Integration**: Reads REGRESSION_DAILY table for enabled test programs
- **Automated Data Ingestion**: Continuously monitors regression text files and datalogs
- **Multi-Module Baseline Tracking**: Tracks module baselines and changes
- **Issue Pattern Recognition**: Identifies recurring failure patterns using domain-specific models
- **Real-time Processing**: Processes daily regression data as it becomes available

### Intelligent Learning System
- **Baseline Comparison Analysis**: Compares source code differences when issues resolve in new baselines
- **Automated Solution Application**: Applies learned solutions without human gating
- **Solution Validation**: Tests proposed fixes through automated build and run cycles
- **User Notification**: Informs users about applied changes and validation results
- **Knowledge Base Evolution**: Continuously expands Oracle database with successful solutions

### V93K Domain Expertise
- **Test Program Knowledge**: Deep understanding of V93K SMT7/8 test program structure and syntax
- **Module-Specific Intelligence**: Specialized knowledge for different modules
- **Error Classification**: Categorizes V93K-specific errors and their typical solutions
- **Code Quality Assurance**: Ensures fixes maintain V93K coding standards and best practices

### Automated Solution Application
- **Risk Assessment**: Evaluates safety of applying solutions based on confidence levels
- **Automated Code Updates**: Updates test program code with validated solutions
- **Build and Test Execution**: Runs automated builds and tests to verify fix effectiveness
- **Dashboard Notification**: Updates database and informs users via dashboard

## Functional Requirements

### Core Features
1. **Daily Regression Monitoring**: Monitor and process 100% of daily regression data automatically
2. **Issue Detection Accuracy**: Identify 95%+ of common V93K regression issues
3. **Baseline Comparison**: Automatically detect and analyze baseline changes when issues resolve
4. **Automated Solution Application**: Apply learned solutions with 90%+ success rate
5. **Continuous Learning**: Demonstrate measurable improvement in issue recognition over time
6. **Dashboard Integration**: Real-time updates to Oracle database and dashboard display
4. **Human Confirmation Workflow**: Email module owners for solution confirmation with 24 hour response tracking
5. **Automated Solution Application**: Apply confirmed solutions with 90%+ success rate
6. **Continuous Learning**: Demonstrate measurable improvement in issue recognition over time

### Learning and Communication Requirements
1. **Email Integration**: Automatic emails to module owners and regression teams
2. **Baseline Tracking**: Track and compare multiple module baselines (contact, ROM, SCAN, etc.)
3. **Solution Confirmation**: Structured workflow for human validation of new solutions
4. **Knowledge Base Management**: File-based storage and retrieval of learned solutions
5. **Cross-site Data Access**: Singapore-Villach file sharing compatibility

### Dashboard Requirements (Windows Compatible)
1. **Web-based Interface**: Accessible from Windows laptops via web browser
2. **Real-time Monitoring**: Live view of daily regression status and issue detection
3. **Baseline Comparison Viewer**: Visual diff display of source code changes
4. **Solution Management**: Review and approval interface for new solutions
5. **Learning Analytics**: Metrics on model performance and solution effectiveness
6. **Configuration Management**: Interface for updating module owner contacts and settings

## Technical Requirements

### Performance Requirements
- **Processing Speed**: Process daily regression data within 30 minutes of availability
- **Response Time**: Dashboard responses within 3 seconds
- **Availability**: 99% uptime with robust error handling
- **Scalability**: Handle multiple concurrent regression sessions across different modules

### Platform Requirements
- **Linux Compatibility**: Full compatibility with Red Hat 7/8 on V93K Advantest testers
- **Cross-platform Access**: Web dashboard accessible from Windows laptops
- **File System Integration**: NFS/shared drive compatibility for Singapore-Villach data sharing
- **No Database Dependency**: Fully file-based storage system

### Security Requirements
- **Data Protection**: Secure handling of V93K test program source code
- **Access Control**: Role-based access through configuration files
- **Audit Logging**: Complete file-based audit trail of all system activities
- **Email Security**: Secure SMTP integration for notifications

### Integration Requirements
- **Email Systems**: SMTP integration for module owner and regression team notifications
- **Git Integration**: Direct integration with baseline repositories for code comparison
- **V93K Build Tools**: Integration with V93K compilation and testing tools
- **File Monitoring**: Real-time monitoring of regression data directories
- **Shared Storage**: NFS/network drive integration for cross-site data access

## Benefits

### Productivity Enhancement
- **Time Savings**: Reduce manual issue resolution time by 70-80%
- **Faster Releases**: Accelerate development cycles through automated fixes
- **Reduced Interruptions**: Minimize disruptions to development workflows
- **Focus on Innovation**: Allow engineers to focus on complex, value-added tasks
- **24/7 Operation**: Continuous monitoring and resolution capabilities

### Quality Improvement
- **Consistent Solutions**: Apply proven, standardized solutions to common issues
- **Error Prevention**: Proactively identify and prevent recurring issues
- **Best Practice Enforcement**: Ensure adherence to coding standards and best practices
- **Knowledge Preservation**: Capture and preserve expert knowledge in the system
- **Continuous Improvement**: Evolve solution quality through machine learning

### Cost Benefits
- **Reduced Labor Costs**: Decrease manual effort required for issue resolution
- **Faster Time-to-Market**: Accelerate product development and release cycles
- **Lower Error Rates**: Reduce costly errors and rework through automated quality checks
- **Resource Optimization**: Better allocation of engineering resources
- **Scalability**: Handle increased regression volume without proportional resource increases

### Risk Mitigation
- **Predictable Outcomes**: Apply proven solutions with known success rates
- **Validation Checks**: Ensure solution safety through automated validation
- **Rollback Capability**: Quick recovery from unsuccessful changes
- **Audit Trail**: Complete traceability of all automated changes
- **Human Oversight**: Maintain control over high-risk or complex changes

## Acceptance Criteria

- ✅ Issue detection accuracy >50%
- ✅ Solution generation success rate >50%
- ✅ Auto-remediation success rate >50%
- ✅ Learning system shows measurable improvement
- ✅ User satisfaction rating >4.0/5.0
- ✅ Code quality maintained or improved

## Success Metrics

### Operational Metrics
- **Issue Detection Rate**: 95%+ of regression issues identified automatically
- **Solution Application Success**: 90%+ of applied solutions resolve issues successfully
- **Processing Time**: Daily regression analysis completed within 30 minutes
- **Database Integration**: 100% reliable Oracle database connectivity and updates

### Business Metrics
- **Time Savings**: 70-80% reduction in manual regression issue resolution
- **Knowledge Preservation**: Continuous growth of V93K domain expertise in the system
- **System Reliability**: Minimal disruption to daily regression workflows
- **Cost Reduction**: Significant decrease in manual effort

## Future Enhancements

### Platform Extension
- **Ultraflex Support**: Extend the system to support Ultraflex test platforms in addition to V93K
- **Multi-Platform Learning**: Cross-platform pattern recognition and solution sharing
- **Universal Test Program Intelligence**: Common domain knowledge across different test platforms

### Model Improvements
- **Enhanced V93K Knowledge**: Deeper understanding of test program patterns and best practices
- **Multi-Module Learning**: Cross-module pattern recognition and solution sharing
- **Predictive Analytics**: Proactive identification of potential issues before they occur
- **Advanced Baseline Analysis**: More sophisticated source code change analysis

### System Enhancements
- **Advanced Analytics**: Detailed insights into regression trends and module performance
- **Automated Reporting**: Regular reports for management and module owners
- **Integration Expansion**: Support for additional V93K tools and workflows

The V93K Regression Auto-Remediation System provides intelligent, domain-specific automation for daily regression monitoring, combining machine learning with V93K expertise to maintain development velocity while ensuring quality and reliability in test program development.
