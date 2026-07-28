/* eslint-disable no-underscore-dangle, max-params, n/prefer-global/process, no-bitwise -- dev-only codegen using the TS Compiler API */
/**
 * Codegen: extract the complete component × property catalog from naive-ui's
 * `GlobalThemeOverrides` type and emit a committed TS module.
 *
 * Run: `pnpm gen-theme-catalog` (from frontend/). Re-run after upgrading naive-ui.
 *
 * The script consumes only the *public type declarations* of naive-ui (via the
 * TypeScript Compiler API) and writes a reviewable, committed artifact. It does
 * NOT read naive-ui implementation source.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const frontendRoot = resolve(__dirname, '..');

// Read the naive-ui version from the project's own dependency declaration.
const rootPkg = JSON.parse(readFileSync(resolve(frontendRoot, 'package.json'), 'utf-8')) as {
  dependencies?: Record<string, string>;
};
const naiveVersion = rootPkg.dependencies?.['naive-ui'] ?? 'unknown';

// A virtual root file that imports the target type so the program pulls in naive-ui's d.ts.
const virtualFileName = resolve(frontendRoot, '__gen_theme_catalog_input.ts');
const virtualContent = `import type { GlobalThemeOverrides } from 'naive-ui';\nexport type _Target = GlobalThemeOverrides;\n`;

const options: ts.CompilerOptions = {
  target: ts.ScriptTarget.ESNext,
  module: ts.ModuleKind.ESNext,
  moduleResolution: ts.ModuleResolutionKind.Bundler,
  skipLibCheck: true,
  noEmit: true,
  strict: false
};

const host = ts.createCompilerHost(options, /* setParentNodes */ true);

const origGetSourceFile = host.getSourceFile.bind(host);
host.getSourceFile = (fileName, languageVersion, onError, shouldCreateNewSourceFile) => {
  if (resolve(fileName) === virtualFileName) {
    return ts.createSourceFile(virtualFileName, virtualContent, languageVersion, true, ts.ScriptKind.TS);
  }
  return origGetSourceFile(fileName, languageVersion, onError, shouldCreateNewSourceFile);
};

const origFileExists = host.fileExists.bind(host);
host.fileExists = (fileName: string) => (resolve(fileName) === virtualFileName ? true : origFileExists(fileName));

const origReadFile = host.readFile.bind(host);
host.readFile = (fileName: string) => (resolve(fileName) === virtualFileName ? virtualContent : origReadFile(fileName));

const program = ts.createProgram({ rootNames: [virtualFileName], options, host });
const checker = program.getTypeChecker();

const sourceFile = program.getSourceFile(virtualFileName);
if (!sourceFile) {
  console.error('[gen-theme-catalog] ERROR: virtual source file not loaded.');
  process.exit(1);
}

// Resolve `GlobalThemeOverrides` via the `export type _Target = GlobalThemeOverrides;` alias.
let targetType: ts.Type | undefined;
sourceFile.forEachChild(node => {
  if (ts.isTypeAliasDeclaration(node) && node.name.text === '_Target') {
    targetType = checker.getTypeFromTypeNode(node.type);
  }
});

if (!targetType) {
  console.error('[gen-theme-catalog] ERROR: could not resolve GlobalThemeOverrides type.');
  process.exit(1);
}

/** Strip `undefined` from an optional property's union type so we can walk its members. */
function nonNullable(type: ts.Type): ts.Type {
  if (type.isUnion()) {
    for (const t of type.types) {
      if (!(t.flags & ts.TypeFlags.Undefined)) return t;
    }
  }
  return type;
}

interface PropDef {
  key: string;
  typeText: string;
}
interface ComponentDef {
  name: string;
  props: PropDef[];
}

const members = checker.getPropertiesOfType(targetType);
if (members.length === 0) {
  console.error(
    '[gen-theme-catalog] ERROR: GlobalThemeOverrides resolved with 0 components — naive-ui types failed to resolve. Check moduleResolution / node_modules.'
  );
  process.exit(1);
}

const catalog: ComponentDef[] = members.map(member => {
  const name = member.getName();
  try {
    const memberType = nonNullable(checker.getTypeOfSymbol(member));
    const subMembers = checker.getPropertiesOfType(memberType);
    const props: PropDef[] = subMembers
      .filter(sm => !sm.getName().startsWith('__'))
      .map(sm => {
        const propType = checker.getTypeOfSymbol(sm);
        const typeText = checker.typeToString(propType).replace(/\s+/g, ' ').trim();
        return { key: sm.getName(), typeText };
      })
      .filter(p => Boolean(p.key));
    return { name, props };
  } catch {
    // Robust fallback: emit the component with no structured props → UI degrades to JSON5-only.
    return { name, props: [] };
  }
});

// Order: `common` first, then alphabetical.
catalog.sort((a, b) => {
  if (a.name === 'common') return -1;
  if (b.name === 'common') return 1;
  return a.name.localeCompare(b.name);
});

const names = catalog.map(c => c.name);
const totalProps = catalog.reduce((acc, c) => acc + c.props.length, 0);

const outFile = resolve(frontendRoot, 'src/layouts/modules/theme-drawer/modules/component/theme-catalog.generated.ts');

const output = `/* eslint-disable */
/* eslint-disable @typescript-eslint/naming-convention */
/**
 * AUTO-GENERATED by \`pnpm gen-theme-catalog\` (scripts/gen-theme-catalog.ts) — DO NOT EDIT BY HAND.
 *
 * Source type: naive-ui GlobalThemeOverrides
 * naive-ui version: ${naiveVersion}
 * Components: ${catalog.length} | Total props: ${totalProps}
 * Re-run after upgrading naive-ui.
 */
import type { ThemeComponentDef } from './prop-meta';

export const themeCatalog: ThemeComponentDef[] = ${JSON.stringify(catalog, null, 2)};

export const themeComponentNames: string[] = ${JSON.stringify(names, null, 2)};
`;

writeFileSync(outFile, output, 'utf-8');

console.log(`[gen-theme-catalog] wrote ${outFile}`);
console.log(`[gen-theme-catalog] components: ${catalog.length} | total props: ${totalProps}`);
console.log(
  `[gen-theme-catalog] sample: common=${catalog[0]?.props.length ?? 0} props, Button=${catalog.find(c => c.name === 'Button')?.props.length ?? 0} props`
);
