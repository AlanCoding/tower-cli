rm -rf awx/
git clone https://github.com/ansible/awx.git awx --depth=1
cp tests_awx/CLI_settings.py awx/awx/settings/CLI_settings.py
python install_awx_req.py
cd awx
python setup.py install
cd ..
# have to add awx dir to path
[[ ":$PYTHONPATH:" != *":$PWD/awx:"* ]] && PYTHONPATH="${PYTHONPATH}:$PWD/awx"
