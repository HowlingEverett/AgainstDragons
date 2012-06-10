from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['usdlc.net']
env.users = ['justin']
env.project_root = '/home/justin/sites/againstdragons.usdlc.net/againstdragons'

def test():
    with settings(warn_only=True):
        result = local("./manage.py test snapshots")
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def commit():
    local("git add -A && git commit")

def push():
    local("git push")

def github():
    test()
    commit()
    push()

repo_dir = '/home/justin/src'
code_dir = '/home/justin/sites/againstdragons.usdlc.net'

def unarchive_latest():
    with cd(repo_dir):
        run("wget --no-check-certificate https://github.com/HowlingEverett/AgainstDragons/tarball/master")
        run("rm -rf %s" % env.project_root)
        run("tar xvzf master && mv HowlingEverett-Snapshots* %s" % env.project_root)
        run("rm -rf master")
        run("mv %s/deploy/settings.py %s/snapshots/settings.py" % (env.project_root, env.project_root))

def create_virtualenv():
    with cd('cd /home/justin/sites'):
        run('virtualenv --no-site-packages againstdragons.usdlc.net')
    
    with cd(code_dir):
        run('source bin/activate')
        run('pip install django')
        run('pip install psycopg2')
        run('pip install pil')
        run('su postgres -c "createdb -T template_postgis againstdragons"')

def configure_deployment():
    with cd(env.project_root):
        run("source ../bin/activate")
        run("chmod 755 manage.py")
        run("./manage.py collectstatic -v0 --noinput")
        run("su root -c '/etc/init.d/snapshots reload'")
        

def deploy():
    result = run('cd %s' % env.project_root)
    if not result.failed:
        create_virtualenv()
    
    unarchive_latest()
    configure_deployment()
    
