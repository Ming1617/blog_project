from celery import Celery
app=Celery('jcm_result',broker='redis://:@127.0.0.1:6379/2',
           backend='redis://:@127.0.0.1:6379/3')

@app.task
def task_test(a,b):
    print('task is running....')
    return a+b