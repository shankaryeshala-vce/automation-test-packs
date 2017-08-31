pipeline {
    agent {
        node{
            label 'maven-builder'
        }
    }
  }
  stages {
    stage('Run pytest Scanner') {
      steps {
        runPyTestScanner()
      }
	}
  }
}
