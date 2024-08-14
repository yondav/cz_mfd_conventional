import os
import re

from commitizen import defaults
from commitizen.cz.base import BaseCommitizen
from commitizen.cz.utils import multiple_line_breaker, required_validator
from commitizen.defaults import Questions

__all__ = ['ConventionalCommitsCz']  # Export the ConventionalCommitsCz class

class mfd_conventional(BaseCommitizen):
    bump_map = defaults.bump_map
    bump_map_major_version_zero = defaults.bump_map_major_version_zero
    bump_pattern = defaults.bump_pattern
    commit_parser = r'^((?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?|\w+!):\s(?P<message>.*)?'  # noqa
    changelog_pattern = defaults.bump_pattern
    change_type_map = {
        'feat': 'Feat',
        'fix': 'Fix',
        'refactor': 'Refactor',
        'perf': 'Perf',
    }
    
    issue_pattern = r'(MFD-\d+)'

    def parse_scope(self, text: str) -> str:
        if not text:
            return ''

        scope = text.strip()
        match = re.search(self.issue_pattern, scope)

        if match:
            return f'ref {match.group(0)}'

        # Join the remaining words with hyphens if no issue pattern is found
        return '-'.join(scope.split())

    def parse_subject(self, text: str) -> str:
        if isinstance(text, str):
            text = text.strip('.').strip()

        return required_validator(text, msg='Subject is required')

    def read_issue_id_from_branch(self) -> str:
        command = 'git branch --show-current'

        with os.popen(command) as proc:
            branch_name = proc.read().strip()
            match = re.search(self.issue_pattern, branch_name)
            
            if match:
                return self.parse_scope(branch_name)

        return ''

    def questions(self) -> Questions:
        commit_type = {
            'type': 'list',
            'name': 'commit_type',
            'message': 'Select the type of change you are committing',
            'choices': [
                {
                    'value': 'fix', # correlates with PATCH in SemVer
                    'name': 'fix: A bug fix',
                    'key': 'x',
                },
                {
                    'value': 'feat', # correlates with MINOR in SemVer
                    'name': 'feat: A new feature',
                    'key': 'f',
                },
                {
                    'value': 'docs',
                    'name': 'docs: Documentation only changes',
                    'key': 'd',
                },
                {
                    'value': 'style',
                    'name': (
                        'style: Changes that do not affect the '
                        'meaning of the code (white-space, formatting,'
                        ' missing semi-colons, etc)'
                    ),
                    'key': 's',
                },
                {
                    'value': 'refactor', # correlates with PATCH in SemVer
                    'name': (
                        'refactor: A code change that neither fixes '
                        'a bug nor adds a feature'
                    ),
                    'key': 'r',
                },
                {
                    'value': 'perf', # correlates with PATCH in SemVer
                    'name': 'perf: A code change that improves performance',
                    'key': 'p',
                },
                {
                    'value': 'test',
                    'name': 'test: Adding missing or correcting ' 'existing tests',
                    'key': 't',
                },
                {
                    'value': 'build',
                    'name': (
                        'build: Changes that affect the build system or '
                        'external dependencies (example scopes: pip, docker, npm)'
                    ),
                    'key': 'b',
                },
                {
                    'value': 'ci',
                    'name': (
                        'ci: Changes to CI configuration files and '
                        'scripts'
                    ),
                    'key': 'c',
                },
                {
                    'value': 'wip',
                    'name': 'wip: Work in progress',
                    'key': 'w',
                },
            ]
        }
        commit_scope = {
            'type': 'input',
            'name': 'commit_scope',
            'message': 'What is the scope of this change? (linear issue-id)\n',
            'filter': self.parse_scope,
            'default': self.read_issue_id_from_branch
        }
        commit_subject = {
            'type': 'input',
            'name': 'commit_subject',
            'message': 'Write a short and imperative summary of the code changes: (lower case and no period)\n',
            'filter': self.parse_subject,
        }
        commit_body = {
            'type': 'input',
            'name': 'commit_body',
            'message': 'Provide additional contextual information about the code changes: (press [enter] to skip)\n',
            'filter': multiple_line_breaker,
        }
        commit_breaking_change = {
            'type': 'confirm',
            'name': 'commit_breaking', # correlates with MAJOR in SemVer
            'message': 'Is this a BREAKING CHANGE?\n',
            'default': False,
        }
        commit_footer = {
            'type': 'input',
            'name': 'commit_footer', # correlates with MAJOR in SemVer
            'message': (
                'Information about Breaking Changes or '
                'reference additional linear tickets (ref [ISSUE-ID]): (press [enter] to skip)\n'
            ),
        }

        return [
            commit_type,
            commit_scope,
            commit_subject,
            commit_body,
            commit_breaking_change,
            commit_footer
        ]

    def message(self, answers: dict) -> str:
        type = answers['commit_type']
        scope = answers['commit_scope']
        subject = answers['commit_subject']
        body = answers['commit_body']
        footer = answers['commit_footer']
        is_breaking_change = answers['commit_breaking']

        if scope:
            scope = f"({scope})"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        message = f"{type}{scope}: {subject}{body}{footer}"

        return message

    def example(self) -> str:
        return (
            "fix(ref MFD-2000): correct minor typos in code\n"
            "\n"
            "see the issue for details on the typos fixed\n"
            "\n"
            "ref MFD-2012"
        )
    
    def schema(self) -> str:
        return (
            "<type>(<scope>): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        PATTERN = (
            r"(?s)"  # To explicitly make . match new line
            r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump|wip)"  # type
            r"(\(\S+\))?!?:"  # scope
            r"( [^\n\r]+)"  # subject
            r"((\n\n.*)|(\s*))?$"
        )
        return PATTERN

    def info(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "cz_mfd_conventional.txt")
        with open(filepath, encoding=self.config.settings["encoding"]) as f:
            content = f.read()
        return content

    def process_commit(self, commit: str) -> str:
        pat = re.compile(self.schema_pattern())
        m = re.match(pat, commit)
        if m is None:
            return ""
        return m.group(3).strip()
