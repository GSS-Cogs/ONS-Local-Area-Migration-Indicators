pipeline {
    agent {
        label 'master'
    }
    stages {
        stage('Clean') {
            steps {
                sh 'rm -rf out'
            }
        }
        stage('Transform') {
            agent {
                docker {
                    image 'cloudfluff/databaker'
                    reuseNode true
                }
            }
            steps {
                sh "jupyter-nbconvert --to python --stdout 'Local area migration indicators UK Migration Flows.ipynb' | ipython"
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    def csvs = []
                    for (def file : findFiles(glob: 'out/*.csv')) {
                        csvs.add("out/${file.name}")
                    }
                    uploadDraftset('ONS Local Area Migration Indicators', csvs)
                }
            }
        }
        stage('Publish') {
            steps {
                script {
                    publishDraftset()
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts 'out/*'
        }
        success {
            build job: '../GDP-tests', wait: false
        }
    }
}
