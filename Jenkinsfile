pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'echo Building..'
	        script {
		    sh 'cd'
		    sh 'PATH=${PATH}:/usr/local/bin'
                    if (!fileExists('.pylot')) {
                        echo 'Creating virtualenv...'
                        sh 'python3 -m venv .pylot'
			sh '. .pylot/bin/activate'
                    } else {
			sh '. .pylot/bin/activate'
                        echo 'Virtualenv already exists.'
                    }
                }
                sh 'cp env.example .env'
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

