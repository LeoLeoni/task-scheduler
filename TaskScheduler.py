import json
from datetime import datetime
import os
import sys
from crontab import CronTab

class TaskScheduler:

    def __init__(self):
        self.cron = CronTab(user=True)

    def load_task_config(self):
        """
        Loads the task config json file
        
        :return: Dict representing the task scheduler config
        """

        with open('config.json') as f:
            config = json.load(f)

        return config


    def schedule_task(self, task):
        """
        Schedules a task with a set time as specified in the config file

        :param task: Dict representing the config for a task
        """

        job = self.cron.new(
            command = task['task_location'],
            #comment = f'task_name={task["task_name"]}',
            comment = task['task_name'],
            user = True
        )

        try:
            job.setall(datetime.fromisoformat(task['task_scheduled_time']))
        except ValueError:
            print(f'Invalid datetime format in config file for task {task["task_name"]} ({task["task_scheduled_time"]})')
            job.delete()
            return

        # Since crontasks can only do minute granularity we're going to assume the task interval is in minutes
        if 'task_interval' in task:
            job.minute.also.every(task['task_interval'])

        #self.cron.write()
        print(f'Scheduled task {task["task_name"]}')

if __name__ == "__main__":

    args = sys.argv[1:] # cut off the filename in args

    # Error checking
    if len(args) == 0 or len(args) == 1:
        print('ERROR missing required arguments: "start"|"stop" "task name"')
        sys.exit()
    elif len(args) > 2:
        print('ERROR Too many arguments')
        sys.exit()

    option = args[0].lower()

    if option != 'start' and option != 'stop':
        print('ERROR first argument must be "start"|"stop"')
    option = args[0].lower()
    task_name = args[1]


    ts = TaskScheduler()

    conf = ts.load_task_config()

    for task in conf['task_config']:

        if task['task_name'] == task_name:

            if task['task_scheduled'] == True:
                # This means it will need scheduled
                ts.schedule_task(task)
            else:
                # Execute it immediately
                os.system(task['task_location'])
                print(f'Executed task {task["task_name"]}')

            # This is a success and we can now exit
            sys.exit()

    # At this point we've gone through the config file and not found the task name
    print('ERROR task name not found in config')
    sys.exit()