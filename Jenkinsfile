node('linux && cura') {
    timeout(time: 5, unit: "MINUTES") {
        // Prepare building
        stage('Prepare') {
            // Ensure we start with a clean build directory.
            step([$class: 'WsCleanup'])

            // Checkout whatever sources are linked to this pipeline.
            checkout scm
        }

        // If any error occurs during building, we want to catch it and continue with the "finale" stage.
        catchError {
            // Perform sanity checks
            stage('Sanity Checks') {
                if (fileExists("scripts/check_material_profiles.py")) {
                    sh "${env.CURA_ENVIRONMENT_PATH}/master/bin/python3 scripts/check_material_profiles.py"
                }
            }
        }
    }
}
