# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the AI Interview Simulation Platform. These workflows automate testing, building, and deployment processes.

## Available Workflows

### Testing Workflow (`testing.yml`)

This workflow is responsible for automated testing and quality checks. It runs on every push to `main` and `develop` branches, on pull requests to these branches, and can be manually triggered.

**Jobs:**

1. **test**: Runs unit tests and code quality checks
   - Python setup with version 3.10
   - Dependency installation
   - Code linting with flake8
   - Code formatting check with black
   - Import sorting check with isort
   - Unit tests with pytest
   - Code coverage reporting

2. **security-scan**: Performs security checks
   - Python setup
   - Dependency security scanning with safety
   - Code security scanning with bandit

3. **frontend-tests**: Tests frontend code (conditional on frontend existing)
   - Node.js setup
   - Frontend dependency installation
   - ESLint checks
   - Frontend unit tests
   - Frontend code coverage reporting

4. **integration-tests**: Runs integration tests
   - Spins up MongoDB and PostgreSQL services
   - Configures test environment
   - Runs integration tests with test databases

### Deployment Workflow (`deployment.yml`)

This workflow handles deployment to staging and production environments. It runs on push to `main` branch, on release tags (v*.*.*), and can be manually triggered.

**Jobs:**

1. **build**: Creates deployment artifacts
   - Builds Python package
   - Builds frontend assets (if frontend exists)
   - Archives artifacts for deployment

2. **deploy-staging**: Deploys to staging environment
   - Triggered automatically on push to main branch
   - Sets up cloud CLI tools
   - Configures cloud provider credentials
   - Runs deployment script for staging
   - Executes smoke tests

3. **deploy-production**: Deploys to production environment
   - Triggered automatically on release tags
   - Can be manually triggered
   - Requires successful staging deployment
   - Deploys using the same artifacts as staging
   - Creates GitHub Release on tag deployment

### Maintenance Workflow (`maintenance.yml`)

This workflow handles routine maintenance tasks. It runs on a weekly schedule (Monday at midnight) and can be manually triggered.

**Jobs:**

1. **update-dependencies**: Checks for dependency updates
   - Updates Python dependencies with pip-upgrader
   - Updates Node.js dependencies with npm-check-updates
   - Creates a pull request with the updates

2. **stale-issues**: Manages stale issues and PRs
   - Marks issues as stale after 30 days of inactivity
   - Closes stale issues after 7 additional days of inactivity
   - Exempts issues with specific labels

3. **code-quality-scan**: Performs code quality analysis
   - Runs SonarCloud scan on the codebase
   - Reports code quality metrics and issues

4. **performance-benchmarks**: Runs performance benchmarks
   - Executes benchmark tests
   - Records and tracks performance metrics over time
   - Alerts on significant performance degradation

## How to Use

### Manually Trigger Workflows

1. Go to the "Actions" tab in the GitHub repository
2. Select the workflow you want to run
3. Click "Run workflow" and select the branch
4. For deployment, select the target environment

### Release Process

1. Run the testing workflow to ensure all tests pass
2. Tag the commit with a version number (e.g., `v1.2.3`)
3. Push the tag to trigger production deployment
4. Monitor the deployment workflow

### View Workflow Results

1. Go to the "Actions" tab
2. Click on a workflow run to see details
3. Review job outputs and logs

## Required Secrets

The following secrets should be configured in your GitHub repository:

- `AWS_ACCESS_KEY_ID`: AWS access key for deployments
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for deployments
- `AWS_REGION`: AWS region for deployments
- `SONAR_TOKEN`: Token for SonarCloud integration

## Adding New Workflows

To add a new workflow:

1. Create a new YAML file in this directory
2. Define the workflow trigger events
3. Set up jobs and steps
4. Update this README with documentation for the new workflow

## Best Practices

- Keep workflows focused on specific tasks
- Reuse steps where possible
- Use GitHub secrets for sensitive data
- Set appropriate caching to speed up builds
- Monitor workflow performance and optimize as needed
- Always run tests before deployment
- Use environment protection rules for production 