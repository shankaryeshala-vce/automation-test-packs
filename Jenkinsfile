pipeline {
    agent {
        node{
            label 'maven-builder'
        }
    }
    stages {
        stage('Run pytest Scanner') {
            steps {
                runPyTestScanner()
            }
	    }
    }
    post {
        always {
            cleanWorkspace()   
        }
        success {
            successEmail()
        }
        failure {
            failureEmail()
        }
    }
}
