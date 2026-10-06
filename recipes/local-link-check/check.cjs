const fs = require('node:fs');
const path = require('node:path');
const MarkdownIt = require('markdown-it');
// Parse only. Never render, execute, fetch, or evaluate a source document.
const parser = new MarkdownIt({html: true});

function inside(root, candidate) {
  const relative = path.relative(root, candidate);
  return !relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative);
}

function inspectPath(root, candidate) {
  if (!inside(root, candidate)) return 'outside-root';
  let current = root;
  for (const part of path.relative(root, candidate).split(path.sep).filter(Boolean)) {
    if (!fs.statSync(current).isDirectory()) return 'missing-file';
    const entries = fs.readdirSync(current);
    if (!entries.includes(part)) {
      return entries.some(name => name.toLowerCase() === part.toLowerCase()) ? 'path-case-mismatch' : 'missing-file';
    }
    current = path.join(current, part);
    if (fs.lstatSync(current).isSymbolicLink()) return 'link-unsupported';
  }
  return fs.statSync(candidate).isDirectory() ? 'directory-exists' : 'file-exists';
}

function audit(root, files) {
  root = fs.realpathSync(root);
  if (!fs.statSync(root).isDirectory() || !Array.isArray(files) || !files.length || files.length > 100
      || files.some(name => typeof name !== 'string') || new Set(files).size !== files.length) {
    throw new Error('Select 1–100 unique Markdown files under a directory root');
  }
  const results = [], skippedHtml = [];
  for (const file of files) {
    const source = path.resolve(root, file);
    if (path.extname(file).toLowerCase() !== '.md' || inspectPath(root, source) !== 'file-exists') {
      throw new Error(`Input is not a contained, exact-case Markdown file: ${file}`);
    }
    if (fs.statSync(source).size > 512 * 1024) throw new Error(`Input exceeds 512 KiB: ${file}`);
    const raw = fs.readFileSync(source);
    const text = new TextDecoder('utf-8', {fatal: true}).decode(raw);
    const display = path.relative(root, source).split(path.sep).join('/');
    const tokens = parser.parse(text, {});
    let blockRange = [0, text.split('\n').length];
    for (const token of tokens) {
      if (token.map) blockRange = token.map;
      if (token.type === 'html_block') skippedHtml.push({source: display, start_line: blockRange[0] + 1});
      if (!token.children) continue;
      for (const child of token.children) {
        if (child.type === 'html_inline') skippedHtml.push({source: display, start_line: blockRange[0] + 1});
        if (!['link_open', 'image'].includes(child.type)) continue;
        const href = child.attrGet(child.type === 'image' ? 'src' : 'href');
        const row = {source: display, start_line: blockRange[0] + 1, end_line: blockRange[1], target: href};
        // The source range belongs to the Markdown block containing this link.
        if (/^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith('//')) {
          results.push({...row, state: 'external-unchecked'});
          continue;
        }
        let target;
        try { target = decodeURIComponent(href.split(/[?#]/, 1)[0]); }
        catch { results.push({...row, state: 'invalid-url-encoding'}); continue; }
        if (/[\\:\x00]/.test(target)) {
          results.push({...row, state: 'unsupported-path'});
          continue;
        }
        const destination = target === '' ? source : target.startsWith('/')
          ? path.resolve(root, `.${target}`) : path.resolve(path.dirname(source), target);
        const state = inspectPath(root, destination);
        results.push({...row, state, fragment_unchecked: href.includes('#')});
      }
    }
  }
  const allowed = new Set(['file-exists', 'directory-exists', 'external-unchecked']);
  return {files_scanned: files.length, references: results, skipped_html: skippedHtml,
    failures: results.filter(row => !allowed.has(row.state)).length,
    notice: 'Local file existence only. External destinations, fragments, raw HTML, and malformed/unresolved Markdown are not validated.'};
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2);
    if (args[0] !== '--root' || args.length < 3) throw new Error('Usage: node check.cjs --root ROOT FILE.md [FILE.md ...]');
    const report = audit(args[1], args.slice(2));
    process.stdout.write(JSON.stringify(report, null, 2) + '\n');
    process.exitCode = report.failures ? 1 : 0;
  } catch (error) {
    process.stderr.write(`link-check: ${error.message}\n`);
    process.exitCode = 2;
  }
}
module.exports = {audit};
