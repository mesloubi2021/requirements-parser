import os
import warnings

from .requirement import Requirement


def parse(reqstr):
    """
    Parse a requirements file into a list of Requirements

    See: pip/req.py:parse_requirements()

    :param reqstr: a string or file like object containing requirements
    :returns: a *generator* of Requirement objects
    """
    filename = getattr(reqstr, 'name', None)
    try:
        # Python 2.x compatibility
        if not isinstance(reqstr, basestring):
            reqstr = reqstr.read()
    except NameError:
        # Python 3.x only
        if not isinstance(reqstr, str):
            reqstr = reqstr.read()

    for line in reqstr.splitlines():
        line = line = line[:-2].strip() if line.endswith('\\') else line.strip()
        index = line.find('--no-binary')
        if index >= 0 :
            line = line[:index]
        if line == '':
            continue
        elif not line or line.startswith('#') or line.startswith('--hash'):
            # comments are lines that start with # only
            # hashes of packages to install are provided using this:
            continue
        elif line.startswith('-r') or line.startswith('--requirement'):
            _, new_filename = line.split()
            new_file_path = os.path.join(os.path.dirname(filename or '.'),
                                         new_filename)
            with open(new_file_path) as f:
                for requirement in parse(f):
                    yield requirement
        elif line.startswith('-f') or line.startswith('--find-links') or \
                line.startswith('-i') or line.startswith('--index-url') or \
                line.startswith('--extra-index-url') or \
                line.startswith('--no-index'):
            warnings.warn('Private repos not supported. Skipping.')
            continue
        elif line.startswith('-Z') or line.startswith('--always-unzip'):
            warnings.warn('Unused option --always-unzip. Skipping.')
            continue
        else:
            try:
                yield Requirement.parse(line)
            except UnicodeDecodeError:
                continue
