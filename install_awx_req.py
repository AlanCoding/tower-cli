from subprocess import call

files = ['requirements.txt', 'requirements_dev.txt']


seen = set([])
failed = set([])


for file_name in files:
    rel_path = 'awx/requirements/{}'.format(file_name)
    with open(rel_path, 'r') as f:
        data = f.read()
    for line in data.split('\n'):
        if not line or line.startswith('#') or not line.split('#'):
            continue
        target = line.split('#')[0].strip()
        pkg = target.split('=')[0]
        # same package listed in multiple files
        if pkg in seen:
            print('Skipping second listing of ' + str(pkg))
            continue
        # exclusions
        if pkg in ['pip', 'setuptools']:
            print('Passing over {}, in exclusions list'.format(target))
            continue
        seen.add(pkg)
        r = call("pip install " + target, shell=True)
        if r:
            failed.add(target)

if failed:
    print 'tower-cli AWX integration failed to install packages \n'
    print ' - \n'.join(failed)
