from celery import Celery
app=Celery('jcm',broker='redis://:@127.0.0.1:6379/2')

@app.task
def task_test():
    print('task is running....')