const fs = require('fs');
const path = require('path');

describe('escapeHtml', () => {
  let escapeHtml;

  beforeAll(() => {
    // Read the HTML file
    const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');

    // Extract the function using regex
    // We look for: function escapeHtml(s) { ... }
    // Using [\s\S]*? to capture any character including newlines up to the first closing brace that makes sense
    // or just match everything between "function escapeHtml(s) {" and the next "}"
    const match = html.match(/function escapeHtml\(s\) \{([\s\S]*?)\}/);
    if (match) {
      // Recreate the function
      escapeHtml = new Function('s', match[1]);
    } else {
      throw new Error("Could not find escapeHtml function in index.html");
    }
  });

  test('escapes & to &amp;', () => {
    expect(escapeHtml('Tom & Jerry')).toBe('Tom &amp; Jerry');
  });

  test('escapes < to &lt;', () => {
    expect(escapeHtml('<div>')).toBe('&lt;div&gt;');
  });

  test('escapes > to &gt;', () => {
    expect(escapeHtml('<div>')).toBe('&lt;div&gt;');
  });

  test('escapes multiple occurrences', () => {
    expect(escapeHtml('1 < 2 & 2 > 1')).toBe('1 &lt; 2 &amp; 2 &gt; 1');
  });

  test('returns the same string if no special characters', () => {
    expect(escapeHtml('Hello World')).toBe('Hello World');
  });

  test('handles empty strings', () => {
    expect(escapeHtml('')).toBe('');
  });
});
