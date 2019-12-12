Repositorio para almacenar datos en el servidor apkinson


## Starting Celery

### Overview:
Celery uses a worker process to run asynchronous tasks.
Communication between the main application and the worker application happens over a queue.
The Queue is a plugable component, that means you can choose from a variety of options (Redis, Rabbitmq, DjangoDB/SQLAlchemy).

### Specifics:

The main application implements task, that are discovered by the worker process that directly speaks with the queue. 
The tasks are implemented with annotations added to them and put into python files named 'tasks.py' under the application folder.
There is a direct integration for Django, to ease working with it.
e.G. Task implemented in "apkinson_server/apkinson_mobile/tasks.py" will be discovered upon starting the worker.
The worker is to be implemented under the file 'celery.py' in the main application (here: apkinson_server/apkinson_server/celery.py). 

### Implementation of a task:
A sample task can look as simple as this:
```python
@shared_task
def add(x, y):
    return x + y
```
Starting this task asynchronously in code:

```python
result = add.delay(x, y)
# get id, for further communication with the task backend:
result.id
```
Getting results from a method in the main application. This needs to job id generated previously
```python
from celery.result import AsyncResult
from apkinson_server import celery_app as capp
def get_results(id):
    result = AsyncResult(task_id, app=capp)
    if result.ready():
        if result.successful():
            res_val = result.get()
            # celanup job, otherwise database will run full:
            result.forget()
            return res_val
        else:
            result.forget()
            return "something went wrong, can return exception here"
    else:
        return "not ready yet"
```

### Steps to run the application using celery

- Starting redis with docker for one time use:
```bash
docker run -d --rm -p 6379:6379 redis
```
- starting the worker from ../apkinson_server

Do not like this in production, demonization is the key here.
[Celery demonization](https://docs.celeryproject.org/en/latest/userguide/daemonizing.html)

```bash
celery -A apkinson_server worker -l info
```
Run Django application with manage.py script (or from pycharm debugger)
```bash
 ./manage.py runserver
```


## Dummy implementation(spike)
from apkinson_mobile views and tasks:

```python
# example task:
@shared_task
def run_hello_sh():
    from random import randint
    wd = '/Users/bayerl/git/apkinson_server'
    subprocess.call([f'{wd}/hello_world.sh', f'{randint(0, 300)}'], shell=True)
    with open(f'{wd}/hello_file.txt') as f:
        lines = f.readlines()
    return lines[0]
```

```python
# Example workflow with calling a subprocess in hello
@csrf_exempt
def hello(request):
    if request.method == 'GET':
        result = run_hello_sh.delay()
        return HttpResponse(result.id)
    else:
        return HttpResponseNotAllowed()

@csrf_exempt
def get_hello(request, task_id):
    if request.method == 'GET':
        result = AsyncResult(task_id, app=capp)
        # should look up result in normal database first, otherwise this is just one shot
        if result.ready():
            if result.successful():
                res_val = result.get(1.0)
                # write shit where it belongs
                result.forget()
                return HttpResponse(res_val)
            else:
                print('Something went wrong, please resubmit request')
                result.forget()
                return HttpResponseGone(f'Computation of {task_id} failed, please resubmit request and/or data')
        else:
            return HttpResponse(f'Result for {task_id} not available, please try again later')


```
Happy Debugging!





