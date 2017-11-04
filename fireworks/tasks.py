from celery import task

@task(priority=1)
def do_nothing():
    print 'hi'
