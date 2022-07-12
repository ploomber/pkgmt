"""
Managing project versions
"""
import sys
import shutil
import subprocess
from pathlib import Path

from pkgmt.changelog import expand_github_from_changelog
from pkgmt.versioner.versionernonsetup import VersionerNonSetup
from pkgmt.versioner.versionersetup import VersionerSetup


def replace_in_file(path_to_file, original, replacement):
    """Replace string in file
    """
    with open(path_to_file, 'r+') as f:
        content = f.read()
        updated = content.replace(original, replacement)
        f.seek(0)
        f.write(updated)
        f.truncate()


def call(*args, **kwargs):
    return subprocess.run(*args, **kwargs, check=True)


def delete_dirs(*dirs):
    for dir_ in dirs:
        if Path(dir_).exists():
            shutil.rmtree(dir_)


def _input(prompt):
    return input(prompt)


def input_str(prompt, default):
    separator = ' ' if len(prompt.splitlines()) == 1 else '\n'
    response = _input(prompt + f'{separator}(Default: {default}): ')

    if not response:
        response = default

    return response


def input_confirm(prompt, abort):
    separator = ' ' if len(prompt.splitlines()) == 1 else '\n'
    response_raw = _input(prompt + f'{separator}Confirm? [y/n]: ')
    response = response_raw in {'y', 'Y', 'yes'}

    if not response and abort:
        print('Aborted!')
        sys.exit(1)

    return response


def is_pre_release(version):
    return 'a' in version or 'b' in version or 'rc' in version


def validate_version_string(version):
    if not len(version):
        raise ValueError(f'Got invalid empty version string: {version!r}')

    if version[0] not in '0123456789':
        raise ValueError(f'Got invalid version string: {version!r} '
                         '(first character must be numeric)')


def version(project_root='.', tag=True, version_package=None):
    """
    Create a new version (projects with setup.py) :
    1. version_package will be None
    2. Set new stable version in package_name/__init__.py
    3. Update header in CHANGELOG file, and ask to review CHANGELOG
    4. Create commit for new version, create git tag, and push
    5. Set new development version in package_name/__init__.py, and CHANGELOG
    6. Commit new development version and push

    Create a new version (projects without setup.py) :
    1. These projects should contain two essential files:
       config.yaml in root directory which should contain the repo
       name
       _version.py file containing __version__ in the required directory
    2. version_package will be the directory containing _version.py file
    3. Set new stable version in package_name/_version.py
    4. Update header in CHANGELOG file, and ask to review CHANGELOG
    5. Create commit for new version, create git tag, and push
    6. Set new development version in package_name/_version.py, and CHANGELOG
    7. Commit new development version and push
    """

    if version_package:
        versioner = VersionerNonSetup(version_package,
                                      project_root=project_root)
    else:
        versioner = VersionerSetup(project_root=project_root)

    current = versioner.current_version()
    release = versioner.release_version()

    release = input_str('Current version in setup.py is {current}. Enter'
                        ' release version'.format(current=current),
                        default=release)

    validate_version_string(release)

    if versioner.path_to_changelog and not is_pre_release(release):
        versioner.update_changelog_release(release)

        changelog = versioner.path_to_changelog.read_text()

        input_confirm(
            f'\n{versioner.path_to_changelog} content:'
            f'\n\n{changelog}\n',
            abort=True)

    # Expand github links
    if (versioner.path_to_changelog
            and versioner.path_to_changelog.suffix == '.md'):
        expand_github_from_changelog(path=versioner.path_to_changelog)
    else:
        print('Skipping github expansion (only supported in .md files)')

    # Replace version number and create tag
    print('Commiting release version: {}'.format(release))
    versioner.commit_version(
        release, msg_template='{package_name} release {new_version}', tag=tag)

    # Create a new dev version and save it
    bumped_version = versioner.bump_up_version()

    if not is_pre_release(release):
        print('Creating new section in CHANGELOG...')
        versioner.add_changelog_new_dev_section(bumped_version)

    print('Commiting dev version: {}'.format(bumped_version))
    versioner.commit_version(
        bumped_version,
        msg_template='Bumps up {package_name} to version {new_version}',
        tag=False)

    call(['git', 'push'])
    print('Version {} was created, you are now in {}'.format(
        release, bumped_version))


def upload(tag, production):
    """
    Check outs a tag, uploads to PyPI
    """
    print('Checking out tag {}'.format(tag))
    call(['git', 'checkout', tag])

    versioner = VersionerSetup()
    current = versioner.current_version()

    input_confirm('Version in {} tag is {}. Do you want to continue?'.format(
        tag, current),
                  abort=True)

    # create distribution
    delete_dirs('dist', 'build', f'{versioner.PACKAGE}.egg-info')
    call(['python', 'setup.py', 'bdist_wheel', 'sdist'])

    print('Publishing to PyPI...')

    if not production:
        call([
            'twine', 'upload', '--repository-url',
            'https://test.pypi.org/legacy/', 'dist/*'
        ])
    else:
        call(['twine', 'upload', 'dist/*'])
