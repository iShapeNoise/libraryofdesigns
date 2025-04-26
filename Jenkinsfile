pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'echo Building...'
		sh 'sudo python3 -m pip install --user pipx'
		sh 'pipx ensurepath'
		sh 'pipx install -r requirements.txt'
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

