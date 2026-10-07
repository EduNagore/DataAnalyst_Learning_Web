// @ts-check
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import eslintPluginAstro from 'eslint-plugin-astro';

export default tseslint.config(
  {
    ignores: [
      'dist/**',
      '.astro/**',
      'node_modules/**',
      'public/pagefind/**',
      'public/data/**',
      'projects/**',
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...eslintPluginAstro.configs.recommended,
  {
    rules: {
      // Las islas interactivas reciben props sin usar en algunos componentes de layout.
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_', caughtErrorsIgnorePattern: '^_' },
      ],
    },
  },
  {
    // Scripts de Node ejecutados fuera de Astro/Vite (CI, generación de datos).
    files: ['scripts/**/*.mjs', '*.config.{js,mjs,ts}', 'data-gen/**/*.mjs'],
    languageOptions: {
      globals: {
        console: 'readonly',
        process: 'readonly',
        setTimeout: 'readonly',
        __dirname: 'readonly',
        module: 'readonly',
      },
    },
  },
);
