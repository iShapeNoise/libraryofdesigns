pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'echo Building...'
		sh 'pip3 install -r requirements.txt'
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

