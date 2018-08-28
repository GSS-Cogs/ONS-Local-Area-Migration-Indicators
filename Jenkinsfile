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
        stage('RDF Data Cube') {
            agent {
                docker {
                    image 'cloudfluff/table2qb'
                    reuseNode true
                }
            }
            steps {
                sh "table2qb exec cube-pipeline --input-csv out/migrationflows.csv --output-file out/observations.ttl --column-config metadata/columns.csv --dataset-name 'ONS Local Area Migration Indicators' --base-uri http://gss-data.org.uk/ --dataset-slug ons-local-area-migration-indicators"
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    def obslist = []
                    for (def file : findFiles(glob: 'out/*.ttl')) {
                        obslist.add("out/${file.name}")
                    }
                    uploadCube('Local Area Migration Indicators', obslist)
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
