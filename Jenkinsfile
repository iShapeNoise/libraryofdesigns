pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'echo Building...'
		sh 'cp env.example .env'
		sh 'python3 -m venv .pylot'
		sh 'source .pylot/bin/activate
		sh 'python3 -m pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'echo Testing..'
                sh 'python3 manage.py test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying....'
            }
        }
    }
}

