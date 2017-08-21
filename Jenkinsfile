pipeline {
  agent any
  stages {
    stage('Run pytest Scanner') {
      steps {
        runPyTestScanner TEST_PACKS_BRANCH: env.BRANCH_NAME
      }
	}
  }
}
