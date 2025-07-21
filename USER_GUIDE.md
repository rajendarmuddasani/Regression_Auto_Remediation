# User Guide - Regression Auto-Remediation System

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Dashboard Interface](#dashboard-interface)
4. [Daily Operations](#daily-operations)
5. [Configuration](#configuration)
6. [Monitoring & Analytics](#monitoring--analytics)
7. [Troubleshooting](#troubleshooting)
8. [FAQs](#faqs)

---

## Overview

The Regression Auto-Remediation System is an intelligent automation platform that monitors V93K test program regression results, automatically identifies issues, and applies validated solutions. The system learns from each regression cycle to improve its effectiveness over time.

### Key Benefits
- **70-80% reduction** in manual regression issue resolution time
- **Automated issue detection** with 95%+ accuracy
- **Real-time monitoring** and notifications
- **Continuous learning** from baseline changes
- **Cross-platform dashboard** access (Linux backend, Windows frontend)

---

## Getting Started

### System Access

#### Dashboard Access
1. **From Windows Laptop**: 
   - Open web browser
   - Navigate to: `http://<linux-server-ip>:3000`
   - Login with your credentials

2. **From Linux Terminal**:
   - SSH to the regression server
   - Access system logs: `tail -f /var/log/regression_auto_remediation.log`

#### First Time Setup
1. Contact system administrator for access credentials
2. Verify dashboard access from your workstation
3. Review current regression configuration
4. Familiarize yourself with the interface

### System Installation Options

When setting up the system on a new laptop/environment, you have two installation options:

#### Option 1: Automated Quick Setup (Recommended)
This is the fastest and easiest way to get the system running:

```bash
# 1. Clone the repository
git clone https://github.com/rajendarmuddasani/Regression_Auto_Remediation.git
cd Regression_Auto_Remediation

# 2. Run the automated setup script
./quick_setup.sh

# 3. Update .env with your database credentials
# Edit the .env file with your Oracle database details

# 4. Start the application
./start_app.sh
```

**What this does:**
- ✅ Automatically checks all prerequisites (Python 3.9+, Node.js 16+)
- ✅ Creates Python virtual environment and installs all dependencies
- ✅ Installs Node.js dependencies for the React frontend
- ✅ Creates environment configuration template (.env file)
- ✅ Generates startup scripts for easy application launch
- ✅ Tests the installation and provides access URLs

#### Option 2: Manual Setup (Advanced Users)
For users who prefer step-by-step manual installation:

```bash
# Backend setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd web_dashboard
npm install
cd ..

# Configuration
cp .env.example .env
# Edit .env with your database settings

# Start servers (requires 2 terminals)
# Terminal 1: uvicorn src.api.main:app --reload --port 8000
# Terminal 2: cd web_dashboard && npm run dev
```

**Important Note:** `requirements.txt` alone is not sufficient for a complete setup. You need:
- Python dependencies (requirements.txt)
- Node.js dependencies (package.json)
- Environment configuration (.env file)
- Database connectivity setup
- Both backend and frontend servers running

**Access URLs after setup:**
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## Dashboard Interface

### Main Dashboard
The main dashboard provides an overview of regression health and system status.

#### Key Sections:
1. **Regression Status Panel**
   - Current active regressions
   - Recent issue detections
   - Applied solutions count
   - System health indicators

2. **Issue Detection Summary**
   - Daily issue count
   - Issue types breakdown
   - Resolution success rate
   - Trending patterns

3. **Recent Activities Feed**
   - Latest applied solutions
   - System notifications
   - User actions log
   - Alert messages

### Navigation Menu
- **Dashboard**: Main overview page
- **Regressions**: Detailed regression monitoring
- **Issues**: Issue tracking and analysis
- **Solutions**: Applied solutions history
- **Baselines**: Baseline comparison viewer
- **Analytics**: Performance metrics and trends
- **Settings**: System configuration

---

## Daily Operations

### Morning Routine (Recommended)

#### 1. Check Daily Status
```
1. Access dashboard
2. Review overnight regression results
3. Check for any failed automated solutions
4. Review system notifications
```

#### 2. Validate Applied Solutions
```
1. Go to "Solutions" tab
2. Review automatically applied fixes
3. Check validation status for each solution
4. Investigate any failed validations
```

#### 3. Monitor Active Regressions
```
1. Navigate to "Regressions" tab
2. Monitor in-progress regression sessions
3. Check for any stuck or failed processes
4. Review real-time issue detection
```

### Throughout the Day

#### Real-time Monitoring
- Dashboard automatically updates every 30 seconds
- Notifications appear for new issues detected
- Solution applications are logged in real-time
- System alerts are displayed immediately

#### Responding to Notifications

**New Issue Detected:**
1. Review issue details in the "Issues" tab
2. Check if similar issues have been resolved before
3. Monitor system's solution generation process
4. Wait for automated solution application and validation

**Solution Applied:**
1. Review the applied solution details
2. Check validation test results
3. Monitor affected test programs
4. Verify issue resolution

**System Alert:**
1. Check alert severity and type
2. Follow recommended actions in alert details
3. Contact administrator if needed
4. Document any manual interventions

---

## Configuration

### User Preferences

#### Dashboard Settings
1. **Refresh Rate**: Set automatic refresh interval (10s - 5min)
2. **Notifications**: Configure alert preferences
3. **Display Options**: Customize dashboard layout
4. **Timezone**: Set local timezone for timestamps

#### Notification Preferences
1. **Email Notifications**: Enable/disable email alerts
2. **Alert Types**: Select which events trigger notifications
3. **Frequency**: Set notification frequency limits
4. **Recipients**: Configure additional notification recipients

### System Configuration (Admin Only)

#### Module Owner Contacts
```json
{
  "contact_module": {
    "owner": "john.doe@company.com",
    "backup": "jane.smith@company.com"
  },
  "rom_module": {
    "owner": "alice.johnson@company.com",
    "backup": "bob.wilson@company.com"
  }
}
```

#### Regression Schedules
- Configure daily regression timing
- Set module baseline update frequency
- Define processing priorities
- Set validation criteria

---

## Monitoring & Analytics

### Performance Metrics

#### Issue Detection Metrics
- **Detection Accuracy**: Percentage of correctly identified issues
- **False Positive Rate**: Incorrectly flagged issues
- **Processing Time**: Time from regression completion to issue detection
- **Coverage**: Percentage of regression sessions analyzed

#### Solution Application Metrics
- **Success Rate**: Percentage of successful automated fixes
- **Validation Rate**: Solutions that pass automated testing
- **Time to Resolution**: Average time from detection to fix
- **Learning Rate**: Improvement in accuracy over time

### Analytics Dashboard

#### Trend Analysis
1. **Issue Trends**: Track issue patterns over time
2. **Module Performance**: Compare performance across modules
3. **Baseline Impact**: Analyze effect of baseline changes
4. **System Performance**: Monitor system health metrics

#### Reporting Features
1. **Daily Reports**: Automated daily summary emails
2. **Weekly Summaries**: Comprehensive weekly performance reports
3. **Monthly Analytics**: Detailed monthly trend analysis
4. **Custom Reports**: Generate reports for specific date ranges

---

## Troubleshooting

### Common Issues

#### Dashboard Not Loading
**Symptoms**: Browser shows connection error or timeout
**Solutions**:
1. Check network connectivity to Linux server
2. Verify server is running: `systemctl status regression-auto-remediation`
3. Check if port 3000 is accessible
4. Contact system administrator

#### No Recent Data
**Symptoms**: Dashboard shows outdated information
**Solutions**:
1. Check if daily regressions are running
2. Verify database connectivity
3. Review system logs for errors
4. Restart data processing service if needed

#### Solution Not Applied
**Symptoms**: Issue detected but no solution applied
**Solutions**:
1. Check solution confidence score (may be below threshold)
2. Verify validation tests passed
3. Review error logs for application failures
4. Check if manual review is required

#### False Issue Detection
**Symptoms**: System detects issues that don't exist
**Solutions**:
1. Review detection criteria
2. Update pattern recognition if needed
3. Provide feedback through dashboard
4. Contact system administrator for pattern updates

### Log File Locations

#### System Logs
```bash
# Main application log
/var/log/regression_auto_remediation.log

# Database connection log
/var/log/db_connection.log

# Model training log
/var/log/model_training.log

# Solution application log
/var/log/solution_application.log
```

#### Error Investigation
```bash
# Check recent errors
tail -f /var/log/regression_auto_remediation.log | grep ERROR

# Search for specific issues
grep "solution application failed" /var/log/solution_application.log

# Check database connectivity
grep "database connection" /var/log/db_connection.log
```

### Getting Help

#### Internal Support
1. **System Administrator**: Contact for infrastructure issues
2. **Development Team**: Contact for feature requests or bugs
3. **Module Owners**: Contact for module-specific questions

#### Self-Help Resources
1. **System Documentation**: Available in `/docs` directory
2. **Training Materials**: Video tutorials and guides
3. **Best Practices**: Documented operational procedures

---

## FAQs

### General Questions

**Q: How often does the system check for new regressions?**
A: The system monitors regression data continuously and processes new sessions within 5 minutes of completion.

**Q: Can I manually trigger regression analysis?**
A: Yes, use the "Manual Trigger" button in the Regressions tab to analyze specific sessions.

**Q: How accurate is the issue detection?**
A: Current accuracy is 95%+ for known issue types, with continuous improvement through learning.

**Q: What happens if a solution fails validation?**
A: Failed solutions are rolled back automatically, and the issue is flagged for manual review.

### Technical Questions

**Q: How do I access historical regression data?**
A: Use the date range selector in the Analytics tab to view historical data and trends.

**Q: Can I customize the dashboard layout?**
A: Yes, go to Settings > Dashboard to customize panel layout and content.

**Q: How do I provide feedback on solution accuracy?**
A: Use the feedback buttons next to each applied solution in the Solutions tab.

**Q: What browsers are supported?**
A: Chrome, Firefox, Safari, and Edge (latest versions recommended).

### Advanced Usage

**Q: How do I export regression data?**
A: Use the Export function in the Analytics tab to download data in CSV or JSON format.

**Q: Can I integrate with external tools?**
A: Yes, REST APIs are available for integration. Contact administrator for API documentation.

**Q: How do I configure custom alert rules?**
A: Custom alerts can be configured in Settings > Notifications by administrators.

**Q: Can I see model learning progress?**
A: Yes, the Analytics tab includes model performance metrics and learning curves.

### Setup & Installation Questions

**Q: Is requirements.txt enough to set up the system on a new laptop?**
A: No, requirements.txt only contains Python dependencies. For a complete setup you need:
- Python virtual environment + pip install -r requirements.txt
- Node.js dependencies: cd web_dashboard && npm install
- Environment configuration: Create .env file with database credentials
- Start both servers: Backend (port 8000) and Frontend (port 3000)
Use ./quick_setup.sh for automated installation or follow the manual setup guide.

**Q: What are the system prerequisites for installation?**
A: You need Python 3.9+, Node.js 16+, Git, and optionally Oracle Client for database connectivity. The quick_setup.sh script will check all prerequisites automatically.

---

## Best Practices

### Daily Usage
1. Start each day by reviewing the dashboard status
2. Monitor notifications throughout the day
3. Validate important solution applications
4. Report any unusual patterns or behaviors
5. Keep the dashboard open for real-time monitoring

### Weekly Reviews
1. Review weekly performance reports
2. Analyze trend patterns and improvements
3. Provide feedback on system performance
4. Suggest improvements or new features
5. Update configuration if needed

### Monthly Maintenance
1. Review system performance metrics
2. Update user preferences and settings
3. Participate in user feedback sessions
4. Review and update documentation
5. Plan for system improvements

---

## Contact Information

### Support Contacts
- **Technical Support**: [support-email@company.com]
- **System Administrator**: [admin-email@company.com]
- **Development Team**: [dev-team@company.com]

### Emergency Contacts
- **24/7 System Issues**: [emergency-contact@company.com]
- **Critical Regression Failures**: [critical-support@company.com]

---

*For additional help or feature requests, please contact the development team or submit a request through the internal ticketing system.*
