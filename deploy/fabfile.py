from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['usdlc.net']
env.user = 'justin'
env.password = 'tmtinfbmo11!'
env.project_root = '/home/justin/sites/againstdragons.usdlc.net/againstdragons'

def test():
    with settings(warn_only=True):
        result = local("./manage.py test geosurvey")
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def commit():
    local("git add -A && git commit")

def push():
    local("git push")

def github():
#    test()
    commit()
    push()

repo_dir = '/home/justin/src'
code_dir = '/home/justin/sites/againstdragons.usdlc.net'

def unarchive_latest():
    with cd(repo_dir):
        run("wget --no-check-certificate https://github.com/HowlingEverett/AgainstDragons/tarball/master")
        run("rm -rf %s" % env.project_root)
        run("tar xvzf master && mv HowlingEverett-AgainstDragons* %s" % env.project_root)
        run("rm -rf master")
        run("mv %s/deploy/settings.py %s/againstdragons/settings.py" % (env.project_root, env.project_root))

def create_virtualenv():
    with cd('/home/justin/sites'):
        run('virtualenv --no-site-packages againstdragons.usdlc.net')
    
    with cd(code_dir):
        run('source bin/activate')
        run('pip install -I django')
        sudo('pip install -I gunicorn')
        sudo('apt-get install python-dev')
        sudo('pip install -I psycopg2')
        sudo('pip install -I pil')

def create_database():
    sudo('su postgres -c "createdb -T template_postgis againstdragons"')
    sudo('su postgres -c "createuser -d -P -R -S againstdragons"')
    sudo('su postgres -c "psql -c \'GRANT ALL ON DATABASE againstdragons TO againstdragons;\'"')

def create_initd():
    with cd(env.project_root):
        sudo('mv deploy/againstdragons_initd /etc/init.d/againstdragons')
        sudo('chmod 755 /etc/init.d/againstdragons')
        sudo('/etc/init.d/againstdragons start')
    

def configure_deployment():
    with cd(env.project_root):
        sudo("chmod 755 manage.py")
        run("%s/bin/python manage.py collectstatic --noinput -v0" % code_dir)
        sudo("pkill python; %s/bin/python manage.py run_gunicorn -D -p /tmp/gunicorn_againstdragons.pid --user=www-data --group=www-data --error-logfile=/var/log/gunicorn/gunicorn.log 127.0.0.1:9006" % code_dir)
        

def deploy():

    with settings(warn_only=True):
        result = run('cd %s' % env.project_root)
        if result.failed:
            create_virtualenv()
            create_database()
        
        unarchive_latest()    
        if result.failed:
            create_initd()
        
        configure_deployment()
    
