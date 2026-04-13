import json
from pathlib import Path
import subprocess
import textwrap


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_ui_runtime_probe():
    script = textwrap.dedent(
        f"""
        const fs = require('fs');
        const vm = require('vm');
        const source = fs.readFileSync({json.dumps(str(REPO_ROOT / "static" / "ui.js"))}, 'utf8');
        const context = {{
          console,
          Math,
          Date,
          URL,
          setTimeout,
          clearTimeout,
          requestAnimationFrame: (cb) => {{ cb(); return 1; }},
          cancelAnimationFrame: () => {{}},
          window: {{ addEventListener() {{}}, removeEventListener() {{}}, location: {{ origin: 'http://127.0.0.1:8788' }} }},
          location: {{ origin: 'http://127.0.0.1:8788' }},
          navigator: {{}},
          localStorage: {{ getItem() {{ return null; }}, setItem() {{}}, removeItem() {{}} }},
          document: {{
            getElementById() {{ return null; }},
            createElement() {{ return {{ style: {{}}, appendChild() {{}}, remove() {{}}, addEventListener() {{}}, className: '', innerHTML: '', textContent: '' }}; }},
            querySelector() {{ return null; }},
            querySelectorAll() {{ return []; }},
          }},
          fetch: async () => ({{ json: async () => ({{}}) }}),
        }};
        context.global = context;
        context.globalThis = context;
        vm.createContext(context);
        vm.runInContext(source, context);

        const target = {{ innerHTML: '' }};
        let renderMdCalls = 0;
        const originalRenderMd = context.renderMd;
        context.renderMd = function(raw) {{
          renderMdCalls += 1;
          return originalRenderMd(raw);
        }};

        const streamText = "Hello\\n```js\\nconst value = 1";
        const liveHtml = context.updateLiveAssistantBody(target, streamText);
        const liveRenderMdCalls = renderMdCalls;
        const settledHtml = originalRenderMd("## Settled");

        process.stdout.write(JSON.stringify({{
          liveHtml,
          targetHtml: target.innerHTML,
          liveRenderMdCalls,
          settledHtml
        }}));
        """
    )
    completed = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_ui_js_defines_live_stream_renderer():
    src = (REPO_ROOT / "static" / "ui.js").read_text()
    assert "function renderLiveMessage(raw)" in src


def test_messages_stream_path_uses_live_renderer_not_full_markdown():
    src = (REPO_ROOT / "static" / "messages.js").read_text()
    assert "updateLiveAssistantBody(assistantBody, assistantText);" in src
    assert "assistantBody.innerHTML=renderMd(assistantText);" not in src


def test_history_render_still_uses_full_markdown():
    src = (REPO_ROOT / "static" / "ui.js").read_text()
    assert "const bodyHtml = isUser ? esc(String(content)).replace(/\\n/g,'<br>') : renderMd(String(content));" in src


def test_live_renderer_runtime_handles_unfinished_code_fence_without_full_markdown():
    probe = run_ui_runtime_probe()
    assert probe["liveRenderMdCalls"] == 0
    assert probe["liveHtml"] == probe["targetHtml"]
    assert '<div class="live-text">Hello<br></div>' in probe["liveHtml"]
    assert '<div class="pre-header">js</div><pre><code>const value = 1</code></pre>' in probe["liveHtml"]
    assert "<h2>Settled</h2>" in probe["settledHtml"]
