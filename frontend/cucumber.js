export default {
  paths: ['e2e/features/**/*.feature'],
  require: ['e2e/step-definitions/**/*.ts'],
  requireModule: ['tsx'],
  format: ['html:reports/cucumber-report.html', 'progress-bar'],
  publishQuiet: true,
};
