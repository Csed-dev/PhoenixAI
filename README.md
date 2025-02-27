# PhoenixAI

PhoenixAI is an advanced tool designed to modernize legacy software systems using state-of-the-art AI technologies. By leveraging Gemini and a modular pipeline architecture, PhoenixAI automates the porting process and enhances code quality through iterative analysis and transformation, enabling organizations to upgrade their outdated systems efficiently.

## Features

- **Automated Legacy Code Porting**: Seamlessly transform legacy code into modern, maintainable codebases using AI-driven code translation.
- **User-Friendly GUI**: Intuitive interface for file selection, process control, and real-time visualization of analysis and transformation pipelines.
- **Comprehensive Code Analysis**: Integrated modules for performance profiling, static analysis, and name checking that generate detailed, versioned reports.
- **Iterative Improvement Pipeline**: Leverages tools like Pylint and SonarQube in an iterative cycle to refine code quality and ensure functional integrity.
- **Customizable Workflow**: Modular design allows easy integration of additional tools and techniques, adapting to the specific needs of any project.


## Prerequisites

Before running this project, ensure you have the following:

1. **Python 3.12+** installed on your system.
2. A Google Cloud Project set up with **access to Google Gemini APIs**.
3. **Sourcery** setup  (workds for open-source project only, that are online on github) 

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Csed-dev/PhoenixAI.git
cd quizcraft
```

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Required File

1. **.env file**:  
   You need to create a `.env` file to store your API key securely. Add the following line to your `.env` file:

   ```
   GOOGLE_API_KEY=your_google_api_key_here
   SOURCERY_TOKEN=your_sourcery_token_here
   SONARQUBE_TOKEN=your_sonarqube_token_here
   ```


## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

## Contact
For any questions or suggestions, please reach out to mikyta.mikyta@gmail.com.
