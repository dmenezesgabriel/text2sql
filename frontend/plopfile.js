/**
 * @param {import('plop').NodePlopAPI} plop
 */
export default function (plop) {
  plop.setGenerator('component', {
    description: 'Scaffold a new component with index, component, spec, and story files',
    prompts: [
      {
        type: 'input',
        name: 'name',
        message: 'Component name (PascalCase, e.g. ChatInput):',
      },
      {
        type: 'input',
        name: 'path',
        message: 'Path relative to src/ (e.g. shared/components):',
      },
    ],
    actions: [
      {
        type: 'add',
        path: 'src/{{path}}/{{kebabCase name}}/index.ts',
        templateFile: 'plop-templates/component/index.ts.hbs',
      },
      {
        type: 'add',
        path: 'src/{{path}}/{{kebabCase name}}/{{kebabCase name}}.tsx',
        templateFile: 'plop-templates/component/component.tsx.hbs',
      },
      {
        type: 'add',
        path: 'src/{{path}}/{{kebabCase name}}/{{kebabCase name}}.spec.tsx',
        templateFile: 'plop-templates/component/component.spec.tsx.hbs',
      },
      {
        type: 'add',
        path: 'src/{{path}}/{{kebabCase name}}/{{kebabCase name}}.stories.tsx',
        templateFile: 'plop-templates/component/component.stories.ts.hbs',
      },
    ],
  });
}
