"""Render the shipped workflow examples into real prepare calls in a tmp lab.

All source and manuscript bytes below are labelled synthetic; no activation,
provider access, actual essay generation, or real archive writes occur.
"""
import json
from pathlib import Path
import re

from test_philosophy_bridge import BridgeFixture, ROOT, bridge


class ClaudeWorkflowTemplatesTests(BridgeFixture):
    def test_author_critic_revision_requests_prepare_with_exact_inputs(self):
        files = {
            'RULES_SOURCE_PATH': ('fixtures/rules.txt', 'Synthetic rules fixture.\n'),
            'SOURCE_INDEX_PATH': ('fixtures/source-index.md', 'Synthetic source index.\n'),
            'PRIMARY_SOURCE_PATH': ('fixtures/primary.txt', 'Synthetic primary text.\n'),
            'EXACT_DRAFT_PATH': ('fixtures/draft.md', 'Synthetic draft fixture; no philosophy.\n'),
            'AUTHOR_SOURCE_MANIFEST_PATH': ('fixtures/source-manifest.json', '{"synthetic":true}\n'),
            'JUDGE_PROFILE_PATH': ('fixtures/judge.md', 'Synthetic judge profile; no real person.\n'),
            'JUDGE_PRIMARY_WORK_PATH': ('fixtures/judge-work.txt', 'Synthetic judge work.\n'),
            'EXACT_CRITIQUE_PATH': ('fixtures/critique.md', 'Synthetic critique fixture.\n'),
        }
        values = {
            'AUTHOR_JOB_ID': 'synthetic-author', 'CRITIC_JOB_ID': 'synthetic-critic',
            'REVISION_JOB_ID': 'synthetic-revision', 'ESSAY_ID': 'synthetic-essay',
            'RUN_ID': 'synthetic-run', 'PARENT_AUTHOR_JOB_ID': 'synthetic-author',
            'REQUESTED_MODEL_OR_UNKNOWN': 'UNKNOWN', 'REQUESTED_EFFORT_OR_UNKNOWN': 'UNKNOWN',
            'STYLE_BRIEF': 'Synthetic style fixture: plain prose.',
            'PUBLIC_WEB_BOOLEAN': False, 'AREA_AND_SCOPE': 'synthetic neutral fixture only',
            'CRITIC_ASSIGNMENTS': 'Synthetic Judge / synthetic-profile-v1',
            'JUDGE_NAME': 'Synthetic Judge', 'JUDGE_PROFILE_ID_VERSION': 'synthetic-profile-v1',
            'DRAFT_INPUT_LABEL': 'input/inputs/draft.md',
            'CRITIQUE_INPUT_LABELS': 'input/inputs/critique-001.md',
        }
        for key, (source, content) in files.items():
            self.write(source, content)
            values[key] = source

        def render(value):
            if isinstance(value, dict): return {k: render(v) for k, v in value.items()}
            if isinstance(value, list): return [render(v) for v in value]
            if not isinstance(value, str): return value
            # Full-field substitutions retain native booleans; prompts stay text.
            match = re.fullmatch(r'\{\{([A-Z_]+)\}\}', value)
            if match: return values[match.group(1)]
            return re.sub(r'\{\{([A-Z_]+)\}\}', lambda m: str(values[m.group(1)]), value)

        template_dir = ROOT / 'templates/philosophy_claude/workflows'
        results = []
        with self.archive.writer() as writer:
            for stage in ('author', 'critic', 'revision'):
                with self.subTest(stage=stage):
                    prompt = render((template_dir / f'{stage}.prompt.md').read_text())
                    values[f'{stage.upper()}_PROMPT_TEXT'] = prompt
                    request = render(json.loads((template_dir / f'{stage}.request.json').read_text()))
                    self.assertNotRegex(json.dumps(request), r'\{\{[A-Z_]+\}\}')
                    self.assertIs(request['public_web'], False)
                    result = bridge.prepare(self.root, request, archive_writer=writer)
                    results.append(result)
                    packet = Path(result['packet'])
                    self.assertEqual((packet / 'prompt.md').read_text(), prompt)
                    manifest = json.loads((packet / 'manifest.json').read_text())
                    self.assertEqual(manifest['stage'], stage)
                    self.assertEqual(manifest['essay_id'], 'synthetic-essay')
                    self.assertEqual(manifest['model_requested'], 'UNKNOWN')
                    self.assertIn('report.md', manifest['required_outputs'])
                    if stage != 'author':
                        self.assertEqual(manifest['parent_job_id'], 'synthetic-author')
                    for selected in request['selected_inputs']:
                        self.assertEqual((packet / 'inputs' / selected['label']).read_bytes(),
                                         (self.root / selected['source']).read_bytes())
                        if selected['scope'] == 'essay':
                            self.assertEqual(selected['owner_essay_id'], 'synthetic-essay')
            events = writer.events()
            self.assertEqual(len([e for e in events if e['kind'] == 'bridge.job.prepared']), 3)
            self.assertFalse(any(e['kind'] in ('bridge.job.activated', 'bridge.job.claimed') for e in events))
        self.assertEqual(len(results), 3)
        self.assertTrue(self.archive.validate()['ok'])
